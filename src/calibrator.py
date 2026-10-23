import cv2
import numpy as np

class ScaleCalibrator:
    """
    Calibrates image scale (pixels per millimeter) using:
    1. ArUco Marker (e.g., DICT_4X4_50 with known physical width, e.g. 30mm)
    2. Circular Coin Reference (e.g. Indian ₹5/₹10 coin with known diameter, e.g. 24.26mm)
    3. Tray Width / Manual Reference
    4. Default Mandi Tray Preset
    """
    def __init__(self, default_px_per_mm: float = 3.8):
        self.px_per_mm = default_px_per_mm

    def calibrate_aruco(self, image: np.ndarray, marker_real_size_mm: float = 30.0) -> float:
        """Detects ArUco marker and computes px_per_mm."""
        try:
            aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
            parameters = cv2.aruco.DetectorParameters()
            detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
            corners, ids, _ = detector.detectMarkers(image)
            
            if ids is not None and len(corners) > 0:
                # Compute width of first detected marker
                pts = corners[0][0]
                side_px = np.linalg.norm(pts[0] - pts[1])
                self.px_per_mm = float(side_px / marker_real_size_mm)
                return self.px_per_mm
        except Exception:
            pass
        return self.px_per_mm

    def calibrate_coin(self, image: np.ndarray, coin_real_diameter_mm: float = 24.26) -> float:
        """Detects circular coin using HoughCircles and computes px_per_mm."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            circles = cv2.HoughCircles(
                blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100,
                param1=50, param2=30, minRadius=20, maxRadius=100
            )
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                # Take the best detected circle radius
                radius_px = circles[0][2]
                diameter_px = radius_px * 2.0
                self.px_per_mm = float(diameter_px / coin_real_diameter_mm)
                return self.px_per_mm
        except Exception:
            pass
        return self.px_per_mm

    def calibrate_tray_width(self, image_width_px: int, tray_real_width_mm: float = 300.0) -> float:
        """Calibrates scale assuming the image frame spans the full tray width."""
        if tray_real_width_mm > 0:
            self.px_per_mm = float(image_width_px / tray_real_width_mm)
        return self.px_per_mm

    def pixels_to_mm(self, pixels: float) -> float:
        """Converts pixel distance to millimeters."""
        if self.px_per_mm <= 0:
            return 0.0
        return float(pixels / self.px_per_mm)

    def mm_to_pixels(self, mm: float) -> float:
        """Converts millimeters to pixel distance."""
        return float(mm * self.px_per_mm)
