import streamlit as st
from components.sidebar import render_sidebar


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="UrbanPulse AI | About",
    page_icon="▣",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "role" not in st.session_state:
    st.session_state.role = None


# ============================================================
# SIDEBAR
# ============================================================

render_sidebar()


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #f5f3ec;
    }

    .block-container {
        max-width: 1320px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* Hide Streamlit default page navigation */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Main header */
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 18px;
        border-bottom: 1px solid #d9d9d2;
        margin-bottom: 42px;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-logo {
        width: 38px;
        height: 38px;
        border-radius: 8px;
        background: #162131;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 850;
    }

    .brand-name {
        color: #182236;
        font-size: 17px;
        font-weight: 850;
    }

    .breadcrumb {
        color: #777b82;
        font-size: 9px;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        font-weight: 800;
    }

    /* Hero */
    .eyebrow {
        color: #777b82;
        font-size: 9px;
        letter-spacing: 2.2px;
        text-transform: uppercase;
        font-weight: 850;
        margin-bottom: 16px;
    }

    .hero-title {
        color: #172033;
        font-size: clamp(48px, 5.5vw, 76px);
        line-height: 0.98;
        letter-spacing: -3.5px;
        font-weight: 900;
        max-width: 900px;
        margin-bottom: 24px;
    }

    .hero-description {
        color: #62686e;
        font-size: 16px;
        line-height: 1.8;
        max-width: 850px;
        margin-bottom: 45px;
    }

    /* Cards */
    .about-card {
        background: #ffffff;
        border: 1px solid #dcdcd5;
        border-radius: 7px;
        padding: 30px;
        height: 100%;
        box-sizing: border-box;
    }

    .dark-card {
        background: #14232d;
        border: 1px solid #263744;
        border-radius: 7px;
        padding: 30px;
        height: 100%;
        box-sizing: border-box;
    }

    .card-label {
        color: #777b82;
        font-size: 8px;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 850;
        margin-bottom: 14px;
    }

    .dark-label {
        color: #e2c300;
        font-size: 8px;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 850;
        margin-bottom: 14px;
    }

    .card-title {
        color: #172033;
        font-size: 27px;
        line-height: 1.15;
        font-weight: 850;
        margin-bottom: 15px;
    }

    .dark-title {
        color: #ffffff;
        font-size: 27px;
        line-height: 1.15;
        font-weight: 850;
        margin-bottom: 15px;
    }

    .card-text {
        color: #62686e;
        font-size: 14px;
        line-height: 1.75;
    }

    .dark-text {
        color: #cbd5dc;
        font-size: 14px;
        line-height: 1.75;
    }

    /* Technology cards */
    .tech-card {
        background: #ffffff;
        border: 1px solid #dcdcd5;
        border-radius: 7px;
        padding: 24px;
        min-height: 170px;
    }

    .tech-name {
        color: #172033;
        font-size: 19px;
        font-weight: 850;
        margin-bottom: 10px;
    }

    .tech-description {
        color: #6d7379;
        font-size: 13px;
        line-height: 1.65;
    }

    /* Section */
    .section-line {
        border-top: 1px solid #d9d9d2;
        margin: 55px 0 35px;
    }

    .section-label {
        color: #777b82;
        font-size: 9px;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 850;
        margin-bottom: 12px;
    }

    .section-title {
        color: #172033;
        font-size: 34px;
        font-weight: 850;
        letter-spacing: -1.2px;
        margin-bottom: 28px;
    }

    /* Workflow */
    .workflow {
        background: #ffffff;
        border: 1px solid #dcdcd5;
        border-radius: 7px;
        padding: 24px;
        height: 100%;
    }

    .workflow-number {
        color: #777b82;
        font-size: 8px;
        letter-spacing: 1.8px;
        font-weight: 850;
        margin-bottom: 12px;
    }

    .workflow-title {
        color: #172033;
        font-size: 17px;
        font-weight: 850;
        margin-bottom: 8px;
    }

    .workflow-text {
        color: #70757c;
        font-size: 12px;
        line-height: 1.6;
    }

    /* Remove Streamlit top blue line */
        header[data-testid="stHeader"] {
            background: transparent !important;
        }
    
        [data-testid="stDecoration"] {
            display: none !important;
        }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TOP HEADER
# ============================================================

st.markdown(
    """
    <div class="page-header">

    <div class="brand">
        <div class="brand-logo">UP</div>
        <div class="brand-name">UrbanPulse AI</div>
    </div>

    <div class="breadcrumb">
        ABOUT&nbsp;&nbsp;/&nbsp;&nbsp;URBANPULSE AI
    </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="eyebrow">
        SMART URBAN COMPLAINT DETECTION SYSTEM
    </div>

    <div class="hero-title">
        Turning visible city problems<br>
        into actionable civic signals.
    </div>

    <div class="hero-description">
        UrbanPulse AI is a smart civic complaint platform that uses
        computer vision, natural language processing, and generative AI
        to help identify, analyse, and record visible urban issues.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# WHAT IS URBANPULSE
# ============================================================

left, right = st.columns(
    [1.25, 0.9],
    gap="large"
)

with left:

    st.markdown(
        """
        <div class="about-card">

        <div class="card-label">
            01 / THE PLATFORM
        </div>

        <div class="card-title">
            Built around real civic problems.
        </div>

        <div class="card-text">
            UrbanPulse AI allows citizens to submit visual evidence
            of urban problems such as potholes and garbage accumulation.
            The system analyses the uploaded image, determines the
            detected issue and stores the complaint for administrative
            follow-up.
            <br><br>
            The goal is simple: reduce manual reporting effort and
            create a clearer connection between citizen reports and
            civic action.
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with right:

    st.markdown(
        """
        <div class="dark-card">

        <div class="dark-label">
            02 / CORE IDEA
        </div>

        <div class="dark-title">
            Detect → Understand → Record
        </div>

        <div class="dark-text">
            Every complaint follows a structured workflow.
            Visual evidence is analysed first, additional information
            is processed using AI, and the final complaint is stored
            for future tracking.
        </div>

        <br>

        <div class="dark-text">
            <strong>01</strong>&nbsp;&nbsp; Image evidence
            <br><br>
            <strong>02</strong>&nbsp;&nbsp; AI analysis
            <br><br>
            <strong>03</strong>&nbsp;&nbsp; Complaint record
            <br><br>
            <strong>04</strong>&nbsp;&nbsp; Administrative follow-up
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# TECHNOLOGIES
# ============================================================

st.markdown(
    '<div class="section-line"></div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-label">
        03 / TECHNOLOGY
    </div>

    <div class="section-title">
        Intelligence behind the workflow.
    </div>
    """,
    unsafe_allow_html=True,
)


t1, t2, t3, t4 = st.columns(4, gap="medium")


with t1:
    st.markdown(
        """
        <div class="tech-card">

        <div class="tech-name">
            YOLO
        </div>

        <div class="tech-description">
            Computer vision models analyse uploaded images
            and identify supported urban issues.
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with t2:
    st.markdown(
        """
        <div class="tech-card">

        <div class="tech-name">
            Gemini AI
        </div>

        <div class="tech-description">
            Generative AI helps produce complaint summaries,
            severity information and recommended actions.
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with t3:
    st.markdown(
        """
        <div class="tech-card">

        <div class="tech-name">
            NLP
        </div>

        <div class="tech-description">
            Natural language processing analyses citizen
            descriptions and assists with department prediction.
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with t4:
    st.markdown(
        """
        <div class="tech-card">

        <div class="tech-name">
            SQLite
        </div>

        <div class="tech-description">
            Complaint information is stored in a lightweight
            database for tracking and administrative review.
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HOW IT WORKS
# ============================================================

st.markdown(
    '<div class="section-line"></div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-label">
        04 / HOW IT WORKS
    </div>

    <div class="section-title">
        From street evidence to civic record.
    </div>
    """,
    unsafe_allow_html=True,
)


w1, w2, w3, w4, w5 = st.columns(5, gap="small")


workflow = [
    (
        "01 / UPLOAD",
        "Submit evidence",
        "A citizen uploads an image of the visible urban issue."
    ),
    (
        "02 / DETECT",
        "Identify issue",
        "YOLO analyses the image and detects a supported issue."
    ),
    (
        "03 / ANALYZE",
        "Generate insight",
        "AI processes the evidence and complaint information."
    ),
    (
        "04 / ASSIGN",
        "Predict department",
        "NLP assists in identifying the relevant civic department."
    ),
    (
        "05 / RECORD",
        "Track complaint",
        "The complaint is stored for administrative follow-up."
    ),
]


for column, item in zip(
    [w1, w2, w3, w4, w5],
    workflow
):

    with column:

        st.markdown(
            f"""
            <div class="workflow">

            <div class="workflow-number">
                {item[0]}
            </div>

            <div class="workflow-title">
                {item[1]}
            </div>

            <div class="workflow-text">
                {item[2]}
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# SUPPORTED ISSUES
# ============================================================

st.markdown(
    '<div class="section-line"></div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-label">
        05 / SUPPORTED SIGNALS
    </div>

    <div class="section-title">
        Focused on visible urban issues.
    </div>
    """,
    unsafe_allow_html=True,
)


s1, s2, s3 = st.columns(3, gap="medium")


with s1:
    st.markdown(
        """
        <div class="about-card">

        <div class="card-label">
            URBAN / ROADS
        </div>

        <div class="card-title">
            Potholes
        </div>

        <div class="card-text">
            Road-surface damage identified from uploaded
            street-level evidence.
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with s2:
    st.markdown(
        """
        <div class="about-card">

        <div class="card-label">
            URBAN / WASTE
        </div>

        <div class="card-title">
            Garbage
        </div>

        <div class="card-text">
            Waste accumulation and visible garbage-related
            problems can be analysed from image evidence.
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with s3:
    st.markdown(
        """
        <div class="about-card">

        <div class="card-label">
            FUTURE EXPANSION
        </div>

        <div class="card-title">
            More signals.
        </div>

        <div class="card-text">
            The platform can be extended with additional
            computer-vision models for other urban infrastructure
            problems.
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        border-top: 1px solid #d9d9d2;
        margin-top: 60px;
        padding-top: 20px;
        color: #777b82;
        font-size: 10px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    ">
        UrbanPulse AI &nbsp;•&nbsp; Smart Urban Complaint Detection System
    </div>
    """,
    unsafe_allow_html=True,
)