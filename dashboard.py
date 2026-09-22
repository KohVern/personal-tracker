import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import altair as alt

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Main page */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* KPI cards */
    .kpi-card {
        padding: 1.3rem;
        border-radius: 12px;
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        min-height: 125px;
    }

    .kpi-title {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
    }

    .kpi-subtitle {
        font-size: 13px;
        color: #6b7280;
        margin-top: 6px;
    }

    /* Section headers */
    .section-header {
        font-size: 22px;
        font-weight: 650;
        color: #111827;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        border-right: 1px solid #e5e7eb;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
    }

    /* Divider */
    hr {
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Load Google Sheets credentials
# ---------------------------------------------------------
creds_dict = st.secrets["google_service_account"]

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    creds_dict,
    scope
)

client = gspread.authorize(creds)


# ---------------------------------------------------------
# Read sheet data
# ---------------------------------------------------------
sheet = client.open("Personal Finance Tracker").sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)


# ---------------------------------------------------------
# Data Preparation
# ---------------------------------------------------------
df["Timestamp"] = pd.to_datetime(
    df["Timestamp"],
    format="%d/%m/%Y %H:%M:%S",
    errors="coerce"
)

df["Total"] = pd.to_numeric(
    df["Total"],
    errors="coerce"
)

filtered_df = df[df["Total"] != 0]


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.title("💰 Personal Finance Dashboard")

st.caption(
    "Track your portfolio value, growth and individual account performance."
)

st.divider()


# ---------------------------------------------------------
# Current Portfolio Value
# ---------------------------------------------------------
if len(filtered_df) == 0:
    st.error("No valid portfolio data found.")
    st.stop()

current_total = filtered_df["Total"].iloc[-1]

previous_total = (
    filtered_df["Total"].iloc[-2]
    if len(filtered_df) >= 2
    else current_total
)

if previous_total != 0:
    period_change = current_total - previous_total
    period_change_pct = (period_change / previous_total) * 100
else:
    period_change = 0
    period_change_pct = 0


# ---------------------------------------------------------
# Growth Summary
# ---------------------------------------------------------
if len(filtered_df) < 2:

    pct_increase = 0
    avg_daily_growth = 0
    avg_yearly_growth = 0
    days_between = 0

    first_val = current_total
    latest_val = current_total
    first_date = filtered_df["Timestamp"].iloc[0]
    latest_date = filtered_df["Timestamp"].iloc[-1]

else:

    first_val = filtered_df["Total"].iloc[0]
    latest_val = filtered_df["Total"].iloc[-1]

    first_date = filtered_df["Timestamp"].iloc[0]
    latest_date = filtered_df["Timestamp"].iloc[-1]

    days_between = (
        latest_date - first_date
    ).total_seconds() / (24 * 3600)

    pct_increase = (
        ((latest_val - first_val) / first_val) * 100
        if first_val != 0
        else 0
    )

    avg_daily_growth = (
        pct_increase / days_between
        if days_between > 0
        else 0
    )

    avg_yearly_growth = avg_daily_growth * 365


# ---------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">💰 Current Portfolio</div>
        <div class="kpi-value">${current_total:,.2f}</div>
        <div class="kpi-subtitle">
            Latest recorded value
        </div>
    </div>
    """, unsafe_allow_html=True)


with col2:

    if period_change_pct > 0:
        change_icon = "▲"
        change_color = "#16a34a"
    elif period_change_pct < 0:
        change_icon = "▼"
        change_color = "#dc2626"
    else:
        change_icon = "—"
        change_color = "#6b7280"

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">📊 Recent Change</div>
        <div class="kpi-value" style="color:{change_color};">
            {change_icon} {period_change_pct:.2f}%
        </div>
        <div class="kpi-subtitle">
            ${period_change:,.2f} from previous record
        </div>
    </div>
    """, unsafe_allow_html=True)


