import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# Define scope and load creds
creds_dict = st.secrets["google_service_account"]

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open Google Sheet
sheet = client.open("Personal Finance Tracker").sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Dashboard Title
st.title("📊 Google Sheets Dashboard")

# Preprocess: Convert timestamps
df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
filtered_df = df[df["Total"] != 0]

if len(filtered_df) < 2:
    st.warning("Not enough non-zero data points to calculate growth.")
else:
    # Extract relevant values
    first_val = filtered_df["Total"].iloc[0]
    latest_val = filtered_df["Total"].iloc[-1]
    first_date = filtered_df["Timestamp"].iloc[0]
    latest_date = filtered_df["Timestamp"].iloc[-1]
    date_diff = latest_date - first_date
    days_between = date_diff.total_seconds() / (24 * 3600)

    # Growth calculations
    pct_increase = ((latest_val - first_val) / first_val) * 100
    avg_daily_growth = pct_increase / days_between if days_between > 0 else 0
    avg_yearly_growth = avg_daily_growth * 365

    # Formatting
    first_date_str = first_date.strftime("%d %b %Y")
    latest_date_str = latest_date.strftime("%d %b %Y")
    arrow = "🔺" if pct_increase > 0 else ("➖" if pct_increase == 0 else "🔻")
    color = "green" if pct_increase > 0 else ("black" if pct_increase == 0 else "red")
    bg_color = "#e0ffe0" if pct_increase > 0 else "#fff0f0" if pct_increase < 0 else "#f9f9f9"

    # Layout columns
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

# Data Table and Chart
st.subheader("📄 Raw Data")
st.dataframe(df)

st.subheader("📈 Total Over Time")
st.line_chart(df["Total"])
