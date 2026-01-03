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

st.subheader("Village Wise Livestock Development Plan")

mandal = st.selectbox("Select Mandal", sorted(plan["mandal"].dropna().unique()))
panchayath = st.selectbox("Select Panchayath", sorted(plan[plan["mandal"]==mandal]["panchayath"].unique()))
village = st.selectbox("Select Village", sorted(plan[(plan["mandal"]==mandal) & (plan["panchayath"]==panchayath)]["village"].unique()))

village_plan = plan[(plan["mandal"]==mandal) & (plan["panchayath"]==panchayath) & (plan["village"]==village)]

livestock_budget = budget[budget["Thematic"]=="Large Ruminants"]

final_plan = []

for _,row in livestock_budget.iterrows():
    col = row["Source Column"]
    if col in village_plan.columns:
        qty = village_plan[col].sum()
        if qty > 0:
            cost = qty * row["Unit Cost (Rs)"]
            final_plan.append([row["Name of the work"], row["Unit"], qty, row["Unit Cost (Rs)"], cost])

final_df = pd.DataFrame(final_plan, columns=["Work","Unit","Quantity","Unit Cost","Total Cost"])

st.dataframe(final_df)

st.metric("Total Livestock Budget (₹)", int(final_df["Total Cost"].sum()))

st.download_button("Download Village Livestock DPR", final_df.to_csv(index=False), f"{village}_livestock_dpr.csv")
