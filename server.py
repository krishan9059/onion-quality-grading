import os
import io
import cv2
import torch
import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.cv_multi_detector import MultiOnionCVDetector

app = FastAPI(title="AI Multi-Bulb Onion Quality Assayer & Sizing Engine")

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

# Initialize multi-bulb detector
detector = MultiOnionCVDetector()

@app.post("/api/analyze")
@app.post("/api/predict")
async def analyze_image(file: UploadFile = File(...)):
    """
    Automated Multi-Bulb Detection & Sizing Engine:
    - Automatically locates and counts ALL onions in the image.
    - Measures equatorial diameter (mm) of each bulb.
    - Classifies EACH bulb individually (Good, Rotten, Sprouted, URS).
    - Returns annotated image with per-bulb boxes and detailed breakdown.
    """
    try:
        content = await file.read()
        pil_img = Image.open(io.BytesIO(content)).convert("RGB")
        results = detector.process_image(pil_img)
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": "Multi-Bulb Onion Quality & Size AI Assayer"}

@app.get("/api/samples")
async def get_samples():
    return []

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Frontend loading...</h1>"

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
