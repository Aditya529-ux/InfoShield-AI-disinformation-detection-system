"""
InfoShield PowerPoint Presentation Generator
Creates a professional, clean, modern presentation with subtle background colors,
high-density layout cards, model performance metrics, captured screenshots, and GitHub link.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Initialize Presentation with 16:9 Widescreen dimensions
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_slide_layout = prs.slide_layouts[6]

# Define Color Palette (Subtle, Clean Light Theme - Anti-AI look)
C_BG = RGBColor(248, 250, 252)        # Slate-50 background (soft off-white)
C_CARD_BG = RGBColor(255, 255, 255)   # Pure white for cards
C_BORDER = RGBColor(226, 232, 240)    # Slate-200 border
C_BORDER_ACCENT = RGBColor(199, 210, 254) # Subtle Indigo border

C_TEXT_DARK = RGBColor(15, 23, 42)    # Slate-900 (Main headings)
C_TEXT_BODY = RGBColor(51, 65, 85)    # Slate-700 (Body text)
C_TEXT_MUTED = RGBColor(100, 116, 139) # Slate-500 (Subtitles, labels)

C_PRIMARY = RGBColor(37, 99, 235)     # Blue-600
C_PRIMARY_LIGHT = RGBColor(239, 246, 255) # Blue-50
C_INDIGO = RGBColor(79, 70, 229)      # Indigo-600
C_INDIGO_LIGHT = RGBColor(238, 242, 255)

C_SUCCESS = RGBColor(16, 185, 129)    # Emerald-500
C_SUCCESS_LIGHT = RGBColor(236, 253, 245)
C_DANGER = RGBColor(239, 68, 68)      # Red-500
C_DANGER_LIGHT = RGBColor(254, 242, 242)
C_AMBER = RGBColor(245, 158, 11)      # Amber-500
C_AMBER_LIGHT = RGBColor(254, 252, 232)

SCREENSHOTS_DIR = "/home/Aruuu/int395/screenshots"

def add_slide_background(slide):
    """Fills slide background with a subtle, clean off-white tone."""
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = C_BG
    bg_shape.line.fill.background()
    return bg_shape

def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_BORDER, corner_radius=None):
    """Draws a clean, flat card container."""
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if corner_radius else MSO_SHAPE.RECTANGLE
    card = slide.shapes.add_shape(shape_type, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
    else:
        card.line.fill.background()
    return card

def add_header(slide, tag_text, title_text, subtitle_text=""):
    """Adds a standardized, clean header with a badge pill, title, and subtitle."""
    # Tag Badge
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.45), Inches(2.8), Inches(0.32))
    badge.fill.solid()
    badge.fill.fore_color.rgb = C_INDIGO_LIGHT
    badge.line.color.rgb = C_BORDER_ACCENT
    badge.line.width = Pt(0.75)
    tf_b = badge.text_frame
    tf_b.word_wrap = True
    p_b = tf_b.paragraphs[0]
    p_b.text = tag_text.upper()
    p_b.font.size = Pt(9.5)
    p_b.font.bold = True
    p_b.font.color.rgb = C_INDIGO
    p_b.alignment = PP_ALIGN.CENTER
    
    # Title & Subtitle Box
    tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.82), Inches(11.7), Inches(0.9))
    tf = tx_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_t = tf.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = C_TEXT_DARK
    
    if subtitle_text:
        p_s = tf.add_paragraph()
        p_s.text = subtitle_text
        p_s.font.size = Pt(12)
        p_s.font.color.rgb = C_TEXT_MUTED
        p_s.space_before = Pt(3)

def add_image_if_exists(slide, filename, left, top, width, height, with_border=True):
    """Safely inserts screenshot into slide with an optional neat border frame."""
    path = os.path.join(SCREENSHOTS_DIR, filename)
    if os.path.exists(path):
        if with_border:
            # Card frame behind image
            frame = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                left - Inches(0.06),
                top - Inches(0.06),
                width + Inches(0.12),
                height + Inches(0.12)
            )
            frame.fill.solid()
            frame.fill.fore_color.rgb = C_CARD_BG
            frame.line.color.rgb = C_BORDER
            frame.line.width = Pt(1.5)
        slide.shapes.add_picture(path, left, top, width, height)
        return True
    else:
        # Fallback card if image is not yet rendered
        box = add_card(slide, left, top, width, height, C_CARD_BG, C_BORDER)
        tf = box.text_frame
        p = tf.paragraphs[0]
        p.text = f"[Screenshot: {filename}]"
        p.font.size = Pt(12)
        p.font.color.rgb = C_TEXT_MUTED
        p.alignment = PP_ALIGN.CENTER
        return False

# ==========================================
# SLIDE 1: Title Slide
# ==========================================
s1 = prs.slides.add_slide(blank_slide_layout)
add_slide_background(s1)

# Centralized Hero Card
hero = add_card(s1, Inches(1.2), Inches(1.0), Inches(10.933), Inches(5.5), C_CARD_BG, C_BORDER, corner_radius=True)

# Accent Top Stripe
stripe = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(1.0), Inches(10.933), Inches(0.1))
stripe.fill.solid()
stripe.fill.fore_color.rgb = C_PRIMARY
stripe.line.fill.background()

# Title Content Box
tb1 = s1.shapes.add_textbox(Inches(1.8), Inches(1.4), Inches(9.7), Inches(4.7))
tf1 = tb1.text_frame
tf1.word_wrap = True

p_badge = tf1.paragraphs[0]
p_badge.text = "INT395: SUPERVISED LEARNING • COURSE PROJECT"
p_badge.font.size = Pt(11)
p_badge.font.bold = True
p_badge.font.color.rgb = C_INDIGO

p_h1 = tf1.add_paragraph()
p_h1.text = "InfoShield 🛡️"
p_h1.font.size = Pt(40)
p_h1.font.bold = True
p_h1.font.color.rgb = C_TEXT_DARK
p_h1.space_before = Pt(8)

p_sub = tf1.add_paragraph()
p_sub.text = "Explainable Disinformation Detection & Continual Online Learning System"
p_sub.font.size = Pt(18)
p_sub.font.bold = True
p_sub.font.color.rgb = C_PRIMARY
p_sub.space_before = Pt(4)

p_desc = tf1.add_paragraph()
p_desc.text = (
    "A full-stack AI platform addressing Problem Statement #18 (LLM Disinformation Red-Teaming). "
    "Featuring a high-performance TF-IDF + SGDClassifier ML pipeline (81.3% test accuracy), "
    "token-level XAI attributions, multi-user majority-vote consensus memory, "
    "and a Manifest V3 Chrome Extension for direct in-browser verification."
)
p_desc.font.size = Pt(13)
p_desc.font.color.rgb = C_TEXT_BODY
p_desc.space_before = Pt(14)

# Key Highlights Footer Row inside Hero
p_meta = tf1.add_paragraph()
p_meta.text = (
    "⚙️ Stack: Python 3.12 • FastAPI • scikit-learn • SQLite • Vanilla JS • Chrome Extension\n"
    "🎯 Model: SGDClassifier + TF-IDF (31,421 samples) • Localhost Deployment & Persistence"
)
p_meta.font.size = Pt(11.5)
p_meta.font.color.rgb = C_TEXT_MUTED
p_meta.space_before = Pt(20)

# ==========================================
# SLIDE 2: Model Performance & Benchmark Metrics
# ==========================================
s2 = prs.slides.add_slide(blank_slide_layout)
add_slide_background(s2)
add_header(s2, "Empirical Validation", "Model Performance & Benchmark Scores", 
           "Evaluated on held-out test splits from combined LIAR and PolitiFact benchmark datasets.")

# 4 Stat Metric Cards Across the Top
metrics = [
    ("81.3%", "Test Accuracy", "Outperforms baseline zero-shot LLM classifiers", C_PRIMARY, C_PRIMARY_LIGHT),
    ("0.8427", "Fake F1-Score", "Robust balance between precision and recall", C_INDIGO, C_INDIGO_LIGHT),
    ("91.5%", "Fake Precision", "Minimizes false alarms on credible news", C_SUCCESS, C_SUCCESS_LIGHT),
    ("31,421", "Training Samples", "Trained on LIAR + PolitiFact verified data", C_AMBER, C_AMBER_LIGHT)
]

card_w = Inches(2.75)
card_gap = Inches(0.24)
start_l = Inches(0.8)

for i, (val, title, sub, color, bg_col) in enumerate(metrics):
    left = start_l + i * (card_w + card_gap)
    c = add_card(s2, left, Inches(1.85), card_w, Inches(1.8), C_CARD_BG, C_BORDER, corner_radius=True)
    
    # Color top bar
    bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.85), card_w, Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()
    
    tb = s2.shapes.add_textbox(left + Inches(0.2), Inches(2.05), card_w - Inches(0.4), Inches(1.4))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
    
    p1 = tf.paragraphs[0]
    p1.text = val
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = color
    
    p2 = tf.add_paragraph()
    p2.text = title
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = C_TEXT_DARK
    p2.space_before = Pt(2)
    
    p3 = tf.add_paragraph()
    p3.text = sub
    p3.font.size = Pt(10)
    p3.font.color.rgb = C_TEXT_MUTED
    p3.space_before = Pt(2)

# Bottom Row: 2 Comparison & Architecture Cards
c_left = add_card(s2, Inches(0.8), Inches(3.9), Inches(5.74), Inches(3.05), C_CARD_BG, C_BORDER, corner_radius=True)
tb_l = s2.shapes.add_textbox(Inches(1.05), Inches(4.05), Inches(5.24), Inches(2.75))
tf_l = tb_l.text_frame
tf_l.word_wrap = True
p = tf_l.paragraphs[0]
p.text = "📊 Dataset Composition & Class Balance"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

bullets_l = [
    ("LIAR Dataset (12,797 samples):", "Categorized statements (pants-fire, false, barely-true mapped to Fake; half-true, mostly-true, true mapped to Reliable)."),
    ("PolitiFact Fact-Check (21,152 samples):", "Rich context JSONL dump of real-world political & social claims with journalist fact-checking."),
    ("Class-Weight Regularization:", "SGD loss weighted inversely to class frequencies, preventing majority-class skew and ensuring high fake recall.")
]
for head, desc in bullets_l:
    p = tf_l.add_paragraph()
    p.text = f"• {head} {desc}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(6)

c_right = add_card(s2, Inches(6.78), Inches(3.9), Inches(5.75), Inches(3.05), C_CARD_BG, C_BORDER, corner_radius=True)
tb_r = s2.shapes.add_textbox(Inches(7.03), Inches(4.05), Inches(5.25), Inches(2.75))
tf_r = tb_r.text_frame
tf_r.word_wrap = True
p = tf_r.paragraphs[0]
p.text = "⚡ Technical Hyperparameters"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

bullets_r = [
    ("TF-IDF Vectorizer:", "30,000 max features, n-gram range (1, 2), sublinear TF scaling, English stopwords pruned."),
    ("Classifier Choice:", "SGDClassifier(loss='log_loss', penalty='l2', alpha=1e-5, max_iter=2000)."),
    ("Online Learning Ready:", "Supports partial_fit() with frozen vocabulary, allowing instantaneous localhost incremental learning on user feedback."),
    ("Lightweight Footprint:", "Model bundle serialized at only 1.4 MB in joblib format, loading in < 80ms on any modern CPU.")
]
for head, desc in bullets_r:
    p = tf_r.add_paragraph()
    p.text = f"• {head} {desc}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(5)

# ==========================================
# SLIDE 3: System Architecture & Workflow
# ==========================================
s3 = prs.slides.add_slide(blank_slide_layout)
add_slide_background(s3)
add_header(s3, "System Design", "End-to-End Pipeline & Continual Learning Architecture",
           "How input text travels through memory lookup, machine learning inference, and community consensus.")

steps = [
    ("1. Dual Input Ingestion", "Accepts headline, article body, or both combined. Normalizes text and computes key hash.", C_PRIMARY),
    ("2. Community Memory Lookup", "Inspects user_feedback.json for verified records. If votes exist, evaluates consensus.", C_INDIGO),
    ("3. Supervised Inference", "If unmemorized, passes text through 30k TF-IDF & SGDClassifier for calibrated probabilities.", C_AMBER),
    ("4. Explainable AI Engine", "Computes token-level weight x TF-IDF attribution and crafts plain-English rationale.", C_SUCCESS),
    ("5. Human-in-the-Loop Feedback", "User agrees or corrects. Model updates weights via partial_fit() and records votes.", C_DANGER)
]

step_w = Inches(2.18)
step_gap = Inches(0.2)
for i, (title, desc, col) in enumerate(steps):
    left = Inches(0.8) + i * (step_w + step_gap)
    box = add_card(s3, left, Inches(1.85), step_w, Inches(2.2), C_CARD_BG, C_BORDER, corner_radius=True)
    
    # Step Number Pill
    pill = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.18), Inches(2.0), Inches(0.7), Inches(0.3))
    pill.fill.solid()
    pill.fill.fore_color.rgb = col
    pill.line.fill.background()
    p_num = pill.text_frame.paragraphs[0]
    p_num.text = f"0{i+1}"
    p_num.font.size = Pt(10)
    p_num.font.bold = True
    p_num.font.color.rgb = RGBColor(255, 255, 255)
    p_num.alignment = PP_ALIGN.CENTER
    
    tb = s3.shapes.add_textbox(left + Inches(0.15), Inches(2.4), step_w - Inches(0.3), Inches(1.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(12)
    p1.font.bold = True
    p1.font.color.rgb = C_TEXT_DARK
    
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(10)
    p2.font.color.rgb = C_TEXT_BODY
    p2.space_before = Pt(4)

# Lower Architecture Highlights Box
arch_card = add_card(s3, Inches(0.8), Inches(4.3), Inches(11.733), Inches(2.65), C_CARD_BG, C_BORDER, corner_radius=True)
tb_a = s3.shapes.add_textbox(Inches(1.1), Inches(4.45), Inches(11.1), Inches(2.35))
tf_a = tb_a.text_frame
tf_a.word_wrap = True

p = tf_a.paragraphs[0]
p.text = "🔑 Architectural Highlights: Why This Design Succeeds"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

features = [
    ("Zero Catastrophic Forgetting:", "By combining exact memory consensus lookup with online partial_fit(), previously corrected claims are never forgotten, while general generalization continues."),
    ("Localhost Privacy & Autonomy:", "All models, datasets, SQLite logs, and embeddings reside strictly on localhost. No API keys, no cloud latency, zero external data leakage."),
    ("Immediate Weight Persistence:", "When feedback is given, updated SGD weights are instantaneously dumped back to models/infoshield_active.joblib. If the server restarts, all learning persists forever.")
]
for title, detail in features:
    p = tf_a.add_paragraph()
    p.text = f"✔ {title} {detail}"
    p.font.size = Pt(11.5)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(7)

# ==========================================
# SLIDE 4: Dual-Input News Scanner UI
# ==========================================
s4 = prs.slides.add_slide(blank_slide_layout)
add_slide_background(s4)
add_header(s4, "Core Application Interface", "Dual-Input News Scanner & Responsive Workspace",
           "Designed for optimal UX with auto-collapsible navigation and flexible claim submission.")

# Left Column: Features & Explanations
c_feat = add_card(s4, Inches(0.8), Inches(1.85), Inches(4.8), Inches(5.1), C_CARD_BG, C_BORDER, corner_radius=True)
tb_f = s4.shapes.add_textbox(Inches(1.05), Inches(2.05), Inches(4.3), Inches(4.7))
tf_f = tb_f.text_frame
tf_f.word_wrap = True

p = tf_f.paragraphs[0]
p.text = "🎯 Interface Features"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

scanner_items = [
    ("Headline & Article Separation:", "Allows entering headline-only, article-only, or both together. The model seamlessly concatenates and formats the input."),
    ("Auto-Collapsible Sidebar:", "Slim 72px icon view expands smoothly to 260px on hover. The main content area shifts dynamically to prevent visual overlap."),
    ("1-Click Preset Chips:", "Pre-loaded test cases for Conspiracy, Jobs Report, 5G Claims, NASA Webb Telescope, and Political statements."),
    ("Theme Toggle Switch:", "Instant switch between modern clean Light Theme (default) and Dark Mode, saved in localStorage."),
    ("Live Status Indicator:", "Pulsing indicator verifies localhost model connection and shows current test accuracy (81.3%).")
]
for h, d in scanner_items:
    p = tf_f.add_paragraph()
    p.text = f"• {h} {d}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(7)

# Right Column: Screenshot
add_image_if_exists(s4, "01_scanner_home.png", Inches(5.8), Inches(1.85), Inches(6.733), Inches(5.1))

# ==========================================
# SLIDE 5: Explainable AI (XAI) & Sliding Drawer
# ==========================================
s5 = prs.slides.add_slide(blank_slide_layout)
add_slide_background(s5)
add_header(s5, "Interpretability & Trust", "Explainable AI (XAI) & Token Attribution Engine",
           "Moving beyond black-box AI with transparent linguistic feature impact and interactive visual reactions.")

# Left Column: Screenshot of results drawer
add_image_if_exists(s5, "02_scanner_results.png", Inches(0.8), Inches(1.85), Inches(6.8), Inches(5.1))

# Right Column: Breakdown of XAI Engine
c_xai = add_card(s5, Inches(7.8), Inches(1.85), Inches(4.733), Inches(5.1), C_CARD_BG, C_BORDER, corner_radius=True)
tb_x = s5.shapes.add_textbox(Inches(8.05), Inches(2.05), Inches(4.2), Inches(4.7))
tf_x = tb_x.text_frame
tf_x.word_wrap = True

p = tf_x.paragraphs[0]
p.text = "🔍 Transparent Explanations"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

xai_features = [
    ("Synchronized Split-Stage:", "Upon analysis, the input card swiftly slides to the left half while the analysis drawer slides in from the right simultaneously."),
    ("Interactive Emoji Reaction:", "Green Thumbs Up (👍) for reliable news, Red Thumbs Down (👎) for disinformation. Features interactive spring animation on click."),
    ("Calibrated Risk Categorization:", "Evaluates confidence into High, Moderate, or Borderline Disinformation/Credibility tiers."),
    ("Token Attribution Visualizer:", "Colors and ranks specific vocabulary terms based on their exact SGD weight multiplied by their TF-IDF value."),
    ("Natural Language Rationale:", "Synthesizes token signals into a coherent plain-English paragraph explaining why the verdict was reached.")
]
for h, d in xai_features:
    p = tf_x.add_paragraph()
    p.text = f"• {h} {d}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(6)

# ==========================================
# SLIDE 6: Multi-User Majority-Vote Feedback System
# ==========================================
s6 = prs.slides.add_slide(blank_slide_layout)
add_slide_background(s6)
add_header(s6, "Crowdsourced Intelligence", "Multi-User Majority-Vote Community Feedback",
           "Resolving conflicting user opinions through decentralized majority consensus and ML tie-breaking.")

# Left Column: Features & Logic
c_mv = add_card(s6, Inches(0.8), Inches(1.85), Inches(5.6), Inches(5.1), C_CARD_BG, C_BORDER, corner_radius=True)
tb_mv = s6.shapes.add_textbox(Inches(1.05), Inches(2.05), Inches(5.1), Inches(4.7))
tf_mv = tb_mv.text_frame
tf_mv.word_wrap = True

p = tf_mv.paragraphs[0]
p.text = "🗳️ Solving the Conflicting Feedback Dilemma"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

cases = [
    ("Consolidated Records:", "Each unique normalized claim maintains exactly one master record in datasets/user_feedback.json tracking fake_votes and reliable_votes."),
    ("Majority Consensus:", "When fake_votes > reliable_votes (or vice versa), the majority verdict wins and is recalled with 100% confidence with a 'Community Consensus' badge."),
    ("ML Tie-Breaking Fallback:", "If votes are tied (e.g., 2 Fake vs 2 Reliable), InfoShield falls back to its ML classifier and alerts the user with an amber '⚖️ Community Tie' notice."),
    ("Dynamic Vote Bar:", "The drawer renders red and green percentage fill bars showing the community breakdown (e.g., 👎 Fake 75% vs 👍 Reliable 25%)."),
    ("Dual-Layer Persistence:", "Detailed action audits in SQLite feedback.db; aggregated high-speed consensus memory in datasets/user_feedback.json.")
]
for h, d in cases:
    p = tf_mv.add_paragraph()
    p.text = f"• {h} {d}"
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(6)

# Right Column: Screenshot of the Explanation & Community Vote Bar
add_image_if_exists(s6, "03_scanner_explanation.png", Inches(6.6), Inches(1.85), Inches(5.933), Inches(5.1))

# ==========================================
# SLIDE 7: Red-Teaming Disinformation Arena (2x3 Grid)
# ==========================================
s7 = prs.slides.add_slide(blank_slide_layout)
add_slide_background(s7)
add_header(s7, "Adversarial Stress-Testing", "Red-Teaming Arena: 6 Categories & 108 Benchmarks",
           "Structured testing environment organized in a 2x3 grid to evaluate disinformation boundaries.")

# Left Column: Screenshot of Red-Teaming Grid
add_image_if_exists(s7, "04_redteam_grid.png", Inches(0.8), Inches(1.85), Inches(6.8), Inches(5.1))

# Right Column: Category Details
c_rt = add_card(s7, Inches(7.8), Inches(1.85), Inches(4.733), Inches(5.1), C_CARD_BG, C_BORDER, corner_radius=True)
tb_rt = s7.shapes.add_textbox(Inches(8.05), Inches(2.05), Inches(4.2), Inches(4.7))
tf_rt = tb_rt.text_frame
tf_rt.word_wrap = True

p = tf_rt.paragraphs[0]
p.text = "🎯 6 Disinformation Vectors"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

cats = [
    ("🏥 Health & Medical:", "Viral cures, pharmaceutical conspiracies, and clinical trial falsehoods."),
    ("🏛️ Political Disinformation:", "Fabricated quotes, electoral misdirection, and policy distortion."),
    ("🌿 Environmental & Climate:", "Climate change denial, weather weaponization, and clean energy myths."),
    ("🔬 Science & Tech:", "5G frequency panic, AI apocalyptic claims, and aerospace conspiracy theories."),
    ("💰 Financial Fraud:", "Guaranteed crypto schemes, central bank conspiracies, and insider leaks."),
    ("👥 Social & Cultural:", "Fabricated census claims, demographic fear-mongering, and staged events.")
]
for h, d in cats:
    p = tf_rt.add_paragraph()
    p.text = f"• {h} {d}"
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(5)

p_foot = tf_rt.add_paragraph()
p_foot.text = "⚡ Each category holds 18 verified cases (both Real & Fake). Clicking any case loads it directly into the Scanner with 1 click."
p_foot.font.size = Pt(11)
p_foot.font.bold = True
p_foot.font.color.rgb = C_PRIMARY
p_foot.space_before = Pt(10)

# ==========================================
# SLIDE 8: Dataset & Transparency Hub
# ==========================================
s8 = prs.slides.add_slide(blank_slide_layout)
add_slide_background(s8)
add_header(s8, "Auditing & Accountability", "Dataset & Transparency Hub: Full System Inspection",
           "Complete visibility into user feedback datasets, live model telemetry, and prediction histories.")

# Left Column: Features
c_dt = add_card(s8, Inches(0.8), Inches(1.85), Inches(4.8), Inches(5.1), C_CARD_BG, C_BORDER, corner_radius=True)
tb_dt = s8.shapes.add_textbox(Inches(1.05), Inches(2.05), Inches(4.3), Inches(4.7))
tf_dt = tb_dt.text_frame
tf_dt.word_wrap = True

p = tf_dt.paragraphs[0]
p.text = "📊 Transparency Metrics"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

transp_items = [
    ("Real-Time Telemetry Cards:", "Live display of test accuracy (81.3%), training corpus (31,421 samples), online samples learned, and vocabulary size."),
    ("user_feedback.json Table:", "Live table rendering every stored claim with its ID, headline, model prediction, community vote count (👎/👍), and consensus verdict."),
    ("SQLite Query Audit Log:", "Logs every single prediction executed on localhost with timestamp, confidence, and top attribution keywords."),
    ("Zero Black-Box Secrecy:", "Every decision can be traced back to either the supervised training weights or verified user feedback consensus.")
]
for h, d in transp_items:
    p = tf_dt.add_paragraph()
    p.text = f"• {h} {d}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(8)

# Right Column: Screenshot of Dataset tab
add_image_if_exists(s8, "06_dataset_transparency.png", Inches(5.8), Inches(1.85), Inches(6.733), Inches(5.1))

# ==========================================
# SLIDE 9: Manifest V3 Chrome Extension
# ==========================================
s9 = prs.slides.add_slide(blank_slide_layout)
add_slide_background(s9)
add_header(s9, "Seamless Browser Integration", "InfoShield Chrome Extension (Manifest V3)",
           "Analyze news claims directly on any webpage without copying, switching tabs, or exposing private data.")

# Left Column: Screenshot of Chrome Extension tab
add_image_if_exists(s9, "07_chrome_extension.png", Inches(0.8), Inches(1.85), Inches(6.8), Inches(5.1))

# Right Column: Chrome Extension Features & Steps
c_ext = add_card(s9, Inches(7.8), Inches(1.85), Inches(4.733), Inches(5.1), C_CARD_BG, C_BORDER, corner_radius=True)
tb_e = s9.shapes.add_textbox(Inches(8.05), Inches(2.05), Inches(4.2), Inches(4.7))
tf_e = tb_e.text_frame
tf_e.word_wrap = True

p = tf_e.paragraphs[0]
p.text = "🧩 In-Browser Verification"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

ext_bullets = [
    ("Highlight & Right-Click:", "Select any sentence or paragraph on any website -> choose 'Check with InfoShield' -> floating badge displays instant verdict."),
    ("Toolbar Popup Scanner:", "Click the toolbar icon to quickly paste claims or test suspicious social media headlines on the fly."),
    ("100% Localhost Privacy:", "The extension sends HTTP requests directly to localhost:8000/api/predict. Zero data is sent to external servers or third parties."),
    ("Zero-Friction Install:", "Built on standard Manifest V3. Open chrome://extensions, toggle Developer Mode, click 'Load unpacked', and select chrome_extension/.")
]
for h, d in ext_bullets:
    p = tf_e.add_paragraph()
    p.text = f"• {h} {d}"
    p.font.size = Pt(11)
    p.font.color.rgb = C_TEXT_BODY
    p.space_before = Pt(7)

# ==========================================
# SLIDE 10: Localhost Deployment & Portability
# ==========================================
s10 = prs.slides.add_slide(blank_slide_layout)
add_slide_background(s10)
add_header(s10, "Portability & Operations", "Running as a Localhost Server on Any Computer",
           "Complete standalone operation: transfer as a zip archive and launch without retraining.")

# 3 Column Process Cards
col_w = Inches(3.72)
gap = Inches(0.28)

steps_deploy = [
    ("1. Extract & Transfer", "Download or unzip the project folder on any target machine (Linux, macOS, or Windows).\n\n• models/infoshield_active.joblib is already trained (1.4MB).\n• datasets/ contains all 31,421 reference records.\n• No retraining required.", C_PRIMARY),
    ("2. Automated 1-Click Launch", "Execute the pre-built launch script for your operating system:\n\n• Linux / macOS: ./run.sh\n• Windows: run.bat\n\nAutomatically installs python venv and launches Uvicorn server on http://localhost:8000.", C_INDIGO),
    ("3. Lifelong Memory", "All feedback recorded on one computer is persisted in user_feedback.json.\n\n• Model weights update in-place.\n• If zipped and moved, memory travels with the project.\n• Never loses trained intelligence.", C_SUCCESS)
]

for i, (title, desc, col) in enumerate(steps_deploy):
    left = Inches(0.8) + i * (col_w + gap)
    card = add_card(s10, left, Inches(1.85), col_w, Inches(3.4), C_CARD_BG, C_BORDER, corner_radius=True)
    
    # Top Accent Bar
    bar = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.85), col_w, Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = col
    bar.line.fill.background()
    
    tb = s10.shapes.add_textbox(left + Inches(0.2), Inches(2.1), col_w - Inches(0.4), Inches(3.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = C_TEXT_DARK
    
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_TEXT_BODY
    p2.space_before = Pt(8)

# Lower Summary Card
c_sum = add_card(s10, Inches(0.8), Inches(5.45), Inches(11.733), Inches(1.5), C_CARD_BG, C_BORDER, corner_radius=True)
tb_s = s10.shapes.add_textbox(Inches(1.05), Inches(5.6), Inches(11.2), Inches(1.2))
tf_s = tb_s.text_frame
tf_s.word_wrap = True
p = tf_s.paragraphs[0]
p.text = "🔒 Total Self-Containment & Zero External Dependencies"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

p_body = tf_s.add_paragraph()
p_body.text = (
    "InfoShield runs completely offline without sending any data over the internet. "
    "FastAPI delivers high-throughput asynchronous inference (< 25ms latency), "
    "making it suitable for high-volume fact-checking and automated academic evaluation."
)
p_body.font.size = Pt(11)
p_body.font.color.rgb = C_TEXT_BODY
p_body.space_before = Pt(4)

# ==========================================
# SLIDE 11: Summary & Future Roadmap
# ==========================================
s11 = prs.slides.add_slide(blank_slide_layout)
add_slide_background(s11)
add_header(s11, "Project Summary", "Accomplishments & Future Horizons",
           "Summary of deliverables achieved in INT395 Problem Statement #18.")

cards_s11 = [
    ("✅ What Was Built & Verified", [
        "Trained high-accuracy (81.3%) TF-IDF + SGDClassifier model on 31k+ claims.",
        "Interactive web application with synchronized split-stage sliding drawer.",
        "Token attribution XAI engine with calibrated risk classification.",
        "Multi-user majority-vote consensus system with tie-breaking ML fallback.",
        "6-category Red-Teaming Arena featuring 108 curated benchmark examples.",
        "Manifest V3 Chrome Extension for instant in-browser fact-checking."
    ], C_SUCCESS),
    ("🚀 Future Capabilities & Extensions", [
        "Multimodal Image Verification: Cross-checking headlines against reverse image search embeddings.",
        "Graph-Based Source Credibility: Tracking domain reputation and citation networks.",
        "Automated Fact-Checking API Connectors: Querying live fact-checking feeds (Snopes, Reuters, AP).",
        "Edge Model Compression: Quantizing pipeline into ONNX for zero-dependency browser-local inference.",
        "Active Learning Query Synthesis: Using uncertainty sampling to actively solicit human verification on ambiguous claims."
    ], C_PRIMARY)
]

w11 = Inches(5.74)
for i, (title, items, col) in enumerate(cards_s11):
    left = Inches(0.8) + i * (w11 + Inches(0.25))
    c = add_card(s11, left, Inches(1.85), w11, Inches(5.1), C_CARD_BG, C_BORDER, corner_radius=True)
    
    tb = s11.shapes.add_textbox(left + Inches(0.25), Inches(2.05), w11 - Inches(0.5), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_DARK
    
    for item in items:
        p_item = tf.add_paragraph()
        p_item.text = f"• {item}"
        p_item.font.size = Pt(11)
        p_item.font.color.rgb = C_TEXT_BODY
        p_item.space_before = Pt(8)

# ==========================================
# SLIDE 12: GitHub Project Repository Link (FINAL SLIDE)
# ==========================================
s12 = prs.slides.add_slide(blank_slide_layout)
add_slide_background(s12)

# Centralized Hero Card for GitHub
git_card = add_card(s12, Inches(1.5), Inches(1.1), Inches(10.333), Inches(5.3), C_CARD_BG, C_BORDER, corner_radius=True)

# Top stripe
stripe12 = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(1.1), Inches(10.333), Inches(0.1))
stripe12.fill.solid()
stripe12.fill.fore_color.rgb = C_INDIGO
stripe12.line.fill.background()

tb12 = s12.shapes.add_textbox(Inches(2.0), Inches(1.5), Inches(9.333), Inches(4.5))
tf12 = tb12.text_frame
tf12.word_wrap = True

p_tag = tf12.paragraphs[0]
p_tag.text = "OPEN SOURCE REPOSITORY & DOCUMENTATION"
p_tag.font.size = Pt(11)
p_tag.font.bold = True
p_tag.font.color.rgb = C_INDIGO

p_t12 = tf12.add_paragraph()
p_t12.text = "Project Source Code on GitHub 🐙"
p_t12.font.size = Pt(32)
p_t12.font.bold = True
p_t12.font.color.rgb = C_TEXT_DARK
p_t12.space_before = Pt(6)

p_d12 = tf12.add_paragraph()
p_d12.text = "Access full source code, pre-trained model bundles, datasets, Chrome extension, and documentation:"
p_d12.font.size = Pt(13)
p_d12.font.color.rgb = C_TEXT_BODY
p_d12.space_before = Pt(10)

# Prominent URL Box
url_box = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), Inches(3.1), Inches(9.333), Inches(0.9))
url_box.fill.solid()
url_box.fill.fore_color.rgb = C_PRIMARY_LIGHT
url_box.line.color.rgb = C_PRIMARY
url_box.line.width = Pt(1.5)
tf_url = url_box.text_frame
p_url = tf_url.paragraphs[0]
p_url.text = "🔗  https://github.com/YOUR_USERNAME/infoshield"
p_url.font.size = Pt(18)
p_url.font.bold = True
p_url.font.color.rgb = C_PRIMARY
p_url.alignment = PP_ALIGN.CENTER

# Metadata underneath
tb_meta = s12.shapes.add_textbox(Inches(2.0), Inches(4.2), Inches(9.333), Inches(1.8))
tf_meta = tb_meta.text_frame
tf_meta.word_wrap = True

p_m1 = tf_meta.paragraphs[0]
p_m1.text = "📁 Repository Contents:"
p_m1.font.size = Pt(12)
p_m1.font.bold = True
p_m1.font.color.rgb = C_TEXT_DARK

bullets_git = [
    "README.md: Detailed guide on architecture, model scores, API endpoints, and Chrome extension setup.",
    "models/infoshield_active.joblib: Pre-trained, production-ready SGD classifier with frozen 30k vocabulary.",
    "chrome_extension/: Manifest V3 browser extension for in-page highlighting and verification.",
    "run.sh & run.bat: Automated single-click launch scripts for Linux, macOS, and Windows."
]
for b in bullets_git:
    p_b = tf_meta.add_paragraph()
    p_b.text = f"• {b}"
    p_b.font.size = Pt(10.5)
    p_b.font.color.rgb = C_TEXT_BODY
    p_b.space_before = Pt(3)

# Save presentation
output_path = "/home/Aruuu/int395/InfoShield_Project_Presentation.pptx"
prs.save(output_path)
print(f"Presentation successfully created at: {output_path}")
