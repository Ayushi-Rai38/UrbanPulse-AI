import streamlit as st
import sqlite3
import pandas as pd

from components.sidebar import render_sidebar


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="UrbanPulse AI | My Complaints",
    page_icon="🚦",
    layout="wide",
)

st.markdown(
    """
    <style>

    /* Hide Streamlit's default page navigation */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Keep the custom sidebar */
    section[data-testid="stSidebar"] {
        display: block !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "role" not in st.session_state:
    st.session_state.role = "user"


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
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 18px;
        border-bottom: 1px solid #d9d9df;
        margin-bottom: 38px;
    }

    .logo-area {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .logo-box {
        width: 42px;
        height: 42px;
        border-radius: 10px;
        background: #172431;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 15px;
        font-weight: 800;
    }

    .logo-name {
        font-size: 18px;
        font-weight: 800;
        color: #172033;
    }

    .breadcrumb {
        color: #777b82;
        font-size: 9px;
        letter-spacing: 1.8px;
        font-weight: 800;
    }

    .eyebrow {
        color: #73777d;
        font-size: 9px;
        letter-spacing: 2.2px;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 15px;
    }

    .page-title {
        color: #172033;
        font-size: 52px;
        line-height: 1.02;
        letter-spacing: -2px;
        font-weight: 850;
        margin-bottom: 15px;
    }

    .page-description {
        color: #62686e;
        font-size: 15px;
        line-height: 1.7;
        max-width: 850px;
    }

    .user-strip {
        background: #eef0f5;
        border: 1px solid #d8dbe2;
        border-radius: 5px;
        padding: 13px 16px;
        margin: 28px 0;
        color: #62686e;
        font-size: 12px;
    }

    .user-strip strong {
        color: #202733;
    }

    .stat-card {
        background: white;
        border: 1px solid #d9d9df;
        border-radius: 7px;
        padding: 20px;
        min-height: 110px;
    }

    .stat-label {
        color: #777b82;
        font-size: 8px;
        font-weight: 800;
        letter-spacing: 1.7px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .stat-value {
        color: #172033;
        font-size: 30px;
        font-weight: 850;
    }

    .complaint-card {
        background: white;
        border: 1px solid #d9d9df;
        border-radius: 7px;
        padding: 22px;
        margin-bottom: 14px;
    }

    .complaint-label {
        color: #777b82;
        font-size: 8px;
        font-weight: 800;
        letter-spacing: 1.7px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .complaint-title {
        color: #172033;
        font-size: 21px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .complaint-info {
        color: #62686e;
        font-size: 12px;
        line-height: 1.7;
    }

    .empty-card {
        background: white;
        border: 1px solid #d9d9df;
        border-radius: 7px;
        padding: 45px;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TOP BAR
# ============================================================

st.markdown(
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
        MY COMPLAINTS &nbsp;/&nbsp; CIVIC SIGNAL
    </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    """
    <div class="eyebrow">
        01 / MY COMPLAINTS
    </div>

    <div class="page-title">
        Track your civic signals.
    </div>

    <div class="page-description">
        View the complaints you have submitted, check their
        current status, and review the AI-generated information
        attached to each report.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# USER STRIP
# ============================================================

user_name = st.session_state.get("user_name", "User")
user_email = st.session_state.get("user_email", "")

st.markdown(
    f"""
    <div class="user-strip">
        Viewing complaints submitted by
        <strong>{user_name}</strong>
        &nbsp;·&nbsp;
        {user_email}
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

DB_PATH = "database/complaints.db"


try:

    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            id,
            issue_type,
            confidence,
            location,
            image_path,
            status,
            date,
            ai_summary
        FROM complaints
        ORDER BY id DESC
    """

    complaints = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

except Exception as e:

    st.error(f"Could not load complaints: {e}")
    st.stop()


# ============================================================
# STATISTICS
# ============================================================

total = len(complaints)

pending = len(
    complaints[
        complaints["status"] == "Pending"
    ]
)

in_progress = len(
    complaints[
        complaints["status"] == "In Progress"
    ]
)

resolved = len(
    complaints[
        complaints["status"] == "Resolved"
    ]
)


# ============================================================
# STAT CARDS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.markdown(
        f"""
        <div class="stat-card">
        <div class="stat-label">
            Total Reports
        </div>

        <div class="stat-value">
            {total}
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with c2:

    st.markdown(
        f"""
        <div class="stat-card">
        <div class="stat-label">
            Pending
        </div>

        <div class="stat-value">
            {pending}
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with c3:

    st.markdown(
        f"""
        <div class="stat-card">
        <div class="stat-label">
            In Progress
        </div>

        <div class="stat-value">
            {in_progress}
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with c4:

    st.markdown(
        f"""
        <div class="stat-card">
        <div class="stat-label">
            Resolved
        </div>

        <div class="stat-value">
            {resolved}
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# COMPLAINTS
# ============================================================

st.markdown(
    """
    <div class="eyebrow">
        02 / REPORT HISTORY
    </div>
    """,
    unsafe_allow_html=True,
)


if complaints.empty:

    st.markdown(
        """
        <div class="empty-card">

        <div style="
            font-size: 40px;
            margin-bottom: 12px;
        ">
            📋
        </div>

        <div style="
            color: #172033;
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 8px;
        ">
            No complaints yet.
        </div>

        <div style="
            color: #62686e;
            font-size: 13px;
        ">
            Your submitted civic reports will appear here.
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "Report an Issue",
        use_container_width=True
    ):

        st.switch_page(
            "pages/report.py"
        )


else:

    for _, complaint in complaints.iterrows():

        issue = complaint["issue_type"]
        confidence = complaint["confidence"]
        location = complaint["location"]
        status = complaint["status"]
        date = complaint["date"]
        complaint_id = complaint["id"]

        if pd.isna(confidence):
            confidence_text = "N/A"
        else:
            confidence_text = f"{float(confidence) * 100:.1f}%"

        st.html(
            f"""
    <div class="complaint-card">

    <div class="complaint-label">
        COMPLAINT #{complaint_id}
    </div>

    <div class="complaint-title">
        {issue}
    </div>

    <div class="complaint-info">

        📍 <strong>Location:</strong>
        {location}

        &nbsp;&nbsp;·&nbsp;&nbsp;

        🤖 <strong>Confidence:</strong>
        {confidence_text}

        <br><br>

        📅 <strong>Submitted:</strong>
        {date}

        &nbsp;&nbsp;·&nbsp;&nbsp;

        📌 <strong>Status:</strong>
        {status}

    </div>

    </div>
    """
)