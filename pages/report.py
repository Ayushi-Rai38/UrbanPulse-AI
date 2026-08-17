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

from database.database import get_connection
from components.sidebar import render_sidebar


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="UrbanPulse AI | Report",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOGIN CHECK
# ============================================================

if not st.session_state.get("logged_in", False):
    st.switch_page("pages/login.py")


# ============================================================
# SIDEBAR
# ============================================================

render_sidebar()


# ============================================================
# GEMINI SETUP
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
else:
    gemini_model = None


# ============================================================
# MODELS
# ============================================================

@st.cache_resource
def load_models():
    pothole_model = YOLO("models/pothole_best.pt")
    garbage_model = YOLO("models/garbage_best.pt")
    return pothole_model, garbage_model


@st.cache_resource
def load_nlp():
    model = joblib.load("models/model.pkl")
    vectorizer = joblib.load("models/tfidf.pkl")
    return model, vectorizer


pothole_model, garbage_model = load_models()
nlp_model, tfidf = load_nlp()


# ============================================================
# HELPERS
# ============================================================

department_names = {
    "Solid Waste (Garbage) Related": "Solid Waste Department",
    "Road Maintenance (Engg)": "Road Maintenance Department",
}


def generate_ai_summary(issue, department, location, description):
    if gemini_model is None:
        return (
            "Gemini API key is not configured. "
            "The complaint was still recorded successfully."
        )

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

Keep the response professional and concise.
"""

    response = gemini_model.generate_content(prompt)
    return response.text


def analyze_image_with_gemini(image_path):
    if gemini_model is None:
        return "Gemini Vision is unavailable because GEMINI_API_KEY is not configured."

    image = Image.open(image_path)

    prompt = """
Analyze this urban complaint image.

Give:
1. Objects detected
2. Severity (Low / Medium / High)
3. Possible Risk
4. Recommended Action

