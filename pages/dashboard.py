import sqlite3
import textwrap
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from components.admin_sidebar import render_admin_sidebar


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
# PATHS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "complaints.db"


def render_html(content):
    """Render multiline HTML without indentation becoming a Markdown code block."""
    st.markdown(textwrap.dedent(content).strip(), unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================
if "selected_complaint_id" not in st.session_state:
    st.session_state.selected_complaint_id = None


# ============================================================
# DATABASE
# ============================================================
def load_complaints():
    if not DB_PATH.exists():
        return pd.DataFrame()

    conn = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(
            "SELECT * FROM complaints ORDER BY id DESC",
            conn,
        )
    finally:
        conn.close()


def update_status(complaint_id, new_status):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "UPDATE complaints SET status = ? WHERE id = ?",
            (new_status, int(complaint_id)),
        )
        conn.commit()
    finally:
        conn.close()


def delete_complaint(complaint_id):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "DELETE FROM complaints WHERE id = ?",
            (int(complaint_id),),
        )
        conn.commit()
    finally:
        conn.close()


# ============================================================
# IMAGE PATH HELPER
# ============================================================
def resolve_image_path(raw_path):
    if not raw_path:
        return None

    raw = str(raw_path).strip()
    if not raw:
        return None

    candidates = [
        Path(raw),
        BASE_DIR / raw,
        BASE_DIR / "uploads" / Path(raw).name,
        BASE_DIR / "database" / raw,
    ]

    for candidate in candidates:
        try:
            if candidate.exists() and candidate.is_file():
                return str(candidate)
        except Exception:
            pass

    return None


