import streamlit as st
import pandas as pd
from datetime import datetime
import auth
import utils

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Intelligent Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    section[data-testid="stSidebar"] { background-color: #f0f9ff; }
    h1, h2, h3 { color: #1e3a8a !important; }
    [data-testid="stMetricValue"] { color: #1e40af; }
    .stButton>button { background-color: #1e40af; color: white; }
    .main { background-color: #f8fafc; }

    /* Role badge */
    .role-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .role-admin { background-color: #fef3c7; color: #92400e; }
    .role-user  { background-color: #dbeafe; color: #1e3a8a; }
</style>
""", unsafe_allow_html=True)

# ── Init Auth ─────────────────────────────────────────────────────────────────
auth.init_auth()

# ── Dataset definitions ───────────────────────────────────────────────────────
DATASETS = {
    "🛒 Supermarket Sales":     "Supermart Grocery Sales - Retail Analytics Dataset.csv",
    "💻 Electronics Store Sales": "Electronics Store Sales - Retail Analytics Dataset.csv",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🚀 Sales Portal")

if not auth.is_authenticated():
    menu_selection = "🔐 Auth"
else:
    role  = st.session_state.get("role", "user")
    badge = "role-admin" if role == "admin" else "role-user"
    st.sidebar.markdown(
        f"Logged in as **{st.session_state.user}** &nbsp;"
        f'<span class="role-badge {badge}">{role.upper()}</span>',
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Logout ⚙"):
        auth.logout()

    st.sidebar.divider()

    # ── Dataset selector ──────────────────────────────────────────────────
    selected_dataset_label = st.sidebar.selectbox(
        "📂 Dataset", list(DATASETS.keys()), key="dataset_selector"
    )
    selected_dataset_file = DATASETS[selected_dataset_label]

    st.sidebar.divider()

    # ── Role-based navigation ─────────────────────────────────────────────
    if auth.is_admin():
        menu_options = [
            "🏠 Home",
            "📊 Dashboard Overview",
            "📈 Advanced Analytics",
            "📑 Reports",
            "👥 User Management",
            "📂 Dataset Overview",
            "📖 About Project",
        ]
    else:
        menu_options = [
            "🏠 Home",
            "📊 Dashboard Overview",
            "📈 Advanced Analytics",
            "📑 Reports",
            "📂 Dataset Overview",
            "📖 About Project",
        ]

    menu_selection = st.sidebar.selectbox("Navigation", menu_options)

# ── Load Data ─────────────────────────────────────────────────────────────────
if auth.is_authenticated():
    try:
        df = utils.load_and_clean_data(selected_dataset_file)
    except Exception as e:
        st.error(f"Error loading dataset **{selected_dataset_label}**: {e}")
        st.stop()
else:
    # Load default dataset for the public home page
    try:
        df = utils.load_and_clean_data("Supermart Grocery Sales - Retail Analytics Dataset.csv")
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()

filtered_df = df.copy()

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not auth.is_authenticated():
    auth.show_auth_page()
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Pages
# ─────────────────────────────────────────────────────────────────────────────

if menu_selection == "🏠 Home":
    st.title("🌟 Intelligent Sales Analytics Dashboard")
    st.markdown(f"""
    ### Unveiling Trends and Key Metrics for Business Growth
    Welcome to the **Intelligent Sales Analytics Dashboard**.
    Currently viewing: **{selected_dataset_label}**

    #### ✨ Key Features:
    - **Interactive KPIs**: Real-time sales, profit, and growth metrics.
    - **Time Series Analysis**: Understand seasonal trends and patterns.
    - **Regional Breakdown**: Identify top-performing geographic areas.
    - **Advanced Analytics**: Profitability studies and discount impact.
    - **Custom Reports**: Generate and export targeted business reports.
    {"- **User Management**: Admin-only tools for managing accounts." if auth.is_admin() else ""}
    """)
    # st.image(
    #     "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80",
    #     caption="Sample Analytics View",
    # )
    st.divider()
    st.subheader("📊 Instant Insights")
    utils.plot_public_overview(df)


elif menu_selection == "📖 About Project":
    st.title("📖 About the Project")
    st.info(f"""
    **Objective:** Build a Python-based sales analytics dashboard for academic/portfolio purposes.

    **Tech Stack:**
    - **Python**: Core logic
    - **Streamlit**: Web Framework
    - **Pandas / NumPy**: Data Processing
    - **Plotly**: Interactive Data Visualization

    **Datasets:**
    - 🛒 Supermart Grocery Sales – Indian retail grocery transactions
    - 💻 Electronics Store Sales – Indian electronics retail (~5 000 synthetic records)

    **Current dataset:** {selected_dataset_label}
    """)


elif menu_selection == "📂 Dataset Overview":
    st.title("📂 Dataset Overview")
    st.caption(f"Viewing: **{selected_dataset_label}**")
    tab1, tab2 = st.tabs(["Data Preview", "Statistics"])
    with tab1:
        st.dataframe(df.head(100))
    with tab2:
        st.write(df.describe())


# ── Admin-only: User Management ───────────────────────────────────────────────
elif menu_selection == "👥 User Management":
    if not auth.is_admin():
        st.error("🚫 Access denied. This page is for administrators only.")
        st.stop()

    st.title("👥 User Management")
    st.caption("Manage registered user accounts.")

    users_df = auth.admin_get_all_users()

    # ── View all users ────────────────────────────────────────────────────
    st.subheader("📋 All Users")
    display_df = users_df[["username", "role"]].copy()
    display_df.index = range(1, len(display_df) + 1)
    st.dataframe(display_df, use_container_width=True)

    st.divider()
    col1, col2 = st.columns(2)

    # ── Delete user ───────────────────────────────────────────────────────
    with col1:
        st.subheader("🗑️ Delete User")
        deletable = users_df[~users_df["username"].isin(["admin", "manager"])]["username"].tolist()
        if deletable:
            del_user = st.selectbox("Select user to delete", deletable, key="del_user")
            if st.button("Delete User", key="do_delete"):
                if del_user == st.session_state.user:
                    st.error("You cannot delete your own account.")
                else:
                    auth.admin_delete_user(del_user)
                    st.success(f"User **{del_user}** deleted.")
                    st.rerun()
        else:
            st.info("No deletable users found.")

    # ── Change role ───────────────────────────────────────────────────────
    with col2:
        st.subheader("🔄 Change User Role")
        changeable = users_df[users_df["username"] != st.session_state.user]["username"].tolist()
        if changeable:
            role_user    = st.selectbox("Select user", changeable, key="role_user")
            current_role = users_df.loc[users_df["username"] == role_user, "role"].values[0]
            new_role     = st.selectbox(
                "New role",
                ["admin", "user"],
                index=0 if current_role == "admin" else 1,
                key="new_role",
            )
            if st.button("Update Role", key="do_role"):
                auth.admin_change_role(role_user, new_role)
                st.success(f"**{role_user}**'s role updated to **{new_role}**.")
                st.rerun()
        else:
            st.info("No other users to modify.")


# ── Private analytical pages ──────────────────────────────────────────────────
elif menu_selection in ["📊 Dashboard Overview", "📈 Advanced Analytics", "📑 Reports"]:

    with st.expander("🎯 Global Filter Panel", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            m_date = df["Order Date"].min().date()
            x_date = df["Order Date"].max().date()
            d_range = st.date_input("Date Range", [m_date, x_date])
        with c2:
            s_regions = st.multiselect("Regions", sorted(df["Region"].unique()))
        with c3:
            s_cats = st.multiselect("Categories", sorted(df["Category"].unique()))
        s_sp = st.multiselect("Salespersons", sorted(df["Customer Name"].unique()))

    filtered_df = utils.get_filtered_data(df, s_regions, s_cats, s_sp, d_range)

    # ── Dataset badge ─────────────────────────────────────────────────────
    st.caption(f"📂 Dataset: **{selected_dataset_label}** — {len(filtered_df):,} rows after filters")

    if menu_selection == "📊 Dashboard Overview":
        st.title("📊 Sales Dashboard Overview")
        utils.show_kpi_metrics(filtered_df)
        tab1, tab2, tab3 = st.tabs(["Time Analysis", "Regional Analysis", "Category Analysis"])
        with tab1:
            utils.plot_time_series(filtered_df)
        with tab2:
            utils.plot_regional_analysis(filtered_df)
        with tab3:
            utils.plot_category_analysis(filtered_df)
            utils.plot_salesperson_analysis(filtered_df)

    elif menu_selection == "📈 Advanced Analytics":
        st.title("📈 Advanced Business Analytics")
        utils.plot_profitability_analysis(filtered_df)
        utils.plot_discount_impact(filtered_df)
        utils.plot_correlation_analysis(filtered_df)
        utils.generate_performance_ranking(filtered_df)

    elif menu_selection == "📑 Reports":
        st.title("📑 Business Reports")
        report_type = st.radio(
            "Select Report Type",
            ["Monthly", "Region-wise", "Category-wise", "Executive Summary"],
            horizontal=True,
        )
        utils.show_reports(filtered_df, type=report_type)


# ── Footer ────────────────────────────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.caption("© 2026 Intelligent Sales Analytics | Dashboard v2.0")
