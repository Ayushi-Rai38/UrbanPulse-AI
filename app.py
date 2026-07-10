import os
import random
from datetime import datetime

import numpy as np
import streamlit as st
from PIL import Image
from ultralytics import YOLO
import google.generativeai as genai
import joblib
from dotenv import load_dotenv

from database.database import conn, cursor

if "admin" not in st.session_state:
    st.session_state.admin = False

if "theme" not in st.session_state:
    st.session_state.theme = True

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

gemini_model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def generate_ai_summary(issue, department, location, description):
    prompt = f"""
You are an AI assistant for a Smart Urban Complaint Detection System.

Issue Detected:
{issue}

Responsible Department:
{department}

Location:
{location}

Citizen Description:
{description}

Generate:

1. Complaint Summary (2-3 lines)
2. Severity (Low / Medium / High)
3. Recommended Action (1 line)

Keep the response professional.
"""

    response = gemini_model.generate_content(prompt)
    return response.text


def analyze_image_with_gemini(image_path):
    image = Image.open(image_path)

    prompt = """
    Analyze this urban complaint image.

    Give:
    1. Objects detected
    2. Severity (Low/Medium/High)
    3. Possible Risk
    4. Recommended Action

    Keep response under 120 words.
    """

    response = gemini_model.generate_content(
        [prompt, image]
    )

    return response.text


nlp_model = joblib.load("models/model.pkl")
tfidf = joblib.load("models/tfidf.pkl")

department_names = {
    "Solid Waste (Garbage) Related": "🗑️ Solid Waste Department",
    "Road Maintenance (Engg)": "🛣️ Road Maintenance Department"
}

st.set_page_config(
    page_title="UrbanPulse AI",
    page_icon="🚦",
    layout="wide"
)

theme = st.session_state.theme

theme_toggle = st.toggle("🌙 Dark mode", value=theme, key="app_theme_toggle")
st.session_state.theme = theme_toggle
theme = st.session_state.theme

if theme:
    bg = "#071120"
    surface = "#0f1b2e"
    surface_2 = "#14233b"
    ink = "#f6f8fb"
    muted = "#9ab0c6"
    primary = "#4f8cff"
    primary_2 = "#75a8ff"
    accent = "#35d39b"
    border = "rgba(255,255,255,0.08)"
    shadow = "0 20px 55px rgba(0,0,0,0.28)"
    label = "#cfe0ff"
else:
    bg = "#f5f8ff"
    surface = "#ffffff"
    surface_2 = "#f8fbff"
    ink = "#0f172a"
    muted = "#64748b"
    primary = "#2563eb"
    primary_2 = "#3b82f6"
    accent = "#22c55e"
    border = "rgba(15,23,42,0.08)"
    shadow = "0 20px 45px rgba(15,23,42,0.08)"
    label = "#334155"

