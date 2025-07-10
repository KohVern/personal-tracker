import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# Define scope and load creds
creds_dict = st.secrets["google_service_account"]

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Authorize and open sheet
client = gspread.authorize(creds)
sheet = client.open("Personal Finance Tracker").sheet1  # Or use .worksheet("Sheet1")

# Convert to DataFrame
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Display
st.title("Google Sheets Dashboard")

# Filter out zeros in 'Total'
non_zero_totals = df[df["Total"] != 0]["Total"]

if len(non_zero_totals) < 2:
    st.warning("Not enough non-zero data points to calculate percentage increase.")
else:
    first_val = non_zero_totals.iloc[0]
    latest_val = non_zero_totals.iloc[-1]
    
    pct_increase = ((latest_val - first_val) / first_val) * 100
    
    arrow = "🔺" if pct_increase > 0 else ("➖" if pct_increase == 0 else "🔻")
    color = "green" if pct_increase > 0 else ("black" if pct_increase == 0 else "red")

    st.markdown(f"""
    <div style='padding: 1em; background-color: #f9f9f9; border-left: 5px solid {color}; border-radius: 8px;'>
    <h3 style='margin-bottom: 0.5em;'>📊 Total Growth</h3>
    <p style='font-size: 24px; color: {color}; margin: 0;'>{arrow} {pct_increase:.2f}%</p>
    <p style='color: gray;'>From ${first_val:,.2f} to ${latest_val:,.2f}</p>
    </div>
    """, unsafe_allow_html=True)

st.dataframe(df)
st.line_chart(df['Total'])