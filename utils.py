import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


@st.cache_data
def load_and_clean_data(file_path: str) -> pd.DataFrame:
    """Load and process any dataset with the standard columns."""
    df = pd.read_csv(file_path)

    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)

    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    df.dropna(subset=["Order Date"], inplace=True)

    df["Month"]      = df["Order Date"].dt.month_name()
    df["Month_Num"]  = df["Order Date"].dt.month
    df["Year"]       = df["Order Date"].dt.year
    df["Quarter"]    = df["Order Date"].dt.quarter
    df["Month_Year"] = df["Order Date"].dt.to_period("M").astype(str)
    df["Profit Margin %"] = (df["Profit"] / df["Sales"]) * 100

    return df


def get_filtered_data(df, regions, categories, salespersons, date_range):
    filtered = df.copy()
    if regions:
        filtered = filtered[filtered["Region"].isin(regions)]
    if categories:
        filtered = filtered[filtered["Category"].isin(categories)]
    if salespersons:
        filtered = filtered[filtered["Customer Name"].isin(salespersons)]
    if date_range and len(date_range) == 2:
        s, e = date_range
        filtered = filtered[
            (filtered["Order Date"].dt.date >= s) &
            (filtered["Order Date"].dt.date <= e)
        ]
    elif date_range and len(date_range) == 1:
        filtered = filtered[filtered["Order Date"].dt.date >= date_range[0]]
    return filtered


# ─────────────────────────────────────────────────────────────────────────────
# Public overview
# ─────────────────────────────────────────────────────────────────────────────