# ============================================================
# GLOBAL STYLE
# Same visual language as the Home page:
# wider content, larger typography, light background,
# simple navy/white cards and ONE sidebar navigation.
# ============================================================
render_html(
    """
<style>
:root {
    --navy: #182338;
    --muted: #68717d;
    --line: #d8d9d5;
    --paper: #f7f5ef;
    --white: #ffffff;
    --dark: #25262f;
}

/* ---------- PAGE ---------- */
.stApp {
    background: var(--paper);
    color: var(--navy);
}

.block-container {
    max-width: 1460px !important;
    padding-top: 1.35rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
}

/* ---------- TOP BRAND ---------- */
.page-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #deddd7;
    padding-bottom: 0.75rem;
    margin-bottom: 1.35rem;
}

.page-brand {
    display: flex;
    align-items: center;
    gap: 10px;
}

.page-logo {
    width: 34px;
    height: 34px;
    border-radius: 8px;
    background: #172231;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 850;
}

.page-brand-name {
    color: #172033;
    font-size: 17px;
    font-weight: 800;
}

.breadcrumb {
    color: #858a92;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 0.15em;
}

/* ---------- LABELS ---------- */
.tag {
    display: inline-block;
    padding: 4px 8px;
    border: 1px solid #737983;
    border-radius: 4px;
    background: #faf9f4;
    color: #273042;
    font-size: 9px;
    font-weight: 850;
    letter-spacing: 0.13em;
}

/* ---------- HERO ---------- */
.hero {
    background: #faf9f4;
    border: 1.4px solid #747b85;
    border-radius: 8px;
    padding: 1.55rem 1.8rem 1.65rem;
    margin-bottom: 1rem;
}

.hero-title {
    color: #172033;
    font-size: clamp(36px, 4vw, 56px);
    line-height: 1.02;
    font-weight: 850;
    letter-spacing: -0.045em;
    margin-top: 0.7rem;
}

.hero-text {
    max-width: 900px;
    color: #68717c;
    font-size: 15px;
    line-height: 1.5;
    margin-top: 0.8rem;
}

/* ---------- METRICS ---------- */
.metrics {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin: 0.95rem 0;
}

.metric {
    background: #fff;
    border: 1px solid #d7d8d4;
    border-radius: 8px;
    padding: 0.95rem 1rem;
    min-height: 105px;
}

.metric-label {
    color: #727780;
    font-size: 9px;
    font-weight: 850;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.metric-number {
    color: #172033;
    font-size: 28px;
    font-weight: 850;
    line-height: 1;
    margin-top: 0.55rem;
}

.metric-sub {
    color: #999da2;
    font-size: 10px;
    margin-top: 0.4rem;
}

/* ---------- SIGNAL ---------- */
.signal {
    background: #172a35;
    color: #eef2f3;
    border-radius: 7px;
    padding: 0.72rem 1rem;
    font-size: 12px;
    margin-bottom: 1.2rem;
}

.signal small {
    color: #f0c62e;
    font-weight: 850;
    letter-spacing: 0.15em;
    margin-right: 0.8rem;
}

/* ---------- SECTION ---------- */
.rule {
    height: 1px;
    background: #deddd7;
    margin: 1.55rem 0 1.1rem;
}

.section-title {
    color: #172033;
    font-size: 24px;
    font-weight: 850;
    margin: 0.45rem 0 0.85rem;
}

.section-subtitle {
    color: #68717c;
    font-size: 14px;
}

/* ---------- INPUTS ---------- */
div[data-testid="stTextInput"] input {
    background: #ffffff !important;
    color: #172033 !important;
    border: 1px solid #737983 !important;
    border-radius: 8px !important;
    min-height: 44px !important;
}

div[data-testid="stSelectbox"] > div > div {
    background: #292a32 !important;
    color: white !important;
    border-radius: 8px !important;
    min-height: 44px !important;
}

div[data-testid="stSelectbox"] span {
    color: white !important;
}

/* ---------- CHART CARDS ---------- */
.chart-card {
    background: #fff;
    border: 1px solid #d1d2cf;
    border-radius: 8px;
    padding: 0.65rem 0.8rem 0.25rem;
}

.chart-heading {
    color: #172033;
    font-size: 14px;
    font-weight: 850;
}

/* ---------- LOWER GRID ---------- */
.lower-heading {
    color: #172033;
    font-size: 23px;
    font-weight: 850;
    margin: 0.45rem 0 0.8rem;
}

/* ---------- DETAIL ---------- */
.detail-card {
    background: #fff;
    border: 1px solid #cfd1d0;
    border-radius: 8px;
    padding: 1rem 1.05rem;
}

.detail-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.7rem 2rem;
}

.detail-label {
    color: #7b8087;
    font-size: 9px;
    font-weight: 850;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.detail-value {
    color: #172033;
    font-size: 13px;
    font-weight: 700;
    margin-top: 2px;
}

.evidence-label {
    color: #172033;
    font-size: 12px;
    font-weight: 850;
    margin: 0.8rem 0 0.4rem;
}

.empty-action {
    background: #faf9f4;
    border: 1px dashed #b8bbc0;
    border-radius: 8px;
    padding: 2.5rem 1.5rem;
    text-align: center;
    color: #737983;
    font-size: 13px;
}

/* ---------- BUTTONS ---------- */
section.main .stButton > button,
section.main .stDownloadButton > button {
    background: #fff !important;
    color: #172033 !important;
    border: 1px solid #68707c !important;
    border-radius: 7px !important;
    min-height: 40px !important;
    font-weight: 650 !important;
}

section.main .stButton > button:hover,
section.main .stDownloadButton > button:hover {
    background: #eef0f2 !important;
    border-color: #172033 !important;
}

/* ---------- MOBILE ---------- */
@media (max-width: 1000px) {
    .metrics {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 700px) {
    .metrics {
        grid-template-columns: 1fr;
    }

    .detail-grid {
        grid-template-columns: 1fr;
    }

    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}
</style>
"""
)


# ============================================================
# ============================================================
# ADMIN SIDEBAR
# ============================================================
render_admin_sidebar()



# DATA
# ============================================================
df = load_complaints()

