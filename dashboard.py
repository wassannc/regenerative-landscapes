import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

st.set_page_config(
    page_title="RLV MEL Portal",
    layout="wide"
)

st.title("Regenerative Landscape Villages")

st.sidebar.markdown("## RLV PORTAL")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Select Thematic Area",
    ["Large Ruminants", "Small Ruminants", "Crop Systems","Desi Poultry", "Fisheries", "Land Development", "Migration", "Farm mechanization"]
)

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(st.secrets["gcp"], scopes=scope)
client = gspread.authorize(creds)
SHEET_ID = "1pq1_1H3Y87D2jWGaOMVM9ypR0039RkQnaW0h2pFAxqs"

if menu == "Large Ruminants":    
    st.subheader("🐄 Large Ruminants")
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

elif menu == "Small Ruminants":

    st.subheader("🐐 Small Ruminants")

    sr_profile = client.open_by_key(SHEET_ID).worksheet("village profile")
    sr_plan    = client.open_by_key(SHEET_ID).worksheet("village plan")

    df_p = pd.DataFrame(sr_profile.get_all_records())
    df_pl = pd.DataFrame(sr_plan.get_all_records())

    df_p = df_p[[
        "mandal","panchayath","village",
        "no of HH","population",
        "SR immunized","SR Mortality",
        "no of sheep / goat sheds","no of elevated sheds"
    ]]

    df_pl = df_pl[[
        "mandal","panchayath","village",
        "SR to be immunized","no of sheds to be elevated"
    ]]

    df = df_p.merge(df_pl, on=["mandal","panchayath","village"], how="left")

    mandal = st.selectbox("Select Mandal", ["All"] + sorted(df["mandal"].dropna().unique()))
    if mandal != "All":
        df = df[df["mandal"] == mandal]

    st.markdown("### Village Wise")
    st.dataframe(df)

    st.markdown("### Panchayath Wise Summary")
    gp = df.groupby("panchayath").agg(
        Villages=("village","nunique"),
        HH=("no of HH","sum"),
        Population=("population","sum"),
        SR_Immunized=("SR immunized","sum"),
        SR_To_Be_Immunized=("SR to be immunized","sum"),
        Mortality=("Mortality","sum"),
        Goat_Sheds=("no of sheep / goat sheds","sum"),
        Elevated=("no of elevated sheds","sum"),
        To_Be_Elevated=("no of sheds to be elevated","sum")
    ).reset_index()

    st.dataframe(gp)
    st.download_button("Download GP Summary", gp.to_csv(index=False), "small_ruminant_gp.csv")

    st.markdown("### Mandal Wise Summary")
    mandal_sum = df.groupby("mandal").agg(
        Panchayaths=("panchayath","nunique"),
        Villages=("village","nunique"),
        HH=("no of HH","sum"),
        Population=("population","sum"),
        SR_Immunized=("SR immunized","sum"),
        SR_To_Be_Immunized=("SR to be immunized","sum"),
        Mortality=("Mortality","sum"),
        Goat_Sheds=("no of sheep / goat sheds","sum"),
        Elevated=("no of elevated sheds","sum"),
        To_Be_Elevated=("no of sheds to be elevated","sum")
    ).reset_index()

    st.dataframe(mandal_sum)
    st.download_button("Download Mandal Summary", mandal_sum.to_csv(index=False), "small_ruminant_mandal.csv")

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


elif menu == "Migration":
    st.header("Migration")
    st.info("Migration dashboard coming soon.")


elif menu == "Farm mechanization":
    st.header("Farm mechanization")
    st.info("Farm mechanization dashboard coming soon.")


elif menu == "Desi Poultry":
    st.header("Desi Poultry")
    st.info("Desi Poultry dashboard coming soon.")



















