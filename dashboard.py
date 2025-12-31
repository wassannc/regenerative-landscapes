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
    ["Large Ruminants", "Small Ruminants", "Desi Poultry", "Crop Systems", "Natural Farming", "Fisheries", "Land Development", "Migration", "Farm mechanization"]
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
        "Total HHs","population","Total animals immunized",
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

    st.metric("Total HH", df["Total HHs"].sum())
    st.metric("Total Population", df["population"].sum())
    st.metric("Animals Immunized", df["Total animals immunized"].sum())
    st.metric("Total Mortality", df["Mortality"].sum())
    st.subheader("GP Wise Summary")

    gp_summary = df.groupby("panchayath").agg({
        "village":"nunique",
        "Total HHs":"sum",
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
        "Total HHs":"sum",
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
        "Total HHs","population",
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

    st.markdown("Panchayath Wise Summary")
    
    gp_summary = df.groupby("panchayath").agg({
        "village":"nunique",
        "Total HHs":"sum",
        "population":"sum",
        "SR immunized":"sum",
        "SR to be immunized":"sum",
        "SR Mortality":"sum",
        "no of sheep / goat sheds":"sum",
        "no of elevated sheds":"sum",
        "no of sheds to be elevated":"sum"
    }).reset_index()

    st.dataframe(gp_summary)
    st.download_button("Download GP Summary", gp_summary.to_csv(index=False), "small_ruminant_gp.csv")

    st.markdown("Mandal Wise Summary")
    
    mandal_summary = df.groupby("mandal").agg({
        "panchayath":"nunique",
        "village":"nunique",
        "Total HHs":"sum",
        "population":"sum",
        "SR immunized":"sum",
        "SR to be immunized":"sum",
        "SR Mortality":"sum",
        "no of sheep / goat sheds":"sum",
        "no of elevated sheds":"sum",
        "no of sheds to be elevated":"sum"
    }).reset_index()

    st.dataframe(mandal_summary)
    st.download_button("Download Mandal Summary", mandal_summary.to_csv(index=False), "small_ruminant_mandal.csv")
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
    st.subheader("🐔 Desi Poultry")

    byp_profile = client.open_by_key(SHEET_ID).worksheet("village profile")
    byp_plan    = client.open_by_key(SHEET_ID).worksheet("village plan")
    byp_epra    = client.open_by_key(SHEET_ID).worksheet("epra")

    df_b  = pd.DataFrame(byp_profile.get_all_records())
    df_b1 = pd.DataFrame(byp_plan.get_all_records())
    df_b2 = pd.DataFrame(byp_epra.get_all_records())
    
    df_b.columns  = df_b.columns.str.strip()
    df_b1.columns = df_b1.columns.str.strip()
    df_b2.columns = df_b2.columns.str.strip()

    # Profile columns
    df_b = df_b[[
        "mandal","panchayath","village",
        "Total HHs","no of BYP HHs",
        "Total Birds","Total birds immunized",
        "birds mortality","poultry service provider"
    ]]

    # Plan columns
    df_b1 = df_b1[[
        "mandal","panchayath","village",
        "Birds to be immunized",
        "No of women are willing to establish breedfarms"
    ]]

    # EPRA columns
    df_b2 = df_b2[[
        "mandal","panchayath","village",
        "No of breedfarms exists"
    ]]

    # Merge all
    df = df_b.merge(df_b1, on=["mandal","panchayath","village"], how="left")
    df = df.merge(df_b2, on=["mandal","panchayath","village"], how="left")

    # Count YES service providers
    df["service_provider_yes"] = df["poultry service provider"].str.strip().str.lower().eq("yes").astype(int)

    mandal = st.selectbox("Select Mandal", ["All"] + sorted(df["mandal"].dropna().unique()))
    if mandal != "All":
        df = df[df["mandal"] == mandal]

    st.markdown("### Village Wise")
    st.dataframe(df)

    # GP Summary
    st.markdown("### Panchayath Wise Summary")
    gp_summary = df.groupby("panchayath").agg({
        "village":"nunique",
        "Total HHs":"sum",
        "no of BYP HHs":"sum",
        "Total Birds":"sum",
        "Total birds immunized":"sum",
        "Birds to be immunized":"sum",
        "birds mortality":"sum",
        "No of breedfarms exists":"sum",
        "No of women are willing to establish breedfarms":"sum",
        "service_provider_yes":"sum"
    }).reset_index()

    st.dataframe(gp_summary)
    st.download_button("Download GP Summary", gp_summary.to_csv(index=False), "desi_poultry_gp.csv")

    # Mandal Summary
    st.markdown("### Mandal Wise Summary")
    mandal_summary = df.groupby("mandal").agg({
        "panchayath":"nunique",
        "village":"nunique",
        "Total HHs":"sum",
        "no of BYP HHs":"sum",
        "Total Birds":"sum",
        "Total birds immunized":"sum",
        "Birds to be immunized":"sum",
        "birds mortality":"sum",
        "No of breedfarms exists":"sum",
        "No of women are willing to establish breedfarms":"sum",
        "service_provider_yes":"sum"
    }).reset_index()

    st.dataframe(mandal_summary)
    st.download_button("Download Mandal Summary", mandal_summary.to_csv(index=False), "desi_poultry_mandal.csv")
    pass

elif menu == "Natural Farming":
    st.subheader("🌱 Natural Farming")

    nf_profile = client.open_by_key(SHEET_ID).worksheet("village profile")
    nf_plan    = client.open_by_key(SHEET_ID).worksheet("village plan")
    nf_epra    = client.open_by_key(SHEET_ID).worksheet("epra")

    df_nf  = pd.DataFrame(nf_profile.get_all_records())
    df_nf1 = pd.DataFrame(nf_plan.get_all_records())
    df_nf2 = pd.DataFrame(nf_epra.get_all_records())

    # Clean column names
    df_nf.columns  = df_nf.columns.str.strip()
    df_nf1.columns = df_nf1.columns.str.strip()
    df_nf2.columns = df_nf2.columns.str.strip()

    # Required columns
    df_nf = df_nf[[
        "mandal","panchayath","village",
        "Total HHs",
        "Total land in the village_acre",
        "Total HH practicing NF",
        "Total land under NF practice_acre"
    ]]

    df_nf1 = df_nf1[[
        "mandal","panchayath","village",
        "Is business plan developed"
    ]]

    df_nf2 = df_nf2[[
        "mandal","panchayath","village",
        "Name of the BRC entrepreneur",
        "No of villages accessing NF inputs",
        "No of farmers accessing NF inputs",
        "Extent covered under BRC_acres"
    ]]

    # Merge 3 sources
    df = df_nf.merge(df_nf1, on=["mandal","panchayath","village"], how="left")
    df = df.merge(df_nf2, on=["mandal","panchayath","village"], how="left")

    df["business_plan_yes"] = df["Is business plan developed"].astype(str).str.strip().str.lower().eq("yes").astype(int)

    # Mandal filter
    mandal = st.selectbox("Select Mandal", ["All"] + sorted(df["mandal"].dropna().unique()))
    if mandal != "All":
        df = df[df["mandal"] == mandal]

    st.markdown("### Village Wise")
    st.dataframe(df)

    # Panchayath summary
    st.markdown("### Panchayath Wise Summary")
    gp_summary = df.groupby("panchayath").agg({
        "village":"nunique",
        "Total HHs":"sum",
        "Total land in the village_acre":"sum",
        "Total HH practicing NF":"sum",
        "Total land under NF practice_acre":"sum",
        "No of villages accessing NF inputs":"sum",
        "No of farmers accessing NF inputs":"sum",
        "Extent covered under BRC_acres":"sum",
        "business_plan_yes":"sum"
    }).reset_index()

    st.dataframe(gp_summary)
    st.download_button("Download GP NF Report", gp_summary.to_csv(index=False), "nf_gp_summary.csv")

    # Mandal summary
    st.markdown("### Mandal Wise Summary")
    mandal_summary = df.groupby("mandal").agg({
        "panchayath":"nunique",
        "village":"nunique",
        "Total HHs":"sum",
        "Total land in the village_acre":"sum",
        "Total HH practicing NF":"sum",
        "Total land under NF practice_acre":"sum",
        "No of villages accessing NF inputs":"sum",
        "No of farmers accessing NF inputs":"sum",
        "Extent covered under BRC_acres":"sum",
        "business_plan_yes":"sum"
    }).reset_index()

    st.dataframe(mandal_summary)
    st.download_button("Download Mandal NF Report", mandal_summary.to_csv(index=False), "nf_mandal_summary.csv")
    pass
    

    









































