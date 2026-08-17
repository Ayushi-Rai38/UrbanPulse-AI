import streamlit as st
from database.database import get_connection
from components.sidebar import render_sidebar
# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="UrbanPulse AI",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)



# ============================================================
# LOGIN SESSION
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "role" not in st.session_state:
    st.session_state.role = None


# ============================================================
# LOGIN CHECK
# ============================================================

if not st.session_state.logged_in:
    st.switch_page("pages/login.py")
# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- APP ---------- */

    .stApp {
        background: #f5f3ec;
    }

    .block-container {
        max-width: 1400px;
        padding: 1rem 2.2rem 3rem;
    }


    /* ---------- SIDEBAR ---------- */

        /* =====================================================
       HIDE STREAMLIT DEFAULT PAGE NAVIGATION
       ===================================================== */

    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    section[data-testid="stSidebar"] {
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;

        background: #f1f1f6 !important;

        border-right: 1px solid #dedee3;
    }

    section[data-testid="stSidebar"] > div {
        padding: 18px 14px 20px !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

        section[data-testid="stSidebar"] .stButton > button {

            background: transparent !important;

            color: #343941 !important;

            border: 1px solid transparent !important;

            border-radius: 4px !important;

            box-shadow: none !important;

            min-height: 34px !important;

            padding: 4px 12px !important;

            font-size: 12px !important;

            font-weight: 500 !important;

            text-align: left !important;
}


/* Main navigation */

section[data-testid="stSidebar"] .stButton[kind="secondary"] > button {
    background: transparent !important;
}


/* Hover */

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #dedfe6 !important;

    color: #172033 !important;
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

    .hero-box {
        background: #f9f7f0;

        border: 1px solid #dedbd1;

        border-radius: 5px;

        padding: 38px 38px 42px;

        min-height: 365px;
    }

    .hero-eyebrow {
        color: #70756f;

        font-size: 10px;

        letter-spacing: 2px;

        text-transform: uppercase;

        font-weight: 800;

        margin-bottom: 22px;
    }

    .hero-title {
        color: #172033;

        font-size: clamp(42px, 5vw, 70px);

        line-height: 0.98;

        letter-spacing: -3px;

        font-weight: 850;

        margin: 0;

        max-width: 800px;
    }

    .hero-description {
        color: #5c6268;

        font-size: 15px;

        line-height: 1.7;

        max-width: 760px;

        margin-top: 25px;
    }


    /* ---------- WORKFLOW ---------- */

    .workflow {
        background: #15222c;

        border-radius: 7px;

        padding: 25px;

        min-height: 365px;

        box-sizing: border-box;
    }

    .workflow-label {
        color: #e3c52b;

        font-size: 9px;

        letter-spacing: 2px;

        text-transform: uppercase;

        font-weight: 850;
    }

    .workflow-title {
        color: white;

        font-size: 27px;

        font-weight: 800;

        margin-top: 8px;
    }

    .workflow-description {
        color: #d5dce0;

        font-size: 13px;

        line-height: 1.55;

        margin-top: 8px;
    }

    .workflow-grid {
        display: grid;

        grid-template-columns: 1fr 1fr;

        gap: 10px;

        margin-top: 25px;
    }

    .workflow-item {
        border: 1px solid rgba(255,255,255,0.18);

        padding: 12px;

        min-height: 65px;
    }

    .workflow-number {
        color: #aeb8be;

        font-size: 8px;

        letter-spacing: 1.3px;
    }

    .workflow-text {
        color: white;

        font-size: 11px;

        margin-top: 5px;
    }


    /* ---------- BUTTONS ---------- */

    div.stButton > button {
        background: white !important;

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


    /* ---------- SECTIONS ---------- */

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
    }

    .section-title {
        color: #172033;

        font-size: 25px;

        font-weight: 820;

        margin-top: 5px;

        margin-bottom: 18px;
    }


    /* ---------- ISSUE CARDS ---------- */

    .issue-card {
        background: white;

        border: 1px solid #deded9;

        border-radius: 5px;

        padding: 20px;

        min-height: 145px;

        box-sizing: border-box;
    }

    .issue-tag {
        color: #777b76;

        font-size: 8px;

        letter-spacing: 1.6px;

        text-transform: uppercase;

        font-weight: 850;
    }

    .issue-title {
        color: #172033;

        font-size: 21px;

        font-weight: 750;

        margin-top: 10px;
    }

    .issue-description {
        color: #62686e;

        font-size: 12px;

        line-height: 1.55;

        margin-top: 7px;
    }


    /* ---------- OPERATING STEPS ---------- */

    .step {
        border-top: 3px solid #2d59d1;

        padding-top: 9px;
    }

    .step-number {
        color: #2d59d1;

        font-size: 9px;

        font-weight: 900;
    }

    .step-title {
        color: #172033;

        font-size: 15px;

        font-weight: 800;

        margin-top: 5px;
    }

    .step-description {
        color: #656a70;

        font-size: 11px;

        line-height: 1.5;

        margin-top: 4px;
    }


    /* ---------- REMOVE DEFAULT STREAMLIT PADDING ---------- */

    [data-testid="stHeader"] {
        background: transparent;
    }

        /* =====================================================
       SIDEBAR ADMIN INPUTS
       ===================================================== */

    section[data-testid="stSidebar"] input {

        background: #ffffff !important;

        border: 1px solid #d8d9df !important;

        border-radius: 5px !important;

        color: #202733 !important;

        font-size: 12px !important;

        min-height: 34px !important;
    }


    section[data-testid="stSidebar"] label {

        color: #4e535b !important;

        font-size: 11px !important;

        font-weight: 600 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# COMMON SIDEBAR
# ============================================================

render_sidebar()




# ============================================================
# TOP BAR
# ============================================================

st.html(
    """
    <div class="topbar">

        <div class="logo-area">

            <div class="logo-box">
                UP
            </div>

            <div class="logo-name">
                UrbanPulse AI
            </div>

        </div>

        <div class="breadcrumb">
            HOME &nbsp;/&nbsp; CIVIC SIGNAL
        </div>

    </div>
    """
)


# ============================================================
# HERO
# ============================================================

hero_left, hero_right = st.columns(
    [1.45, 0.72],
    gap="large"
)


with hero_left:

    st.html(
        """
        <div class="hero-box">

            <div class="hero-eyebrow">
                Smart Urban Complaint Detection System
            </div>

            <div class="hero-title">
                A city issue becomes a civic signal.
            </div>

            <div class="hero-description">
                UrbanPulse AI helps people report potholes,
                garbage, and other visible infrastructure
                problems with image evidence, confidence,
                and a clear record for follow-up.
            </div>

        </div>
        """
    )

    st.write("")

    button1, button2 = st.columns(2)

    with button1:

        if st.button(
            "Report an Issue",
            key="hero_report",
            use_container_width=True
        ):
            st.switch_page("pages/report.py")

    with button2:
        if st.button(
            "My Complaints",
            key="hero_complaints",
            use_container_width=True
    ):
            st.switch_page("pages/my_complaints.py")

    


# ============================================================
# WORKFLOW
# ============================================================

with hero_right:

    st.html(
        """
        <div class="workflow">

            <div class="workflow-label">
                Live Evidence Workflow
            </div>

            <div class="workflow-title">
                Detect → Report → Track
            </div>

            <div class="workflow-description">
                Every submission keeps the image,
                location, model confidence, and status
                together.
            </div>

            <div class="workflow-grid">

                <div class="workflow-item">
                    <div class="workflow-number">
                        01 / IMAGE
                    </div>

                    <div class="workflow-text">
                        Street-level proof
                    </div>
                </div>

                <div class="workflow-item">
                    <div class="workflow-number">
                        02 / SIGNAL
                    </div>

                    <div class="workflow-text">
                        Confidence score
                    </div>
                </div>

                <div class="workflow-item">
                    <div class="workflow-number">
                        03 / RECORD
                    </div>

                    <div class="workflow-text">
                        SQLite complaint
                    </div>
                </div>

                <div class="workflow-item">
                    <div class="workflow-number">
                        04 / ACTION
                    </div>

                    <div class="workflow-text">
                        Human follow-up
                    </div>
                </div>

            </div>

        </div>
        """
    )


# ============================================================
# SUPPORTED SIGNALS
# ============================================================

st.html(
    """
    <div class="section">

        <div class="section-label">
            Supported Signals
        </div>

        <div class="section-title">
            Built around visible urban issues.
        </div>

    </div>
    """
)


cards = [
    (
        "URBAN / POTHOLES",
        "Potholes",
        "Road-surface damage identified from an uploaded image."
    ),
    (
        "URBAN / GARBAGE",
        "Garbage",
        "Waste accumulation and overflow evidence."
    ),
    (
        "URBAN / OTHER INFRASTRUCTURE",
        "Other Infrastructure",
        "The system explains when a supported model is unavailable."
    )
]


columns = st.columns(3)


for column, (tag, title, description) in zip(columns, cards):

    with column:

        st.html(
            f"""
            <div class="issue-card">

                <div class="issue-tag">
                    {tag}
                </div>

                <div class="issue-title">
                    {title}
                </div>

                <div class="issue-description">
                    {description}
                </div>

            </div>
            """
        )


# ============================================================
# OPERATING LOOP
# ============================================================

st.html(
    """
    <div class="section">

        <div class="section-label">
            The Operating Loop
        </div>

        <div class="section-title">
            From observation to improvement.
        </div>

    </div>
    """
)


steps = [
    (
        "01",
        "Capture",
        "Upload an image from the street."
    ),
    (
        "02",
        "Detect",
        "AI identifies the issue and confidence."
    ),
    (
        "03",
        "Report",
        "Details are stored in the complaint database."
    ),
    (
        "04",
        "Track",
        "Review, resolve and close the loop."
    )
]


step_columns = st.columns(4)


for column, (number, title, description) in zip(
    step_columns,
    steps
):

    with column:

        st.html(
            f"""
            <div class="step">

                <div class="step-number">
                    {number}
                </div>

                <div class="step-title">
                    {title}
                </div>

                <div class="step-description">
                    {description}
                </div>

            </div>
            """
        )