import os

# Base paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = r"C:\Users\Asus\Downloads\ONIONN.v1i.multiclass"
MODEL_SAVE_PATH = os.path.join(PROJECT_ROOT, "models", "onion_quality_model.pt")
ONNX_SAVE_PATH = os.path.join(PROJECT_ROOT, "models", "onion_quality_model.onnx")

# Procurement & Grading Parameters (2026 Procurement Norms)
DEFAULT_GRADING_CONFIG = {
    "grade_a_min_diameter_mm": 35.0,     # Relaxed 2026 norm (formerly 45-55 mm)
    "grade_a_max_diameter_mm": 70.0,     # Max acceptable equatorial diameter
    "urs_min_diameter_mm": 25.0,         # Under Relaxed Specification lower bound
    "urs_max_diameter_mm": 80.0,         # Under Relaxed Specification upper bound
    "enable_urs": True,                  # Toggle between Grade A only and Grade A + URS
    "max_allowed_blemish_pct": 10.0,     # Maximum surface blemish allowed for Grade A
    "urs_max_blemish_pct": 25.0,         # Surface blemish tolerance for URS
    "confidence_level": 0.95,            # Statistical Confidence Interval (95%)
}

# Image Processing & Calibration Defaults
DEFAULT_CALIBRATION = {
    "default_px_per_mm": 3.8,            # Standard estimated pixel-per-mm for 640x640 tray capture
    "marker_type": "aruco",              # 'aruco', 'coin', or 'manual_tray'
    "coin_diameter_mm": 24.26,           # e.g., Standard Indian ₹5 / ₹10 coin
    "tray_width_mm": 300.0,              # Standard 30cm Mandi assay tray
}

# Training Hyperparameters
TRAIN_CONFIG = {
    "img_size": 224,
    "batch_size": 64,
    "epochs": 3,
    "learning_rate": 1e-3,
    "weight_decay": 1e-4,
    "num_classes": 2,                    # [0: Defective/Bad, 1: Good/Healthy]
    "device": "cpu"                      # will fallback to 'cpu' if cuda unavailable
}
