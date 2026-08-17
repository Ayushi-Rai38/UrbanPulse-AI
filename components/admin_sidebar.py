import streamlit as st


def render_admin_sidebar():

    with st.sidebar:

        # ==============================
        # BRAND
        # ==============================

        st.markdown(
            """
            <div style="
                padding: 5px 4px 18px;
                color: #202733;
                font-size: 17px;
                font-weight: 850;
                letter-spacing: -0.3px;
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
                margin: 2px 0 8px;
            ">
                Admin Console
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ==============================
        # DASHBOARD
        # ==============================

        if st.button(
            "Dashboard",
            key="admin_dashboard",
            use_container_width=True,
        ):
            st.switch_page("pages/dashboard.py")

        # ==============================
        # COMPLAINTS
        # ==============================

        if st.button(
            "Complaints",
            key="admin_complaints",
            use_container_width=True,
        ):
            st.switch_page("pages/admin_complaints.py")

        # ==============================
        # ANALYTICS
        # ==============================

        if st.button(
            "Analytics",
            key="admin_analytics",
            use_container_width=True,
        ):
            st.switch_page("pages/dashboard.py")

        # ==============================
        # REPORT
        # ==============================

        

        # ==============================
        # DIVIDER
        # ==============================

        st.markdown(
            """
            <div style="
                border-top: 1px solid #d9d9df;
                margin: 16px 0 14px;
            "></div>
            """,
            unsafe_allow_html=True,
        )

        # ==============================
        # ADMIN ACCOUNT
        # ==============================

        st.markdown(
            f"""
            <div style="
                background: #e8e8ed;
                border: 1px solid #d8d8de;
                border-radius: 6px;
                padding: 12px;
                margin-top: 2px;
            ">

            <div style="
                color: #777b82;
                font-size: 8px;
                font-weight: 800;
                letter-spacing: 1.5px;
                margin-bottom: 5px;
            ">
                ADMIN
            </div>

            <div style="
                color: #202733;
                font-size: 13px;
                font-weight: 750;
            ">
                {st.session_state.get("user_name", "Administrator")}
            </div>

            <div style="
                color: #70757c;
                font-size: 9px;
                margin-top: 3px;
                overflow-wrap: anywhere;
            ">
                {st.session_state.get("user_email", "")}
            </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # ==============================
        # LOGOUT
        # ==============================

        if st.button(
            "Logout",
            key="admin_logout",
            use_container_width=True,
        ):

            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.rerun()