Keep the response under 120 words.
"""

    response = gemini_model.generate_content([prompt, image])
    return response.text


def detect_issue(image_array):
    models = [
        ("Pothole", pothole_model),
        ("Garbage", garbage_model),
    ]

    best_result = None
    best_issue = ""
    best_confidence = 0.0

    for issue_name, model in models:
        prediction = model.predict(
            source=image_array,
            verbose=False,
        )

        boxes = prediction[0].boxes

        if len(boxes) > 0:
            # Use the highest confidence detection from this model.
            confidence = float(boxes.conf.max())

            if confidence > best_confidence:
                best_confidence = confidence
                best_issue = issue_name
                best_result = prediction

    return best_result, best_issue, best_confidence


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "report_detected": False,
    "report_show_form": False,
    "report_issue": "",
    "report_confidence": 0.0,
    "report_result_image": None,
    "report_image_path": "",
    "report_uploaded_name": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CSS — SAME VISUAL LANGUAGE AS OTHER PAGES
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f5f3ec;
    }

    .block-container {
        max-width: 1400px;
        padding: 1rem 2.2rem 4rem;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    /* ---------- SHARED SIDEBAR ---------- */

    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    section[data-testid="stSidebar"] {
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
        background: #f1f1f6 !important;
        border-right: 1px solid #dedee3 !important;
    }

    section[data-testid="stSidebar"] > div {
        background: #f1f1f6 !important;
    }

    /* ---------- TOP BAR ---------- */

    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.2rem 0 0.85rem;
        border-bottom: 1px solid #deddd6;
        margin-bottom: 1.5rem;
    }

    .logo-area {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .logo-box {
        width: 32px;
        height: 32px;
        background: #17212b;
        color: white;
        border-radius: 7px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 900;
    }

    .logo-name {
        color: #17212b;
        font-size: 16px;
        font-weight: 850;
    }

    .breadcrumb {
        color: #777b76;
        font-size: 10px;
        letter-spacing: 1.4px;
        text-transform: uppercase;
    }

    /* ---------- HERO ---------- */

    .report-eyebrow {
        color: #777b76;
        font-size: 9px;
        letter-spacing: 2.2px;
        text-transform: uppercase;
        font-weight: 850;
        margin-top: 8px;
        margin-bottom: 22px;
    }

    .report-title {
        color: #172033;
        font-size: clamp(48px, 5.5vw, 78px);
        line-height: 0.96;
        letter-spacing: -4px;
        font-weight: 850;
        margin: 0;
        max-width: 900px;
    }

    .report-description {
        color: #62686e;
        font-size: 15px;
        line-height: 1.7;
        max-width: 980px;
        margin-top: 25px;
    }

    /* ---------- USER STRIP ---------- */

    .user-strip {
        background: #eef0f5;
        border: 1px solid #d9dce3;
        border-radius: 5px;
        padding: 11px 16px;
        color: #626a73;
        font-size: 11px;
        margin-top: 30px;
        margin-bottom: 30px;
    }

    .user-strip strong {
        color: #202733;
    }

    /* ---------- CARDS ---------- */

    .card {
        background: #ffffff;
        border: 1px solid #deded9;
        border-radius: 6px;
        padding: 28px;
        box-sizing: border-box;
        height: 100%;
    }

    .card-label {
        color: #777b76;
        font-size: 8px;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 850;
        margin-bottom: 12px;
    }

    .card-title {
        color: #172033;
        font-size: 28px;
        font-weight: 820;
        margin-bottom: 8px;
    }

    .card-description {
        color: #666d74;
        font-size: 12px;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    /* ---------- DARK AI CARD ---------- */

    .card-dark {
        background: #15232d;
        border-radius: 6px;
        padding: 28px;
        min-height: 100%;
        box-sizing: border-box;
    }

    .dark-label {
        color: #e3c52b;
        font-size: 8px;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 850;
        margin-bottom: 12px;
    }

    .dark-title {
        color: white;
        font-size: 28px;
        font-weight: 820;
        margin-bottom: 10px;
    }

    .dark-description {
        color: #d5dce0;
        font-size: 12px;
        line-height: 1.6;
        margin-bottom: 18px;
    }

    .workflow-item {
        border: 1px solid rgba(255,255,255,0.18);
        padding: 13px;
        margin-top: 10px;
    }

    .workflow-number {
        color: #9daab1;
        font-size: 8px;
        letter-spacing: 1.3px;
    }

    .workflow-text {
        color: white;
        font-size: 11px;
        font-weight: 650;
        margin-top: 5px;
    }

    /* ---------- SECTION ---------- */

    .section {
        border-top: 1px solid #deddd6;
        margin-top: 32px;
        padding-top: 17px;
    }

    .section-label {
        color: #777b76;
        font-size: 9px;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 850;
        margin-bottom: 14px;
    }

    .section-title {
        color: #172033;
        font-size: 27px;
        font-weight: 820;
        margin-bottom: 18px;
    }

    /* ---------- BUTTONS ---------- */

    div.stButton > button {
        background: #ffffff !important;
        color: #172033 !important;
        border: 1px solid #2d59d1 !important;
        border-radius: 4px !important;
        min-height: 44px !important;
        font-weight: 750 !important;
        box-shadow: none !important;
    }

    div.stButton > button:hover {
        background: #f7f8ff !important;
        color: #2148bb !important;
        border-color: #2148bb !important;
    }

    /* ---------- INPUTS ---------- */

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background: #ffffff !important;
        color: #202733 !important;
        border: 1px solid #d8d9df !important;
        border-radius: 5px !important;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: #2d59d1 !important;
        box-shadow: 0 0 0 2px rgba(45,89,209,0.10) !important;
    }

    label {
        color: #4e535b !important;
        font-size: 11px !important;
        font-weight: 650 !important;
    }

    /* ---------- UPLOADER ---------- */

    [data-testid="stFileUploader"] {
        background: #fafaf8;
        border: 1px dashed #cfd1d2;
        border-radius: 5px;
        padding: 10px;
    }

    /* ---------- RESULT ---------- */

    .result-card {
        background: #ffffff;
        border: 1px solid #deded9;
        border-radius: 6px;
        padding: 24px;
        margin-top: 20px;
    }

    .result-dark {
        background: #15232d;
        border-radius: 6px;
        padding: 24px;
        color: white;
    }

    .result-label {
        color: #777b76;
        font-size: 8px;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 850;
    }

    .result-dark .result-label {
        color: #e3c52b;
    }

    .result-title {
        color: #172033;
        font-size: 25px;
        font-weight: 820;
        margin-top: 7px;
    }

    .result-dark .result-title {
        color: white;
    }

    .complaint-id {
        background: #eef0f5;
        border: 1px solid #d9dce3;
        border-radius: 5px;
        padding: 16px;
        color: #202733;
        font-size: 14px;
        font-weight: 750;
        margin-top: 18px;
    }

    /* ---------- METRIC ---------- */

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #deded9;
        border-radius: 5px;
        box-shadow: none;
    }

    /* ---------- MOBILE ---------- */

    @media (max-width: 900px) {
        .report-title {
            font-size: 48px;
            letter-spacing: -2px;
        }

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TOP BAR
# ============================================================

st.html(
    """
    <div class="topbar">

    <div class="logo-area">
        <div class="logo-box">UP</div>
        <div class="logo-name">UrbanPulse AI</div>
    </div>

    <div class="breadcrumb">
        REPORT &nbsp;/&nbsp; CIVIC SIGNAL
    </div>

    </div>
    """
)


# ============================================================
# HERO
# ============================================================

st.html(
    """
    <div class="report-eyebrow">
        01 / REPORT AN ISSUE
    </div>

    <div class="report-title">
        Turn a street issue<br>
        into a civic signal.
    </div>

    <div class="report-description">
        Upload an image of a visible urban problem.
        UrbanPulse AI analyses the evidence, identifies the
        issue type, and creates a complaint record for follow-up.
    </div>
    """
)


# ============================================================
# USER STRIP
# ============================================================

user_name = st.session_state.get("user_name") or "Citizen"
user_email = st.session_state.get("user_email") or ""

st.markdown(
    f"""
    <div class="user-strip">
        Reporting as <strong>{user_name}</strong>
        &nbsp;·&nbsp; {user_email}
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MAIN EVIDENCE / AI WORKFLOW
# ============================================================