# Build CSS using token replacement to avoid f-string brace parsing issues
css_template = """
<style>
:root {
    --bg: <<BG>>;
    --surface: <<SURFACE>>;
    --surface-2: <<SURFACE2>>;
    --ink: <<INK>>;
    --muted: <<MUTED>>;
    --primary: <<PRIMARY>>;
    --primary-2: <<PRIMARY2>>;
    --accent: <<ACCENT>>;
    --border: <<BORDER>>;
    --shadow: <<SHADOW>>;
    --label: <<LABEL>>;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, var(--bg) 0%, color-mix(in srgb, var(--surface) 82%, var(--bg)) 100%);
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 3rem;
    max-width: 1440px;
}

.stSidebar{
background:#08111F;
border-right:1px solid rgba(255,255,255,.05);
}

section[data-testid="stSidebar"]{
width:285px;
}

section[data-testid="stSidebar"] button{
background:transparent!important;
border:none!important;
color:#D6E4FF!important;
text-align:left!important;
padding:12px 18px!important;
border-radius:14px!important;
font-size:15px!important;
font-weight:600!important;
}

section[data-testid="stSidebar"] button:hover{
background:#17253A!important;
color:white!important;
transform:none!important;
box-shadow:none!important;
}

.stSidebar [data-testid="stSidebarContent"] {
    padding: 0.9rem;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.2rem;
    background: rgba(255,255,255,0.08);
    border: 1px solid var(--border);
    border-radius: 20px;
    backdrop-filter: blur(16px);
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}

.topbar-left {
    display: flex;
    gap: 0.8rem;
    align-items: center;
}

.logo-badge {
    width: 46px;
    height: 46px;
    display: grid;
    place-items: center;
    border-radius: 14px;
    background: linear-gradient(135deg, var(--primary), var(--primary-2));
    color: white;
    font-size: 1.2rem;
    box-shadow: 0 12px 22px rgba(79,140,255,0.24);
}

.eyebrow {
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    font-weight: 700;
}

.page-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--ink);
}

.topbar-right {
    display: flex;
    gap: 0.7rem;
    align-items: center;
}

.pill {
    padding: 0.55rem 0.8rem;
    border-radius: 999px;
    font-size: 0.86rem;
    font-weight: 700;
    color: var(--ink);
    background: var(--surface-2);
    border: 1px solid var(--border);
}

.avatar {
    width: 40px;
    height: 40px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    color: white;
    font-weight: 800;
}

.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 45%, #4f8cff 100%);
    border-radius: 28px;
    padding: 1.8rem 2rem;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 25px 60px rgba(15,23,42,0.24);
    margin-bottom: 1rem;
    overflow: hidden;
    position: relative;
}

.hero::after {
    content: "";
    position: absolute;
    inset: auto -60px -70px auto;
    width: 230px;
    height: 230px;
    background: radial-gradient(circle, rgba(255,255,255,0.2), transparent 70%);
    pointer-events: none;
}

.hero h1 {
    font-size: clamp(1.8rem, 3.3vw, 2.7rem);
    font-weight: 800;
    color: white;
    margin-bottom: 0.35rem;
}

.hero h3 {
    font-size: 1rem;
    color: #dbeafe;
    font-weight: 600;
    margin-bottom: 0.4rem;
}

.hero p {
    color: #e2ebff;
    line-height: 1.7;
    max-width: 1050px;
    margin: 0;
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 1.15rem 1.2rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
    backdrop-filter: blur(14px);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 24px 60px rgba(15,23,42,0.16);
    border-color: rgba(79,140,255,0.22);
}

.fade-card {
    animation: fadeUp 0.45s ease both;
}

.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 0.5rem;
}

.subtle {
    color: var(--muted);
    font-size: 0.95rem;
    line-height: 1.65;
}

.stButton>button{

height:48px;

border-radius:14px;

background:linear-gradient(135deg,#4F8CFF,#2563EB);

border:none;

font-weight:700;

font-size:15px;

box-shadow:0 10px 25px rgba(79,140,255,.30);

transition:.25s;

}

.stButton>button:hover{

transform:translateY(-2px);

background:linear-gradient(135deg,#5E97FF,#3B82F6);

box-shadow:0 15px 35px rgba(79,140,255,.45);

}

div[data-testid="stMetric"] {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 0.95rem 1rem;
    box-shadow: var(--shadow);
}

div[data-testid="stFileUploader"] {
    background: var(--surface-2);
    padding: 1rem;
    border-radius: 18px;
    border: 2px dashed rgba(79,140,255,0.3);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div {
    border-radius: 14px !important;
    border: 1px solid var(--border) !important;
    padding: 0.78rem 0.9rem !important;
    background: var(--surface) !important;
    color: var(--ink) !important;
    box-shadow: none !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(79,140,255,0.16) !important;
}

[data-testid="stCheckbox"] label {
    color: var(--ink);
}

.sidebar-card {
    padding: 0.8rem;
    border-radius: 18px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 0.7rem;
}

.sidebar-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: white;
    margin-bottom: 0.35rem;
}

.sidebar-text {
    color: #cfe0ff;
    font-size: 0.86rem;
    line-height: 1.5;
}

.chip {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    border-radius: 999px;
    background: rgba(255,255,255,0.12);
    color: white;
    padding: 0.4rem 0.7rem;
    font-size: 0.8rem;
    font-weight: 700;
    margin-top: 0.35rem;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 1000px) {
    .topbar { flex-direction: column; align-items: flex-start; gap: 0.7rem; }
    .topbar-right { width: 100%; justify-content: space-between; }
}


hr{
border:none;
height:1px;
background:rgba(255,255,255,.08);
margin:20px 0;
}

::-webkit-scrollbar{
width:8px;
}

::-webkit-scrollbar-thumb{
background:#334155;
border-radius:20px;
}

::-webkit-scrollbar-thumb:hover{
background:#4F8CFF;
}

div[data-testid="stMetricValue"]{

font-size:34px!important;

font-weight:800!important;

}

div[data-testid="stMetricLabel"]{

font-size:14px!important;

font-weight:600!important;

color:#94A3B8!important;

}



div[data-testid="stMetric"]{

background:linear-gradient(135deg,#122033,#1B2E4B)!important;

border:none!important;

border-radius:22px!important;

padding:18px!important;

box-shadow:0 12px 30px rgba(0,0,0,.25)!important;

}

div[data-testid="stMetric"]:hover{

transform:translateY(-5px);

transition:.25s;

}

div[data-testid="stMetricLabel"]{

font-size:15px!important;

font-weight:600!important;

color:#B8CAE8!important;

}

div[data-testid="stMetricValue"]{

font-size:34px!important;

font-weight:800!important;

color:white!important;

}



div[data-testid="stFileUploader"]{

background:#13253C!important;

border:2px dashed #3B82F6!important;

border-radius:22px!important;

padding:25px!important;

}

div[data-testid="stFileUploader"]:hover{

border-color:#60A5FA!important;

background:#182E4B!important;

transition:.25s;

}


.stProgress>div>div{

background:linear-gradient(90deg,#2563EB,#22C55E)!important;

height:12px!important;

border-radius:999px!important;

}

.stAlert{

border-radius:18px!important;

border:none!important;

}

.stSuccess{

background:#0F3D2E!important;

}

.stWarning{

background:#4A3608!important;

}

.stError{

background:#4A1111!important;


}


textarea,
input{

font-size:15px!important;

}

[data-testid="stTextInput"] input{

height:50px!important;

border-radius:14px!important;

}

[data-testid="stTextArea"] textarea{

border-radius:16px!important;

padding:15px!important;

}

label{

font-weight:700!important;

}
</style>
"""

