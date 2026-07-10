import streamlit as st

if not st.session_state.get("admin", False):

    st.error("Please login as Admin.")

    st.stop()
import os
import sqlite3
import pandas as pd
import plotly.express as px


# ---------------- Page ----------------

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 UrbanPulse AI Dashboard")

# ---------------- Database ----------------

conn = sqlite3.connect("database/complaints.db")

df = pd.read_sql_query(
    "SELECT * FROM complaints",
    conn
)

conn.close()

# ---------------- Statistics ----------------

total = len(df)

pending = len(df[df["status"] == "Pending"])
in_progress = len(df[df["status"] == "In Progress"])
resolved = len(df[df["status"] == "Resolved"])

# ---------------- Cards ----------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📋 Total",
        total
    )

with col2:
    st.metric(
        "🟡 Pending",
        pending
    )

with col3:
    st.metric(
        "🟠 In Progress",
        in_progress
    )

with col4:
    st.metric(
        "🟢 Resolved",
        resolved
    )


st.divider()

st.markdown("---")

st.subheader("📈 Dashboard Overview")


#--------------------charts-----------------------
col1, col2 = st.columns(2)

with col1:

    pie = px.pie(
        df,
        names="issue_type",
        title="Complaints by Issue Type"
    )

    st.plotly_chart(
        pie,
        use_container_width=True
    )

with col2:

    status = df["status"].value_counts().reset_index()

    status.columns = ["Status", "Count"]

    bar = px.bar(
        status,
        x="Status",
        y="Count",
        title="Complaint Status"
    )

    st.plotly_chart(
        bar,
        use_container_width=True
    )

search = st.text_input(
    "🔍 Search Location"
)

if search != "":

    df = df[
        df["location"].str.contains(
            search,
            case=False,
            na=False
        )
    ]
# ---------------- Complaint Table ----------------

st.subheader("📑 Complaint Records")



status_filter = st.selectbox(

    "Filter by Status",

    [
    "All",
    "Pending",
    "In Progress",
    "Resolved"
]

)

if status_filter != "All":

    df = df[df["status"] == status_filter]


st.dataframe(

    df[
        [
            "issue_type",
            "location",
            "status",
            "confidence",
            "ai_summary",
            "date"
        ]
    ],

    use_container_width=True
)
st.subheader("🛠 Update Complaint Status")

complaints = {}

for _, row in df.iterrows():

    display = f"#{row['id']} | {row['issue_type']} | {row['location']} | {row['status']}"

    complaints[display] = row["id"]

selected = st.selectbox(

    "Select Complaint",

    list(complaints.keys())

)

selected_id = complaints[selected]
selected_row = df[df["id"] == selected_id].iloc[0]

st.markdown("---")

st.subheader("📄 Complaint Details")

col1, col2 = st.columns(2)

with col1:

    st.write("**Issue Type:**", selected_row["issue_type"])

    st.write("**Location:**", selected_row["location"])

    st.write("**Status:**", selected_row["status"])

    st.write(
        "**Confidence:**",
        f"{selected_row['confidence']*100:.2f}%"
    )

with col2:

    st.write("**Date:**", selected_row["date"])

    st.write("**Image Path:**")

    st.code(selected_row["image_path"])

st.markdown("---")

confirm_delete = st.checkbox(
    "I confirm that I want to delete this complaint."
)

if st.button("🗑 Delete Complaint"):

    if not confirm_delete:

        st.warning(
            "Please confirm before deleting."
        )

    else:

        conn = sqlite3.connect(
            "database/complaints.db"
        )

        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM complaints WHERE id=?",
            (selected_id,)
        )

        conn.commit()

        conn.close()

        st.success(
            "Complaint Deleted Successfully."
        )

        st.rerun()

st.subheader("🖼 Complaint Image")

if os.path.exists(selected_row["image_path"]):

    st.image(
        selected_row["image_path"],
        use_container_width=True
    )

else:

    st.warning("Image not found.")




new_status = st.selectbox(
    "New Status",
    [
        "Pending",
        "In Progress",
        "Resolved"
    ]
)

if st.button("Update Status"):

    conn = sqlite3.connect("database/complaints.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE complaints
        SET status=?
        WHERE id=?
        """,
        (
            new_status,
            selected_id
        )
    )

    conn.commit()

    conn.close()

    st.success("Status Updated Successfully")

    st.rerun()


#-------------------- Download Report --------------------
csv = df.to_csv(index=False)

st.download_button(

    "📥 Download Report",

    csv,

    "complaints.csv",

    "text/csv"
)


# ---------------- AI Summary ----------------

st.subheader("🤖 AI Complaint Summaries")

for i, row in df.iterrows():

    with st.expander(
        f"{row['issue_type']} | {row['location']}"
    ):

        if row["ai_summary"]:

            st.write(row["ai_summary"])

        else:

            st.info("No AI Summary Available.")