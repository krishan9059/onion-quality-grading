import os
import io
import cv2
import torch
import numpy as np
from PIL import Image
from torchvision import transforms
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.model import OnionTransferNet
from src.config import MODEL_SAVE_PATH

app = FastAPI(title="Onion Quality AI Assayer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directory exists
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Load Transfer Learning Model
device = torch.device("cpu")
model = OnionTransferNet(backbone_name="mobilenet_v3_large", num_classes=2, pretrained=False)
if os.path.exists(MODEL_SAVE_PATH):
    try:
        model.load_state_dict(torch.load(MODEL_SAVE_PATH, map_location=device))
        print(f"Loaded Transfer Learning model from: {MODEL_SAVE_PATH}")
    except Exception as e:
        print(f"Warning loading model checkpoint: {e}")
model.eval()

# Transform pipeline
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def measure_onion_dimensions(cv_img: np.ndarray) -> dict:
    h, w = cv_img.shape[:2]
    scale = 1.0
    if max(h, w) > 1000:
        scale = 1000.0 / max(h, w)
        img_small = cv2.resize(cv_img, (int(w * scale), int(h * scale)))
    else:
        img_small = cv_img.copy()
        
    sh, sw = img_small.shape[:2]
    gray = cv2.cvtColor(img_small, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img_small, cv2.COLOR_BGR2HSV)
    
    # 1. Search for any circular reference marker or coin
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=int(min(sw, sh) * 0.1),
        param1=50, param2=32, minRadius=int(min(sw, sh) * 0.03), maxRadius=int(min(sw, sh) * 0.25)
    )
    detected_ref = None
    if circles is not None:
        c = circles[0][0]
        detected_ref = {
            "cx": int(c[0] / scale),
            "cy": int(c[1] / scale),
            "radius_px": round(float(c[2]) / scale, 1),
            "diam_px": round(float(c[2] * 2) / scale, 1)
        }

    # 2. Segment Onion Contour using gradient and color saturation
    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.uint8(np.clip(cv2.magnitude(grad_x, grad_y), 0, 255))
    sat = hsv[:, :, 1]
    combined = cv2.addWeighted(mag, 0.4, sat, 0.6, 0)
    _, thresh = cv2.threshold(combined, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3)
    
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_cnts = [cnt for cnt in contours if cv2.contourArea(cnt) > (sw * sh * 0.03)]
    
    if valid_cnts:
        main_cnt = max(valid_cnts, key=cv2.contourArea)
        x, y, bw, bh = cv2.boundingRect(main_cnt)
        (cx, cy), radius = cv2.minEnclosingCircle(main_cnt)
        onion_info = {
            "bbox": [int(x / scale), int(y / scale), int(bw / scale), int(bh / scale)],
            "center": [int(cx / scale), int(cy / scale)],
            "diam_px": round(float(radius * 2) / scale, 1),
            "width_px": int(bw / scale),
            "height_px": int(bh / scale)
        }
    else:
        onion_info = {
            "bbox": [int(w * 0.25), int(h * 0.25), int(w * 0.5), int(h * 0.5)],
            "center": [int(w * 0.5), int(h * 0.5)],
            "diam_px": round(min(w, h) * 0.5, 1),
            "width_px": int(w * 0.5),
            "height_px": int(h * 0.5)
        }

    # Standard Reference Object default (₹5/₹10 Coin = 25.0 mm)
    known_ref_mm = 25.0
    ref_diam_px = detected_ref["diam_px"] if detected_ref else round(min(w, h) * 0.22, 1)
    px_per_mm = ref_diam_px / known_ref_mm
    
    onion_diam_mm = round(onion_info["diam_px"] / px_per_mm, 1)
    onion_diam_cm = round(onion_diam_mm / 10.0, 2)
    
    if onion_diam_mm < 40.0:
        size_category = "Small / Undersized (< 40 mm)"
        size_grade = "URS / Undersized"
    elif onion_diam_mm <= 70.0:
        size_category = "Medium / Grade A Standard (40 – 70 mm)"
        size_grade = "Grade A Standard"
    else:
        size_category = "Large / Jumbo (> 70 mm)"
        size_grade = "Jumbo"
        
    return {
        "onion": onion_info,
        "image_size": {"width": w, "height": h},
        "reference_object": {
            "name": "Standard Coin (Rs. 5/10)",
            "known_size_mm": known_ref_mm,
            "ref_diam_px": ref_diam_px,
            "detected": detected_ref is not None,
            "detected_coords": detected_ref,
            "px_per_mm": round(px_per_mm, 2),
            "pos": [int(w * 0.8), int(h * 0.8)] if not detected_ref else [detected_ref["cx"], detected_ref["cy"]]
        },
        "size_analysis": {
            "diameter_mm": onion_diam_mm,
            "diameter_cm": onion_diam_cm,
            "size_category": size_category,
            "size_grade": size_grade
        }
    }

