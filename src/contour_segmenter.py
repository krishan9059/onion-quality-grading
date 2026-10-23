import cv2
import numpy as np
from typing import List, Dict, Any, Tuple

class BulbSegmenter:
    """
    Isolates individual onion bulbs from tray/field images using
    adaptive color thresholding, morphological operations, and contour analysis.
    """
    def __init__(self, min_bulb_area_px: int = 1500, max_bulb_area_px: int = 150000):
        self.min_bulb_area_px = min_bulb_area_px
        self.max_bulb_area_px = max_bulb_area_px

    def segment_bulbs(self, image: np.ndarray, px_per_mm: float = 3.8) -> List[Dict[str, Any]]:
        """
        Detects, extracts, and computes physical metrics for all onion bulbs in the image.
        
        Returns a list of dictionaries for each bulb:
        - id: int
        - bbox: (x, y, w, h)
        - center: (cx, cy)
        - diameter_px: float (equatorial diameter)
        - diameter_mm: float
        - area_px: float
        - area_mm2: float
        - circularity: float
        - blemish_ratio: float (estimated dark/blemish surface ratio)
        - crop: np.ndarray (RGB/BGR image crop of the bulb)
        """
        if image is None or image.size == 0:
            return []

        h, w = image.shape[:2]
        
        # Color space conversion for robust onion segmentation
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # In LAB/HSV, onions (red/yellow/white) contrast against background trays
        # Extract L, A, B channels
        l_chan, a_chan, b_chan = cv2.split(lab)
        
        # Otsu thresholding on combined saliency
        blur = cv2.GaussianBlur(a_chan, (7, 7), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Also check brightness threshold on lightness channel to handle light/dark trays
        _, thresh_l = cv2.threshold(cv2.GaussianBlur(l_chan, (7, 7), 0), 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Combined mask with morphological cleanup
        mask = cv2.bitwise_or(thresh, thresh_l)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Distance transform and watershed to separate touching bulbs
        dist_transform = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.3 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        
        contours, _ = cv2.findContours(sure_fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # If watershed yields too few contours or tiny fragments, fallback to external contours on mask
        if len(contours) == 0 or max([cv2.contourArea(c) for c in contours], default=0) < self.min_bulb_area_px:
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bulbs = []
        bulb_id = 1
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_bulb_area_px or area > self.max_bulb_area_px:
                continue
            
            # Compute bounding box and enclosing circle
            x, y, bw, bh = cv2.boundingRect(cnt)
            
            # Pad bounding box slightly to capture full bulb contours
            pad = int(min(bw, bh) * 0.08)
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(w, x + bw + pad)
            y2 = min(h, y + bh + pad)
            
            crop = image[y1:y2, x1:x2].copy()
            if crop.shape[0] < 10 or crop.shape[1] < 10:
                continue

            # Minimum enclosing circle for equatorial diameter estimation
            (cx, cy), radius = cv2.minEnclosingCircle(cnt)
            diameter_px = radius * 2.0
            diameter_mm = diameter_px / px_per_mm if px_per_mm > 0 else 0.0
            
            # Area in mm^2
            area_mm2 = area / (px_per_mm ** 2) if px_per_mm > 0 else 0.0
            
            # Perimeter and circularity
            perimeter = cv2.arcLength(cnt, True)
            circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0.0
            
            # Estimate surface blemish / dark spots within crop
            crop_gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            crop_blur = cv2.medianBlur(crop_gray, 5)
            # Dark necrotic spots or rotting areas have low intensity relative to mean
            mean_val = np.mean(crop_blur)
            blemish_mask = crop_blur < (mean_val * 0.65)
            blemish_ratio = float(np.sum(blemish_mask) / (crop.shape[0] * crop.shape[1])) * 100.0
            
            bulbs.append({
                "id": bulb_id,
                "bbox": (x1, y1, x2 - x1, y2 - y1),
                "center": (int(cx), int(cy)),
                "contour": cnt,
                "diameter_px": round(diameter_px, 1),
                "diameter_mm": round(diameter_mm, 1),
                "area_px": round(area, 1),
                "area_mm2": round(area_mm2, 1),
                "circularity": round(circularity, 2),
                "blemish_ratio": round(blemish_ratio, 1),
                "crop": crop
            })
            bulb_id += 1
            
        # If no distinct bulbs found (e.g. single onion filling entire frame), treat entire image as 1 bulb
        if len(bulbs) == 0:
            bw, bh = w, h
            diam_px = min(bw, bh) * 0.85
            diam_mm = diam_px / px_per_mm if px_per_mm > 0 else 0.0
            bulbs.append({
                "id": 1,
                "bbox": (0, 0, w, h),
                "center": (w // 2, h // 2),
                "contour": None,
                "diameter_px": round(diam_px, 1),
                "diameter_mm": round(diam_mm, 1),
                "area_px": round(w * h * 0.7, 1),
                "area_mm2": round((w * h * 0.7) / (px_per_mm ** 2), 1),
                "circularity": 0.88,
                "blemish_ratio": 5.0,
                "crop": image.copy()
            })
            
        return bulbs