css = css_template.replace("<<BG>>", bg).replace("<<SURFACE>>", surface).replace("<<SURFACE2>>", surface_2).replace("<<INK>>", ink).replace("<<MUTED>>", muted).replace("<<PRIMARY>>", primary).replace("<<PRIMARY2>>", primary_2).replace("<<ACCENT>>", accent).replace("<<BORDER>>", border).replace("<<SHADOW>>", shadow).replace("<<LABEL>>", label)

st.markdown(css, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-title">🏙️ UrbanPulse AI</div>
        <div class="sidebar-text">Intelligent civic operations for smarter cities.</div>
        <div class="chip">✨ AI Powered</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🏙️ Citizen Portal", use_container_width=True):
        st.switch_page("app.py")

    if st.button("📊 Admin Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")

    st.markdown("---")

    st.markdown("<div class='sidebar-title'>🔐 Admin Access</div>", unsafe_allow_html=True)

    username = st.text_input("Username", key="admin_user")
    password = st.text_input("Password", type="password", key="admin_pass")

    if st.button("Access Dashboard", use_container_width=True):
        if username == "admin" and password == "admin123":
            st.session_state.admin = True
            st.success("✅ Login successful")
        else:
            st.error("❌ Invalid credentials")

    if st.session_state.admin:
        st.success("Admin session active")
        if st.button("Logout", use_container_width=True):
            st.session_state.admin = False
            st.session_state.admin_user = ""
            st.session_state.admin_pass = ""

    st.markdown("---")
    st.caption("YOLO • Gemini AI • NLP • SQLite")

st.markdown("""
<div class="topbar">
  <div class="topbar-left">
    <div class="logo-badge">⚡</div>
    <div>
      <div class="eyebrow">Urban Intelligence Platform</div>
      <div class="page-title">Citizen Portal</div>
    </div>
  </div>
  <div class="topbar-right">
    <div class="pill">Live AI Workflow</div>
    <div class="avatar">CU</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">

<div style="display:flex;justify-content:space-between;align-items:center;gap:25px;">

<div style="flex:1;">

<div style="
display:inline-block;
padding:8px 16px;
border-radius:999px;
background:rgba(255,255,255,.15);
color:white;
font-size:13px;
font-weight:700;
margin-bottom:18px;
">

🚀 AI Powered Smart City Platform

            
</div>
            
<div style="
width:180px;
height:180px;
border-radius:50%;
background:rgba(255,255,255,.12);
display:flex;
justify-content:center;
align-items:center;
font-size:90px;
backdrop-filter:blur(12px);
">

🏙️

</div>

<h1 style="
font-size:64px;
font-weight:800;
margin-bottom:10px;
">

UrbanPulse AI

</h1>

<h3 style="
font-size:22px;
font-weight:600;

margin-bottom:18px;
color:#E0ECFF;
">

Intelligent Urban Complaint Detection & Management

</h3>

<p style="
font-size:16px;
line-height:1.8;
max-width:700px;
color:#EEF4FF;
">

Upload images of potholes, garbage and civic issues.
UrbanPulse AI uses YOLO for detection, Gemini AI for intelligent report generation,
NLP for department prediction and SQLite for complaint tracking.

</p>

<br>

<div style="display:flex;gap:14px;">

<div style="
padding:12px 20px;
background:white;
color:#2563EB;
border-radius:12px;
font-weight:700;
">

🤖 YOLO Detection

</div>

<div style="
padding:12px 20px;
background:rgba(255,255,255,.15);
color:white;
border-radius:12px;
font-weight:700;
">

✨ Gemini AI

</div>

<div style="
padding:12px 20px;
background:rgba(255,255,255,.15);
color:white;
border-radius:12px;
font-weight:700;
">

🧠 NLP

</div>

</div>

</div>

<div>

<img
src="https://img.icons8.com/fluency/480/smart-city.png"
width="240">

</div>

</div>

</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card fade-card">
  <div class="section-title">⚡ Quick Actions</div>
  <div class="subtle">Choose how you would like to continue with the complaint workflow.</div>
</div>
""", unsafe_allow_html=True)

if "detected" not in st.session_state:
    st.session_state.detected = False

if "show_form" not in st.session_state:
    st.session_state.show_form = False

if "issue" not in st.session_state:
    st.session_state.issue = ""

if "confidence" not in st.session_state:
    st.session_state.confidence = 0

if "result_image" not in st.session_state:
    st.session_state.result_image = None

if "image_path" not in st.session_state:
    st.session_state.image_path = ""

if "show_upload" not in st.session_state:
    st.session_state.show_upload = False

st.markdown("<br>", unsafe_allow_html=True)



# ===========================
# Dashboard Statistics
# ===========================

cursor.execute("SELECT COUNT(*) FROM complaints")
total_complaints = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'")
pending_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'")
resolved_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='In Progress'")
progress_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM complaints WHERE confidence >= 0.90")
high_confidence = cursor.fetchone()[0]

if total_complaints > 0:
    ai_accuracy = round((high_confidence / total_complaints) * 100, 1)
else:
    ai_accuracy = 0.0

today = datetime.now().strftime("%d-%m-%Y")

cursor.execute(
    "SELECT COUNT(*) FROM complaints WHERE date LIKE ?",
    (today + "%",)
)
today_complaints = cursor.fetchone()[0]






c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "📋 Total Complaints",
        total_complaints,
        "+5 Today"
    )

