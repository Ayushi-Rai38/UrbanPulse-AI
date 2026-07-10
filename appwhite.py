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


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="UrbanPulse AI",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {

    "page":"dashboard",

    "admin":False,

    "theme":"light",

    "uploaded_image":None,

    "result_image":None,

    "image_path":"",

    "issue":"",

    "confidence":0.0,

    "detected":False,

    "department":"",

    "location":"",

    "description":"",

    "citizen":"",

    "phone":""

}

for key,value in DEFAULTS.items():

    if key not in st.session_state:

        st.session_state[key]=value


# ============================================================
# LOAD ENV
# ============================================================

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

gemini = genai.GenerativeModel("gemini-2.5-flash")


# ============================================================
# LOAD MODELS
# ============================================================

YOLO_MODELS = {

    "Pothole":YOLO("models/pothole_best.pt"),

    "Garbage":YOLO("models/garbage_best.pt")

}

nlp_model = joblib.load("models/model.pkl")

tfidf = joblib.load("models/tfidf.pkl")


DEPARTMENTS={

"Solid Waste (Garbage) Related":"🗑️ Solid Waste Department",

"Road Maintenance (Engg)":"🛣️ Road Maintenance Department"

}


# ============================================================
# COLORS
# ============================================================

PRIMARY="#4F8CFF"

SECONDARY="#35D39B"

PURPLE="#8B5CF6"

RED="#EF4444"

ORANGE="#F59E0B"

BACKGROUND="#F4F7FB"

CARD="#FFFFFF"

TEXT="#111827"

BORDER="#E8ECF4"

MUTED="#6B7280"


# ============================================================
# PREMIUM CSS
# ============================================================

