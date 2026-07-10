import streamlit as st

st.set_page_config(
    page_title="UrbanPulse AI",
    page_icon="🚦",
    layout="centered"
)

st.title("🚦 UrbanPulse AI")
st.subheader("Smart Urban Complaint Detection System")

st.write(
    "AI Powered Detection • Verification • Complaint Management"
)

st.divider()

col1, col2 = st.columns(2)

with col1:

    if st.button("👤 Citizen Portal", use_container_width=True):

        st.switch_page("app.py")

with col2:

    if st.button("🔐 Admin Login", use_container_width=True):

        st.switch_page("pages/login.py")