with col3:

    growth_color = (
        "#16a34a"
        if pct_increase > 0
        else "#dc2626"
        if pct_increase < 0
        else "#6b7280"
    )

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">📈 Total Growth</div>
        <div class="kpi-value" style="color:{growth_color};">
            {pct_increase:+.2f}%
        </div>
        <div class="kpi-subtitle">
            Since first recorded value
        </div>
    </div>
    """, unsafe_allow_html=True)


with col4:

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">📅 Tracking Period</div>
        <div class="kpi-value">{int(days_between)}</div>
        <div class="kpi-subtitle">
            Days tracked
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# Growth Summary
# ---------------------------------------------------------
st.markdown(
    '<div class="section-header">📈 Portfolio Growth</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns([1.4, 1])

with col1:

    arrow = (
        "🔺"
        if pct_increase > 0
        else "🔻"
        if pct_increase < 0
        else "➖"
    )

    color = (
        "green"
        if pct_increase > 0
        else "red"
        if pct_increase < 0
        else "gray"
    )

    bg_color = (
        "#ecfdf5"
        if pct_increase > 0
        else "#fef2f2"
        if pct_increase < 0
        else "#f9fafb"
    )

    first_date_str = first_date.strftime("%d %b %Y")
    latest_date_str = latest_date.strftime("%d %b %Y")

    st.markdown(f"""
    <div style="
        padding:1.5rem;
        background:{bg_color};
        border-radius:12px;
        border:1px solid #e5e7eb;
    ">

        <div style="
            font-size:14px;
            color:#6b7280;
            margin-bottom:8px;
        ">
            Overall portfolio performance
        </div>

        <div style="
            font-size:32px;
            font-weight:700;
            color:{color};
        ">
            {arrow} {pct_increase:+.2f}%
        </div>

        <div style="
            margin-top:12px;
            color:#6b7280;
            font-size:14px;
        ">
            ${first_val:,.2f} on {first_date_str}
            <br>
            ↓
            <br>
            ${latest_val:,.2f} on {latest_date_str}
        </div>

    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown(f"""
    <div style="
        padding:1.5rem;
        background:#ffffff;
        border-radius:12px;
        border:1px solid #e5e7eb;
    ">

        <div style="
            font-size:14px;
            color:#6b7280;
            margin-bottom:12px;
        ">
            Growth Statistics
        </div>

        <div style="
            font-size:18px;
            margin-bottom:10px;
        ">
            📆 Daily Average
            <strong>{avg_daily_growth:+.2f}%</strong>
        </div>

        <div style="
            font-size:18px;
            margin-bottom:10px;
        ">
            📅 Annualised Average
            <strong>{avg_yearly_growth:+.2f}%</strong>
        </div>

        <div style="
            font-size:18px;
        ">
            💵 Absolute Growth
            <strong>${latest_val - first_val:+,.2f}</strong>
        </div>

    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------
st.sidebar.header("🔎 Dashboard Filters")

min_date = df["Timestamp"].min()
max_date = df["Timestamp"].max()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date.date(), max_date.date()),
    min_value=min_date.date(),
    max_value=max_date.date()
)

if len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)

    chart_df = df[
        (df["Timestamp"] >= start_date) &
        (df["Timestamp"] < end_date)
    ]

else:

    chart_df = df.copy()


# ---------------------------------------------------------
# Portfolio Trend
# ---------------------------------------------------------
st.markdown(
    '<div class="section-header">📈 Portfolio Value Over Time</div>',
    unsafe_allow_html=True
)

total_chart_data = chart_df.dropna(
    subset=["Total", "Timestamp"]
)

total_chart = (
    alt.Chart(total_chart_data)
    .mark_line(
        point=True,
        strokeWidth=3
    )
    .encode(
        x=alt.X(
            "Timestamp:T",
            title="Date",
            axis=alt.Axis(
                format="%d %b",
                labelAngle=-45
            )
        ),
        y=alt.Y(
            "Total:Q",
            title="Portfolio Value ($)",
            scale=alt.Scale(zero=False)
        ),
        tooltip=[
            alt.Tooltip(
                "Timestamp:T",
                title="Date",
                format="%d %b %Y %H:%M"
            ),
            alt.Tooltip(
                "Total:Q",
                title="Portfolio",
                format="$,.2f"
            )
        ]
    )
    .properties(
        height=380
    )
    .interactive()
)

st.altair_chart(
    total_chart,
    use_container_width=True
)


# ---------------------------------------------------------
# Account Trend Viewer
# ---------------------------------------------------------
st.markdown(
    '<div class="section-header">🏦 Account Performance</div>',
    unsafe_allow_html=True
)

accounts = [
    col
    for col in df.columns
    if col not in ["Timestamp", "Total"]
]

if accounts:

    selected_account = st.selectbox(
        "Select an account / platform",
        accounts
    )

    df[selected_account] = pd.to_numeric(
        df[selected_account],
        errors="coerce"
    )

    account_chart_data = chart_df.dropna(
        subset=["Timestamp", selected_account]
    )

    account_chart = (
        alt.Chart(account_chart_data)
        .mark_line(
            point=True,
            strokeWidth=3
        )
        .encode(
            x=alt.X(
                "Timestamp:T",
                title="Date",
                axis=alt.Axis(
                    format="%d %b",
                    labelAngle=-45
                )
            ),
            y=alt.Y(
                f"{selected_account}:Q",
                title=f"{selected_account} Balance ($)",
                scale=alt.Scale(zero=False)
            ),
            tooltip=[
                alt.Tooltip(
                    "Timestamp:T",
                    title="Date",
                    format="%d %b %Y %H:%M"
                ),
                alt.Tooltip(
                    f"{selected_account}:Q",
                    title=selected_account,
                    format="$,.2f"
                )
            ]
        )
        .properties(
            height=350,
            title=f"{selected_account} Trend"
        )
        .interactive()
    )

    st.altair_chart(
        account_chart,
        use_container_width=True
    )

else:

    st.info("No account/platform columns were found.")


# ---------------------------------------------------------
# Account Summary
# ---------------------------------------------------------
if accounts:

    st.markdown(
        '<div class="section-header">💼 Account Summary</div>',
        unsafe_allow_html=True
    )

    summary_data = []

    for account in accounts:

        account_values = pd.to_numeric(
            df[account],
            errors="coerce"
        ).dropna()

        if len(account_values) > 0:

            latest = account_values.iloc[-1]

            if len(account_values) >= 2:
                previous = account_values.iloc[-2]
                change = latest - previous

                if previous != 0:
                    change_pct = (
                        change / previous
                    ) * 100
                else:
                    change_pct = 0
            else:
                change = 0
                change_pct = 0

            summary_data.append({
                "Account": account,
                "Current Value": latest,
                "Change": change,
                "Change %": change_pct
            })

    if summary_data:

        summary_df = pd.DataFrame(summary_data)

        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Current Value": st.column_config.NumberColumn(
                    "Current Value",
                    format="$%,.2f"
                ),
                "Change": st.column_config.NumberColumn(
                    "Change",
                    format="$%+.2f"
                ),
                "Change %": st.column_config.NumberColumn(
                    "Change %",
                    format="%+.2f%%"
                )
            }
        )


# ---------------------------------------------------------
# Raw Data
# ---------------------------------------------------------
st.markdown(
    '<div class="section-header">📄 Transaction History</div>',
    unsafe_allow_html=True
)

st.caption(
    f"{len(df):,} records"
)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Timestamp": st.column_config.DatetimeColumn(
            "Timestamp",
            format="DD MMM YYYY HH:mm"
        ),
        "Total": st.column_config.NumberColumn(
            "Total",
            format="$%,.2f"
        )
    }
)