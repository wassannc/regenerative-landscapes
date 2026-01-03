import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

st.set_page_config(page_title="RLV Planning", layout="wide")

st.title("RLV – Village Planning & Budget Engine")

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(st.secrets["gcp"], scopes=scope)
client = gspread.authorize(creds)

SHEET_ID = "1pq1_1H3Y87D2jWGaOMVM9ypR0039RkQnaW0h2pFAxqs"

profile = pd.DataFrame(client.open_by_key(SHEET_ID).worksheet("village profile").get_all_records())
plan    = pd.DataFrame(client.open_by_key(SHEET_ID).worksheet("village plan").get_all_records())
epra    = pd.DataFrame(client.open_by_key(SHEET_ID).worksheet("epra").get_all_records())
budget  = pd.DataFrame(client.open_by_key(SHEET_ID).worksheet("budget").get_all_records())

st.success("All planning data & budget master loaded successfully")
