import streamlit as st
from database.database import get_connection


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="UrbanPulse AI | Login",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(
    """
    <style>

    /* Hide Streamlit default navigation */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Hide sidebar completely on login page */
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HIDE ONLY DEFAULT STREAMLIT PAGE NAVIGATION
# KEEP SIDEBAR
# ============================================================

st.markdown(
    """
    <style>

    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "user_role" not in st.session_state:
    st.session_state.user_role = None


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
        max-width: 1100px;
        padding-top: 5rem;
        padding-bottom: 4rem;
    }


    /* LOGIN CARD */

    .login-card {
        background: #ffffff;
        border: 1px solid #deded9;
        border-radius: 8px;
        padding: 42px;
        max-width: 520px;
        margin: auto;
    }


    .login-label {
        color: #73777d;
        font-size: 9px;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 850;
    }


    .login-title {
        color: #172033;
        font-size: 38px;
        font-weight: 850;
        letter-spacing: -1.5px;
        margin-top: 10px;
    }


    .login-description {
        color: #62686e;
        font-size: 13px;
        line-height: 1.6;
        margin: 10px 0 25px;
    }


    /* INPUTS */

    div[data-baseweb="input"] {
        background: #ffffff !important;
    }


    input {
        color: #172033 !important;
    }


    /* BUTTON */

    div.stButton > button {
        background: #ffffff !important;
        color: #172033 !important;
        border: 1px solid #2d59d1 !important;
        border-radius: 4px !important;
        min-height: 44px !important;
        font-weight: 750 !important;
    }


    div.stButton > button:hover {
        background: #f7f8ff !important;
        color: #2148bb !important;
        border-color: #2148bb !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOGIN UI
# ============================================================

left, center, right = st.columns(
    [1, 2, 1]
)


with center:

    # --------------------------------------------------------
    # LOGIN CARD
    # --------------------------------------------------------

    st.html(
        """
        <div class="login-card">

            <div class="login-label">
                URBANPULSE AI
            </div>

            <div class="login-title">
                Welcome back.
            </div>

            <div class="login-description">
                Sign in to report urban issues, track your
                complaints, or manage civic reports.
            </div>

        </div>
        """
    )


    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    email = st.text_input(
        "Email",
        placeholder="Enter your email",
        key="login_email",
    )


    # --------------------------------------------------------
    # PASSWORD
    # --------------------------------------------------------

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password",
    )


    # --------------------------------------------------------
    # SIGN IN
    # --------------------------------------------------------

    if st.button(
        "Sign In",
        key="login_button",
        use_container_width=True
    ):

        # Check empty fields

        if not email or not password:

            st.warning(
                "Please enter your email and password."
            )

        else:

            # Connect to database

            conn = get_connection()
            cursor = conn.cursor()


            # Find user

            cursor.execute(
                """
                SELECT id, name, email, role
                FROM users
                WHERE email = ? AND password = ?
                """,
                (email.strip(), password)
            )


            user = cursor.fetchone()

            conn.close()


            # ------------------------------------------------
            # USER FOUND
            # ------------------------------------------------

            if user:

                st.session_state.logged_in = True

                st.session_state.user_id = user[0]

                st.session_state.user_name = user[1]

                st.session_state.user_email = user[2]

                st.session_state.user_role = user[3]


                # ADMIN

                if user[3] == "admin":

                    st.success(
                        f"Welcome, {user[1]}!"
                    )

                    st.switch_page(
                        "pages/dashboard.py"
                    )


                # NORMAL USER

                else:

                    st.success(
                        f"Welcome, {user[1]}!"
                    )

                    st.switch_page(
                        "pages/report.py"
                    )


            # ------------------------------------------------
            # USER NOT FOUND
            # ------------------------------------------------

            else:

                st.error(
                    "Invalid email or password."
                )