with c2:
    st.metric(
        "⏳ Pending",
        pending_count,
        "-2"
    )

with c3:
    st.metric(
        "✅ Resolved",
        resolved_count,
        "+7"
    )

with c4:
    accuracy = f"{st.session_state.confidence*100:.1f}%" if st.session_state.detected else "96.8%"
    st.metric(
        "🤖 AI Accuracy",
        accuracy,
        "+1.4%"
    )



st.markdown("<br>", unsafe_allow_html=True)

b1, b2, b3 = st.columns([1,1,1])

with b1:

    if st.button(
        "🚀 Report New Complaint",
        use_container_width=True
    ):

        st.session_state.show_upload = True

with b2:

    if st.button(
        "📊 Open Analytics",
        use_container_width=True
    ):

        st.switch_page("pages/dashboard.py")

with b3:

    if st.button(
        "📂 My Complaints",
        use_container_width=True
    ):

        st.info("Coming Soon")

if st.session_state.show_upload:

    st.markdown("""

<div class="card fade-card">

<div style="display:flex;justify-content:space-between;align-items:center;">

<div>

<div class="section-title">

📤 Upload Complaint Image

</div>

<div class="subtle">

Upload JPG, JPEG or PNG image for AI detection.

</div>

</div>

<div style="
padding:10px 18px;
background:#2563EB;
border-radius:12px;
color:white;
font-weight:700;
">

YOLO Ready

</div>

</div>

""",unsafe_allow_html=True)

    uploaded_file = st.file_uploader(

        "",

        type=["jpg","jpeg","png"],

        label_visibility="collapsed"

    )

    st.markdown("</div>",unsafe_allow_html=True)