left, right = st.columns(
    [1.55, 1],
    gap="large",
)


# ============================================================
# LEFT — COMPLAINT EVIDENCE
# ============================================================

with left:

    st.html(
        """
        <div class="card">

        <div class="card-label">
            COMPLAINT EVIDENCE
        </div>

        <div class="card-title">
            Submit a new report
        </div>

        <div class="card-description">
            Start by uploading a clear image of the urban
            problem you want to report.
        </div>

        </div>
        """
    )

    uploaded_file = st.file_uploader(
        "Upload complaint image",
        type=["jpg", "jpeg", "png"],
        label_visibility="visible",
    )

    if uploaded_file is not None:
        preview = Image.open(uploaded_file).convert("RGB")

        st.image(
            preview,
            caption="Uploaded evidence",
            use_container_width=True,
        )

    detect_clicked = st.button(
        "Analyse Evidence",
        use_container_width=True,
    )


# ============================================================
# RIGHT — AI EVIDENCE
# ============================================================

with right:

    st.html(
        """
        <div class="card-dark">

        <div class="dark-label">
            02 / AI EVIDENCE
        </div>

        <div class="dark-title">
            Detect → Verify → Record
        </div>

        <div class="dark-description">
            The uploaded evidence is analysed using
            computer vision before the complaint is submitted.
        </div>

        <div class="workflow-item">
        <div class="workflow-number">01 / IMAGE</div>
        <div class="workflow-text">Street-level evidence</div>
        </div>

        <div class="workflow-item">
        <div class="workflow-number">02 / AI</div>
        <div class="workflow-text">YOLO issue detection</div>
        </div>

        <div class="workflow-item">
        <div class="workflow-number">03 / RECORD</div>
        <div class="workflow-text">SQLite complaint record</div>
        </div>

        </div>
        """
    )


