import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import altair as alt

# Load Google Sheets credentials
creds_dict = st.secrets["google_service_account"]

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Read sheet data
sheet = client.open("Personal Finance Tracker").sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Title
st.title("📊 Google Sheets Dashboard")

# Convert Timestamp to datetime
df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
filtered_df = df[df["Total"] != 0]
current_total = filtered_df["Total"].iloc[-1]
st.markdown(f"""
<div style="
    background-color: #f0f8ff;
    padding: 1.5em;
    border-left: 6px solid #1f77b4;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    margin-bottom: 1.5em;">
    <h2 style='margin: 0 0 0.5em 0;'>💰 Current Portfolio Value</h2>
    <p style='font-size: 36px; color: #1f77b4; margin: 0; font-weight: bold;'>${current_total:,.2f}</p>
</div>
""", unsafe_allow_html=True)
# ----- Growth Summary -----
if len(filtered_df) < 2:
    st.warning("Not enough non-zero data points to calculate growth.")
else:
    first_val = filtered_df["Total"].iloc[0]
    latest_val = filtered_df["Total"].iloc[-1]
    first_date = filtered_df["Timestamp"].iloc[0]
    latest_date = filtered_df["Timestamp"].iloc[-1]
    days_between = (latest_date - first_date).total_seconds() / (24 * 3600)

    pct_increase = ((latest_val - first_val) / first_val) * 100
    avg_daily_growth = pct_increase / days_between if days_between > 0 else 0
    avg_yearly_growth = avg_daily_growth * 365

    first_date_str = first_date.strftime("%d %b %Y")
    latest_date_str = latest_date.strftime("%d %b %Y")
    arrow = "🔺" if pct_increase > 0 else ("➖" if pct_increase == 0 else "🔻")
    color = "green" if pct_increase > 0 else ("black" if pct_increase == 0 else "red")
    bg_color = "#e0ffe0" if pct_increase > 0 else "#fff0f0" if pct_increase < 0 else "#f9f9f9"

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style='padding: 1em; background-color: {bg_color}; border-left: 5px solid {color}; border-radius: 8px;'>
        <h3 style='margin-bottom: 0.5em;'>📈 Total Growth</h3>
        <p style='font-size: 24px; color: {color}; margin: 0;'><strong>{arrow} {pct_increase:.2f}%</strong></p>
        <p style='color: gray; font-size: 14px;'>From ${first_val:,.2f} on {first_date_str}<br>To ${latest_val:,.2f} on {latest_date_str}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style='padding: 1em; background-color: #f9f9f9; border-left: 5px solid {color}; border-radius: 8px;'>
        <h3 style='margin-bottom: 0.5em;'>📆 Growth Dashboard</h3>
        <p style='font-size: 20px; color: {color}; margin: 0;'>📅 Days Tracked: <strong>{int(days_between)}</strong></p>
        <p style='font-size: 20px; color: {color}; margin: 0;'>📈 Daily Avg: <strong>{avg_daily_growth:.2f}%</strong></p>
        <p style='font-size: 20px; color: {color}; margin: 0;'>📆 Yearly Avg: <strong>{avg_yearly_growth:.2f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)

# ----- Altair: Total Over Time -----
st.subheader("📈 Total Over Time")
df["Total"] = pd.to_numeric(df["Total"], errors="coerce")
total_chart = alt.Chart(df.dropna(subset=["Total", "Timestamp"])).mark_line(color="blue").encode(
    x=alt.X("Timestamp:T", title="Date"),
    y=alt.Y("Total:Q", title="Total Value ($)", scale=alt.Scale(zero=False))
).properties(
    width="container",
    height=300,
    title="Total Portfolio Trend"
)
st.altair_chart(total_chart, use_container_width=True)

# ----- Altair: Platform Trend Viewer -----
st.subheader("🏦 Account Trend Viewer")
accounts = [col for col in df.columns if col not in ["Timestamp", "Total"]]
selected_account = st.selectbox("Select a platform to view trend", accounts)

df[selected_account] = pd.to_numeric(df[selected_account], errors="coerce")
account_chart = alt.Chart(df.dropna(subset=["Timestamp", selected_account])).mark_line(color="orange").encode(
    x=alt.X("Timestamp:T", title="Date"),
    y=alt.Y(f"{selected_account}:Q", title=f"{selected_account} Balance", scale=alt.Scale(zero=False))
).properties(
    width="container",
    height=300,
    title=f"{selected_account} Trend"
)
st.altair_chart(account_chart, use_container_width=True)

# ----- Data Table -----
st.subheader("📄 Data")
st.dataframe(df)