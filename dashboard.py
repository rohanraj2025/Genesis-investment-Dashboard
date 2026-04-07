import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="GENESIS INVESTMENTS DASHBOARD",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: #f4f7fb;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 96%;
}
.main-title-box {
    background: linear-gradient(90deg, #0a3d91, #1f66d1);
    padding: 28px 32px;
    border-radius: 22px;
    color: white;
    box-shadow: 0 8px 24px rgba(16, 59, 120, 0.22);
    margin-bottom: 18px;
}
.main-title {
    font-size: 2.35rem;
    font-weight: 900;
    margin-bottom: 0;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.kpi-card {
    background: white;
    border-radius: 20px;
    padding: 20px 18px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    border-left: 8px solid #1f66d1;
    min-height: 170px;
    margin-bottom: 14px;
}
.kpi-label {
    color: #667085;
    font-size: 0.96rem;
    font-weight: 700;
    margin-bottom: 12px;
}
.kpi-value {
    color: #101828;
    font-size: 1.65rem;
    font-weight: 900;
    line-height: 1.28;
    word-break: break-word;
}
.kpi-sub {
    color: #667085;
    font-size: 0.82rem;
    margin-top: 10px;
}
.section-header {
    font-size: 1.15rem;
    font-weight: 800;
    color: #12344d;
    margin: 10px 0 12px 0;
}
.insight-box {
    background: white;
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: 0 5px 18px rgba(0,0,0,0.08);
    min-height: 115px;
}
.insight-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #667085;
    margin-bottom: 10px;
}
.insight-value {
    font-size: 1.15rem;
    font-weight: 800;
    color: #12344d;
}
.insight-sub {
    font-size: 0.83rem;
    color: #667085;
    margin-top: 6px;
}
[data-testid="stSidebar"] {
    background: #ffffff;
}
.stDownloadButton button {
    width: 100%;
    border-radius: 10px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


def find_excel_file():
    possible_files = [
        "Investment data.xlsx",
        "Investment Data.xlsx",
        "investment data.xlsx",
        "Investment data_short_units.xlsx",
        "Investment data_units_fixed.xlsx"
    ]
    current_folder = Path(".")
    for name in possible_files:
        path = current_folder / name
        if path.exists():
            return path
    files = list(current_folder.glob("*.xlsx"))
    return files[0] if files else None


def get_existing_column(df, possible_names):
    for col in possible_names:
        if col in df.columns:
            return col
    return None


def get_startup_column(df):
    return get_existing_column(df, ["Startup Registered Name", "Startup Name", "Name of Startup"])


def get_sector_column(df):
    return get_existing_column(df, ["Sector", "Industry Sector"])


def get_incubator_column(df):
    return get_existing_column(df, ["Name of Enabling Partner / Incubation Center", "Incubator"])


def get_tier_column(df):
    return get_existing_column(df, ["Tier Classification (Startup Based out of)", "Tier"])


def get_stage_column(df):
    return get_existing_column(df, ["Stage of Startup", "Stage"])


def get_funds_column(df):
    return get_existing_column(df, [
        "Total Funds Raised",
        "Total Funds Raised (Lakh)",
        "Funds Raised (Lakh)"
    ])


def get_rev_fy_column(df):
    return get_existing_column(df, [
        "Revenue Generated (FY 24-25)",
        "Revenue Generated (FY 24-25) (Cr)",
        "Revenue FY24-25 (Cr)"
    ])


def get_rev_recent_column(df):
    return get_existing_column(df, [
        "Revenue Generated Apr 25 - Feb 26",
        "Revenue Generated Apr 25 - Feb 26 (Cr)",
        "Revenue Apr25-Feb26 (Cr)"
    ])


def get_customers_column(df):
    return get_existing_column(df, ["Total No. of Customers"])


def get_employment_column(df):
    return get_existing_column(df, ["Total Number of Employment Generated Till Date"])


def extract_numeric_part(x):
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)

    s = str(x).strip().lower()
    s = s.replace("₹", "").replace(",", "").replace("rs.", "").replace("rs", "").strip()

    if s in {"", "na", "n/a", "none", "nil", "-", "--"}:
        return 0.0

    match = re.search(r"-?\d+(\.\d+)?", s)
    return float(match.group()) if match else 0.0


def parse_funds_to_lakh(x):
    if pd.isna(x):
        return 0.0

    raw = str(x).strip().lower().replace(",", "").replace("₹", "").strip()
    num = extract_numeric_part(x)

    if raw in {"", "na", "n/a", "none", "nil", "-", "--"}:
        return 0.0

    if "cr" in raw or "crore" in raw:
        return num * 100

    if "lakh" in raw or "lac" in raw or "lakhs" in raw or "lacs" in raw:
        return num

    if num >= 100000:
        return num / 100000

    return num


def parse_revenue_to_cr(x):
    if pd.isna(x):
        return 0.0

    if isinstance(x, (int, float)):
        return float(x)

    raw = str(x).strip().lower()
    raw = raw.replace(",", "").replace("₹", "").replace("rs.", "").replace("rs", "").strip()

    if raw in {"", "na", "n/a", "none", "nil", "-", "--", "pre revenue", "pre-revenue"}:
        return 0.0

    if any(word in raw for word in ["lakh", "lac", "lakhs", "lacs", "cr", "crore"]):
        crore_match = re.findall(r'(\d+(?:\.\d+)?)\s*(?:cr|crore)', raw)
        lakh_match = re.findall(r'(\d+(?:\.\d+)?)\s*(?:lakh|lac|lakhs|lacs)', raw)

        if crore_match:
            return float(crore_match[-1])
        if lakh_match:
            return float(lakh_match[-1]) / 100

    if re.fullmatch(r'-?\d+(\.\d+)?', raw):
        num = float(raw)
        if num >= 100000:
            return num / 10000000
        return num

    return 0.0


def fmt_currency_cr(x):
    try:
        return f"₹ {float(x):,.2f} Cr"
    except Exception:
        return "₹ 0.00 Cr"


def fmt_number(x):
    try:
        return f"{float(x):,.0f}"
    except Exception:
        return "0"


def fmt_decimal(x):
    try:
        return f"{float(x):,.2f}"
    except Exception:
        return "0.00"


def customers_served_value(series):
    clean = series.dropna().astype(str).str.strip()
    clean = clean[clean != ""]
    if clean.empty:
        return "No Data"

    india_count = clean.str.contains("india", case=False, na=False).sum()
    global_count = clean.str.contains("global", case=False, na=False).sum()

    if india_count > 0 or global_count > 0:
        return f"India: {india_count}<br>Global: {global_count}"

    return f"Reported: {len(clean)}"


def kpi_card(label, value, sub=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def insight_box(title, value, sub=""):
    st.markdown(
        f"""
        <div class="insight-box">
            <div class="insight-title">{title}</div>
            <div class="insight-value">{value}</div>
            <div class="insight-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    df.columns = [str(c).strip() for c in df.columns]

    startup_col = get_startup_column(df)
    sector_col = get_sector_column(df)
    incubator_col = get_incubator_column(df)
    tier_col = get_tier_column(df)
    stage_col = get_stage_column(df)
    funds_col = get_funds_column(df)
    rev_fy_col = get_rev_fy_column(df)
    rev_recent_col = get_rev_recent_column(df)
    customers_col = get_customers_column(df)
    employment_col = get_employment_column(df)

    if funds_col:
        df["Funds Raised (Lakh)"] = df[funds_col].apply(parse_funds_to_lakh)
    else:
        df["Funds Raised (Lakh)"] = 0.0

    if rev_fy_col:
        df["Revenue FY24-25 (Cr)"] = df[rev_fy_col].apply(parse_revenue_to_cr)
    else:
        df["Revenue FY24-25 (Cr)"] = 0.0

    if rev_recent_col:
        df["Revenue Apr25-Feb26 (Cr)"] = df[rev_recent_col].apply(parse_revenue_to_cr)
    else:
        df["Revenue Apr25-Feb26 (Cr)"] = 0.0

    if customers_col:
        df["Total Customers"] = df[customers_col].apply(extract_numeric_part)
    else:
        df["Total Customers"] = 0.0

    if employment_col:
        df["Employment Generated"] = df[employment_col].apply(extract_numeric_part)
    else:
        df["Employment Generated"] = 0.0

    text_cols = [
        "State", "Sector", "Industry Sector", "Stage", "Stage of Startup",
        "Customers Served", "Startup Registered Name", "Startup Name",
        "Name of Startup", "Name of Enabling Partner / Incubation Center",
        "Incubator", "Centre Type", "Tier Classification (Startup Based out of)",
        "Tier", "City", "District"
    ]

    for col in text_cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str).str.strip()
                .replace({"nan": None, "None": None, "": None})
            )

    df["Funds Raised (Cr)"] = df["Funds Raised (Lakh)"] / 100

    return df


def to_csv_download(df):
    return df.to_csv(index=False).encode("utf-8")


file_path = find_excel_file()

if file_path is None:
    st.error("Excel file nahi mili. dashboard.py ke same folder me file rakho.")
    st.stop()

df = load_data(file_path)

startup_col = get_startup_column(df)
sector_col = get_sector_column(df)
incubator_col = get_incubator_column(df)
tier_col = get_tier_column(df)
stage_col = get_stage_column(df)

filtered_df = df.copy()

st.sidebar.title("Dashboard Filters")
st.sidebar.caption("GENESIS investments analysis filters")

if "State" in filtered_df.columns:
    state_options = sorted(filtered_df["State"].dropna().unique().tolist())
    selected_states = st.sidebar.multiselect("Filter by State", state_options)
    if selected_states:
        filtered_df = filtered_df[filtered_df["State"].isin(selected_states)]

if sector_col:
    sector_options = sorted(filtered_df[sector_col].dropna().unique().tolist())
    selected_sectors = st.sidebar.multiselect("Filter by Sector", sector_options)
    if selected_sectors:
        filtered_df = filtered_df[filtered_df[sector_col].isin(selected_sectors)]

if incubator_col:
    incubator_options = sorted(filtered_df[incubator_col].dropna().unique().tolist())
    selected_incubators = st.sidebar.multiselect("Filter by Incubator", incubator_options)
    if selected_incubators:
        filtered_df = filtered_df[filtered_df[incubator_col].isin(selected_incubators)]

if stage_col:
    stage_options = sorted(filtered_df[stage_col].dropna().unique().tolist())
    selected_stages = st.sidebar.multiselect("Filter by Stage", stage_options)
    if selected_stages:
        filtered_df = filtered_df[filtered_df[stage_col].isin(selected_stages)]

if tier_col:
    tier_options = sorted(filtered_df[tier_col].dropna().unique().tolist())
    selected_tiers = st.sidebar.multiselect("Filter by Tier", tier_options)
    if selected_tiers:
        filtered_df = filtered_df[filtered_df[tier_col].isin(selected_tiers)]

if not filtered_df.empty:
    min_fund = float(filtered_df["Funds Raised (Lakh)"].min())
    max_fund = float(filtered_df["Funds Raised (Lakh)"].max())
    fund_range = st.sidebar.slider(
        "Funding Range (Lakh)",
        min_value=float(min_fund),
        max_value=float(max_fund),
        value=(float(min_fund), float(max_fund))
    )
    filtered_df = filtered_df[
        (filtered_df["Funds Raised (Lakh)"] >= fund_range[0]) &
        (filtered_df["Funds Raised (Lakh)"] <= fund_range[1])
    ]

if not filtered_df.empty:
    min_rev = float(filtered_df["Revenue Apr25-Feb26 (Cr)"].min())
    max_rev = float(filtered_df["Revenue Apr25-Feb26 (Cr)"].max())
    rev_range = st.sidebar.slider(
        "Revenue Range (Cr)",
        min_value=float(min_rev),
        max_value=float(max_rev),
        value=(float(min_rev), float(max_rev))
    )
    filtered_df = filtered_df[
        (filtered_df["Revenue Apr25-Feb26 (Cr)"] >= rev_range[0]) &
        (filtered_df["Revenue Apr25-Feb26 (Cr)"] <= rev_range[1])
    ]

if startup_col:
    startup_search = st.sidebar.text_input("Search Startup")
    if startup_search:
        filtered_df = filtered_df[
            filtered_df[startup_col].astype(str).str.contains(startup_search, case=False, na=False)
        ]

top_n = st.sidebar.slider("Top N for charts", 5, 20, 10)

if startup_col:
    total_startups = filtered_df[startup_col].dropna().nunique()
else:
    total_startups = len(filtered_df)

total_funds_lakh = filtered_df["Funds Raised (Lakh)"].sum()
total_funds_cr = filtered_df["Funds Raised (Cr)"].sum()
rev_fy = filtered_df["Revenue FY24-25 (Cr)"].sum()
rev_recent = filtered_df["Revenue Apr25-Feb26 (Cr)"].sum()
total_customers = filtered_df["Total Customers"].sum()
employment = filtered_df["Employment Generated"].sum()
customers_served = customers_served_value(filtered_df["Customers Served"]) if "Customers Served" in filtered_df.columns else "No Data"

avg_funding_cr = total_funds_cr / total_startups if total_startups else 0
avg_revenue_cr = rev_recent / total_startups if total_startups else 0
avg_customers = total_customers / total_startups if total_startups else 0
avg_employment = employment / total_startups if total_startups else 0
revenue_funding_ratio = rev_recent / total_funds_cr if total_funds_cr else 0

st.markdown("""
<div class="main-title-box">
    <div class="main-title">GENESIS INVESTMENTS DASHBOARD</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c5, c6, c7 = st.columns(3)

with c1:
    kpi_card("Total Startups", fmt_number(total_startups), "Unique startups in current selection")
with c2:
    kpi_card("Total Funds Raised", fmt_currency_cr(total_funds_cr), f"Source unit: Lakh | Total = {fmt_decimal(total_funds_lakh)} Lakh")
with c3:
    kpi_card("Revenue (FY 24-25)", fmt_currency_cr(rev_fy), "Reported revenue in Cr")
with c4:
    kpi_card("Revenue (Apr 25 - Feb 26)", fmt_currency_cr(rev_recent), "Reported revenue in Cr")
with c5:
    kpi_card("Total Customers", fmt_number(total_customers), "Total reported customer base")
with c6:
    kpi_card("Customers Served", customers_served, "Market reach summary")
with c7:
    kpi_card("Employment Generated", fmt_number(employment), "Employment impact")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Funding & Revenue",
    "Incubator Analysis",
    "Startup Leaderboard",
    "Data Table"
])

with tab1:
    st.markdown('<div class="section-header">Executive Highlights</div>', unsafe_allow_html=True)

    ic1, ic2, ic3, ic4 = st.columns(4)

    if "State" in filtered_df.columns and startup_col and not filtered_df.empty:
        top_state_data = filtered_df.groupby("State")[startup_col].nunique().sort_values(ascending=False)
        top_state = top_state_data.index[0] if len(top_state_data) else "N/A"
        top_state_val = int(top_state_data.iloc[0]) if len(top_state_data) else 0
    else:
        top_state, top_state_val = "N/A", 0

    if sector_col and startup_col and not filtered_df.empty:
        top_sector_data = filtered_df.groupby(sector_col)[startup_col].nunique().sort_values(ascending=False)
        top_sector = top_sector_data.index[0] if len(top_sector_data) else "N/A"
        top_sector_val = int(top_sector_data.iloc[0]) if len(top_sector_data) else 0
    else:
        top_sector, top_sector_val = "N/A", 0

    if incubator_col and not filtered_df.empty:
        top_incubator_data = filtered_df.groupby(incubator_col)["Funds Raised (Cr)"].sum().sort_values(ascending=False)
        top_incubator = top_incubator_data.index[0] if len(top_incubator_data) else "N/A"
        top_incubator_val_cr = top_incubator_data.iloc[0] if len(top_incubator_data) else 0
    else:
        top_incubator, top_incubator_val_cr = "N/A", 0

    with ic1:
        insight_box("Top State by Startup Count", top_state, f"{top_state_val} startups")
    with ic2:
        insight_box("Top Sector by Startup Count", top_sector, f"{top_sector_val} startups")
    with ic3:
        insight_box("Top Incubator by Funding", top_incubator, fmt_currency_cr(top_incubator_val_cr))
    with ic4:
        insight_box("Revenue to Funding Ratio", fmt_decimal(revenue_funding_ratio), "Revenue Cr / Funds Cr")

    ch1, ch2 = st.columns(2)

    with ch1:
        if "State" in filtered_df.columns and startup_col and not filtered_df.empty:
            state_df = (
                filtered_df.groupby("State")[startup_col]
                .nunique()
                .reset_index(name="Startup Count")
                .sort_values("Startup Count", ascending=False)
                .head(top_n)
            )
            fig_state = px.bar(
                state_df,
                x="State",
                y="Startup Count",
                text="Startup Count",
                title=f"Top {top_n} States by Startup Count"
            )
            fig_state.update_traces(
                texttemplate="%{y:.0f}",
                hovertemplate="<b>%{x}</b><br>Startup Count: %{y:.0f}<extra></extra>"
            )
            fig_state.update_layout(height=430, title_x=0)
            st.plotly_chart(fig_state, use_container_width=True)

    with ch2:
        if sector_col and startup_col and not filtered_df.empty:
            sector_df = (
                filtered_df.groupby(sector_col)[startup_col]
                .nunique()
                .reset_index(name="Startup Count")
                .sort_values("Startup Count", ascending=False)
                .head(top_n)
            )
            fig_sector = px.pie(
                sector_df,
                names=sector_col,
                values="Startup Count",
                hole=0.5,
                title="Sector-wise Startup Distribution"
            )
            fig_sector.update_traces(
                texttemplate="%{percent:.1%}",
                hovertemplate="<b>%{label}</b><br>Startup Count: %{value:.0f}<br>Share: %{percent}<extra></extra>"
            )
            fig_sector.update_layout(height=430, title_x=0)
            st.plotly_chart(fig_sector, use_container_width=True)

with tab2:
    st.markdown('<div class="section-header">Funding and Revenue Analysis</div>', unsafe_allow_html=True)

    fr1, fr2 = st.columns(2)

    with fr1:
        if "State" in filtered_df.columns and not filtered_df.empty:
            fund_state_df = (
                filtered_df.groupby("State")["Funds Raised (Cr)"]
                .sum()
                .reset_index()
                .sort_values("Funds Raised (Cr)", ascending=False)
                .head(top_n)
            )

            fig_fund_state = px.bar(
                fund_state_df,
                x="Funds Raised (Cr)",
                y="State",
                orientation="h",
                text="Funds Raised (Cr)",
                title=f"Top {top_n} States by Funds Raised (Cr)"
            )

            fig_fund_state.update_traces(
                texttemplate="%{x:.2f}",
                hovertemplate="<b>%{y}</b><br>Funds Raised: %{x:.2f} Cr<extra></extra>"
            )

            fig_fund_state.update_layout(
                height=430,
                title_x=0,
                yaxis={'categoryorder': 'total ascending'}
            )

            st.plotly_chart(fig_fund_state, use_container_width=True)

    with fr2:
        if sector_col and not filtered_df.empty:
            fund_sector_df = (
                filtered_df.groupby(sector_col)["Funds Raised (Cr)"]
                .sum()
                .reset_index()
                .sort_values("Funds Raised (Cr)", ascending=False)
                .head(top_n)
            )

            fig_fund_sector = px.pie(
                fund_sector_df,
                names=sector_col,
                values="Funds Raised (Cr)",
                hole=0.5,
                title="Sector-wise Funding Share (Cr)"
            )

            fig_fund_sector.update_traces(
                texttemplate="%{percent:.1%}",
                hovertemplate="<b>%{label}</b><br>Funds Raised: %{value:.2f} Cr<br>Share: %{percent}<extra></extra>"
            )

            fig_fund_sector.update_layout(height=430, title_x=0)

            st.plotly_chart(fig_fund_sector, use_container_width=True)

    fr3, fr4 = st.columns(2)

    with fr3:
        if startup_col and not filtered_df.empty:
            scatter_df = filtered_df[[startup_col, "Funds Raised (Cr)", "Revenue Apr25-Feb26 (Cr)"]].copy()
            fig_scatter = px.scatter(
                scatter_df,
                x="Funds Raised (Cr)",
                y="Revenue Apr25-Feb26 (Cr)",
                hover_name=startup_col,
                size="Revenue Apr25-Feb26 (Cr)",
                title="Revenue vs Funds Raised"
            )
            fig_scatter.update_traces(
                hovertemplate="<b>%{hovertext}</b><br>Funds Raised: %{x:.2f} Cr<br>Revenue: %{y:.2f} Cr<extra></extra>"
            )
            fig_scatter.update_layout(height=430, title_x=0)
            st.plotly_chart(fig_scatter, use_container_width=True)

    with fr4:
        if startup_col and not filtered_df.empty:
            top_rev_df = (
                filtered_df[[startup_col, "Revenue Apr25-Feb26 (Cr)"]]
                .groupby(startup_col, as_index=False)
                .sum()
                .sort_values("Revenue Apr25-Feb26 (Cr)", ascending=False)
                .head(top_n)
            )

            fig_top_rev = px.bar(
                top_rev_df,
                x="Revenue Apr25-Feb26 (Cr)",
                y=startup_col,
                orientation="h",
                text="Revenue Apr25-Feb26 (Cr)",
                title=f"Top {top_n} Startups by Revenue (Cr)"
            )

            fig_top_rev.update_traces(
                texttemplate="%{x:.2f}",
                hovertemplate="<b>%{y}</b><br>Revenue: %{x:.2f} Cr<extra></extra>"
            )

            fig_top_rev.update_layout(
                height=430,
                title_x=0,
                yaxis={'categoryorder': 'total ascending'}
            )

            st.plotly_chart(fig_top_rev, use_container_width=True)

with tab3:
    st.markdown('<div class="section-header">Incubator Performance Analysis</div>', unsafe_allow_html=True)

    if incubator_col and startup_col and not filtered_df.empty:
        summary_df = filtered_df.groupby(incubator_col).agg(
            Startups=(startup_col, "nunique"),
            **{
                "Funds Raised (Cr)": ("Funds Raised (Cr)", "sum"),
                "Revenue FY24-25 (Cr)": ("Revenue FY24-25 (Cr)", "sum"),
                "Revenue Apr25-Feb26 (Cr)": ("Revenue Apr25-Feb26 (Cr)", "sum"),
                "Customers": ("Total Customers", "sum"),
                "Employment": ("Employment Generated", "sum")
            }
        ).reset_index()

        summary_df["Revenue/Funding Ratio"] = summary_df.apply(
            lambda row: row["Revenue Apr25-Feb26 (Cr)"] / row["Funds Raised (Cr)"]
            if row["Funds Raised (Cr)"] not in [0, None] else 0,
            axis=1
        )

        summary_df = summary_df.sort_values("Funds Raised (Cr)", ascending=False)

        numeric_cols = [
            "Funds Raised (Cr)",
            "Revenue FY24-25 (Cr)",
            "Revenue Apr25-Feb26 (Cr)",
            "Customers",
            "Employment",
            "Revenue/Funding Ratio"
        ]
        for col in numeric_cols:
            if col in summary_df.columns:
                summary_df[col] = summary_df[col].round(2)

        st.dataframe(summary_df, use_container_width=True)

with tab4:
    st.markdown('<div class="section-header">Startup Leaderboard</div>', unsafe_allow_html=True)

    if startup_col and not filtered_df.empty:
        leaderboard_cols = [startup_col]

        optional_cols = [
            sector_col,
            incubator_col,
            "State",
            stage_col,
            tier_col,
            "Funds Raised (Lakh)",
            "Funds Raised (Cr)",
            "Revenue FY24-25 (Cr)",
            "Revenue Apr25-Feb26 (Cr)",
            "Total Customers",
            "Employment Generated"
        ]

        for col in optional_cols:
            if col and col in filtered_df.columns and col not in leaderboard_cols:
                leaderboard_cols.append(col)

        leaderboard_df = filtered_df[leaderboard_cols].copy()
        leaderboard_df = leaderboard_df.sort_values("Revenue Apr25-Feb26 (Cr)", ascending=False)

        for col in ["Funds Raised (Lakh)", "Funds Raised (Cr)", "Revenue FY24-25 (Cr)", "Revenue Apr25-Feb26 (Cr)"]:
            if col in leaderboard_df.columns:
                leaderboard_df[col] = leaderboard_df[col].round(2)

        for col in ["Total Customers", "Employment Generated"]:
            if col in leaderboard_df.columns:
                leaderboard_df[col] = leaderboard_df[col].round(0)

        st.dataframe(leaderboard_df, use_container_width=True)

with tab5:
    st.markdown('<div class="section-header">Complete GENESIS Startup Data</div>', unsafe_allow_html=True)

    display_df = filtered_df.copy()
    for col in [
        "Funds Raised (Lakh)",
        "Funds Raised (Cr)",
        "Revenue FY24-25 (Cr)",
        "Revenue Apr25-Feb26 (Cr)",
        "Total Customers",
        "Employment Generated"
    ]:
        if col in display_df.columns:
            display_df[col] = display_df[col].round(2)

    st.dataframe(display_df, use_container_width=True)

st.markdown("### Download Filtered Data")
st.download_button(
    label="Download Filtered Data as CSV",
    data=to_csv_download(filtered_df),
    file_name="genesis_filtered_dashboard_data.csv",
    mime="text/csv"
)