if df.empty:
    render_html(
        """
        <div class="hero">
            <div class="tag">01 / OPERATIONS BRIEF</div>
            <div class="hero-title">See the signal, then act.</div>
            <div class="hero-text">
                No complaints have been submitted yet.
            </div>
        </div>
        """
    )
    st.stop()

# Ensure optional columns exist.
for col in ["issue_type", "confidence", "location", "status", "date", "image_path"]:
    if col not in df.columns:
        df[col] = ""


# ============================================================
# TOP HEADER
# ============================================================
render_html(
    """
    <div class="page-top">
        <div class="page-brand">
            <div class="page-logo">UP</div>
            <div class="page-brand-name">UrbanPulse AI</div>
        </div>
        <div class="breadcrumb">DASHBOARD &nbsp; / &nbsp; OPERATIONS</div>
    </div>
    """
)


# ============================================================
# 01 / OPERATIONS BRIEF
# ============================================================
render_html(
    """
    <div class="hero">
        <div class="tag">01 / OPERATIONS BRIEF</div>
        <div class="hero-title">See the signal, then act.</div>
        <div class="hero-text">
            A live operational view of urban complaints, detection confidence,
            issue distribution, and resolution progress.
        </div>
    </div>
    """
)


# ============================================================
# METRICS
# ============================================================
total = len(df)
pending = int((df["status"] == "Pending").sum())
in_progress = int((df["status"] == "In Progress").sum())
resolved = int((df["status"] == "Resolved").sum())

conf = pd.to_numeric(df["confidence"], errors="coerce").dropna()
avg_conf = float(conf.mean() * 100) if not conf.empty else 0.0

issue_counts = df["issue_type"].astype(str).value_counts()
most_reported = issue_counts.index[0] if len(issue_counts) else "—"

render_html(
    f"""
    <div class="metrics">
        <div class="metric">
            <div class="metric-label">Total Complaints</div>
            <div class="metric-number">{total}</div>
            <div class="metric-sub">All time</div>
        </div>
        <div class="metric">
            <div class="metric-label">Pending Review</div>
            <div class="metric-number">{pending}</div>
            <div class="metric-sub">Awaiting attention</div>
        </div>
        <div class="metric">
            <div class="metric-label">In Progress</div>
            <div class="metric-number">{in_progress}</div>
            <div class="metric-sub">Under review</div>
        </div>
        <div class="metric">
            <div class="metric-label">Resolved</div>
            <div class="metric-number">{resolved}</div>
            <div class="metric-sub">Completed</div>
        </div>
        <div class="metric">
            <div class="metric-label">Avg Confidence</div>
            <div class="metric-number">{avg_conf:.1f}%</div>
            <div class="metric-sub">Model confidence</div>
        </div>
    </div>

    <div class="signal">
        <small>CURRENT SIGNAL</small>
        Most reported issue: <strong>{most_reported}</strong>
        &nbsp; • &nbsp; {pending} complaint(s) pending review
        &nbsp; • &nbsp; Average confidence: <strong>{avg_conf:.1f}%</strong>
    </div>
    """,
)


# ============================================================
# 02 / PATTERNS
# ============================================================
st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
st.markdown('<div class="tag">02 / PATTERNS</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-title">Where attention is accumulating.</div>',
    unsafe_allow_html=True,
)

f1, f2 = st.columns([2.5, 1], gap="large")

with f1:
    search = st.text_input(
        "Search location",
        placeholder="Enter location...",
        key="location_filter",
    )

with f2:
    status_filter = st.selectbox(
        "Filter by status",
        ["All", "Pending", "In Progress", "Resolved"],
        key="status_filter",
    )

filtered = df.copy()

if search.strip():
    filtered = filtered[
        filtered["location"].astype(str).str.contains(
            search.strip(),
            case=False,
            na=False,
        )
    ]

if status_filter != "All":
    filtered = filtered[filtered["status"] == status_filter]


