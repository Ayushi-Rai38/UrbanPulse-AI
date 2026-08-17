import os
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="UrbanPulse AI | Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# ADMIN SESSION
# ============================================================
# Main Admin Login ke baad admin session already active hota hai.
# Dono existing session keys ko support kar rahe hain:
#   1. admin
#   2. admin_authenticated
#
# Koi second login nahi hoga.

is_admin = (
    st.session_state.get("admin", False)
    or st.session_state.get("admin_authenticated", False)
)

if not is_admin:
    # Agar genuinely admin login nahi hua hai,
    # tab direct admin login page par bhejo.
    st.switch_page("pages/admin_login.py")


# ============================================================
# ADMIN SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            padding: 8px 4px 20px;
            color: #172033;
            font-size: 18px;
            font-weight: 850;
            letter-spacing: -0.4px;
        ">
            ▣ &nbsp; UrbanPulse AI
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            font-size: 9px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #73777d;
            font-weight: 800;
            margin: 4px 0 10px;
        ">
            Admin Console
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    if st.button(
        "Dashboard",
        key="admin_side_dashboard",
        use_container_width=True,
    ):
        st.switch_page("pages/dashboard.py")

    # --------------------------------------------------------
    # COMPLAINTS
    # --------------------------------------------------------

    if st.button(
        "Complaints",
        key="admin_side_complaints",
        use_container_width=True,
    ):
        st.switch_page("pages/admin_complaints.py")

    # --------------------------------------------------------
    # ANALYTICS
    # --------------------------------------------------------

    if st.button(
        "Analytics",
        key="admin_side_analytics",
        use_container_width=True,
    ):
        st.switch_page("pages/analytics.py")

    # --------------------------------------------------------
    # DIVIDER
    # --------------------------------------------------------

    st.markdown(
        """
        <div style="
            border-top: 1px solid #d9d9df;
            margin: 18px 0 16px;
        "></div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # ADMIN ACCOUNT
    # --------------------------------------------------------

    admin_name = st.session_state.get(
        "admin_name",
        "Admin"
    )

    admin_email = st.session_state.get(
        "admin_email",
        "admin@urbanpulse.ai"
    )

    st.markdown(
        f"""
        <div style="
            background: #e8e8ed;
            border: 1px solid #d8d8de;
            border-radius: 7px;
            padding: 13px;
            margin-top: 2px;
        ">

            <div style="
                color: #777b82;
                font-size: 8px;
                font-weight: 800;
                letter-spacing: 1.5px;
                margin-bottom: 6px;
            ">
                ADMIN
            </div>

            <div style="
                color: #202733;
                font-size: 14px;
                font-weight: 800;
            ">
                {admin_name}
            </div>

            <div style="
                color: #70757c;
                font-size: 10px;
                margin-top: 4px;
                overflow-wrap: anywhere;
            ">
                {admin_email}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    if st.button(
        "Logout",
        key="admin_side_logout",
        use_container_width=True,
    ):

        # Clear admin-related session values
        st.session_state["admin"] = False
        st.session_state["admin_authenticated"] = False

        if "admin_name" in st.session_state:
            del st.session_state["admin_name"]

        if "admin_email" in st.session_state:
            del st.session_state["admin_email"]

        st.switch_page("pages/admin_login.py")


# ============================================================
# HIDE STREAMLIT DEFAULT PAGE NAVIGATION
# ============================================================
# Ye jo left side mein:
# app
# about
# dashboard
# login
# ...
# aa raha tha, usko hide karega.

st.markdown(
    """
    <style>

    /* Hide Streamlit's default multipage navigation */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Main application background */
    .stApp {
        background: #f5f4ee;
    }

    /* Main content width */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #eef0f5;
        border-right: 1px solid #d8dbe1;
    }

    /* General text */
    h1, h2, h3, h4, p, div, label {
        color: #172033;
    }

    /* Buttons */
    div.stButton > button {
        background: #ffffff;
        color: #172033;
        border: 1px solid #1d5cff;
        border-radius: 5px;
        padding: 0.65rem 1rem;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background: #f5f7ff;
        color: #172033;
        border-color: #174fd0;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #d9dce1;
        border-radius: 7px;
        padding: 1rem 1.2rem;
    }

    div[data-testid="stMetricLabel"] {
        color: #6d737c !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #172033 !important;
        font-weight: 800 !important;
    }

    /* Section headings */
    .section-heading {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #73777d;
        margin-bottom: 12px;
    }

    /* Header */
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #d9d9d4;
        padding-bottom: 18px;
        margin-bottom: 35px;
    }

    .page-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .logo-box {
        width: 38px;
        height: 38px;
        background: #172431;
        color: white;
        border-radius: 7px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 800;
    }

    .brand-name {
        font-size: 18px;
        font-weight: 850;
        color: #172033;
    }

    .breadcrumb {
        color: #73777d;
        font-size: 9px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    /* Hero */
    .hero {
        background: #ffffff;
        border: 1px solid #d9d9d4;
        border-radius: 7px;
        padding: 35px;
        margin-bottom: 25px;
    }

    .hero-label {
        font-size: 9px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #73777d;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 42px;
        line-height: 1.05;
        letter-spacing: -1.8px;
        font-weight: 850;
        color: #172033;
        margin-bottom: 14px;
    }

    .hero-text {
        color: #666e78;
        font-size: 15px;
        line-height: 1.6;
        max-width: 850px;
    }

    /* White panels */
    .panel {
        background: #ffffff;
        border: 1px solid #d9d9d4;
        border-radius: 7px;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background: #ffffff;
        border: 1px solid #d9dce1;
        border-radius: 5px;
    }

    /* Text input */
    .stTextInput > div > div > input {
        background: #ffffff;
        border: 1px solid #d9dce1;
        border-radius: 5px;
    }

    /* Dataframe */
    .stDataFrame {
        border: 1px solid #d9dce1;
        border-radius: 7px;
        overflow: hidden;
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

        <div class="page-brand">

            <div class="logo-box">
                UP
            </div>

            <div class="brand-name">
                UrbanPulse AI
            </div>

        </div>

        <div class="breadcrumb">
            DASHBOARD &nbsp; / &nbsp; OPERATIONS
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
    <div class="hero">

        <div class="hero-label">
            01 / OPERATIONS BRIEF
        </div>

        <div class="hero-title">
            See the signal, then act.
        </div>

        <div class="hero-text">
            A live operational view of urban complaints,
            detection confidence, issue distribution,
            and resolution progress.
        </div>

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

    df = pd.read_sql_query(
        "SELECT * FROM complaints",
        conn
    )

    conn.close()

except Exception as e:

    st.error(
        f"Unable to load complaint database: {e}"
    )

    st.stop()


# ============================================================
# EMPTY DATABASE
# ============================================================

if df.empty:

    st.info(
        "No complaint data available yet."
    )

    st.stop()


# ============================================================
# ENSURE REQUIRED COLUMNS
# ============================================================

required_columns = [
    "id",
    "issue_type",
    "confidence",
    "location",
    "status",
    "date",
    "image_path",
    "ai_summary",
]

for column in required_columns:

    if column not in df.columns:
        df[column] = ""


# ============================================================
# STATISTICS
# ============================================================

total = len(df)

pending = len(
    df[df["status"] == "Pending"]
)

in_progress = len(
    df[df["status"] == "In Progress"]
)

resolved = len(
    df[df["status"] == "Resolved"]
)

avg_confidence = pd.to_numeric(
    df["confidence"],
    errors="coerce"
).mean()


# ============================================================
# METRICS
# ============================================================

st.markdown(
    '<div class="section-heading">Live Operations</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.metric(
        "Total Complaints",
        total
    )

with col2:

    st.metric(
        "Pending",
        pending
    )

with col3:

    st.metric(
        "In Progress",
        in_progress
    )

with col4:

    st.metric(
        "Resolved",
        resolved
    )

with col5:

    if pd.notna(avg_confidence):

        confidence_value = (
            f"{avg_confidence * 100:.1f}%"
        )

    else:

        confidence_value = "—"

    st.metric(
        "Avg Confidence",
        confidence_value
    )


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# FILTER SECTION
# ============================================================

st.markdown(
    '<div class="section-heading">Complaint Patterns</div>',
    unsafe_allow_html=True
)

filter_col1, filter_col2 = st.columns(
    [1.5, 1]
)


with filter_col1:

    search = st.text_input(
        "Search Location",
        placeholder="Enter location..."
    )


with filter_col2:

    status_filter = st.selectbox(
        "Filter by Status",
        [
            "All",
            "Pending",
            "In Progress",
            "Resolved",
        ]
    )


# ============================================================
# APPLY FILTERS
# ============================================================

display_df = df.copy()


if search:

    display_df = display_df[
        display_df["location"]
        .astype(str)
        .str.contains(
            search,
            case=False,
            na=False
        )
    ]


if status_filter != "All":

    display_df = display_df[
        display_df["status"] == status_filter
    ]


# ============================================================
# NO FILTERED DATA
# ============================================================

if display_df.empty:

    st.warning(
        "No complaints match the selected filters."
    )

    st.stop()


# ============================================================
# CHARTS
# ============================================================

chart_col1, chart_col2 = st.columns(2)


# ------------------------------------------------------------
# ISSUE TYPE CHART
# ------------------------------------------------------------

with chart_col1:

    issue_counts = (
        display_df["issue_type"]
        .astype(str)
        .value_counts()
        .reset_index()
    )

    issue_counts.columns = [
        "Issue Type",
        "Count"
    ]

    pie = px.pie(
        issue_counts,
        names="Issue Type",
        values="Count",
        title="Complaints by Issue Type",
        template="plotly_white",
    )

    pie.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            color="#172033"
        ),
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        ),
    )

    st.plotly_chart(
        pie,
        use_container_width=True
    )


# ------------------------------------------------------------
# STATUS CHART
# ------------------------------------------------------------

with chart_col2:

    status_counts = (
        display_df["status"]
        .astype(str)
        .value_counts()
        .reset_index()
    )

    status_counts.columns = [
        "Status",
        "Count"
    ]

    bar = px.bar(
        status_counts,
        x="Status",
        y="Count",
        title="Complaint Status",
        template="plotly_white",
    )

    bar.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            color="#172033"
        ),
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        ),
        xaxis=dict(
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#e5e7eb"
        ),
    )

    st.plotly_chart(
        bar,
        use_container_width=True
    )


# ============================================================
# RECENT COMPLAINTS
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-heading">Recent Complaints</div>',
    unsafe_allow_html=True
)


recent = display_df.head(10).copy()


recent_columns = [
    "id",
    "issue_type",
    "location",
    "status",
    "confidence",
    "date",
]

recent_columns = [
    column
    for column in recent_columns
    if column in recent.columns
]

recent = recent[recent_columns]


if "confidence" in recent.columns:

    recent["confidence"] = recent[
        "confidence"
    ].apply(
        lambda x:
        f"{float(x) * 100:.1f}%"
        if pd.notna(x) and str(x) != ""
        else "—"
    )


st.dataframe(
    recent,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# COMPLAINT DETAILS / ACTION
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-heading">Review Complaint</div>',
    unsafe_allow_html=True
)


complaints = {}

for _, row in display_df.iterrows():

    label = (
        f"#{row['id']} | "
        f"{row['issue_type']} | "
        f"{row['location']} | "
        f"{row['status']}"
    )

    complaints[label] = row["id"]


selected = st.selectbox(
    "Select Complaint",
    list(complaints.keys())
)


selected_id = complaints[selected]


selected_rows = display_df[
    display_df["id"] == selected_id
]


if not selected_rows.empty:

    selected_row = selected_rows.iloc[0]

    detail_col1, detail_col2 = st.columns(2)


    # --------------------------------------------------------
    # DETAILS
    # --------------------------------------------------------

    with detail_col1:

        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )

        st.write(
            "**Issue Type:**",
            selected_row["issue_type"]
        )

        st.write(
            "**Location:**",
            selected_row["location"]
        )

        st.write(
            "**Status:**",
            selected_row["status"]
        )

        confidence = pd.to_numeric(
            selected_row["confidence"],
            errors="coerce"
        )

        if pd.notna(confidence):

            st.write(
                "**Confidence:**",
                f"{confidence * 100:.2f}%"
            )

        else:

            st.write(
                "**Confidence:**",
                "—"
            )

        st.write(
            "**Date:**",
            selected_row["date"]
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # IMAGE
    # --------------------------------------------------------

    with detail_col2:

        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )

        image_path = str(
            selected_row["image_path"]
        )

        if (
            image_path
            and image_path != "nan"
            and os.path.exists(image_path)
        ):

            st.image(
                image_path,
                use_container_width=True
            )

        else:

            st.info(
                "Complaint image not found."
            )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    # ========================================================
    # AI SUMMARY
    # ========================================================

    ai_summary = str(
        selected_row.get(
            "ai_summary",
            ""
        )
    )

    if (
        ai_summary
        and ai_summary != "nan"
    ):

        st.markdown(
            '<div class="section-heading">AI Complaint Summary</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="panel">
                {ai_summary}
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # UPDATE STATUS
    # ========================================================

    st.markdown(
        '<div class="section-heading">Update Status</div>',
        unsafe_allow_html=True
    )

    new_status = st.selectbox(
        "New Status",
        [
            "Pending",
            "In Progress",
            "Resolved",
        ],
        index=[
            "Pending",
            "In Progress",
            "Resolved",
        ].index(
            selected_row["status"]
        )
        if selected_row["status"]
        in [
            "Pending",
            "In Progress",
            "Resolved",
        ]
        else 0,
    )


    if st.button(
        "Update Status",
        key=f"update_status_{selected_id}",
        use_container_width=True,
    ):

        conn = sqlite3.connect(
            DB_PATH
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE complaints
            SET status = ?
            WHERE id = ?
            """,
            (
                new_status,
                selected_id,
            ),
        )

        conn.commit()
        conn.close()

        st.success(
            "Complaint status updated successfully."
        )

        st.rerun()


    # ========================================================
    # DELETE COMPLAINT
    # ========================================================

    st.markdown("<br>", unsafe_allow_html=True)

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this complaint.",
        key=f"delete_confirm_{selected_id}",
    )


    if st.button(
        "Delete Complaint",
        key=f"delete_complaint_{selected_id}",
        use_container_width=True,
    ):

        if not confirm_delete:

            st.warning(
                "Please confirm before deleting."
            )

        else:

            conn = sqlite3.connect(
                DB_PATH
            )

            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM complaints
                WHERE id = ?
                """,
                (selected_id,),
            )

            conn.commit()
            conn.close()

            st.success(
                "Complaint deleted successfully."
            )

            st.rerun()


# ============================================================
# DOWNLOAD REPORT
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-heading">Export</div>',
    unsafe_allow_html=True
)


csv_data = display_df.to_csv(
    index=False
)


st.download_button(
    "Download Complaint Report",
    csv_data,
    "urbanpulse_complaints.csv",
    "text/csv",
    use_container_width=True,
)