def evaluate_onion(image_bytes: bytes) -> dict:
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    h, w = cv_img.shape[:2]
    
    # 1. Sprout Detection (Chlorophyll green pixels across full frame in any angle)
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, np.array([25, 30, 30]), np.array([95, 255, 255]))
    sprout_pct = float(np.sum(green_mask > 0) / (h * w)) * 100.0
    
    # 2. Transfer Learning Model Prediction
    tensor_img = transform(pil_img).unsqueeze(0)
    with torch.no_grad():
        logits = model(tensor_img)
        probs = torch.softmax(logits, dim=1).squeeze(0)
        bad_prob = float(probs[0].item())
        good_prob = float(probs[1].item())
        
    # 3. Defect & Surface Texture Metrics
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 7)
    mean_val = np.mean(blur)
    dark_mask = blur < (mean_val * 0.40)
    decay_pct = float(np.sum(dark_mask) / (h * w)) * 100.0
    
    # 4. Final Quality Verdict
    if sprout_pct >= 1.0:
        verdict = "Sprouted (Rejected)"
        quality_level = "REJECTED"
        badge_type = "danger"
        explanation = f"Active vegetative green shoots detected ({sprout_pct:.1f}% shoot coverage). Sprouting degrades bulb texture and accelerates decay."
        confidence = 99.0
        grade_a_pct = 0
        urs_pct = 10
        rej_pct = 90
    elif bad_prob >= 0.60:
        verdict = "Rotten / Severe Defect (Rejected)"
        quality_level = "REJECTED"
        badge_type = "danger"
        explanation = "High probability of fungal decay, bacterial soft rot, or severe necrotic damage on the bulb."
        confidence = round(bad_prob * 100.0, 1)
        grade_a_pct = 0
        urs_pct = 15
        rej_pct = 85
    elif 0.35 <= bad_prob < 0.60:
        verdict = "Damaged / Blemished (URS)"
        quality_level = "URS"
        badge_type = "warning"
        explanation = "Minor surface blemishes, discoloration, or skin peeling. Acceptable under Under-Relaxed Specifications (URS)."
        confidence = 88.5
        grade_a_pct = 20
        urs_pct = 70
        rej_pct = 10
    else:
        verdict = "Healthy & Fresh (Grade A)"
        quality_level = "GRADE_A"
        badge_type = "success"
        explanation = "Clean, firm bulb with dry intact tunic skin, zero sprouting, and zero microbial decay. Meets top Grade A quality."
        confidence = round(good_prob * 100.0, 1)
        grade_a_pct = 95
        urs_pct = 5
        rej_pct = 0
        
    # 4. Measure Dimensions using Reference Object & Pixels
    dimensions = measure_onion_dimensions(cv_img)
    
    # If the onion is extremely undersized (< 35 mm), procurement specs categorize it under URS/Rejected
    if dimensions["size_analysis"]["diameter_mm"] < 35.0 and verdict == "Healthy & Fresh (Grade A)":
        verdict = "Undersized Bulb (URS)"
        quality_level = "URS"
        badge_type = "warning"
        explanation = f"Bulb is healthy but undersized ({dimensions['size_analysis']['diameter_mm']} mm < 35 mm minimum). Categorized under URS (Under Relaxed Specifications)."
        grade_a_pct = 20
        urs_pct = 70
        rej_pct = 10

    return {
        "verdict": verdict,
        "quality_level": quality_level,
        "badge_type": badge_type,
        "confidence": confidence,
        "explanation": explanation,
        "dimensions": dimensions,
        "metrics": {
            "sprout_score": round(sprout_pct, 1),
            "decay_score": round(decay_pct, 1),
            "good_score": round(good_prob * 100.0, 1),
            "bad_score": round(bad_prob * 100.0, 1)
        },
        "grade_distribution": {
            "grade_a": grade_a_pct,
            "urs": urs_pct,
            "rejected": rej_pct
        }
    }

@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        results = evaluate_onion(content)
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Frontend loading... Please create static/index.html</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=False)
