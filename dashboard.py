import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

st.set_page_config(
    page_title="RLV MEL Portal",
    layout="wide"
)

st.title("Regenerative Landscape Villages")

st.sidebar.markdown("## RLV MEL PORTAL")
st.sidebar.markdown("### Regenerative Landscape Villages")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Select Thematic Area",
    ["Livestock", "Crop Systems", "Fisheries", "Land Development"]
)

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(st.secrets["gcp"], scopes=scope)
client = gspread.authorize(creds)
SHEET_ID = "1pq1_1H3Y87D2jWGaOMVM9ypR0039RkQnaW0h2pFAxqs"

if menu == "Livestock":    
    profile_ws = client.open_by_key(SHEET_ID).worksheet("village profile")
    plan_ws    = client.open_by_key(SHEET_ID).worksheet("village plan")
    df_profile = pd.DataFrame(profile_ws.get_all_records())
    df_plan    = pd.DataFrame(plan_ws.get_all_records())

    df_profile = df_profile[[
        "mandal","panchayath","village",
        "no of HH","population","Total animals immunized",
        "Mortality","no of cattle sheds","no of sheds rennovated"
]]

    df_plan = df_plan[[
        "mandal","panchayath","village",
        "no of sheds to be rennovated","Animals to be immunized"
]]

    df = df_profile.merge(
        df_plan,
        on=["mandal","panchayath","village"],
        how="left"
)


    st.title("Habitation-wise Livestock Dashboard")

    mandal = st.selectbox("Select Mandal", ["All"] + sorted(df["mandal"].dropna().unique()))


    if mandal != "All":
        df = df[df["mandal"] == mandal]

    st.dataframe(df)

    st.metric("Total HH", df["no of HH"].sum())
    st.metric("Total Population", df["population"].sum())
    st.metric("Animals Immunized", df["Total animals immunized"].sum())
    st.metric("Total Mortality", df["Mortality"].sum())
    st.subheader("GP Wise Summary")

    gp_summary = df.groupby("panchayath").agg({
        "village":"nunique",
        "no of HH":"sum",
        "population":"sum",
        "Total animals immunized":"sum",
        "Animals to be immunized":"sum",
        "Mortality":"sum",
        "no of cattle sheds":"sum",
        "no of sheds rennovated":"sum",
        "no of sheds to be rennovated":"sum"
    }).reset_index()
    st.dataframe(gp_summary)
    st.download_button("Download GP Wise Excel", gp_summary.to_csv(index=False), "GP_Wise_Report.csv")

    st.subheader("Mandal Wise Summary")

    mandal_summary = df.groupby("mandal").agg({
        "panchayath":"nunique",
        "village":"nunique",
        "no of HH":"sum",
        "population":"sum",
        "Total animals immunized":"sum",
        "Animals to be immunized":"sum",
        "Mortality":"sum",
        "no of cattle sheds":"sum",
        "no of sheds rennovated":"sum",
        "no of sheds to be rennovated":"sum"
    }).reset_index()
    st.dataframe(mandal_summary)
    st.download_button("Download Mandal Wise Excel", mandal_summary.to_csv(index=False), "Mandal_Wise_Report.csv")
    pass
    
elif menu == "Crop Systems":
    st.header("🌾 Crop Systems")
    st.info("Crop systems dashboard coming soon.")


elif menu == "Fisheries":
    st.header("🐟 Fisheries")
    st.info("Fisheries dashboard coming soon.")


elif menu == "Land Development":
    st.header("🌱 Land Development")
    st.info("Land development dashboard coming soon.")

