# ============================================================
# DETECTION
# ============================================================

if detect_clicked:

    if uploaded_file is None:
        st.warning("Please upload an image first.")

    else:

        with st.spinner("Analysing the uploaded evidence..."):

            image = Image.open(uploaded_file).convert("RGB")
            image_array = np.array(image)

            result, issue, confidence = detect_issue(image_array)

            if result is None:

                st.session_state.report_detected = False
                st.error(
                    "No supported urban issue was detected. "
                    "Try a clearer pothole or garbage image."
                )

            elif confidence < 0.70:

                st.session_state.report_detected = False
                st.warning(
                    "Detection confidence is low. "
                    "Please upload a clearer image."
                )

            else:

                result_image = result[0].plot()

                os.makedirs("uploads", exist_ok=True)

                safe_name = (
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                    f"{uploaded_file.name}"
                )

                image_path = os.path.join(
                    "uploads",
                    safe_name,
                )

                with open(image_path, "wb") as file:
                    file.write(uploaded_file.getbuffer())

                st.session_state.report_detected = True
                st.session_state.report_issue = issue
                st.session_state.report_confidence = confidence
                st.session_state.report_result_image = result_image
                st.session_state.report_image_path = image_path
                st.session_state.report_uploaded_name = uploaded_file.name
                st.session_state.report_show_form = False

                st.success("Detection completed successfully.")


# ============================================================
# DETECTION RESULT
# ============================================================

if st.session_state.report_detected:

    st.markdown(
        '<div class="section"><div class="section-label">03 / DETECTION</div></div>',
        unsafe_allow_html=True,
    )

    result_left, result_right = st.columns(
        [1.45, 1],
        gap="large",
    )

    with result_left:

        st.html(
            """
            <div class="result-card">
            <div class="result-label">DETECTION PREVIEW</div>
            <div class="result-title">Verified visual evidence</div>
            </div>
            """
        )

        st.image(
            st.session_state.report_result_image,
            use_container_width=True,
        )

    with result_right:

        st.html(
            """
            <div class="result-dark">
            <div class="result-label">AI VERIFICATION</div>
            <div class="result-title">Detection result</div>
            </div>
            """
        )

        st.metric(
            "Detected Issue",
            st.session_state.report_issue,
        )

        st.metric(
            "Confidence",
            f"{st.session_state.report_confidence * 100:.2f}%",
        )

        st.progress(
            st.session_state.report_confidence
        )

        if st.session_state.report_confidence >= 0.90:
            st.success("High confidence detection")
        elif st.session_state.report_confidence >= 0.75:
            st.warning("Medium confidence detection")
        else:
            st.info("Low confidence detection")

        if st.button(
            "Continue to Complaint Details",
            use_container_width=True,
        ):
            st.session_state.report_show_form = True


# ============================================================
# COMPLAINT FORM
# ============================================================