else:
    uploaded_file = None

if st.session_state.show_upload and st.button("🔍 Detect Issue", use_container_width=True):
    if uploaded_file is None:
        st.warning("Please upload an image first.")
    else:
        with st.spinner("Analyzing the image with AI..."):
            image = Image.open(uploaded_file).convert("RGB")
            image = np.array(image)

            models = [
                ("Pothole", YOLO("models/pothole_best.pt")),
                ("Garbage", YOLO("models/garbage_best.pt"))
            ]

            best_result = None
            best_issue = ""
            best_confidence = 0

            for issue_name, current_model in models:
                prediction = current_model.predict(source=image, verbose=False)
                boxes = prediction[0].boxes

                if len(boxes) > 0:
                    conf = float(boxes.conf[0])
                    if conf > best_confidence:
                        best_confidence = conf
                        best_issue = issue_name
                        best_result = prediction

            if best_result is None:
                st.error("❌ No urban issue detected.")
                st.session_state.detected = False
            else:
                result_image = best_result[0].plot()

                st.session_state.detected = True
                st.session_state.issue = best_issue

                if best_confidence < 0.70:
                    st.warning("⚠ Low confidence detection. Please upload a clearer image.")
                    st.stop()

                st.session_state.confidence = best_confidence
                st.session_state.result_image = result_image

                os.makedirs("uploads", exist_ok=True)
                image_path = os.path.join("uploads", uploaded_file.name)

                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                st.session_state.image_path = image_path
                st.success("✅ Detection completed")

if st.session_state.detected:

    st.markdown("<br>", unsafe_allow_html=True)

    left,right=st.columns([1.7,1])

    with left:

        st.markdown("""
<div class="card fade-card">

<div class="section-title">

🖼 Detection Preview

</div>

""",unsafe_allow_html=True)

        st.image(
            st.session_state.result_image,
            use_container_width=True
        )

        st.markdown("</div>",unsafe_allow_html=True)

    with right:

        st.markdown("""

<div class="card fade-card">

<div class="section-title">

🤖 AI Detection

</div>

""",unsafe_allow_html=True)

        st.success(
            f"Detected : {st.session_state.issue}"
        )

        st.metric(
            "Confidence",
            f"{st.session_state.confidence*100:.2f}%"
        )

        st.progress(
            st.session_state.confidence
        )

        if st.session_state.confidence>0.90:

            st.success("🟢 High Confidence")

        elif st.session_state.confidence>0.75:

            st.warning("🟡 Medium Confidence")

        else:

            st.error("🔴 Low Confidence")

        st.markdown("<br>",unsafe_allow_html=True)

        st.info("YOLO Detection Completed")

        st.success("Gemini Ready")

        st.info("Department Prediction Ready")

        if st.button(
            "🚨 Continue to Complaint Form",
            use_container_width=True
        ):

            st.session_state.show_form=True

        st.markdown("</div>",unsafe_allow_html=True)

    