def plot_public_overview(df):
    cat_sales = df.groupby("Category")["Sales"].sum().reset_index()
    fig = px.pie(
        cat_sales, values="Sales", names="Category",
        title="Quick Glance: Sales Distribution by Category",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Chart description
    top_cat  = cat_sales.loc[cat_sales["Sales"].idxmax(), "Category"]
    top_pct  = cat_sales["Sales"].max() / cat_sales["Sales"].sum() * 100
    st.info(
        f"📊 **Category Sales Overview:** The **{top_cat}** category dominates with "
        f"**{top_pct:.1f}%** of total sales revenue. "
        f"There are **{len(cat_sales)}** distinct categories contributing to the overall sales mix. "
        f"This snapshot gives a quick sense of where revenue is concentrated across the product portfolio."
    )


# ─────────────────────────────────────────────────────────────────────────────
# KPI Metrics
# ─────────────────────────────────────────────────────────────────────────────

def show_kpi_metrics(df):
    if df.empty:
        st.warning("⚠️ No data available for the selected filters.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col5, col6 = st.columns(2)

    total_revenue  = df["Sales"].sum()
    total_profit   = df["Profit"].sum()
    total_orders   = len(df)
    avg_order_val  = total_revenue / total_orders if total_orders > 0 else 0
    profit_margin  = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

    years  = sorted(df["Year"].unique())
    growth = 0.0
    if len(years) > 1:
        ty = df[df["Year"] == years[-1]]["Sales"].sum()
        ly = df[df["Year"] == years[-2]]["Sales"].sum()
        if ly > 0:
            growth = (ty - ly) / ly * 100

    col1.metric("Total Revenue",    f"₹{total_revenue:,.0f}")
    col2.metric("Total Profit",     f"₹{total_profit:,.0f}")
    col3.metric("Total Orders",     f"{total_orders:,}")
    col4.metric("Avg Order Value",  f"₹{avg_order_val:,.2f}")
    col5.metric("Profit Margin %",  f"{profit_margin:.2f}%")
    col6.metric("Sales Growth %",   f"{growth:.2f}%")


# ─────────────────────────────────────────────────────────────────────────────
# Time Series
# ─────────────────────────────────────────────────────────────────────────────

def plot_time_series(df):
    if df.empty:
        st.warning("No data available for time series analysis.")
        return
    st.subheader("📅 Monthly Sales & Profit Trend")

    monthly = (
        df.groupby("Month_Year")
        .agg({"Sales": "sum", "Profit": "sum"})
        .reset_index()
        .sort_values("Month_Year")
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["Month_Year"], y=monthly["Sales"],
        name="Revenue", mode="lines+markers",
        line=dict(color="royalblue", width=3), marker=dict(size=8),
    ))
    fig.add_trace(go.Scatter(
        x=monthly["Month_Year"], y=monthly["Profit"],
        name="Profit", mode="lines+markers",
        line=dict(color="steelblue", width=3, dash="dash"),
        marker=dict(size=8), yaxis="y2",
    ))
    fig.update_layout(
        title="Revenue vs Profit Monthly Progression",
        xaxis_title="Month-Year",
        yaxis=dict(title=dict(text="Revenue (INR)", font=dict(color="royalblue")),
                   tickfont=dict(color="royalblue")),
        yaxis2=dict(title=dict(text="Profit (INR)", font=dict(color="steelblue")),
                    tickfont=dict(color="steelblue"),
                    overlaying="y", side="right"),
        legend=dict(x=0, y=1.1, orientation="h"),
        hovermode="x unified", template="plotly_white",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Chart description ──────────────────────────────────────────────────
    peak_month  = monthly.loc[monthly["Sales"].idxmax(), "Month_Year"]
    trough_month = monthly.loc[monthly["Sales"].idxmin(), "Month_Year"]
    first_sales  = monthly["Sales"].iloc[0]
    last_sales   = monthly["Sales"].iloc[-1]
    trend_dir    = "upward 📈" if last_sales >= first_sales else "downward 📉"
    avg_monthly  = monthly["Sales"].mean()
    st.info(
        f"📅 **Monthly Trend Insight:** Sales peaked in **{peak_month}** "
        f"(₹{monthly['Sales'].max():,.0f}) and hit their lowest point in **{trough_month}** "
        f"(₹{monthly['Sales'].min():,.0f}). "
        f"The overall trajectory is **{trend_dir}** with an average monthly revenue of "
        f"₹{avg_monthly:,.0f}. "
        f"Profit generally mirrors sales movement, though margins may compress during high-discount periods."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Regional Analysis
# ─────────────────────────────────────────────────────────────────────────────

def plot_regional_analysis(df):
    if df.empty:
        st.warning("No data available for regional analysis.")
        return
    st.subheader("📍 Regional Performance")

    reg = df.groupby("Region").agg({"Sales": "sum", "Profit": "sum"}).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(reg, x="Region", y="Sales", title="Revenue by Region",
                      labels={"Sales": "Total Revenue"},
                      color="Sales", color_continuous_scale="Blues")
        st.plotly_chart(fig1, use_container_width=True)

        # Description – revenue
        best_r  = reg.loc[reg["Sales"].idxmax(), "Region"]
        worst_r = reg.loc[reg["Sales"].idxmin(), "Region"]
        st.info(
            f"📍 **Regional Revenue:** **{best_r}** leads all regions in total revenue "
            f"(₹{reg['Sales'].max():,.0f}), while **{worst_r}** records the lowest "
            f"(₹{reg['Sales'].min():,.0f}). "
            f"The gap between the top and bottom regions is "
            f"₹{reg['Sales'].max() - reg['Sales'].min():,.0f}, "
            f"suggesting opportunities to develop weaker markets."
        )

    with col2:
        fig2 = px.bar(reg, x="Region", y="Profit", title="Profit by Region",
                      labels={"Profit": "Total Profit"},
                      color="Profit", color_continuous_scale="GnBu")
        st.plotly_chart(fig2, use_container_width=True)

        # Description – profit
        best_rp  = reg.loc[reg["Profit"].idxmax(), "Region"]
        worst_rp = reg.loc[reg["Profit"].idxmin(), "Region"]
        loss_regions = reg[reg["Profit"] < 0]["Region"].tolist()
        loss_note = (f" ⚠️ **{', '.join(loss_regions)}** recorded net losses."
                     if loss_regions else " All regions are profitable.")
        st.info(
            f"💰 **Regional Profitability:** **{best_rp}** is the most profitable region "
            f"(₹{reg['Profit'].max():,.0f}), followed by others.{loss_note}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Category Analysis
# ─────────────────────────────────────────────────────────────────────────────

def plot_category_analysis(df):
    if df.empty:
        st.warning("No data available for category analysis.")
        return
    st.subheader("📂 Category Analysis")

    cat = df.groupby("Category").agg({"Sales": "sum", "Profit": "sum"}).reset_index()

    fig = px.bar(cat, x="Category", y=["Sales", "Profit"],
                 title="Sales vs Profit by Category", barmode="group",
                 color_discrete_sequence=["royalblue", "steelblue"])
    st.plotly_chart(fig, use_container_width=True)

    # Sub-category sunburst
    sub_cat = df.groupby(["Category", "Sub Category"])["Sales"].sum().reset_index()
    fig_sun = px.sunburst(sub_cat, path=["Category", "Sub Category"], values="Sales",
                          title="Detailed Category Hierarchy")
    st.plotly_chart(fig_sun, use_container_width=True)

    # ── Chart description ──────────────────────────────────────────────────
    top_cat  = cat.loc[cat["Sales"].idxmax(), "Category"]
    top_sub  = sub_cat.loc[sub_cat["Sales"].idxmax(), "Sub Category"]
    top_sub_cat = sub_cat.loc[sub_cat["Sales"].idxmax(), "Category"]
    st.info(
        f"📂 **Category Insights:** **{top_cat}** is the highest-grossing category overall. "
        f"Drilling further, **{top_sub}** (under *{top_sub_cat}*) is the best-performing sub-category "
        f"with ₹{sub_cat['Sales'].max():,.0f} in sales. "
        f"The sunburst chart reveals the nested contribution of each sub-category, "
        f"helping identify which product lines drive the most revenue within each group."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Salesperson Analysis
# ─────────────────────────────────────────────────────────────────────────────

def plot_salesperson_analysis(df):
    if df.empty:
        st.warning("No data available for salesperson analysis.")
        return
    st.subheader("👤 Salesperson Performance")

    sp = df.groupby("Customer Name").agg({"Sales": "sum", "Profit": "sum"}).reset_index()
    top5    = sp.nlargest(5, "Sales")
    bottom5 = sp.nsmallest(5, "Sales")

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Top 5 Performers (Sales)**")
        st.dataframe(top5, hide_index=True)
    with col2:
        st.write("**Bottom 5 Performers (Sales)**")
        st.dataframe(bottom5, hide_index=True)

    fig = px.scatter(sp, x="Sales", y="Profit", hover_name="Customer Name",
                     size="Sales", color="Profit",
                     title="Profit vs Sales per Customer")
    st.plotly_chart(fig, use_container_width=True)

    # ── Chart description ──────────────────────────────────────────────────
    top_person    = top5.iloc[0]["Customer Name"]
    top_sales_val = top5.iloc[0]["Sales"]
    bot_person    = bottom5.iloc[0]["Customer Name"]
    bot_sales_val = bottom5.iloc[0]["Sales"]
    st.info(
        f"👤 **Salesperson Insights:** **{top_person}** leads with ₹{top_sales_val:,.0f} in total sales, "
        f"while **{bot_person}** has the lowest contribution at ₹{bot_sales_val:,.0f}. "
        f"The scatter plot maps each customer's sales against profit — customers in the upper-right "
        f"quadrant are the most valuable, combining high revenue with strong profitability."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Profitability Analysis
# ─────────────────────────────────────────────────────────────────────────────

def plot_profitability_analysis(df):
    if df.empty:
        st.warning("No data available for profitability analysis.")
        return
    st.subheader("📈 Profitability Analysis")

    median_sales  = df["Sales"].median()
    median_profit = df["Profit"].median()
    alert_df      = df[(df["Sales"] > median_sales) & (df["Profit"] < median_profit)]

    col1, col2 = st.columns(2)
    with col1:
        fig = px.box(df, x="Category", y="Profit Margin %",
                     title="Profit Margin Distribution by Category")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.write("**Alert: High Revenue – Low Profit Orders**")
        st.dataframe(alert_df[["Order ID", "Category", "Sales", "Profit"]].head(10),
                     hide_index=True)

    # ── Chart description ──────────────────────────────────────────────────
    overall_avg_margin = df["Profit Margin %"].mean()
    top_margin_cat = (df.groupby("Category")["Profit Margin %"].mean()
                       .idxmax())
    st.info(
        f"📈 **Profitability Summary:** The overall average profit margin is "
        f"**{overall_avg_margin:.1f}%**. "
        f"**{top_margin_cat}** has the healthiest average margin across categories. "
        f"There are **{len(alert_df)}** orders with above-median revenue but below-median profit — "
        f"these are prime candidates for cost review, discount rationalisation, or pricing adjustments."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Discount Impact
# ─────────────────────────────────────────────────────────────────────────────

def plot_discount_impact(df):
    if df.empty:
        st.warning("No data available for discount impact study.")
        return
    st.subheader("🏷️ Discount Impact Study")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.scatter(df, x="Discount", y="Profit", color="Category",
                         size="Sales", hover_data=["Sub Category", "City"],
                         title="Profit vs Discount Intensity",
                         labels={"Discount": "Discount Rate", "Profit": "Profit (INR)"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_copy = df.copy()
        df_copy["Discount_Bin"] = pd.cut(
            df_copy["Discount"],
            bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5],
            labels=["0–10%", "10–20%", "20–30%", "30–40%", "40%+"],
        )
        fig2 = px.box(df_copy, x="Discount_Bin", y="Profit", color="Discount_Bin",
                      title="Profitability Distribution by Discount Tier",
                      labels={"Discount_Bin": "Discount Bracket"})
        st.plotly_chart(fig2, use_container_width=True)

    # ── Chart description ──────────────────────────────────────────────────
    corr = df["Discount"].corr(df["Profit"])
    corr_word = "strong negative" if corr < -0.4 else ("moderate negative" if corr < -0.1 else "weak/no")
    high_disc  = df[df["Discount"] >= 0.3]
    avg_profit_high = high_disc["Profit"].mean() if not high_disc.empty else 0
    st.info(
        f"🏷️ **Discount Impact:** There is a **{corr_word} correlation** (r = {corr:.2f}) "
        f"between discount rate and profit. "
        f"Orders with discounts ≥ 30% have an average profit of ₹{avg_profit_high:,.0f}, "
        f"suggesting that deep discounts often erode margins significantly. "
        f"The box plot highlights how profit variability increases at higher discount tiers, "
        f"pointing to inconsistent pricing strategy for heavily discounted products."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Correlation Analysis
# ─────────────────────────────────────────────────────────────────────────────

def plot_correlation_analysis(df):
    if df.empty:
        st.warning("No data available for correlation analysis.")
        return
    st.subheader("🔗 Interactive Correlation Analysis")

    corr_cols = ["Sales", "Profit", "Discount", "Profit Margin %"]
    corr_matrix = df[corr_cols].corr()

    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                    color_continuous_scale="Blues",
                    title="Correlation Matrix Heatmap (Interactive)")
    st.plotly_chart(fig, use_container_width=True)

    # ── Chart description ──────────────────────────────────────────────────
    # Find strongest positive & negative pairs (excluding diagonal)
    cm = corr_matrix.copy()
    np.fill_diagonal(cm.values, np.nan)
    stacked = cm.stack()
    strongest_pos = stacked.idxmax()
    strongest_neg = stacked.idxmin()
    st.info(
        f"🔗 **Correlation Insights:** The strongest **positive** correlation is between "
        f"**{strongest_pos[0]}** and **{strongest_pos[1]}** "
        f"(r = {stacked[strongest_pos]:.2f}), meaning they tend to move together. "
        f"The strongest **negative** correlation is between "
        f"**{strongest_neg[0]}** and **{strongest_neg[1]}** "
        f"(r = {stacked[strongest_neg]:.2f}), indicating an inverse relationship. "
        f"These insights can guide where to focus operational improvements."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Performance Ranking
# ─────────────────────────────────────────────────────────────────────────────

def generate_performance_ranking(df):
    st.subheader("🏆 Performance Ranking")

    tab1, tab2, tab3 = st.tabs(["Regions", "Categories", "Salespersons"])

    with tab1:
        r = df.groupby("Region")["Sales"].sum().sort_values(ascending=False).reset_index()
        r["Rank"] = range(1, len(r) + 1)
        st.table(r)

    with tab2:
        r = df.groupby("Category")["Sales"].sum().sort_values(ascending=False).reset_index()
        r["Rank"] = range(1, len(r) + 1)
        st.table(r)

    with tab3:
        r = df.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False).reset_index()
        r["Rank"] = range(1, len(r) + 1)
        st.dataframe(r.head(10))


# ─────────────────────────────────────────────────────────────────────────────
# Reports
# ─────────────────────────────────────────────────────────────────────────────

def show_reports(df, type="Monthly"):
    st.subheader(f"📑 {type} Summary Report")

    if type == "Monthly":
        grp = df.groupby(["Year", "Month"])
        report = grp["Sales"].sum().to_frame("Sales")
        report["Profit"]       = grp["Profit"].sum()
        report["Orders"]       = grp.size()
        report["Avg Discount"] = grp["Discount"].mean()
        report = report.reset_index()

    elif type == "Region-wise":
        grp = df.groupby("Region")
        report = grp["Sales"].sum().to_frame("Sales")
        report["Profit"]       = grp["Profit"].sum()
        report["Orders"]       = grp.size()
        report["Avg Discount"] = grp["Discount"].mean()
        report = report.reset_index()

    elif type == "Executive Summary":
        grp_cat = df.groupby("Category")
        cat_s = grp_cat["Sales"].sum().to_frame("Sales")
        cat_s["Profit"] = grp_cat["Profit"].sum()
        cat_s["Orders"] = grp_cat.size()
        cat_s = cat_s.reset_index()

        grp_reg = df.groupby("Region")
        reg_s = grp_reg["Sales"].sum().to_frame("Sales")
        reg_s["Profit"] = grp_reg["Profit"].sum()
        reg_s["Orders"] = grp_reg.size()
        reg_s = reg_s.reset_index()

        st.write("### 🏆 Category-wise Snapshot")
        st.dataframe(cat_s, use_container_width=True)
        st.write("### 📍 Region-wise Snapshot")
        st.dataframe(reg_s, use_container_width=True)
        report = pd.concat([cat_s.assign(Type="Category"),
                            reg_s.assign(Type="Region")], ignore_index=True)

    else:  # Category-wise
        grp = df.groupby("Category")
        report = grp["Sales"].sum().to_frame("Sales")
        report["Profit"]      = grp["Profit"].sum()
        report["Orders"]      = grp.size()
        report["Avg Margin %"] = grp["Profit Margin %"].mean()
        report = report.reset_index()

    st.dataframe(report, use_container_width=True)
    st.download_button("📥 Download CSV", report.to_csv(index=False),
                       f"{type}_report.csv", "text/csv")
