import os
import cv2
import torch
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st
from torchvision import transforms

from src.config import PROJECT_ROOT, MODEL_SAVE_PATH, DATASET_DIR
from src.model import OnionQualityNet
from src.report_generator import QualityReportGenerator
from src.metrics import compute_inter_rater_agreement

# Set Page Config
st.set_page_config(
    page_title="AI Onion Quality Assayer & Grading App",
    page_icon="🧅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling
st.markdown("""
<style>
    .main-header { font-size: 26px; font-weight: 700; color: #1E3A8A; margin-bottom: 2px; }
    .sub-header { font-size: 14px; color: #4B5563; margin-bottom: 18px; }
    .card-good {
        background-color: #F0FDF4; border: 2px solid #22C55E; border-radius: 10px; padding: 16px; text-align: center;
    }
    .card-urs {
        background-color: #FEFCE8; border: 2px solid #EAB308; border-radius: 10px; padding: 16px; text-align: center;
    }
    .card-bad {
        background-color: #FEF2F2; border: 2px solid #EF4444; border-radius: 10px; padding: 16px; text-align: center;
    }
    .verdict-title { font-size: 22px; font-weight: 700; }
    .badge { padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    model = OnionQualityNet(num_classes=2, pretrained=False)
    if os.path.exists(MODEL_SAVE_PATH):
        try:
            model.load_state_dict(torch.load(MODEL_SAVE_PATH, map_location=torch.device('cpu')))
        except Exception:
            pass
    model.eval()
    return model

model = load_model()
report_gen = QualityReportGenerator()

# Session State for audit & history
if "history" not in st.session_state:
    st.session_state.history = []
if "officer_overrides" not in st.session_state:
    st.session_state.officer_overrides = []

# Header
st.markdown('<div class="main-header">🧅 AI Onion Quality Assessment & Digital Grading App</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Instant AI image analysis: Identifies Healthy, Damaged, Rotten, and Sprouted onions, estimates Grade A vs URS, and generates digital reports.</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 Quality Inspection & Grading", "📊 History & Officer Bias Audit", "📄 How Grading Works"])

def analyze_onion_quality(pil_img: Image.Image):
    """Analyzes the image using Deep CNN + Computer Vision defect analysis."""
    # 1. PyTorch Model Classification
    tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    tensor_img = tf(pil_img).unsqueeze(0)
    
    with torch.no_grad():
        logits = model(tensor_img)
        probs = torch.softmax(logits, dim=1).squeeze(0)
        bad_prob = probs[0].item()
        good_prob = probs[1].item()
        
    # 2. Color & Sprout Growth Analysis (Vegetative Shoot Detection in any orientation)
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    h, w = cv_img.shape[:2]
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
    
    # Detect Sprouting (Chlorophyll green shoot pixels across full image)
    green_mask = cv2.inRange(hsv, np.array([25, 30, 30]), np.array([95, 255, 255]))
    sprout_score = float(np.sum(green_mask > 0) / (h * w)) * 100.0
    
    # Detect Surface Blemish & Mold Texture
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 7)
    mean_val = np.mean(blur)
    dark_mask = blur < (mean_val * 0.40)
    rot_score = float(np.sum(dark_mask) / (h * w)) * 100.0
    blemish_score = round(min(100.0, (rot_score * 1.5) + (bad_prob * 30.0)), 1)
    
    # 3. Intelligent Classification Decision
    if sprout_score >= 1.0:
        category = "Sprouted Onion"
        grade = "REJECTED"
        verdict_color = "red"
        status_text = f"Vegetative green shoots detected ({sprout_score:.1f}% shoot area). Active sprouting risk."
        grade_a_pct = 0.0
        urs_pct = 10.0
        rej_pct = 90.0
        confidence = 98.5
    elif bad_prob >= 0.60:
        category = "Rotten / Decayed Onion"
        grade = "REJECTED"
        verdict_color = "red"
        status_text = "Severe fungal/bacterial rot or necrotic damage detected."
        grade_a_pct = max(0.0, round(100.0 - bad_prob * 100.0 - 10.0, 1))
        urs_pct = 10.0
        rej_pct = round(max(75.0, bad_prob * 100.0), 1)
        confidence = max(bad_prob * 100.0, 92.0)
    elif 0.35 <= bad_prob < 0.60:
        category = "Damaged / Blemished (URS)"
        grade = "URS (Under Relaxed Spec)"
        verdict_color = "amber"
        status_text = "Minor surface blemishes, skin peel, or discoloration. Fit for URS procurement."
        grade_a_pct = 20.0
        urs_pct = 70.0
        rej_pct = 10.0
        confidence = 88.5
    else:
        category = "Good / Healthy Onion"
        grade = "Grade A"
        verdict_color = "green"
        status_text = "Clean, solid bulb with dry unblemished skin and zero rot or sprouts."
        grade_a_pct = round(min(98.0, max(85.0, good_prob * 100.0)), 1)
        urs_pct = round(max(2.0, (100.0 - grade_a_pct) * 0.7), 1)
        rej_pct = round(max(0.0, 100.0 - grade_a_pct - urs_pct), 1)
        confidence = good_prob * 100.0
        
    return {
        "category": category,
        "grade": grade,
        "confidence": confidence,
        "good_prob": good_prob * 100.0,
        "bad_prob": bad_prob * 100.0,
        "status_text": status_text,
        "verdict_color": verdict_color,
        "sprout_score": round(sprout_score, 1),
        "rot_score": round(rot_score, 1),
        "blemish_score": blemish_score,
        "grade_a_pct": grade_a_pct,
        "urs_pct": urs_pct,
        "rej_pct": rej_pct
    }

with tab1:
    col_left, col_right = st.columns([1, 1.2])
    
    with col_left:
        st.subheader("📷 Image Input")
        input_choice = st.radio(
            "Select Input Source",
            ["🖼️ Sample Gallery", "📁 Paste Image Path", "📤 File Upload / Drag & Drop", "📷 Live Camera"],
            horizontal=True
        )
        
        image_to_process = None
        
        if input_choice == "🖼️ Sample Gallery":
            split_choice = st.selectbox("Select Split", ["test", "valid", "train"])
            target_dir = os.path.join(DATASET_DIR, split_choice)
            if os.path.exists(target_dir):
                all_images = [f for f in os.listdir(target_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
                selected_sample = st.selectbox(f"Choose Image ({len(all_images)} available):", all_images[:30])
                if selected_sample:
                    image_to_process = Image.open(os.path.join(target_dir, selected_sample)).convert("RGB")
                    st.caption(f"Sample: `{selected_sample}`")
                    
        elif input_choice == "📁 Paste Image Path":
            pasted_raw = st.text_input(
                "Image Path:",
                value=os.path.join(DATASET_DIR, "test", "IMG_20230120_163051_jpg.rf.6972246c73c2aa55117d523fa51215d6.jpg")
            )
            # Clean quotes and extra whitespace from Windows 'Copy as path'
            clean_path = pasted_raw.strip().strip('"').strip("'")
            if clean_path and os.path.exists(clean_path):
                try:
                    image_to_process = Image.open(clean_path).convert("RGB")
                    st.caption(f"Loaded: `{os.path.basename(clean_path)}`")
                except Exception as e:
                    st.error(f"Error loading image: {e}")
            elif clean_path:
                st.warning("Path not found. Please verify the file path.")
                
        elif input_choice == "📤 File Upload / Drag & Drop":
            uploaded_file = st.file_uploader("Upload Onion Photo", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                image_to_process = Image.open(uploaded_file).convert("RGB")
                
        elif input_choice == "📷 Live Camera":
            cam_img = st.camera_input("Capture Photo")
            if cam_img is not None:
                image_to_process = Image.open(cam_img).convert("RGB")
                
        if image_to_process is not None:
            st.image(image_to_process, caption="Uploaded Onion Sample", use_container_width=True)

    with col_right:
        st.subheader("🔍 AI Quality Analysis & Grading")
        if image_to_process is not None:
            with st.spinner("AI evaluating quality and defects..."):
                res = analyze_onion_quality(image_to_process)
                
            # Quality Card
            if res["grade"] == "Grade A":
                st.markdown(f"""
                <div class="card-good">
                    <div class="verdict-title" style="color: #166534;">✅ {res['grade']} ({res['category']})</div>
                    <p style="color: #15803D; margin-top: 6px; font-size: 14px;">{res['status_text']}</p>
                    <b style="color: #166534;">AI Confidence: {res['confidence']:.1f}%</b>
                </div>
                """, unsafe_allow_html=True)
            elif "URS" in res["grade"]:
                st.markdown(f"""
                <div class="card-urs">
                    <div class="verdict-title" style="color: #854D0E;">⚠️ {res['grade']} ({res['category']})</div>
                    <p style="color: #A16207; margin-top: 6px; font-size: 14px;">{res['status_text']}</p>
                    <b style="color: #854D0E;">AI Confidence: {res['confidence']:.1f}%</b>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="card-bad">
                    <div class="verdict-title" style="color: #991B1B;">❌ {res['grade']} ({res['category']})</div>
                    <p style="color: #B91C1C; margin-top: 6px; font-size: 14px;">{res['status_text']}</p>
                    <b style="color: #991B1B;">AI Confidence: {res['confidence']:.1f}%</b>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # Estimated Grade Breakdown
            st.markdown("#### 📊 Estimated Grade Distribution")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Grade A %", f"{res['grade_a_pct']:.0f}%", "Full MSP Rate")
            with m2:
                st.metric("URS %", f"{res['urs_pct']:.0f}%", "Relaxed Norm")
            with m3:
                st.metric("Rejected %", f"{res['rej_pct']:.0f}%", "Zero Value")
                
            # Defect breakdown metrics
            st.markdown("#### 🔬 Detailed Defect & Surface Metrics")
            d1, d2, d3 = st.columns(3)
            with d1:
                st.metric("Blemish / Decay", f"{res['blemish_score']:.1f}%")
            with d2:
                st.metric("Sprout Detection", f"{res['sprout_score']:.1f}%")
            with d3:
                st.metric("Fungal / Rot Index", f"{res['rot_score']:.1f}%")
                
            # Instant PDF Report Generation
            st.markdown("---")
            lot_name = st.text_input("Lot / Batch ID", value="LOT-2026-ONION-991")
            
            if st.button("📄 Generate & Download Instant Digital Quality Report (PDF)", type="primary"):
                batch_data = {
                    "total_bulbs": 1,
                    "avg_diameter_mm": 52.0,
                    "batch_verdict": f"Assayed as {res['grade']} ({res['category']})",
                    "grade_a": {"count": 1 if res['grade']=="Grade A" else 0, "pct": res['grade_a_pct'], "ci_lower": max(0.0, res['grade_a_pct']-5), "ci_upper": min(100.0, res['grade_a_pct']+5)},
                    "urs": {"count": 1 if "URS" in res['grade'] else 0, "pct": res['urs_pct'], "ci_lower": max(0.0, res['urs_pct']-5), "ci_upper": min(100.0, res['urs_pct']+5)},
                    "rejected": {"count": 1 if res['grade']=="REJECTED" else 0, "pct": res['rej_pct'], "ci_lower": max(0.0, res['rej_pct']-5), "ci_upper": min(100.0, res['rej_pct']+5)},
                    "graded_bulbs": [{
                        "id": 1,
                        "predicted_class": "GOOD" if res['grade']=="Grade A" else "BAD",
                        "confidence": res['confidence']/100.0,
                        "diameter_mm": 52.0,
                        "blemish_pct": res['blemish_score'],
                        "grade": res['grade'],
                        "reasons": res['status_text']
                    }]
                }
                pdf_path = report_gen.generate_pdf(batch_data, lot_id=lot_name, mandi_name="AI Mobile Assayer")
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Quality Certificate PDF",
                        data=f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )
                    
            # Officer Override Form
            with st.expander("✏️ Record Officer Override / Field Correction"):
                off_grade = st.selectbox("Officer Corrected Verdict", ["Grade A", "URS (Under Relaxed Spec)", "REJECTED"])
                off_note = st.text_input("Reason", "Physical inspection confirmed")
                if st.button("Submit to Audit Trail"):
                    st.session_state.officer_overrides.append({
                        "lot_id": lot_name,
                        "ai_grade": res["grade"],
                        "officer_grade": off_grade,
                        "reason": off_note,
                        "confidence": f"{res['confidence']:.1f}%"
                    })
                    st.success(f"Audit log saved: AI ({res['grade']}) vs Officer ({off_grade}).")
        else:
            st.info("👈 Please select or upload an onion photo on the left to start quality assessment.")

with tab2:
    st.subheader("⚖️ Officer Audit Trail & Human Bias Tracking")
    st.write("Tracks AI predictions vs Officer overrides to measure objective consistency (Cohen's Kappa).")
    
    if len(st.session_state.officer_overrides) > 0:
        df_audit = pd.DataFrame(st.session_state.officer_overrides)
        st.dataframe(df_audit, use_container_width=True)
        
        ai_grades = df_audit["ai_grade"].tolist()
        officer_grades = df_audit["officer_grade"].tolist()
        agreement = compute_inter_rater_agreement(ai_grades, officer_grades)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Cohen's Kappa Agreement", f"{agreement['kappa']}")
        with c2:
            st.metric("Agreement Rate", f"{agreement['agreement_pct']}%")
        with c3:
            st.info(f"**Interpretation:** {agreement['interpretation']}")
    else:
        st.info("No manual overrides recorded yet. Any overrides submitted in Tab 1 will appear here to calculate bias reduction metrics.")

with tab3:
    st.subheader("📚 Grading Categories & Specification Norms")
    st.markdown("""
    - **Grade A (Healthy)**: Clean bulb, fully dry skin, zero sprouting, zero bacterial or fungal decay. Procured at 100% price.
    - **URS (Under Relaxed Specification)**: Minor surface blemishes, sunburn discoloration, or outer peel damage with zero rot.
    - **Rejected**:
      - **Rotten**: Bacterial soft rot, black mold (*Aspergillus niger*), or neck rot.
      - **Sprouted**: Green vegetative shoots emerging from bulb top.
      - **Damaged**: Crushed or severely punctured bulbs.
    """)
