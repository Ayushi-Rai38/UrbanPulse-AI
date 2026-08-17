import streamlit as st


def render_sidebar():

    # ============================================================
    # SIDEBAR MASTER CSS
    # ============================================================

    st.markdown(
        """
        <style>

        /* -------------------------------------------------------
           SIDEBAR CONTAINER
        ------------------------------------------------------- */

        section[data-testid="stSidebar"] {
            background: #f1f1f6 !important;
            border-right: 1px solid #d9d9df !important;
        }

        section[data-testid="stSidebar"] > div {
            padding: 2rem 1.25rem 1.25rem 1.25rem !important;
        }

        /* -------------------------------------------------------
           SIDEBAR CONTENT
        ------------------------------------------------------- */

        [data-testid="stSidebarContent"] {
            background: #f1f1f6 !important;
        }

        /* -------------------------------------------------------
           ALL SIDEBAR BUTTONS
        ------------------------------------------------------- */

        section[data-testid="stSidebar"] div.stButton > button {
            width: 100% !important;

            min-height: 48px !important;

            background: transparent !important;

            color: #202733 !important;

            border: 1px solid transparent !important;

            border-radius: 5px !important;

            font-size: 15px !important;

            font-weight: 500 !important;

            text-align: center !important;

            box-shadow: none !important;

            transition: all 0.15s ease !important;

            margin-bottom: 8px !important;
        }

        /* Hover */

        section[data-testid="stSidebar"] div.stButton > button:hover {
            background: #e5e5eb !important;

            color: #172033 !important;

            border: 1px solid #d1d1d8 !important;

            box-shadow: none !important;

            transform: none !important;
        }

        /* Focus */

        section[data-testid="stSidebar"] div.stButton > button:focus {
            background: #ffffff !important;

            color: #172033 !important;

            border: 1px solid #2d59d1 !important;

            box-shadow: none !important;
        }

        /* -------------------------------------------------------
           LOGOUT BUTTON
        ------------------------------------------------------- */

        section[data-testid="stSidebar"] div.stButton > button:last-child {
            margin-top: 8px !important;
        }

        section[data-testid="stSidebar"] div.stButton > button {
            transition: 
            background 0.2s ease,
            border 0.2s ease,
            transform 0.2s ease !important;

        section[data-testid="stSidebar"] div.stButton > button:hover {
            background: #e5e5eb !important;
            border-color: #d1d1d8 !important;
            transform: translateX(2px) !important;
}
}

        </style>
        """,
        unsafe_allow_html=True,
    )

    # ============================================================
    # SIDEBAR
    # ============================================================

    with st.sidebar:

        # ========================================================
        # BRAND
        # ========================================================

        st.markdown(
            """
            <div style="
                padding: 5px 4px 25px;
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

        # ========================================================
        # NAVIGATION LABEL
        # ========================================================

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
                Navigation
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ========================================================
        # HOME
        # ========================================================

        if st.button(
            "Home",
            key="side_home",
            use_container_width=True,
        ):
            st.switch_page("app.py")

        # ========================================================
        # REPORT ISSUE
        # ========================================================

        if st.button(
            "Report Issue",
            key="side_report",
            use_container_width=True,
        ):
            st.switch_page("pages/report.py")

        # ========================================================
        # MY COMPLAINTS
        # ========================================================

        if st.button(
            "My Complaints",
            key="side_complaints",
            use_container_width=True,
        ):
            st.switch_page("pages/my_complaints.py")

        # ========================================================
        # ADMIN DASHBOARD
        # ========================================================

        if st.session_state.get("role") == "admin":

            if st.button(
                "Admin Dashboard",
                key="side_dashboard",
                use_container_width=True,
            ):
                st.switch_page("pages/dashboard.py")

        # ========================================================
        # ABOUT
        # ========================================================

        if st.button(
            "About",
            key="side_about",
            use_container_width=True,
        ):
            st.switch_page("pages/about.py")

        # ========================================================
        # DIVIDER
        # ========================================================

        st.markdown(
            """
            <div style="
                border-top: 1px solid #d1d1d8;
                margin: 18px 0 16px;
            "></div>
            """,
            unsafe_allow_html=True,
        )

        # ========================================================
        # ACCOUNT
        # ========================================================

        if st.session_state.get("logged_in", False):

            user_name = st.session_state.get(
                "user_name",
                "User"
            )

            user_email = st.session_state.get(
                "user_email",
                ""
            )

            role = st.session_state.get(
                "role",
                "user"
            )

            role_label = (
                "ADMIN"
                if role == "admin"
                else "USER"
            )

            # ----------------------------------------------------
            # USER CARD
            # ----------------------------------------------------

            st.markdown(
                f"""
                <div style="
                    background: #e7e7ed;
                    border: 1px solid #d2d2d9;
                    border-radius: 6px;
                    padding: 14px;
                    margin-top: 2px;
                    margin-bottom: 12px;
                ">

                <div style="
                    color: #777b82;
                    font-size: 8px;
                    font-weight: 800;
                    letter-spacing: 1.5px;
                    margin-bottom: 7px;
                ">
                    {role_label}
                </div>

                <div style="
                    color: #202733;
                    font-size: 14px;
                    font-weight: 750;
                ">
                    {user_name}
                </div>

                <div style="
                    color: #70757c;
                    font-size: 9px;
                    margin-top: 4px;
                    overflow-wrap: anywhere;
                ">
                    {user_email}
                </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            # ----------------------------------------------------
            # LOGOUT
            # ----------------------------------------------------

            if st.button(
                "Logout",
                key="side_logout",
                use_container_width=True,
            ):

                # Clear login-related session state
                for key in [
                    "logged_in",
                    "user_id",
                    "user_name",
                    "user_email",
                    "role",
                ]:
                    if key in st.session_state:
                        del st.session_state[key]

                st.switch_page("pages/login.py")

        else:

            # ----------------------------------------------------
            # NOT LOGGED IN
            # ----------------------------------------------------

            st.markdown(
                """
                <div style="
                    color: #73777d;
                    font-size: 10px;
                    line-height: 1.5;
                    padding: 4px 2px;
                ">
                    Sign in to submit complaints<br>
                    and track your reports.
                </div>
                """,
                unsafe_allow_html=True,
            )