if st.session_state.report_show_form:

    st.markdown(
        '<div class="section"><div class="section-label">04 / COMPLAINT DETAILS</div></div>',
        unsafe_allow_html=True,
    )

    st.html(
        """
        <div class="card">

        <div class="card-label">
            CIVIC RECORD
        </div>

        <div class="card-title">
            Complete the report
        </div>

        <div class="card-description">
            Add the location and citizen description so the
            AI can prepare the complaint for the appropriate department.
        </div>

        </div>
        """
    )

    c1, c2 = st.columns(2)

    with c1:

        location = st.text_input(
            "Complaint Location",
            placeholder="e.g. Lucknow, Gomti Nagar",
        )

        citizen = st.text_input(
            "Citizen Name",
            value=user_name,
        )

    with c2:

        phone = st.text_input(
            "Phone Number",
            placeholder="Enter phone number",
        )

        ward = st.text_input(
            "Ward / Area",
            placeholder="Enter ward or area",
        )

    description = st.text_area(
        "Describe the Issue",
        placeholder="Describe what you observed at the location...",
        height=150,
    )

    submit = st.button(
        "Submit Complaint",
        use_container_width=True,
    )

    if submit:

        if not location.strip():
            st.warning("Please enter complaint location.")
            st.stop()

        predicted_issue = ""
        department = "General Urban Department"

        if description.strip():

            text = tfidf.transform([description])

            predicted_issue = nlp_model.predict(text)[0]

            department = department_names.get(
                predicted_issue,
                predicted_issue,
            )

        with st.spinner("Generating AI complaint report..."):

            ai_report = generate_ai_summary(
                st.session_state.report_issue,
                department,
                location,
                description,
            )

            vision_report = analyze_image_with_gemini(
                st.session_state.report_image_path,
            )

        complaint_id = (
            f"UPA-{random.randint(100000, 999999)}"
        )

        current_date = datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO complaints (
                issue_type,
                confidence,
                location,
                image_path,
                status,
                date,
                ai_summary,
                latitude,
                longitude
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                st.session_state.report_issue,
                st.session_state.report_confidence,
                location,
                st.session_state.report_image_path,
                "Pending",
                current_date,
                ai_report,
                None,
                None,
            ),
        )

        conn.commit()
        conn.close()

        # ====================================================
        # SUCCESS RESULT
        # ====================================================

        st.markdown(
            '<div class="section"><div class="section-label">05 / COMPLAINT CREATED</div></div>',
            unsafe_allow_html=True,
        )

        st.html(
            f"""
            <div class="card">

            <div class="card-label">
                COMPLAINT CREATED
            </div>

            <div class="card-title">
                {complaint_id}
            </div>

            <div class="card-description">
                Your civic complaint has been recorded and is
                now available for administrative follow-up.
            </div>

            </div>
            """
        )

        info1, info2 = st.columns(2)

        with info1:
            st.html(
                f"""
                <div class="result-card">
                <div class="result-label">ISSUE</div>
                <div class="result-title">
                    {st.session_state.report_issue}
                </div>
                </div>
                """
            )

        with info2:
            st.html(
                f"""
                <div class="result-card">
                <div class="result-label">DEPARTMENT</div>
                <div class="result-title">
                    {department}
                </div>
                </div>
                """
            )

        st.html(
            """
            <div class="result-card">
            <div class="result-label">GEMINI AI</div>
            <div class="result-title">
                Complaint Summary
            </div>
            </div>
            """
        )

        st.info(ai_report)

        st.html(
            """
            <div class="result-card">
            <div class="result-label">GEMINI VISION</div>
            <div class="result-title">
                Image Analysis
            </div>
            </div>
            """
        )

        st.info(vision_report)

        st.session_state.report_show_form = False
        st.session_state.report_detected = False


# ============================================================
# FOOTER INFORMATION
# ============================================================

st.markdown(
    """
    <div class="section">

    <div class="section-label">
        06 / SYSTEM WORKFLOW
    </div>

    <div style="
        display:grid;
        grid-template-columns:repeat(5,minmax(0,1fr));
        gap:10px;
    ">

    <div class="card">
    <div class="card-label">01</div>
    <div class="card-title" style="font-size:18px;">
        Upload
    </div>
    <div class="card-description">
        Add street-level evidence.
    </div>
    </div>

    <div class="card">
    <div class="card-label">02</div>
    <div class="card-title" style="font-size:18px;">
        Detect
    </div>
    <div class="card-description">
        YOLO identifies the issue.
    </div>
    </div>

    <div class="card">
    <div class="card-label">03</div>
    <div class="card-title" style="font-size:18px;">
        Analyse
    </div>
    <div class="card-description">
        Gemini processes the evidence.
    </div>
    </div>

    <div class="card">
    <div class="card-label">04</div>
    <div class="card-title" style="font-size:18px;">
        Assign
    </div>
    <div class="card-description">
        NLP predicts the department.
    </div>
    </div>

    <div class="card">
    <div class="card-label">05</div>
    <div class="card-title" style="font-size:18px;">
        Record
    </div>
    <div class="card-description">
        SQLite stores the complaint.
    </div>
    </div>

    </div>

    </div>
    """,
    unsafe_allow_html=True,
)