import streamlit as st
import pandas as pd
import os

USER_DB = "users.csv"

HARDCODED_ADMINS = [
    {"username": "admin",   "password": "1234",      "role": "admin"},
    {"username": "manager", "password": "sales123",  "role": "admin"},
]


def init_auth():
    """Initialize session state and seed the user database."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "role" not in st.session_state:
        st.session_state.role = None

    if not os.path.exists(USER_DB):
        df = pd.DataFrame(HARDCODED_ADMINS)
        df.to_csv(USER_DB, index=False)
    else:
        df = pd.read_csv(USER_DB)
        if "role" not in df.columns:
            df["role"] = "user"
            df.loc[df["username"].isin(["admin", "manager"]), "role"] = "admin"
            df.to_csv(USER_DB, index=False)


def get_users() -> pd.DataFrame:
    df = pd.read_csv(USER_DB)
    if "role" not in df.columns:
        df["role"] = "user"
    return df


def save_users(df: pd.DataFrame):
    df.to_csv(USER_DB, index=False)


def show_auth_page():
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
    }
    [data-testid="stHeader"] { background: transparent; }
    .auth-card {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        text-align: center;
        max-width: 500px;
        margin: auto;
    }
    .app-title { color: #1e3a8a; font-size: 28px; font-weight: 700; margin-bottom: 8px; }
    .app-subtitle { color: #6b7280; font-size: 16px; margin-bottom: 30px; }
    div.stButton > button {
        background-color: #1e3a8a !important;
        color: white !important;
        width: 100% !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        border: none !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 10px;
    }
    .main .block-container {
        display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        padding-top: 2rem;
    }
    .stTextInput input {
        border-radius: 8px !important;
        background-color: #f3f4f6 !important;
        border: 1px solid #e5e7eb !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="auth-card">
            <div style="font-size:50px;margin-bottom:20px">🏢</div>
            <div class="app-title">Intelligent Sales Analytics</div>
            <div class="app-subtitle">Welcome back! Please enter your details.</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        mode = st.radio(" ", ["🔑 Login", "📝 Register"],
                        horizontal=True, label_visibility="collapsed")
        st.divider()
        if "Login" in mode:
            _render_login()
        else:
            _render_register()


def _render_login():
    username = st.text_input("Username", placeholder="Enter your username", key="login_user_main")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass_main")
    if st.button("SIGN IN", key="login_btn"):
        users_df = get_users()
        match = users_df[
            (users_df["username"] == username) &
            (users_df["password"].astype(str) == str(password))
        ]
        if not match.empty:
            role = match.iloc[0]["role"]
            st.session_state.authenticated = True
            st.session_state.user = username
            st.session_state.role = role
            st.success(f"Welcome back, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password.")


def _render_register():
    new_user     = st.text_input("Username",          placeholder="Choose a username",     key="reg_user")
    new_pass     = st.text_input("Password",          type="password", placeholder="Choose a password",    key="reg_pass")
    confirm_pass = st.text_input("Confirm Password",  type="password", placeholder="Confirm your password", key="reg_conf")
    if st.button("CREATE ACCOUNT", key="reg_btn"):
        if not new_user or not new_pass:
            st.error("Please fill in all fields.")
        elif new_pass != confirm_pass:
            st.error("Passwords do not match.")
        elif new_user in ["admin", "manager"]:
            st.error("That username is reserved.")
        else:
            users_df = get_users()
            if new_user in users_df["username"].values:
                st.error("Username already exists.")
            else:
                new_row = pd.DataFrame([{"username": new_user, "password": str(new_pass), "role": "user"}])
                users_df = pd.concat([users_df, new_row], ignore_index=True)
                save_users(users_df)
                st.success("Account created! Please log in.")


def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def is_admin() -> bool:
    return st.session_state.get("role") == "admin"


def admin_get_all_users() -> pd.DataFrame:
    return get_users()


def admin_delete_user(username: str):
    users_df = get_users()
    users_df = users_df[users_df["username"] != username]
    save_users(users_df)


def admin_change_role(username: str, new_role: str):
    users_df = get_users()
    users_df.loc[users_df["username"] == username, "role"] = new_role
    save_users(users_df)