# ============================================================
# CHARTS
# ============================================================
c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown(
        '<div class="chart-card"><div class="chart-heading">Issue Distribution</div>',
        unsafe_allow_html=True,
    )

    issue_data = filtered["issue_type"].astype(str).value_counts().reset_index()
    issue_data.columns = ["Issue", "Count"]

    if issue_data.empty:
        st.info("No records match the selected filters.")
    else:
        fig_pie = px.pie(
            issue_data,
            names="Issue",
            values="Count",
            hole=0.48,
        )
        fig_pie.update_traces(
            textinfo="label+percent",
            textfont_size=13,
        )
        fig_pie.update_layout(
            height=350,
            margin=dict(l=15, r=15, t=10, b=10),
            showlegend=True,
            legend=dict(orientation="h", y=-0.08),
            paper_bgcolor="white",
            plot_bgcolor="white",
        )
        st.plotly_chart(
            fig_pie,
            use_container_width=True,
            config={"displaylogo": False},
        )

    st.markdown("</div>", unsafe_allow_html=True)


with c2:
    st.markdown(
        '<div class="chart-card"><div class="chart-heading">Current Workload</div>',
        unsafe_allow_html=True,
    )

    workload = pd.DataFrame(
        {
            "Status": ["Pending", "In Progress", "Resolved"],
            "Count": [
                int((filtered["status"] == "Pending").sum()),
                int((filtered["status"] == "In Progress").sum()),
                int((filtered["status"] == "Resolved").sum()),
            ],
        }
    )

    fig_bar = px.bar(
        workload,
        x="Status",
        y="Count",
        text="Count",
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(
        height=350,
        margin=dict(l=20, r=15, t=10, b=20),
        yaxis_title="Count",
        xaxis_title="",
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
    )
    st.plotly_chart(
        fig_bar,
        use_container_width=True,
        config={"displaylogo": False},
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# 03 + 04 LOWER AREA
# Important: BOTH panels stay side-by-side.
# The action details are hidden until a complaint is selected.
# ============================================================
st.markdown('<div class="rule"></div>', unsafe_allow_html=True)

left, right = st.columns([1.05, 1], gap="large")


# ============================================================
# 03 / RECENT COMPLAINTS
# ============================================================
with left:
    st.markdown('<div class="tag">03 / RECENT COMPLAINTS</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="lower-heading">Recent complaints.</div>',
        unsafe_allow_html=True,
    )

    table_df = filtered.copy()

    if not table_df.empty:
        table_df["confidence"] = pd.to_numeric(
            table_df["confidence"],
            errors="coerce",
        ).apply(
            lambda x: f"{x * 100:.1f}%"
            if pd.notna(x) and x <= 1
            else (f"{x:.1f}%" if pd.notna(x) else "—")
        )

        visible_cols = [
            col
            for col in [
                "id",
                "issue_type",
                "location",
                "status",
                "confidence",
                "date",
            ]
            if col in table_df.columns
        ]

        st.dataframe(
            table_df[visible_cols],
            use_container_width=True,
            hide_index=True,
            height=285,
        )
    else:
        st.info("No complaints match the current filters.")


# ============================================================
# 04 / ACTION
# ============================================================
with right:
    st.markdown('<div class="tag">04 / ACTION</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="lower-heading">Review, resolve and close the loop.</div>',
        unsafe_allow_html=True,
    )

    # No complaint is selected automatically.
    complaint_options = [
        "Select a complaint..."
    ]

    option_map = {}

    for _, row in filtered.iterrows():
        label = (
            f"#{int(row['id'])} | "
            f"{row['issue_type']} | "
            f"{row['location']} | "
            f"{row['status']}"
        )
        complaint_options.append(label)
        option_map[label] = int(row["id"])

    # Keep selection empty until user explicitly chooses one.
    current_index = 0

    selected_label = st.selectbox(
        "Select complaint",
        complaint_options,
        index=current_index,
        key="complaint_selector",
    )

    if selected_label == "Select a complaint...":
        render_html(
            """
            <div class="empty-action">
                <strong>No complaint selected.</strong><br>
                Choose a complaint above to view its evidence and
                update or delete the record.
            </div>
            """
        )
        st.session_state.selected_complaint_id = None

    else:
        selected_id = option_map[selected_label]
        st.session_state.selected_complaint_id = selected_id

        selected_row = df[df["id"] == selected_id].iloc[0]

        confidence_raw = pd.to_numeric(
            pd.Series([selected_row["confidence"]]),
            errors="coerce",
        ).iloc[0]

        if pd.isna(confidence_raw):
            confidence_text = "—"
        elif confidence_raw <= 1:
            confidence_text = f"{confidence_raw * 100:.2f}%"
        else:
            confidence_text = f"{confidence_raw:.2f}%"

        render_html(
            f"""
            <div class="detail-card">
                <div class="detail-grid">
                    <div>
                        <div class="detail-label">Issue Type</div>
                        <div class="detail-value">{selected_row['issue_type']}</div>
                    </div>

                    <div>
                        <div class="detail-label">Date</div>
                        <div class="detail-value">{selected_row['date']}</div>
                    </div>

                    <div>
                        <div class="detail-label">Location</div>
                        <div class="detail-value">{selected_row['location']}</div>
                    </div>

                    <div>
                        <div class="detail-label">Confidence</div>
                        <div class="detail-value">{confidence_text}</div>
                    </div>

                    <div>
                        <div class="detail-label">Status</div>
                        <div class="detail-value">{selected_row['status']}</div>
                    </div>

                    <div>
                        <div class="detail-label">Complaint ID</div>
                        <div class="detail-value">#{selected_id}</div>
                    </div>
                </div>
            </div>
            """
        )

        # Evidence
        image_path = resolve_image_path(selected_row.get("image_path", ""))

        if image_path:
            st.markdown(
                '<div class="evidence-label">Complaint Evidence</div>',
                unsafe_allow_html=True,
            )
            st.image(
                image_path,
                use_container_width=True,
            )
        else:
            st.markdown(
                '<div class="evidence-label">Complaint Evidence</div>',
                unsafe_allow_html=True,
            )
            st.info("Evidence image is not available for this complaint.")

        # Controls remain compact and side-by-side.
        st.markdown(
            '<div style="margin-top:.65rem;"></div>',
            unsafe_allow_html=True,
        )

        action1, action2 = st.columns([1, 1], gap="small")

        with action1:
            new_status = st.selectbox(
                "New status",
                ["Pending", "In Progress", "Resolved"],
                index=(
                    ["Pending", "In Progress", "Resolved"].index(
                        selected_row["status"]
                    )
                    if selected_row["status"] in ["Pending", "In Progress", "Resolved"]
                    else 0
                ),
                key=f"new_status_{selected_id}",
            )

            if st.button(
                "Update Status",
                key=f"update_{selected_id}",
                use_container_width=True,
            ):
                update_status(selected_id, new_status)
                st.success("Status updated.")
                st.rerun()

        with action2:
            st.markdown(
                '<div class="delete-note">Danger zone</div>',
                unsafe_allow_html=True,
            )

            confirm_delete = st.checkbox(
                "I confirm deletion.",
                key=f"confirm_delete_{selected_id}",
            )

            if st.button(
                "Delete Complaint",
                key=f"delete_{selected_id}",
                use_container_width=True,
            ):
                if not confirm_delete:
                    st.warning("Please confirm deletion first.")
                else:
                    delete_complaint(selected_id)
                    st.session_state.selected_complaint_id = None
                    st.success("Complaint deleted.")
                    st.rerun()


# ============================================================
# FOOTER / REPORT DOWNLOAD
# ============================================================
st.markdown('<div class="rule"></div>', unsafe_allow_html=True)

csv_data = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "↓  Download Complaint Report",
    data=csv_data,
    file_name="urbanpulse_complaint_report.csv",
    mime="text/csv",
)