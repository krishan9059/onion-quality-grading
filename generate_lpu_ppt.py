# -*- coding: utf-8 -*-
"""
Generate 6-Slide High-Impact Executive Presentation for:
Onion Quality and Grading of Onions
Author: Krishan Kumar | Lovely Professional University
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation(output_path="Onion_Quality_Grading_Presentation_Krishan_Kumar.pptx"):
    prs = Presentation()
    # Set 16:9 Widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Color Palette
    C_NAVY = RGBColor(15, 23, 42)       # #0F172A
    C_BLUE = RGBColor(30, 58, 138)      # #1E3A8A
    C_TEAL = RGBColor(15, 118, 110)     # #0F766E
    C_GREEN = RGBColor(16, 185, 129)    # #10B981
    C_LIGHT_BG = RGBColor(248, 250, 252)# #F8FAFC
    C_CARD_BG = RGBColor(255, 255, 255) # White
    C_BORDER = RGBColor(226, 232, 240)  # #E2E8F0
    C_TEXT_DARK = RGBColor(30, 41, 59)  # #1E293B
    C_TEXT_MUTED = RGBColor(100, 116, 139) # #64748B
    C_RED = RGBColor(239, 68, 68)       # #EF4444
    C_AMBER = RGBColor(245, 158, 11)    # #F59E0B
    C_WHITE = RGBColor(255, 255, 255)

    # Helper: Add Slide Header
    def add_header(slide, title_text, category_text="LOVELY PROFESSIONAL UNIVERSITY | B.TECH CAPSTONE PROJECT"):
        # Category / Breadcrumb
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_right = tf_cat.margin_top = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_TEAL
        p_cat.font.name = "Arial"

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = C_BLUE
        p_title.font.name = "Arial"

        # Divider Line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = C_BORDER
        line.line.color.rgb = C_BORDER

    # Helper: Add Background Canvas
    def set_slide_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_LIGHT_BG
        bg.line.fill.background()
        return bg

    # =========================================================================
    # SLIDE 1: TITLE & HERO SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)

    # Top Brand Ribbon
    ribbon = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.15))
    ribbon.fill.solid()
    ribbon.fill.fore_color.rgb = C_BLUE
    ribbon.line.fill.background()

    # Main Card Container
    card1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.7), Inches(11.733), Inches(6.1))
    card1.fill.solid()
    card1.fill.fore_color.rgb = C_CARD_BG
    card1.line.color.rgb = C_BORDER
    card1.line.width = Pt(1)

    # LPU Logo
    lpu_logo_path = os.path.join(os.path.dirname(__file__), "assets", "lpu_logo.png")
    if os.path.exists(lpu_logo_path):
        s1.shapes.add_picture(lpu_logo_path, Inches(1.2), Inches(1.1), width=Inches(2.5))

    # University Header Text
    univ_box = s1.shapes.add_textbox(Inches(3.9), Inches(1.1), Inches(8.2), Inches(0.8))
    tf_u = univ_box.text_frame
    tf_u.word_wrap = True
    p_u1 = tf_u.paragraphs[0]
    p_u1.text = "LOVELY PROFESSIONAL UNIVERSITY"
    p_u1.font.size = Pt(14)
    p_u1.font.bold = True
    p_u1.font.color.rgb = C_NAVY
    p_u2 = tf_u.add_paragraph()
    p_u2.text = "School of Computer Science & Engineering | Department of CSE | Session 2025-2026"
    p_u2.font.size = Pt(10.5)
    p_u2.font.color.rgb = C_TEXT_MUTED

    # Project Title
    title_box1 = s1.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.9), Inches(1.5))
    tf_t1 = title_box1.text_frame
    tf_t1.word_wrap = True
    p_t1 = tf_t1.paragraphs[0]
    p_t1.text = "AI-Based Quality Assessment and Grading of Onions"
    p_t1.font.size = Pt(28)
    p_t1.font.bold = True
    p_t1.font.color.rgb = C_BLUE
    p_t2 = tf_t1.add_paragraph()
    p_t2.text = "A Multi-Spectral Deep Learning & Scale-Calibrated Vision Framework for APMC Mandi Produce Certification"
    p_t2.font.size = Pt(13)
    p_t2.font.color.rgb = C_TEAL
    p_t2.space_before = Pt(6)

    # 4 Key Metrics Badges
    badges = [
        ("94.44% Accuracy", "MobileNetV3 2-Stage Transfer Learning", C_GREEN),
        ("< 120 ms Latency", "Commodity CPU Edge-Deployable REST API", C_BLUE),
        ("0.41 mm Sizing Error", "Interactive Reference Coin Calibration", C_AMBER),
        ("APMC Mandi Norms", "Grade A, URS, Rejection & Cohen's Kappa", C_TEAL),
    ]

    for idx, (b_title, b_sub, b_col) in enumerate(badges):
        bx = Inches(1.2 + idx * 2.78)
        by = Inches(3.9)
        bw = Inches(2.6)
        bh = Inches(1.2)
        
        b_shape = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, by, bw, bh)
        b_shape.fill.solid()
        b_shape.fill.fore_color.rgb = C_LIGHT_BG
        b_shape.line.color.rgb = b_col
        b_shape.line.width = Pt(1.5)

        tf_b = b_shape.text_frame
        tf_b.word_wrap = True
        tf_b.margin_left = tf_b.margin_right = Inches(0.12)
        tf_b.margin_top = Inches(0.15)
        p_b1 = tf_b.paragraphs[0]
        p_b1.text = b_title
        p_b1.font.size = Pt(12)
        p_b1.font.bold = True
        p_b1.font.color.rgb = b_col
        p_b2 = tf_b.add_paragraph()
        p_b2.text = b_sub
        p_b2.font.size = Pt(8.5)
        p_b2.font.color.rgb = C_TEXT_DARK
        p_b2.space_before = Pt(3)

    # Student Credits Box (Bottom)
    cred_box = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(5.4), Inches(10.9), Inches(1.0))
    cred_box.fill.solid()
    cred_box.fill.fore_color.rgb = RGBColor(239, 246, 255) # Light blue
    cred_box.line.color.rgb = C_BLUE
    cred_box.line.width = Pt(1)

    tf_c = cred_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = Inches(0.2)
    tf_c.margin_top = Inches(0.12)
    p_c1 = tf_c.paragraphs[0]
    p_c1.text = "SUBMITTED BY: Krishan Kumar | Registration Number: 12410760 | Section: K2P24WM"
    p_c1.font.size = Pt(12)
    p_c1.font.bold = True
    p_c1.font.color.rgb = C_NAVY
    p_c2 = tf_c.add_paragraph()
    p_c2.text = "Bachelor of Technology in Computer Science & Engineering | Lovely Professional University, Punjab, India"
    p_c2.font.size = Pt(9.5)
    p_c2.font.color.rgb = C_TEXT_MUTED
    p_c2.space_before = Pt(3)


    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT & PROJECT OBJECTIVES (Project Part 1)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_header(s2, "Problem Statement, Agricultural Motivation & Project Objectives")

    # Column 1: The Crisis in Mandi Procurement (Left Card)
    c1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.4))
    c1.fill.solid()
    c1.fill.fore_color.rgb = C_CARD_BG
    c1.line.color.rgb = C_BORDER
    c1.line.width = Pt(1)

    tf_c1 = c1.text_frame
    tf_c1.word_wrap = True
    tf_c1.margin_left = tf_c1.margin_right = tf_c1.margin_top = Inches(0.25)
    p_c1_t = tf_c1.paragraphs[0]
    p_c1_t.text = "The Mandi Procurement Crisis"
    p_c1_t.font.size = Pt(14)
    p_c1_t.font.bold = True
    p_c1_t.font.color.rgb = C_RED

    problems = [
        ("Massive Post-Harvest Loss:", "India produces 25M+ metric tonnes annually; 25%–40% is lost to fungal rot (Aspergillus niger) and premature sprouting during transit and storage."),
        ("Human Subjectivity & Bias:", "In APMC Mandis, grading is manual. Quality inspectors look at a heap for 3-5 seconds and assign arbitrary price deductions, creating severe grower disputes."),
        ("Ignorance of URS Norms:", "Government procurement (NAFED) legally permits 'Under-Relaxed Specifications' (35–40 mm) at a fair 10-15% discount. Manual assayer glance arbitrarily rejects these valid lots."),
        ("Zero Digital Auditability:", "Traditional assay slips lack photographic proof, timestamps, or physical caliper measurements, leaving smallholder farmers with no legal right of appeal.")
    ]
    for p_head, p_desc in problems:
        p_h = tf_c1.add_paragraph()
        p_h.text = "• " + p_head
        p_h.font.size = Pt(10.5)
        p_h.font.bold = True
        p_h.font.color.rgb = C_NAVY
        p_h.space_before = Pt(8)
        p_d = tf_c1.add_paragraph()
        p_d.text = "   " + p_desc
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = C_TEXT_DARK

    # Column 2: What We Set Out To Solve (Right Card)
    c2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.4))
    c2.fill.solid()
    c2.fill.fore_color.rgb = C_CARD_BG
    c2.line.color.rgb = C_BORDER
    c2.line.width = Pt(1)

    tf_c2 = c2.text_frame
    tf_c2.word_wrap = True
    tf_c2.margin_left = tf_c2.margin_right = tf_c2.margin_top = Inches(0.25)
    p_c2_t = tf_c2.paragraphs[0]
    p_c2_t.text = "Core Project Deliverables & Objectives"
    p_c2_t.font.size = Pt(14)
    p_c2_t.font.bold = True
    p_c2_t.font.color.rgb = C_TEAL

    objectives = [
        ("Automated Multi-Defect Vision:", "Engineer a deep learning classifier that isolates fresh healthy bulbs from fungal rot and emerging green vegetative shoots with >94% accuracy."),
        ("Scale Sizing without Depth Cameras:", "Develop a zero-hardware optical calibration engine using standard reference coins (Rs. 5/10) to calculate true equatorial diameter in mm and cm."),
        ("Official Mandi Policy Decision Engine:", "Map defect probabilities and physical millimeter dimensions into commercial tiers: Grade A (40-70mm), URS (35-40mm), and Rejection."),
        ("Mathematical Bias Audit Trail:", "Compute inter-rater reliability via Cohen's Kappa score to objectively verify AI-human consistency and eliminate fraudulent lot downgrades.")
    ]
    for o_head, o_desc in objectives:
        p_oh = tf_c2.add_paragraph()
        p_oh.text = "• " + o_head
        p_oh.font.size = Pt(10.5)
        p_oh.font.bold = True
        p_oh.font.color.rgb = C_TEAL
        p_oh.space_before = Pt(8)
        p_od = tf_c2.add_paragraph()
        p_od.text = "   " + o_desc
        p_od.font.size = Pt(9)
        p_od.font.color.rgb = C_TEXT_DARK


    # =========================================================================
    # SLIDE 3: SYSTEM METHODOLOGY & TECHNICAL ARCHITECTURE (Project Part 2)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)
    add_header(s3, "System Methodology: Architecture, Transfer Learning & Calibration")

    # Architecture Diagram (Top Section)
    arch_img_path = os.path.join(os.path.dirname(__file__), "assets", "architecture_diagram.png")
    if os.path.exists(arch_img_path):
        s3.shapes.add_picture(arch_img_path, Inches(0.8), Inches(1.5), width=Inches(11.733))

    # 3 Pillar Cards (Bottom Section)
    pillars = [
        ("1. 2-Stage Transfer Learning", 
         "Backbone: MobileNetV3-Large\n"
         "• Stage 1 (Warmup): Frozen backbone, train Linear(960->256) head for 2 epochs (lr=1e-3).\n"
         "• Stage 2 (Fine-Tuning): Unfreeze full backbone with differential lr=1e-4 & Cosine Annealing.\n"
         "• Validation Acc: 94.44% | F1 = 0.9405", C_BLUE),
        
        ("2. 360° Chlorophyll Shoot Engine", 
         "Dual-Spectrum HSV + CIE-Lab Filter\n"
         "• Isolates vegetative green shoots (HSV H: 25°-95°, Lab a* < -5) regardless of orientation.\n"
         "• Prevents false negatives from horizontal shoots blending with dry brown tunics.\n"
         "• Sprout Detection Confidence: 99.0%", C_TEAL),
        
        ("3. Optical Reference Sizing", 
         "Scale Ratio Formula: S = D_ref(px) / 25.0mm\n"
         "• True Diameter (mm) = D_onion(px) / S\n"
         "• Eliminates $2,500 stereo cameras & fixed mounts.\n"
         "• Mean Vernier Error: 0.41 mm (>99.1% Acc)\n"
         "• Classifies: Grade A vs. URS vs. Undersized", C_AMBER)
    ]

    for idx, (p_title, p_body, p_col) in enumerate(pillars):
        px = Inches(0.8 + idx * 4.0)
        py = Inches(3.9)
        pw = Inches(3.733)
        ph = Inches(3.1)

        p_card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, py, pw, ph)
        p_card.fill.solid()
        p_card.fill.fore_color.rgb = C_CARD_BG
        p_card.line.color.rgb = p_col
        p_card.line.width = Pt(1.5)

        tf_p = p_card.text_frame
        tf_p.word_wrap = True
        tf_p.margin_left = tf_p.margin_right = tf_p.margin_top = Inches(0.18)
        p_pt = tf_p.paragraphs[0]
        p_pt.text = p_title
        p_pt.font.size = Pt(11.5)
        p_pt.font.bold = True
        p_pt.font.color.rgb = p_col

        for line in p_body.split("\n"):
            p_l = tf_p.add_paragraph()
            p_l.text = line
            p_l.font.size = Pt(8.8)
            p_l.font.color.rgb = C_TEXT_DARK
            p_l.space_before = Pt(3)


    # =========================================================================
    # SLIDE 4: SYSTEM IMPLEMENTATION & EXPERIMENTAL RESULTS (Project Part 3)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)
    add_header(s4, "System Implementation, Verification & Empirical Results")

    # Left Column: Experimental Visual Verification Image
    case_img_path = os.path.join(os.path.dirname(__file__), "assets", "case_study_images.png")
    if os.path.exists(case_img_path):
        s4.shapes.add_picture(case_img_path, Inches(0.8), Inches(1.5), width=Inches(5.7))

    # Caption for Left Image
    cap_box = s4.shapes.add_textbox(Inches(0.8), Inches(4.7), Inches(5.7), Inches(0.4))
    tf_cap = cap_box.text_frame
    p_cap = tf_cap.paragraphs[0]
    p_cap.text = "Figure 4.1: Live Inference Verification on Harvest Bulbs (Fresh vs. Horizontal Sprout)"
    p_cap.font.size = Pt(8.5)
    p_cap.font.italic = True
    p_cap.font.color.rgb = C_TEXT_MUTED

    # Bottom Left Box: Full Stack Specs
    stack_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.15), Inches(5.7), Inches(1.85))
    stack_box.fill.solid()
    stack_box.fill.fore_color.rgb = C_CARD_BG
    stack_box.line.color.rgb = C_BORDER
    tf_st = stack_box.text_frame
    tf_st.word_wrap = True
    tf_st.margin_left = tf_st.margin_top = Inches(0.15)
    p_st_t = tf_st.paragraphs[0]
    p_st_t.text = "Full-Stack Production Implementation"
    p_st_t.font.size = Pt(11)
    p_st_t.font.bold = True
    p_st_t.font.color.rgb = C_BLUE
    st_lines = [
        "• Asynchronous REST API: FastAPI + Uvicorn (< 120 ms CPU latency).",
        "• Pure HTML5/Canvas Client: Zero UI dependencies, animated cybernetic laser scan bar.",
        "• Interactive Touch/Mouse Canvas: Drag and scale golden reference coin overlay.",
        "• Official LPU ReportLab Generator: 13-page automated capstone report PDF."
    ]
    for st_l in st_lines:
        p_s = tf_st.add_paragraph()
        p_s.text = st_l
        p_s.font.size = Pt(8.2)
        p_s.font.color.rgb = C_TEXT_DARK

    # Right Column: Performance Tables & Cohen's Kappa (Card)
    rc = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.5))
    rc.fill.solid()
    rc.fill.fore_color.rgb = C_CARD_BG
    rc.line.color.rgb = C_BORDER

    tf_rc = rc.text_frame
    tf_rc.word_wrap = True
    tf_rc.margin_left = tf_rc.margin_right = tf_rc.margin_top = Inches(0.2)
    p_rc_t = tf_rc.paragraphs[0]
    p_rc_t.text = "Empirical Validation Metrics"
    p_rc_t.font.size = Pt(13)
    p_rc_t.font.bold = True
    p_rc_t.font.color.rgb = C_TEAL

    # Table 1: Classification Report
    p_t1_t = tf_rc.add_paragraph()
    p_t1_t.text = "1. Classification Performance (54 Hold-Out Validation Samples):"
    p_t1_t.font.size = Pt(9.5)
    p_t1_t.font.bold = True
    p_t1_t.space_before = Pt(6)

    # Let's add classification table
    cls_table_shape = s4.shapes.add_table(4, 4, Inches(7.0), Inches(2.35), Inches(5.3), Inches(1.1))
    cls_table = cls_table_shape.table
    cls_table.columns[0].width = Inches(2.3)
    cls_table.columns[1].width = Inches(1.0)
    cls_table.columns[2].width = Inches(1.0)
    cls_table.columns[3].width = Inches(1.0)

    cls_headers = ["Class Category", "Precision", "Recall", "F1-Score"]
    cls_row1 = ["Defective (Rot / Sprout)", "0.95", "0.90", "0.92"]
    cls_row2 = ["Healthy (Grade A Fresh)", "0.94", "0.97", "0.95"]
    cls_row3 = ["Overall Weighted Average", "0.94", "0.94", "0.9405"]

    for col_i, h in enumerate(cls_headers):
        cell = cls_table.cell(0, col_i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_TEAL
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(8)
            p.font.bold = True
            p.font.color.rgb = C_WHITE
            p.alignment = PP_ALIGN.CENTER

    for row_i, r_data in enumerate([cls_row1, cls_row2, cls_row3]):
        for col_i, val in enumerate(r_data):
            cell = cls_table.cell(row_i + 1, col_i)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if row_i == 2 else C_WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(8)
                p.font.bold = (row_i == 2)
                p.font.color.rgb = C_NAVY
                p.alignment = PP_ALIGN.CENTER if col_i > 0 else PP_ALIGN.LEFT

    # Table 2: Sizing Accuracy Callout
    sz_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), Inches(3.6), Inches(5.3), Inches(1.4))
    sz_box.fill.solid()
    sz_box.fill.fore_color.rgb = RGBColor(254, 243, 199) # Light amber
    sz_box.line.color.rgb = C_AMBER
    tf_sz = sz_box.text_frame
    tf_sz.word_wrap = True
    tf_sz.margin_left = tf_sz.margin_top = Inches(0.12)
    p_sz_t = tf_sz.paragraphs[0]
    p_sz_t.text = "2. Physical Vernier Caliper Benchmark (Sub-mm Precision):"
    p_sz_t.font.size = Pt(9.5)
    p_sz_t.font.bold = True
    p_sz_t.font.color.rgb = RGBColor(146, 64, 14)
    sz_pts = [
        "• Tested against digital vernier caliper (0.01mm resolution) ground-truth.",
        "• Rs. 5 Coin: 25.00mm (0.00mm err) | Grade A Bulb: 52.40mm vs 51.85mm AI (0.55mm err)",
        "• Mean Absolute Error: 0.41 mm | Sizing Accuracy: 99.17%"
    ]
    for pt in sz_pts:
        p_z = tf_sz.add_paragraph()
        p_z.text = pt
        p_z.font.size = Pt(8)
        p_z.font.color.rgb = C_TEXT_DARK

    # Table 3: Cohen's Kappa Box
    kap_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), Inches(5.15), Inches(5.3), Inches(1.65))
    kap_box.fill.solid()
    kap_box.fill.fore_color.rgb = RGBColor(240, 253, 250) # Light teal
    kap_box.line.color.rgb = C_TEAL
    tf_k = kap_box.text_frame
    tf_k.word_wrap = True
    tf_k.margin_left = tf_k.margin_top = Inches(0.12)
    p_kt = tf_k.paragraphs[0]
    p_kt.text = "3. Inter-Rater Reliability & Human Bias Reduction:"
    p_kt.font.size = Pt(9.5)
    p_kt.font.bold = True
    p_kt.font.color.rgb = C_TEAL
    k_pts = [
        "• Cohen's Kappa Formula: κ = (P_observed - P_chance) / (1 - P_chance)",
        "• Across 120 Mandi procurement trials: P_obs = 0.925, P_chance = 0.485",
        "• Resulting Score: κ = 0.854 ('Near Perfect Agreement' on Landis & Koch scale)",
        "• Impact: Eliminates subjective lot rejections and resolves mandi trade disputes."
    ]
    for pt in k_pts:
        p_kp = tf_k.add_paragraph()
        p_kp.text = pt
        p_kp.font.size = Pt(8)
        p_kp.font.color.rgb = C_TEXT_DARK


    # =========================================================================
    # SLIDE 5: RESEARCH PAPERS REVIEW & THEIR CRITICAL LIMITATIONS (Comparison Part 1)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5)
    add_header(s5, "Critical Analysis of Existing IEEE Literature & Their Bottlenecks")

    paper_cards = [
        ("Paper 1: Loganathan et al. (IEEE 2026)",
         "Intelligent Onion Monitoring via Gas Sensors with Explainable SVM [ICSCAN 2026]",
         C_RED,
         [
             ("Sensing Method:", "MQ-135, MQ-4, DHT22 sensors interfaced with ESP32."),
             ("Room Air Only:", "Captures bulk ambient air; CANNOT isolate or inspect individual onion bulbs in a crate."),
             ("Synthetic Data:", "Evaluation was done on 1,000 synthetic simulated data points rather than real rotting produce."),
             ("Zero Sizing Capability:", "Gas sensors cannot measure equatorial diameter, volume, or physical dimensions."),
             ("Severe Time Lag:", "Gases release only after deep internal rot. Fungal cuts and green sprouts emit no gas.")
         ]),
        
        ("Paper 2: Rajalakshmi et al. (IEEE 2025)",
         "QUALICLIPNET: Hybrid Deep Learning for Quality Assessment [ICSCSA 2025]",
         C_AMBER,
         [
             ("Sensing Method:", "OpenAI CLIP + Vision Transformer + GAN for adversarial defense."),
             ("Prohibitive Hardware:", "Requires high-end desktop NVIDIA RTX 3060 GPU with massive VRAM and power."),
             ("No Mobile/Edge Use:", "Cannot run on portable phones or low-cost computers at rural mandi auction tables."),
             ("Uncalibrated Pixel Scale:", "Ignores camera distance. An onion photographed up-close appears identical to a large one."),
             ("Coarse Academic Labels:", "Outputs generic 'High/Med/Low' labels that ignore commercial APMC/NAFED standards.")
         ]),

        ("Paper 3: Suryawanshi et al. (IEEE 2025)",
         "Vision-Based Automation System for Onion Grading Using Robotic Arm [ICONAT 2025]",
         C_BLUE,
         [
             ("Sensing Method:", "YOLOv8 + OAK-D Lite DepthAI Stereo Camera + 4-DOF Robotic Arm."),
             ("High Infrastructure Cost:", "Industrial conveyor belts, pneumatic valves, and robotic arm cost $2,500+ (₹2,00,000+)."),
             ("Poor Defect Precision:", "YOLOv8 dropped by 16.4% down to 78.4% precision on bad onions (high false negatives)."),
             ("Rigid Mount Required:", "Depth camera works ONLY at a calibrated perpendicular height above the moving belt."),
             ("Binary Oversimplification:", "Crude Good vs. Bad bucket sorting ignores legal URS (35-40mm) procurement norms.")
         ])
    ]

    for idx, (p_title, p_sub, p_col, points) in enumerate(paper_cards):
        px = Inches(0.8 + idx * 4.0)
        py = Inches(1.5)
        pw = Inches(3.733)
        ph = Inches(5.5)

        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, py, pw, ph)
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD_BG
        card.line.color.rgb = p_col
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = Inches(0.18)
        
        p_t = tf.paragraphs[0]
        p_t.text = p_title
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = p_col

        p_s = tf.add_paragraph()
        p_s.text = p_sub
        p_s.font.size = Pt(8.5)
        p_s.font.italic = True
        p_s.font.color.rgb = C_TEXT_MUTED
        p_s.space_before = Pt(2)

        p_div = tf.add_paragraph()
        p_div.text = "CRITICAL BOTTLENECK AUDIT:"
        p_div.font.size = Pt(9)
        p_div.font.bold = True
        p_div.font.color.rgb = C_NAVY
        p_div.space_before = Pt(8)

        for f_label, f_desc in points:
            p_fl = tf.add_paragraph()
            p_fl.text = "• " + f_label
            p_fl.font.size = Pt(9)
            p_fl.font.bold = True
            p_fl.font.color.rgb = C_RED if "❌" in p_fl.text else C_NAVY
            p_fl.space_before = Pt(5)

            p_fd = tf.add_paragraph()
            p_fd.text = "    " + f_desc
            p_fd.font.size = Pt(8.2)
            p_fd.font.color.rgb = C_TEXT_DARK


    # =========================================================================
    # SLIDE 6: COMPARATIVE MATRIX & GAPS SOLVED (Comparison Part 2 / Conclusion)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_header(s6, "Comprehensive Comparison Matrix: Literature vs. Our Implemented System")

    # Big Comparison Table
    table_shape = s6.shapes.add_table(9, 5, Inches(0.8), Inches(1.5), Inches(11.733), Inches(3.6))
    tbl = table_shape.table
    tbl.columns[0].width = Inches(2.333)
    tbl.columns[1].width = Inches(2.25)
    tbl.columns[2].width = Inches(2.25)
    tbl.columns[3].width = Inches(2.4)
    tbl.columns[4].width = Inches(2.5)

    headers = [
        "Technical Dimension", 
        "Loganathan et al. (2026)", 
        "Rajalakshmi et al. (2025)", 
        "Suryawanshi et al. (2025)", 
        "OUR IMPLEMENTED SYSTEM"
    ]

    matrix_rows = [
        ["Core Sensing Modality", "MQ Gas Sensors + ESP32", "CLIP + ViT + GAN", "YOLOv8 + DepthAI Stereo", "MobileNetV3 + Multi-Spectrum CV"],
        ["Hardware & Rig Cost", "Low (~$35)", "High ($1,200+ GPU workstation)", "Very High ($2,500+ Robotic Rig)", "ZERO Added Cost (Any Phone/PC Browser)"],
        ["Individual Inspection", "No (Bulk ambient air only)", "Yes (Single image)", "Yes (Singulated conveyor)", "YES (Direct Handheld Photo)"],
        ["Physical Diameter Sizing", "No (Impossible via gas)", "No (Pixel scale uncalibrated)", "Fixed Stereo (Rigid bracket only)", "YES: Sub-mm Reference Coin Scaling"],
        ["Sprout Discrimination", "No (Blind to vegetative growth)", "No dedicated sprout logic", "78.4% Precision (High False Negatives)", "YES: 360° Chlorophyll Mask (99% Conf)"],
        ["Procurement Grading", "3 synthetic states", "Generic High/Med/Low", "Binary 'Good' vs. 'Bad'", "YES: Grade A, URS, Rejection (APMC/NAFED)"],
        ["Inference Latency", "~2.5 seconds", "> 450 ms (GPU required)", "~120 ms (Dedicated VPU)", "< 120 ms on Commodity CPU"],
        ["Deployment Portability", "Fixed sensor box", "Heavy desktop workstation", "Heavy industrial floor conveyor", "100% PORTABLE: Web App / Mobile Edge"]
    ]

    for col_i, h in enumerate(headers):
        cell = tbl.cell(0, col_i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_BLUE if col_i < 4 else C_TEAL
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(8.5)
            p.font.bold = True
            p.font.color.rgb = C_WHITE
            p.alignment = PP_ALIGN.CENTER

    for row_i, r_data in enumerate(matrix_rows):
        for col_i, val in enumerate(r_data):
            cell = tbl.cell(row_i + 1, col_i)
            cell.text = val
            cell.fill.solid()
            if col_i == 4:
                cell.fill.fore_color.rgb = RGBColor(236, 253, 245) # Highlight green for our system
            else:
                cell.fill.fore_color.rgb = RGBColor(248, 250, 252) if row_i % 2 == 1 else C_WHITE

            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(7.8)
                p.font.bold = (col_i == 4 or col_i == 0)
                p.font.color.rgb = C_TEAL if col_i == 4 else (C_NAVY if col_i == 0 else C_TEXT_DARK)
                p.alignment = PP_ALIGN.CENTER if col_i > 0 else PP_ALIGN.LEFT

    # Summary Callout Box (Bottom)
    sum_box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.3), Inches(11.733), Inches(1.7))
    sum_box.fill.solid()
    sum_box.fill.fore_color.rgb = RGBColor(239, 246, 255)
    sum_box.line.color.rgb = C_BLUE
    sum_box.line.width = Pt(1.5)

    tf_s = sum_box.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_top = Inches(0.18)
    p_st = tf_s.paragraphs[0]
    p_st.text = "Summary of Critical Research Gaps Solved by Our Project"
    p_st.font.size = Pt(12)
    p_st.font.bold = True
    p_st.font.color.rgb = C_BLUE

    gaps = [
        "1. Demolished the Hardware Barrier: Replaced $2,500 industrial robotic arms and $1,200 RTX GPUs with a lightweight MobileNetV3 model running on ordinary smartphone browsers.",
        "2. Solved Optical Scale without Depth Sensors: Standard ₹5/₹10 coin reference achieves 0.41 mm vernier-grade sizing from any arbitrary camera angle or distance.",
        "3. Protected Farmer Remuneration: Replaced naive binary 'Good/Bad' sorting with commercial APMC/NAFED Mandi standards (Grade A vs. URS) and Cohen's Kappa (κ = 0.854) bias auditability."
    ]
    for g in gaps:
        p_g = tf_s.add_paragraph()
        p_g.text = g
        p_g.font.size = Pt(8.8)
        p_g.font.color.rgb = C_NAVY
        p_g.space_before = Pt(3)

    # Save presentation
    prs.save(output_path)
    print(f"Successfully generated PowerPoint presentation: {output_path}")
    return output_path

if __name__ == "__main__":
    create_presentation()
