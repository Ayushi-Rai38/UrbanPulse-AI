import os
import random
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import streamlit as st

from PIL import Image
from dotenv import load_dotenv
from ultralytics import YOLO

from database.database import conn, cursor


# ===========================================================
# PAGE CONFIG
# ===========================================================

st.set_page_config(
    page_title="UrbanPulse AI",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ===========================================================
# SESSION STATE
# ===========================================================

DEFAULT_STATE = {

    "page": "dashboard",

    "admin": False,

    "theme": "light",

    "uploaded_file": None,

    "image_path": "",

    "result_image": None,

    "issue": "",

    "confidence": 0.0,

    "detected": False,

    "ai_summary": "",

    "vision_summary": "",

    "department": "",

    "location": "",

    "description": "",

    "citizen_name": "",

    "phone": ""

}

for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ===========================================================
# LOAD ENV
# ===========================================================

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

gemini = genai.GenerativeModel(
    "gemini-2.5-flash"
)


# ===========================================================
# LOAD MODELS
# ===========================================================

YOLO_MODELS = {

    "Pothole": YOLO("models/pothole_best.pt"),

    "Garbage": YOLO("models/garbage_best.pt")

}

nlp_model = joblib.load(
    "models/model.pkl"
)

tfidf = joblib.load(
    "models/tfidf.pkl"
)


# ===========================================================
# DEPARTMENTS
# ===========================================================

DEPARTMENTS = {

    "Solid Waste (Garbage) Related":
    "🗑️ Solid Waste Department",

    "Road Maintenance (Engg)":
    "🛣️ Road Maintenance Department"

}


# ===========================================================
# COLORS
# ===========================================================

PRIMARY = "#2563EB"
SECONDARY = "#14B8A6"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
DANGER = "#EF4444"

BACKGROUND = "#F8FAFC"

CARD = "#FFFFFF"

TEXT = "#0F172A"

MUTED = "#64748B"

BORDER = "#E2E8F0"


# ===========================================================
# GOOGLE FONT
# ===========================================================

st.markdown("""

<link rel="preconnect" href="https://fonts.googleapis.com">

<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

""", unsafe_allow_html=True)


# ===========================================================
# CSS
# ===========================================================

st.markdown(f"""

<style>

html,
body,
[class*=css]{{

font-family:'Inter',sans-serif;

}}

.stApp{{

background:{BACKGROUND};

}}

.block-container{{

max-width:1550px;

padding-top:1rem;

padding-left:2rem;

padding-right:2rem;

padding-bottom:2rem;

}}

section[data-testid="stSidebar"]{{

background:white;

border-right:1px solid {BORDER};

}}

section[data-testid="stSidebar"] *{{

color:{TEXT};

}}

.topbar{{

background:white;

border:1px solid {BORDER};

border-radius:20px;

padding:18px 25px;

display:flex;

justify-content:space-between;

align-items:center;

margin-bottom:25px;

box-shadow:0 15px 35px rgba(0,0,0,.05);

}}

.logo{{

display:flex;

align-items:center;

gap:15px;

}}

.logoBox{{

width:58px;

height:58px;

border-radius:18px;

background:linear-gradient(135deg,#2563EB,#14B8A6);

display:flex;

justify-content:center;

align-items:center;

font-size:25px;

font-weight:800;

color:white;

}}

.hero{{

background:linear-gradient(135deg,#2563EB,#14B8A6);

padding:45px;

border-radius:25px;

margin-bottom:25px;

color:white;

box-shadow:0 18px 45px rgba(37,99,235,.25);

}}

.hero h1{{

font-size:40px;

font-weight:800;

}}

.hero p{{

font-size:16px;

line-height:1.8;

}}

.card{{

background:white;

border:1px solid {BORDER};

border-radius:20px;

padding:22px;

margin-bottom:18px;

box-shadow:0 12px 35px rgba(0,0,0,.05);

}}

.metricCard{{

background:white;

border:1px solid {BORDER};

border-radius:18px;

padding:20px;

}}

.metricTitle{{

font-size:14px;

color:{MUTED};

}}

.metricValue{{

font-size:34px;

font-weight:800;

color:{TEXT};

margin-top:8px;

}}

.sectionTitle{{

font-size:22px;

font-weight:700;

margin-bottom:15px;

color:{TEXT};

}}

.stButton>button{{

height:48px;

border-radius:12px;

background:#2563EB;

color:white;

border:none;

font-weight:700;

}}

.stButton>button:hover{{

background:#1D4ED8;

}}

[data-testid="stFileUploader"]{{

border:2px dashed #CBD5E1;

border-radius:20px;

background:white;

}}

.footer{{

text-align:center;

padding:35px;

color:{MUTED};

}}

</style>

""", unsafe_allow_html=True)


# ===========================================================
# HELPER FUNCTIONS
# ===========================================================

def change_page(page):

    st.session_state.page = page

    st.rerun()


def save_image(uploaded):

    os.makedirs("uploads", exist_ok=True)

    path = os.path.join(
        "uploads",
        uploaded.name
    )

    with open(path, "wb") as file:

        file.write(uploaded.getbuffer())

    return path


def total_complaints():

    cursor.execute(
        "SELECT COUNT(*) FROM complaints"
    )

    return cursor.fetchone()[0]


def pending_complaints():

    cursor.execute(
        "SELECT COUNT(*) FROM complaints WHERE status='Pending'"
    )

    return cursor.fetchone()[0]


def resolved_complaints():

    cursor.execute(
        "SELECT COUNT(*) FROM complaints WHERE status='Resolved'"
    )

    return cursor.fetchone()[0]


def high_priority():

    cursor.execute("""

    SELECT COUNT(*)

    FROM complaints

    WHERE confidence>=0.85

    """)

    return cursor.fetchone()[0]


def recent_complaints(limit=5):

    cursor.execute("""

    SELECT

    issue_type,

    location,

    status,

    date

    FROM complaints

    ORDER BY id DESC

    LIMIT ?

    """,(limit,))

    return cursor.fetchall()


def generate_ai_summary(issue, department, location, description):

    prompt=f"""

You are an AI Smart City Assistant.

Generate a professional complaint report.

Issue : {issue}

Department : {department}

Location : {location}

Description : {description}

Return:

1. Summary

2. Severity

3. Root Cause

4. Municipal Action

5. Estimated Resolution Time

Professional tone only.

"""

    try:

        response=gemini.generate_content(prompt)

        return response.text

    except:

        return "Unable to generate AI summary."


def analyze_image(image_path):

    try:

        image=Image.open(image_path)

        response=gemini.generate_content([

            """

Analyze this civic complaint image.

Tell:

• Issue

• Severity

• Public Safety Risk

• Recommended Action

""",

            image

        ])

        return response.text

    except:

        return "Image analysis unavailable."


# ===========================================================
# SIDEBAR
# ===========================================================

with st.sidebar:

    st.markdown("""

    <div style="padding-top:10px;padding-bottom:25px;">

        <div style="display:flex;align-items:center;gap:14px;">

            <div style="
            width:58px;
            height:58px;
            border-radius:18px;
            background:linear-gradient(135deg,#2563EB,#14B8A6);
            display:flex;
            justify-content:center;
            align-items:center;
            color:white;
            font-size:22px;
            font-weight:800;
            ">
            UP
            </div>

            <div>

            <div style="font-size:22px;font-weight:800;">
            UrbanPulse AI
            </div>

            <div style="font-size:13px;color:#64748B;">
            Smart Urban Intelligence
            </div>

            </div>

        </div>

    </div>

    """,unsafe_allow_html=True)

    st.caption("Navigation")

    if st.button("🏠 Dashboard",use_container_width=True):
        change_page("dashboard")

    if st.button("📤 Report Complaint",use_container_width=True):
        change_page("report")

    if st.button("📂 My Complaints",use_container_width=True):
        change_page("complaints")

    if st.button("📈 Analytics",use_container_width=True):
        change_page("analytics")

    st.divider()

    st.caption("Administrator")

    if not st.session_state.admin:

        user=st.text_input("Username")

        pwd=st.text_input(
            "Password",
            type="password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            if user=="admin" and pwd=="admin123":

                st.session_state.admin=True

                st.success("Login Successful")

                st.rerun()

            else:

                st.error("Invalid Credentials")

    else:

        st.success("Admin Logged In")

        if st.button(
            "Admin Dashboard",
            use_container_width=True
        ):
            change_page("admin")

        if st.button(
            "Logout",
            use_container_width=True
        ):

            st.session_state.admin=False

            st.rerun()

    st.divider()

    st.caption("UrbanPulse AI v2")


# ===========================================================
# TOP BAR
# ===========================================================

st.markdown("""

<div class="topbar">

<div class="logo">

<div class="logoBox">

🏙️

</div>

<div>

<div style="font-size:24px;font-weight:800;">

UrbanPulse AI

</div>

<div style="font-size:13px;color:#64748B;">

AI Powered Smart Complaint Management

</div>

</div>

</div>

<div style="display:flex;gap:15px;align-items:center;">

<div style="
padding:8px 15px;
background:#EFF6FF;
border-radius:12px;
font-weight:700;
color:#2563EB;
">

LIVE

</div>

<div style="
width:45px;
height:45px;
border-radius:50%;
background:#2563EB;
display:flex;
justify-content:center;
align-items:center;
color:white;
font-weight:700;
">

CU

</div>

</div>

</div>

""",unsafe_allow_html=True)



# ===========================================================
# PAGE ROUTING
# ===========================================================

if st.session_state.page == "dashboard":

    st.markdown("""

    <div class="hero">

    <h1>🚦 Welcome to UrbanPulse AI</h1>

    <p>

    AI Powered Smart Urban Complaint Detection & Management Platform.

    Detect potholes, garbage, damaged roads and other civic issues using
    Computer Vision, NLP and Gemini AI.

    </p>

    </div>

    """, unsafe_allow_html=True)

    total = total_complaints()
    pending = pending_complaints()
    resolved = resolved_complaints()
    priority = high_priority()

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.markdown(f"""

        <div class="metricCard">

        <div class="metricTitle">
        Total Complaints
        </div>

        <div class="metricValue">
        {total}
        </div>

        </div>

        """, unsafe_allow_html=True)

    with c2:

        st.markdown(f"""

        <div class="metricCard">

        <div class="metricTitle">
        Pending
        </div>

        <div class="metricValue">
        {pending}
        </div>

        </div>

        """, unsafe_allow_html=True)

    with c3:

        st.markdown(f"""

        <div class="metricCard">

        <div class="metricTitle">
        Resolved
        </div>

        <div class="metricValue">
        {resolved}
        </div>

        </div>

        """, unsafe_allow_html=True)

    with c4:

        st.markdown(f"""

        <div class="metricCard">

        <div class="metricTitle">
        High Priority
        </div>

        <div class="metricValue">
        {priority}
        </div>

        </div>

        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([2,1])

    with left:

        cursor.execute("""

        SELECT issue_type,
        COUNT(*)

        FROM complaints

        GROUP BY issue_type

        """)

        rows = cursor.fetchall()

        if len(rows) == 0:

            chart_df = pd.DataFrame({

                "Issue":[
                    "Pothole",
                    "Garbage"
                ],

                "Count":[
                    8,
                    5
                ]

            })

        else:

            chart_df = pd.DataFrame(

                rows,

                columns=[

                    "Issue",

                    "Count"

                ]

            )

        fig = px.bar(

            chart_df,

            x="Issue",

            y="Count",

            color="Issue",

            text="Count"

        )

        fig.update_layout(

            height=400,

            template="plotly_white"

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

    with right:

        pie = px.pie(

            chart_df,

            names="Issue",

            values="Count",

            hole=.60

        )

        pie.update_layout(

            height=400

        )

        st.plotly_chart(

            pie,

            use_container_width=True

        )

    st.markdown("### 📋 Recent Complaints")

    recent = recent_complaints()

    if len(recent) == 0:

        st.info("No complaints found.")

    else:

        for issue, location, status, date in recent:

            st.markdown(f"""

            <div class="card">

            <b>{issue}</b><br>

            📍 {location}<br>

            📅 {date}<br>

            <b>Status :</b> {status}

            </div>

            """, unsafe_allow_html=True)

    st.markdown("### 🚀 Quick Actions")

    q1, q2, q3 = st.columns(3)

    with q1:

        if st.button(

            "📤 Report Complaint",

            use_container_width=True

        ):

            change_page("report")

    with q2:

        if st.button(

            "📈 Analytics",

            use_container_width=True

        ):

            change_page("analytics")

    with q3:

        if st.button(

            "📂 My Complaints",

            use_container_width=True

        ):

            change_page("complaints")


elif st.session_state.page == "report":

    st.markdown("""

    <div class="hero">

    <h1>📤 Report Urban Complaint</h1>

    <p>

    Upload an image and UrbanPulse AI will automatically detect
    the urban issue using YOLO AI.

    </p>

    </div>

    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(

        "Upload Image",

        type=["jpg", "jpeg", "png"]

    )

    if uploaded_file:

        image = Image.open(uploaded_file)

        st.image(

            image,

            use_container_width=True

        )

        if st.button(

            "🚀 Detect Issue",

            use_container_width=True

        ):

            with st.spinner("Running AI Detection..."):

                img = np.array(

                    image.convert("RGB")

                )

                best_prediction = None

                best_issue = ""

                best_confidence = 0

                for issue, model in YOLO_MODELS.items():

                    prediction = model.predict(

                        source=img,

                        verbose=False

                    )

                    boxes = prediction[0].boxes

                    if len(boxes) == 0:

                        continue

                    confidence = float(

                        boxes.conf.max()

                    )

                    if confidence > best_confidence:

                        best_confidence = confidence

                        best_issue = issue

                        best_prediction = prediction

                if best_prediction is None:

                    st.error(

                        "No issue detected."

                    )

                else:

                    st.session_state.detected = True

                    st.session_state.issue = best_issue

                    st.session_state.confidence = best_confidence

                    st.session_state.result_image = best_prediction[0].plot()

                    st.session_state.image_path = save_image(

                        uploaded_file

                    )

                    change_page("detect")


# ===========================================================
# DETECTION PAGE
# ===========================================================

elif st.session_state.page == "detect":

    if not st.session_state.detected:

        st.warning(

            "No detection available."

        )

        st.stop()

    left, right = st.columns([1.6, 1])

    with left:

        st.image(

            st.session_state.result_image,

            use_container_width=True

        )

    with right:

        st.success(

            st.session_state.issue

        )

        st.metric(

            "Confidence",

            f"{st.session_state.confidence*100:.2f}%"

        )

        if st.button(

            "Continue",

            use_container_width=True

        ):

            change_page("form")


# ===========================================================
# FORM PAGE
# ===========================================================

elif st.session_state.page == "form":

    st.markdown("## 📝 Complaint Details")

    st.session_state.citizen_name = st.text_input(

        "Citizen Name"

    )

    st.session_state.phone = st.text_input(

        "Phone Number"

    )

    st.session_state.location = st.text_input(

        "Location"

    )

    st.session_state.description = st.text_area(

        "Complaint Description"

    )

    if st.button(

        "Generate AI Report",

        use_container_width=True

    ):

        if st.session_state.location.strip() == "":

            st.warning(

                "Please enter location."

            )

            st.stop()

        change_page("submit")



# ===========================================================
# SUBMIT PAGE
# ===========================================================

elif st.session_state.page == "submit":

    department = "General Urban Department"

    if st.session_state.description.strip() != "":

        vector = tfidf.transform(

            [st.session_state.description]

        )

        prediction = nlp_model.predict(vector)[0]

        department = DEPARTMENTS.get(

            prediction,

            prediction

        )

    with st.spinner("Generating AI Summary..."):

        ai_summary = generate_ai_summary(

            st.session_state.issue,

            department,

            st.session_state.location,

            st.session_state.description

        )

    with st.spinner("Analyzing Image..."):

        vision_summary = analyze_image(

            st.session_state.image_path

        )

    cursor.execute(

        """

        SELECT COUNT(*)

        FROM complaints

        WHERE

        issue_type=?

        AND

        location=?

        AND

        status='Pending'

        """,

        (

            st.session_state.issue,

            st.session_state.location

        )

    )

    duplicate = cursor.fetchone()[0]

    if duplicate > 0:

        st.error(

            "Similar complaint already exists."

        )

        st.stop()

    complaint_id = f"UP-{random.randint(100000,999999)}"

    today = datetime.now().strftime(

        "%d-%m-%Y %H:%M"

    )

    cursor.execute(

        """

        INSERT INTO complaints(

        issue_type,

        confidence,

        location,

        image_path,

        status,

        date,

        ai_summary

        )

        VALUES(

        ?,?,?,?,?,?,?

        )

        """,

        (

            st.session_state.issue,

            st.session_state.confidence,

            st.session_state.location,

            st.session_state.image_path,

            "Pending",

            today,

            ai_summary

        )

    )

    conn.commit()

    st.balloons()

    st.success(

        "Complaint Submitted Successfully"

    )

    st.info(

        f"Complaint ID : {complaint_id}"

    )

    st.success(

        f"Assigned Department : {department}"

    )

    st.markdown("---")

    st.subheader("🤖 AI Summary")

    st.write(ai_summary)

    st.markdown("---")

    st.subheader("👁 Gemini Vision Analysis")

    st.write(vision_summary)

    c1, c2 = st.columns(2)

    with c1:

        if st.button(

            "🏠 Dashboard",

            use_container_width=True

        ):

            st.session_state.detected = False

            change_page("dashboard")

    with c2:

        if st.button(

            "📤 Report New Complaint",

            use_container_width=True

        ):

            st.session_state.detected = False

            change_page("report")


# ===========================================================
# MY COMPLAINTS
# ===========================================================

elif st.session_state.page == "complaints":

    st.title("📂 My Complaints")

    cursor.execute(

        """

        SELECT

        id,

        issue_type,

        confidence,

        location,

        status,

        date

        FROM complaints

        ORDER BY id DESC

        """

    )

    rows = cursor.fetchall()

    if len(rows) == 0:

        st.info("No complaints found.")

    else:

        df = pd.DataFrame(

            rows,

            columns=[

                "ID",

                "Issue",

                "Confidence",

                "Location",

                "Status",

                "Date"

            ]

        )

        df["Confidence"] = (

            df["Confidence"] * 100

        ).round(2).astype(str) + "%"

        st.dataframe(

            df,

            use_container_width=True,

            hide_index=True

        )

        st.download_button(

            "⬇ Download CSV",

            df.to_csv(index=False),

            "complaints.csv",

            "text/csv",

            use_container_width=True

        )



# ===========================================================
# ANALYTICS PAGE
# ===========================================================

elif st.session_state.page == "analytics":

    st.title("📈 Analytics Dashboard")

    cursor.execute("""

    SELECT

    issue_type,

    COUNT(*)

    FROM complaints

    GROUP BY issue_type

    """)

    rows = cursor.fetchall()

    if len(rows) == 0:

        rows = [

            ("Pothole", 5),

            ("Garbage", 3)

        ]

    analytics = pd.DataFrame(

        rows,

        columns=[

            "Issue",

            "Count"

        ]

    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(

            analytics,

            x="Issue",

            y="Count",

            color="Issue",

            text="Count"

        )

        fig.update_layout(

            height=420,

            template="plotly_white"

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

    with col2:

        pie = px.pie(

            analytics,

            names="Issue",

            values="Count",

            hole=.60

        )

        pie.update_layout(

            height=420

        )

        st.plotly_chart(

            pie,

            use_container_width=True

        )

    cursor.execute("""

    SELECT

    status,

    COUNT(*)

    FROM complaints

    GROUP BY status

    """)

    status = cursor.fetchall()

    if len(status):

        status_df = pd.DataFrame(

            status,

            columns=[

                "Status",

                "Count"

            ]

        )

        fig = px.bar(

            status_df,

            x="Status",

            y="Count",

            color="Status",

            text="Count"

        )

        fig.update_layout(

            height=420,

            template="plotly_white"

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )


# ===========================================================
# ADMIN DASHBOARD
# ===========================================================

elif st.session_state.page == "admin":

    if not st.session_state.admin:

        st.error("Unauthorized")

        st.stop()

    st.title("🛠 Admin Dashboard")

    cursor.execute("""

    SELECT

    id,

    issue_type,

    confidence,

    location,

    status,

    date

    FROM complaints

    ORDER BY id DESC

    """)

    complaints = cursor.fetchall()

    if len(complaints) == 0:

        st.info("No complaints available.")

    else:

        for row in complaints:

            cid, issue, conf, location, status, date = row

            st.markdown("---")

            st.subheader(f"Complaint #{cid}")

            st.write(f"**Issue :** {issue}")

            st.write(f"**Confidence :** {conf*100:.2f}%")

            st.write(f"**Location :** {location}")

            st.write(f"**Status :** {status}")

            st.write(f"**Date :** {date}")

            a, b, c, d = st.columns(4)

            with a:

                if st.button(

                    "Approve",

                    key=f"a{cid}"

                ):

                    cursor.execute(

                        "UPDATE complaints SET status='Approved' WHERE id=?",

                        (cid,)

                    )

                    conn.commit()

                    st.rerun()

            with b:

                if st.button(

                    "Resolve",

                    key=f"r{cid}"

                ):

                    cursor.execute(

                        "UPDATE complaints SET status='Resolved' WHERE id=?",

                        (cid,)

                    )

                    conn.commit()

                    st.rerun()

            with c:

                if st.button(

                    "Reject",

                    key=f"rej{cid}"

                ):

                    cursor.execute(

                        "UPDATE complaints SET status='Rejected' WHERE id=?",

                        (cid,)

                    )

                    conn.commit()

                    st.rerun()

            with d:

                if st.button(

                    "Delete",

                    key=f"del{cid}"

                ):

                    cursor.execute(

                        "DELETE FROM complaints WHERE id=?",

                        (cid,)

                    )

                    conn.commit()

                    st.rerun()


# ===========================================================
# FOOTER
# ===========================================================

st.markdown("""

<hr>

<div class="footer">

<h3>🏙 UrbanPulse AI v2</h3>

<p>

AI Powered Smart Urban Complaint Detection &
Management Platform

</p>

<p>

YOLO • Gemini AI • NLP • SQLite • Streamlit

</p>

</div>

""", unsafe_allow_html=True)