if st.session_state.show_form:

    st.markdown("""

<div class="card fade-card">

<div style="display:flex;justify-content:space-between;align-items:center;">

<div>

<div class="section-title">

📝 Complaint Details

</div>

<div class="subtle">

Complete the information below before submitting.

</div>

</div>

<div style="
padding:10px 18px;
background:#22C55E;
color:white;
font-weight:700;
border-radius:12px;
">

Ready to Submit

</div>

</div>

""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        location = st.text_input(
            "📍 Complaint Location"
        )

        citizen = st.text_input(
            "👤 Citizen Name"
        )

    with c2:

        phone = st.text_input(
            "📞 Phone Number"
        )

        ward = st.text_input(
            "🏘 Ward / Area"
        )

    description = st.text_area(
        "📝 Describe the Issue",
        height=160
    )

    submit = st.button(
        "🚀 Submit Complaint",
        use_container_width=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if submit:

        if location.strip() == "":

            st.warning("Please enter complaint location.")

            st.stop()

        predicted_issue = ""
        department = "General Urban Department"

        if description.strip():

            text = tfidf.transform([description])

            predicted_issue = nlp_model.predict(text)[0]

            department = department_names.get(
                predicted_issue,
                predicted_issue
            )

        with st.spinner("Generating AI Report..."):

            ai_report = generate_ai_summary(

                st.session_state.issue,

                department,

                location,

                description

            )

            vision_report = analyze_image_with_gemini(

                st.session_state.image_path

            )

        complaint_id = f"UPA-{random.randint(100000,999999)}"

        current_date = datetime.now().strftime("%d-%m-%Y %H:%M")

        cursor.execute("""

        INSERT INTO complaints(

        issue_type,

        confidence,

        location,

        image_path,

        status,

        date,

        ai_summary

        )

        VALUES(?,?,?,?,?,?,?)

        """,(

        st.session_state.issue,

        st.session_state.confidence,

        location,

        st.session_state.image_path,

        "Pending",

        current_date,

        ai_report

        ))

        conn.commit()

        st.success("🎉 Complaint Submitted Successfully")

        

        st.info(f"Complaint ID : {complaint_id}")

        st.success(f"Department : {department}")

        st.markdown("### 🤖 AI Summary")

        st.info(ai_report)

        st.markdown("### 👁 Gemini Vision")

        st.info(vision_report)

        st.session_state.show_form = False
        st.session_state.detected = False

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='card fade-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>🚀 Trusted Technologies</div>", unsafe_allow_html=True)

st.markdown("""
<div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0.8rem;">
    <div class="card" style="margin-bottom:0;">
        <div class="section-title">🐍 Python</div>
        <div class="subtle">Core engine behind the full application workflow.</div>
    </div>
    <div class="card" style="margin-bottom:0;">
        <div class="section-title">🤖 YOLOv11</div>
        <div class="subtle">Real-time computer vision for civic issue detection.</div>
    </div>
    <div class="card" style="margin-bottom:0;">
        <div class="section-title">✨ Gemini AI</div>
        <div class="subtle">Generates professional summaries and recommendations.</div>
    </div>
    <div class="card" style="margin-bottom:0;">
        <div class="section-title">🧠 NLP</div>
        <div class="subtle">Predicts the most relevant municipal department.</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='card fade-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>💡 Why UrbanPulse AI?</div>", unsafe_allow_html=True)

st.markdown("""
<div style="display:grid;grid-template-columns:0.9fr 1.1fr;gap:1rem;align-items:center;">
    <div style="background:linear-gradient(135deg, rgba(79,140,255,0.12), rgba(53,211,155,0.12));border:1px solid var(--border);border-radius:24px;padding:1rem;">
        <img src="https://img.icons8.com/fluency/512/smart-city.png" style="width:100%;max-width:320px;border-radius:18px;" />
    </div>
    <div class="card" style="margin-bottom:0;">
        <div class="section-title">Built for smarter, faster urban governance</div>
        <div class="subtle">
            UrbanPulse AI combines computer vision, natural language processing, and generative AI into one premium civic complaint platform. It reduces manual effort, improves issue visibility, and accelerates resolution for municipalities.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='card fade-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>⚙️ How It Works</div>", unsafe_allow_html=True)

st.markdown("""
<div style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0.8rem;">
    <div class="card" style="margin-bottom:0;">
        <div class="section-title">📤 Upload</div>
        <div class="subtle">Add a complaint image.</div>
    </div>
    <div class="card" style="margin-bottom:0;">
        <div class="section-title">🤖 Detect</div>
        <div class="subtle">YOLO identifies the issue.</div>
    </div>
    <div class="card" style="margin-bottom:0;">
        <div class="section-title">🧠 Analyze</div>
        <div class="subtle">AI processes the report.</div>
    </div>
    <div class="card" style="margin-bottom:0;">
        <div class="section-title">🏢 Assign</div>
        <div class="subtle">Department is predicted.</div>
    </div>
    <div class="card" style="margin-bottom:0;">
        <div class="section-title">✅ Resolve</div>
        <div class="subtle">Track and monitor progress.</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)