st.markdown("""

<link rel="preconnect" href="https://fonts.googleapis.com">

<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<style>

html,
body,
[class*=css]{

font-family:'Inter',sans-serif;

background:#F4F7FB;

}

.stApp{

background:#F4F7FB;

}

.block-container{

max-width:1600px;

padding-top:18px;

padding-left:28px;

padding-right:28px;

padding-bottom:30px;

}

section[data-testid="stSidebar"]{

background:white;

border-right:1px solid #E8ECF4;

}

section[data-testid="stSidebar"] *{

color:#111827;

}

.sidebarLogo{

display:flex;

align-items:center;

gap:15px;

margin-bottom:30px;

}

.logoCircle{

width:58px;

height:58px;

border-radius:18px;

background:linear-gradient(135deg,#4F8CFF,#35D39B);

display:flex;

justify-content:center;

align-items:center;

font-size:24px;

font-weight:800;

color:white;

}

.topbar{

background:white;

padding:18px 24px;

border-radius:20px;

display:flex;

justify-content:space-between;

align-items:center;

margin-bottom:24px;

border:1px solid #E8ECF4;

box-shadow:0 15px 35px rgba(0,0,0,.05);

}

.hero{

background:linear-gradient(135deg,#4F8CFF,#35D39B);

padding:45px;

border-radius:24px;

color:white;

margin-bottom:25px;

}

.hero h1{

font-size:42px;

font-weight:800;

margin-bottom:10px;

}

.hero p{

font-size:16px;

line-height:1.8;

opacity:.95;

}

.card{

background:white;

border-radius:20px;

padding:22px;

border:1px solid #E8ECF4;

box-shadow:0 15px 35px rgba(0,0,0,.05);

margin-bottom:20px;

}

.metricCard{

background:white;

border-radius:18px;

padding:22px;

border:1px solid #E8ECF4;

transition:.25s;

}

.metricCard:hover{

transform:translateY(-4px);

}

.metricTitle{

font-size:14px;

color:#6B7280;

}

.metricValue{

font-size:34px;

font-weight:800;

margin-top:8px;

}

.sectionTitle{

font-size:22px;

font-weight:700;

margin-bottom:18px;

}

.stButton>button{

height:48px;

border:none;

border-radius:12px;

background:#4F8CFF;

color:white;

font-weight:700;

}

.stButton>button:hover{

background:#3478ff;

}

[data-testid="stFileUploader"]{

background:white;

border:2px dashed #CBD5E1;

border-radius:18px;

}

</style>

""",unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def change_page(page):

    st.session_state.page = page

    st.rerun()


def save_uploaded_image(uploaded_file):

    os.makedirs("uploads", exist_ok=True)

    path = os.path.join("uploads", uploaded_file.name)

    with open(path, "wb") as f:

        f.write(uploaded_file.getbuffer())

    return path


def get_total():

    cursor.execute("SELECT COUNT(*) FROM complaints")

    return cursor.fetchone()[0]


def get_pending():

    cursor.execute(

        "SELECT COUNT(*) FROM complaints WHERE status='Pending'"

    )

    return cursor.fetchone()[0]


def get_resolved():

    cursor.execute(

        "SELECT COUNT(*) FROM complaints WHERE status='Resolved'"

    )

    return cursor.fetchone()[0]


def get_rejected():

    cursor.execute(

        "SELECT COUNT(*) FROM complaints WHERE status='Rejected'"

    )

    return cursor.fetchone()[0]


def get_priority():

    cursor.execute("""

    SELECT COUNT(*)

    FROM complaints

    WHERE confidence>=0.85

    """)

    return cursor.fetchone()[0]


def get_recent(limit=6):

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

You are an AI Smart City Officer.

Generate a professional municipal report.

Issue : {issue}

Department : {department}

Location : {location}

Citizen Description : {description}

Return:

1. Summary

2. Severity

3. Cause

4. Government Action

5. Estimated Resolution Time

"""

    try:

        response=gemini.generate_content(prompt)

        return response.text

    except:

        return "Unable to generate AI report."


def analyze_image(image_path):

    try:

        image=Image.open(image_path)

        response=gemini.generate_content([

"""

Analyze this civic complaint image.

Return

• Issue

• Severity

• Public Risk

• Recommendation

""",

image

])

        return response.text

    except:

        return "Image analysis unavailable."


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("""

<div class="sidebarLogo">

<div class="logoCircle">

UP

</div>

<div>

<div style="font-size:24px;font-weight:800;">

UrbanPulse AI

</div>

<div style="font-size:13px;color:#6B7280;">

Smart City Platform

</div>

</div>

</div>

""",unsafe_allow_html=True)

    st.caption("MAIN")

    if st.button("🏠 Dashboard",use_container_width=True):

        change_page("dashboard")

    if st.button("📤 Report Complaint",use_container_width=True):

        change_page("report")

    if st.button("📂 My Complaints",use_container_width=True):

        change_page("complaints")

    if st.button("📊 Analytics",use_container_width=True):

        change_page("analytics")

    st.divider()

    st.caption("ADMIN")

    if not st.session_state.admin:

        user=st.text_input("Username")

        pwd=st.text_input("Password",type="password")

        if st.button("Login",use_container_width=True):

            if user=="admin" and pwd=="admin123":

                st.session_state.admin=True

                st.rerun()

            else:

                st.error("Invalid Credentials")

    else:

        st.success("Administrator")

        if st.button("Open Admin",use_container_width=True):

            change_page("admin")

        if st.button("Logout",use_container_width=True):

            st.session_state.admin=False

            st.rerun()

    st.divider()

    st.info("UrbanPulse AI v2")


# ============================================================
# TOP NAVBAR
# ============================================================

st.markdown("""

<div class="topbar">

<div style="display:flex;align-items:center;gap:18px;">

<div style="
width:56px;
height:56px;
border-radius:18px;
background:linear-gradient(135deg,#4F8CFF,#35D39B);
display:flex;
justify-content:center;
align-items:center;
font-size:24px;
font-weight:800;
color:white;
">
UP
</div>

<div>

<div style="
font-size:26px;
font-weight:800;
color:#111827;
">
UrbanPulse AI
</div>

<div style="
font-size:14px;
color:#6B7280;
">
AI Powered Smart Urban Complaint Detection Platform
</div>

</div>

</div>

<div style="
display:flex;
align-items:center;
gap:18px;
">

<div style="
background:#EEF4FF;
padding:10px 18px;
border-radius:12px;
font-weight:700;
color:#4F8CFF;
">
🟢 LIVE
</div>

<div style="
background:#F9FAFB;
border:1px solid #E8ECF4;
padding:10px 18px;
border-radius:12px;
">
🔔
</div>

<div style="
background:#4F8CFF;
width:46px;
height:46px;
border-radius:50%;
display:flex;
justify-content:center;
align-items:center;
font-weight:700;
color:white;
">
CU
</div>

</div>

</div>

""",unsafe_allow_html=True)


# ============================================================
# DASHBOARD
# ============================================================

if st.session_state.page=="dashboard":

    st.markdown("""

<div class="hero">

<h1>

🚦 Welcome to UrbanPulse AI

</h1>

<p>

Monitor complaints, detect urban issues using Artificial Intelligence,
track municipal response,
view analytics,
manage departments,
and improve smart city operations from one dashboard.

</p>

</div>

""",unsafe_allow_html=True)

    total=get_total()

    pending=get_pending()

    resolved=get_resolved()

    rejected=get_rejected()

    priority=get_priority()

    c1,c2,c3,c4,c5=st.columns(5)

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

""",unsafe_allow_html=True)

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

""",unsafe_allow_html=True)

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

""",unsafe_allow_html=True)

    with c4:

        st.markdown(f"""

<div class="metricCard">

<div class="metricTitle">

Rejected

</div>

<div class="metricValue">

{rejected}

</div>

</div>

""",unsafe_allow_html=True)

    with c5:

        st.markdown(f"""

<div class="metricCard">

<div class="metricTitle">

High Priority

</div>

<div class="metricValue">

{priority}

</div>

</div>

""",unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    left,right=st.columns([2.2,1])

    with left:

        cursor.execute("""

        SELECT issue_type,
        COUNT(*)

        FROM complaints

        GROUP BY issue_type

        """)

        data=cursor.fetchall()

        if len(data)==0:

            df=pd.DataFrame({

            "Issue":[
            "Pothole",
            "Garbage"
            ],

            "Count":[
            14,
            8
            ]

            })

        else:

            df=pd.DataFrame(

            data,

            columns=[

            "Issue",

            "Count"

            ]

            )

        fig=px.bar(

        df,

        x="Issue",

        y="Count",

        color="Issue",

        text="Count",

        template="plotly_white"

        )

        fig.update_layout(

        height=420,

        title="Complaint Statistics"

        )

        st.plotly_chart(

        fig,

        use_container_width=True

        )

    with right:

        pie=px.pie(

        df,

        names="Issue",

        values="Count",

        hole=.65

        )

        pie.update_layout(

        height=420,

        title="Issue Distribution"

        )

        st.plotly_chart(

        pie,

        use_container_width=True

        )


    st.markdown("### 📋 Recent Complaints")

    recent = get_recent()

    if len(recent) == 0:

        st.info("No complaints available.")

    else:

        for issue, location, status, date in recent:

            if status == "Resolved":
                color = "#22C55E"

            elif status == "Pending":
                color = "#F59E0B"

            elif status == "Rejected":
                color = "#EF4444"

            else:
                color = "#4F8CFF"

            st.markdown(f"""

<div style="
background:white;
border:1px solid #E8ECF4;
border-left:6px solid {color};
border-radius:18px;
padding:18px;
margin-bottom:12px;
">

<div style="
display:flex;
justify-content:space-between;
align-items:center;
">

<div>

<div style="
font-size:18px;
font-weight:700;
color:#111827;
">
{issue}
</div>

<div style="
font-size:14px;
color:#6B7280;
margin-top:4px;
">
📍 {location}
</div>

<div style="
font-size:13px;
color:#94A3B8;
margin-top:4px;
">
🕒 {date}
</div>

</div>

<div style="
background:{color};
padding:8px 16px;
border-radius:20px;
color:white;
font-weight:700;
">
{status}
</div>

</div>

</div>

""",unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    left,right=st.columns([1.2,1])

    with left:

        st.markdown("""

<div class="card">

<div class="sectionTitle">

🤖 AI Detection Summary

</div>

""",unsafe_allow_html=True)

        cursor.execute("""

        SELECT

        issue_type,

        COUNT(*)

        FROM complaints

        GROUP BY issue_type

        ORDER BY COUNT(*) DESC

        """)

        rows = cursor.fetchall()

        if len(rows)==0:

            rows=[

                ("Pothole",14),

                ("Garbage",8)

            ]

        for issue,count in rows:

            st.markdown(f"""

<div style="
display:flex;
justify-content:space-between;
align-items:center;
padding:14px;
border:1px solid #E8ECF4;
border-radius:15px;
margin-bottom:12px;
">

<div>

<b>{issue}</b>

</div>

<div style="
font-size:22px;
font-weight:800;
color:#4F8CFF;
">

{count}

</div>

</div>

""",unsafe_allow_html=True)

        st.markdown("</div>",unsafe_allow_html=True)

    with right:

        st.markdown("""

<div class="card">

<div class="sectionTitle">

🏢 Department Status

</div>

""",unsafe_allow_html=True)

        departments=[

            ("Road Department","🟢 Active"),

            ("Waste Department","🟢 Active"),

            ("Electric Department","🟡 Busy"),

            ("Water Department","🟢 Active"),

            ("Emergency","🔴 High Load")

        ]

        for dep,status in departments:

            st.markdown(f"""

<div style="
display:flex;
justify-content:space-between;
align-items:center;
padding:14px;
border:1px solid #E8ECF4;
border-radius:15px;
margin-bottom:10px;
">

<div>

{dep}

</div>

<div>

{status}

</div>

</div>

""",unsafe_allow_html=True)

        st.markdown("</div>",unsafe_allow_html=True)

    st.markdown("### ⚡ Quick Actions")

    q1,q2,q3,q4=st.columns(4)

    with q1:

        if st.button(
            "📤 Report Complaint",
            use_container_width=True
        ):
            change_page("report")

    with q2:

        if st.button(
            "📂 My Complaints",
            use_container_width=True
        ):
            change_page("complaints")

    with q3:

        if st.button(
            "📊 Analytics",
            use_container_width=True
        ):
            change_page("analytics")

    with q4:

        if st.button(
            "🛠 Admin",
            use_container_width=True
        ):

            if st.session_state.admin:

                change_page("admin")

            else:

                st.warning("Admin Login Required")

# ============================================================
# REPORT COMPLAINT PAGE
# ============================================================

elif st.session_state.page == "report":

    st.markdown("""
<div class="hero">
<h1>📤 Report Urban Complaint</h1>
<p>
Upload an image of the urban issue. UrbanPulse AI will detect the problem,
generate an AI report, predict the responsible department and register
the complaint automatically.
</p>
</div>
""", unsafe_allow_html=True)

    left, right = st.columns([1.4, 1])

    with left:

        st.markdown("""
<div class="card">
<div class="sectionTitle">
📤 Upload Complaint Image
</div>
""", unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Choose Image",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_file:

            image = Image.open(uploaded_file)

            st.image(
                image,
                use_container_width=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown("""
<div class="card">
<div class="sectionTitle">
ℹ Detection Information
</div>
""", unsafe_allow_html=True)

        st.info("✔ Supported Issues")
        st.write("• Potholes")
        st.write("• Garbage")
        st.write("• Road Damage")
        st.write("• Waste Overflow")

        st.success("AI Engine Ready")

        st.markdown("</div>", unsafe_allow_html=True)

    if st.button(
        "🚀 Start AI Detection",
        use_container_width=True
    ):

        if uploaded_file is None:

            st.warning("Please upload an image.")

            st.stop()

        with st.spinner("Running YOLO Models..."):

            image = np.array(
                Image.open(uploaded_file).convert("RGB")
            )

            best_prediction = None
            best_issue = ""
            best_confidence = 0

            for issue, model in YOLO_MODELS.items():

                prediction = model.predict(
                    source=image,
                    verbose=False
                )

                boxes = prediction[0].boxes

                if len(boxes) == 0:
                    continue

                confidence = float(boxes.conf.max())

                if confidence > best_confidence:

                    best_confidence = confidence
                    best_issue = issue
                    best_prediction = prediction

            if best_prediction is None:

                st.error("No Issue Detected.")

                st.stop()

            st.session_state.detected = True

            st.session_state.issue = best_issue

            st.session_state.confidence = best_confidence

            st.session_state.result_image = best_prediction[0].plot()

            st.session_state.image_path = save_uploaded_image(
                uploaded_file
            )

            change_page("detect")


# ============================================================
# DETECTION PAGE
# ============================================================

elif st.session_state.page == "detect":

    st.markdown("""
<div class="hero">
<h1>🤖 AI Detection Result</h1>
<p>
UrbanPulse AI successfully analyzed the uploaded image.
</p>
</div>
""", unsafe_allow_html=True)

    if not st.session_state.detected:

        st.warning("No Detection Available")

        st.stop()

    left, right = st.columns([1.6, 1])

    with left:

        st.image(
            st.session_state.result_image,
            use_container_width=True
        )

    with right:

        st.markdown("""
<div class="card">
<div class="sectionTitle">
Detection Summary
</div>
""", unsafe_allow_html=True)

        st.metric(
            "Detected Issue",
            st.session_state.issue
        )

        st.metric(
            "Confidence",
            f"{st.session_state.confidence*100:.2f}%"
        )

        if st.session_state.confidence > 0.90:

            st.success("High Confidence")

        elif st.session_state.confidence > 0.75:

            st.warning("Medium Confidence")

        else:

            st.error("Low Confidence")

        st.progress(
            st.session_state.confidence
        )

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button(
            "➡ Continue",
            use_container_width=True
        ):
            change_page("form")
# ============================================================
# COMPLAINT FORM
# ============================================================

elif st.session_state.page == "form":

    st.markdown("""
<div class="hero">
<h1>📝 Complaint Information</h1>
<p>
Complete the details below to submit your complaint to the respective municipal department.
</p>
</div>
""", unsafe_allow_html=True)

    left, right = st.columns([1.5, 1])

    with left:

        st.markdown("""
<div class="card">
<div class="sectionTitle">
Citizen Details
</div>
""", unsafe_allow_html=True)

        st.session_state.citizen = st.text_input(
            "👤 Full Name"
        )

        st.session_state.phone = st.text_input(
            "📱 Phone Number"
        )

        st.session_state.location = st.text_input(
            "📍 Complaint Location"
        )

        st.session_state.description = st.text_area(
            "📝 Describe the Problem",
            height=170
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:

        st.markdown("""
<div class="card">
<div class="sectionTitle">
Detection Preview
</div>
""", unsafe_allow_html=True)

        st.metric(
            "Detected Issue",
            st.session_state.issue
        )

        st.metric(
            "Confidence",
            f"{st.session_state.confidence*100:.2f}%"
        )

        st.success("AI Detection Completed")

        st.info("Department will be predicted automatically.")

        st.markdown("</div>", unsafe_allow_html=True)

    if st.button(
        "🤖 Generate AI Report",
        use_container_width=True
    ):

        if st.session_state.location.strip() == "":

            st.warning("Enter Complaint Location")

            st.stop()

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

        with st.spinner("Generating AI Report..."):

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

        st.session_state.department = department

        st.session_state.ai_summary = ai_summary

        st.session_state.vision_summary = vision_summary

        change_page("submit")


# ============================================================
# SUBMIT PAGE
# ============================================================

elif st.session_state.page == "submit":

    st.markdown("""
<div class="hero">
<h1>✅ Review & Submit</h1>
<p>
Verify AI generated information before submitting the complaint.
</p>
</div>
""", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1])

    with c1:

        st.image(
            st.session_state.result_image,
            use_container_width=True
        )

    with c2:

        st.markdown("""
<div class="card">
<div class="sectionTitle">
Complaint Summary
</div>
""", unsafe_allow_html=True)

        st.write(
            f"**Issue :** {st.session_state.issue}"
        )

        st.write(
            f"**Department :** {st.session_state.department}"
        )

        st.write(
            f"**Location :** {st.session_state.location}"
        )

        st.write(
            f"**Citizen :** {st.session_state.citizen}"
        )

        st.write(
            f"**Phone :** {st.session_state.phone}"
        )

        st.metric(
            "Confidence",
            f"{st.session_state.confidence*100:.2f}%"
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 🤖 AI Complaint Summary")

    st.info(st.session_state.ai_summary)

    st.markdown("### 👁 Gemini Vision Report")

    st.info(st.session_state.vision_summary)

    if st.button(
        "📨 Submit Complaint",
        use_container_width=True
    ):

        complaint_id = f"UP-{random.randint(100000,999999)}"

        today = datetime.now().strftime("%d-%m-%Y %H:%M")

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

        """,

        (

            st.session_state.issue,

            st.session_state.confidence,

            st.session_state.location,

            st.session_state.image_path,

            "Pending",

            today,

            st.session_state.ai_summary

        )

        )

        conn.commit()

        st.balloons()

        st.success("Complaint Submitted Successfully")

        st.success(f"Complaint ID : {complaint_id}")

        if st.button(
            "🏠 Back To Dashboard",
            use_container_width=True
        ):

            st.session_state.detected = False

            change_page("dashboard")



# ============================================================
# MY COMPLAINTS
# ============================================================

elif st.session_state.page == "complaints":

    st.markdown("""
<div class="hero">
<h1>📂 My Complaints</h1>
<p>
View every complaint submitted through UrbanPulse AI.
</p>
</div>
""", unsafe_allow_html=True)

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

    rows = cursor.fetchall()

    if len(rows) == 0:

        st.info("No complaints found.")

    else:

        complaints = []

        for row in rows:

            complaints.append({

                "Complaint ID": row[0],

                "Issue": row[1],

                "Confidence": f"{row[2]*100:.2f}%",

                "Location": row[3],

                "Status": row[4],

                "Date": row[5]

            })

        df = pd.DataFrame(complaints)

        st.dataframe(

            df,

            use_container_width=True,

            hide_index=True

        )

        st.download_button(

            "⬇ Download CSV",

            df.to_csv(index=False),

            "UrbanPulse_Complaints.csv",

            "text/csv",

            use_container_width=True

        )


# ============================================================
# ANALYTICS
# ============================================================

elif st.session_state.page == "analytics":

    st.markdown("""
<div class="hero">
<h1>📊 Analytics Dashboard</h1>
<p>
Visual insights of complaints registered in UrbanPulse AI.
</p>
</div>
""", unsafe_allow_html=True)

    cursor.execute("""

    SELECT issue_type,

    COUNT(*)

    FROM complaints

    GROUP BY issue_type

    """)

    rows = cursor.fetchall()

    if len(rows) == 0:

        rows = [

            ("Pothole",12),

            ("Garbage",7)

        ]

    df = pd.DataFrame(

        rows,

        columns=[

            "Issue",

            "Count"

        ]

    )

    left,right=st.columns(2)

    with left:

        fig=px.bar(

            df,

            x="Issue",

            y="Count",

            color="Issue",

            text="Count"

        )

        fig.update_layout(

            template="plotly_white",

            height=430

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

    with right:

        fig=px.pie(

            df,

            names="Issue",

            values="Count",

            hole=.65

        )

        fig.update_layout(

            height=430

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

    cursor.execute("""

    SELECT

    status,

    COUNT(*)

    FROM complaints

    GROUP BY status

    """)

    rows = cursor.fetchall()

    if len(rows):

        status_df = pd.DataFrame(

            rows,

            columns=[

                "Status",

                "Total"

            ]

        )

        fig = px.bar(

            status_df,

            x="Status",

            y="Total",

            color="Status",

            text="Total"

        )

        fig.update_layout(

            template="plotly_white",

            height=420

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

elif st.session_state.page=="admin":

    if not st.session_state.admin:

        st.error("Unauthorized Access")

        st.stop()

    st.markdown("""
<div class="hero">
<h1>🛠 Admin Dashboard</h1>
<p>
Manage all complaints, monitor departments and update complaint status.
</p>
</div>
""",unsafe_allow_html=True)

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

    rows=cursor.fetchall()

    if len(rows)==0:

        st.info("No complaints available.")

    else:

        for row in rows:

            cid,issue,conf,location,status,date=row

            st.markdown(f"""

<div class="card">

### Complaint #{cid}

**Issue :** {issue}

**Confidence :** {conf*100:.2f}%

**Location :** {location}

**Status :** {status}

**Date :** {date}

</div>

""",unsafe_allow_html=True)

            a,b,c,d=st.columns(4)

            with a:

                if st.button("Approve",key=f"a{cid}"):

                    cursor.execute(

                        "UPDATE complaints SET status='Approved' WHERE id=?",

                        (cid,)

                    )

                    conn.commit()

                    st.rerun()

            with b:

                if st.button("Resolve",key=f"r{cid}"):

                    cursor.execute(

                        "UPDATE complaints SET status='Resolved' WHERE id=?",

                        (cid,)

                    )

                    conn.commit()

                    st.rerun()

            with c:

                if st.button("Reject",key=f"rej{cid}"):

                    cursor.execute(

                        "UPDATE complaints SET status='Rejected' WHERE id=?",

                        (cid,)

                    )

                    conn.commit()

                    st.rerun()

            with d:

                if st.button("Delete",key=f"d{cid}"):

                    cursor.execute(

                        "DELETE FROM complaints WHERE id=?",

                        (cid,)

                    )

                    conn.commit()

                    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown("""

<hr>

<div style="text-align:center;padding:25px;color:#6B7280;">

<h3>

🏙 UrbanPulse AI v2

</h3>

AI Powered Smart Urban Complaint Detection & Management Platform

<br><br>

YOLO • Gemini AI • NLP • SQLite • Streamlit

</div>

""",unsafe_allow_html=True)


