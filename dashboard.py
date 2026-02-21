import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# ---------- LOGIN CONFIG ----------
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login("Login", location="main")

if authentication_status is False:
    st.error("Username/password is incorrect")

if authentication_status is None:
    st.warning("Please enter your credentials")

if not authentication_status:
    st.stop()

authenticator.logout("Logout", "sidebar")
st.sidebar.write(f"Welcome {name}")

st.set_page_config(
    page_title="RLV MEL Portal",
    layout="wide"
)

page = "dashboard"

st.markdown(f"""
<style>
/* Hide Streamlit default sidebar navigation */
[data-testid="stSidebarNav"] {{display: none;}}

/* Top navigation bar */
.topnav {{
    background: linear-gradient(90deg, #0f2b46, #123e63);
    padding: 12px 30px;
    border-radius: 0 0 12px 12px;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}}

.topnav a {{
    color: white;
    margin-right: 40px;
    font-size: 18px;
    font-weight: 600;
    text-decoration: none;
    padding: 6px 12px;
    border-radius: 6px;
}}

.topnav a:hover {{
    background-color: rgba(255,255,255,0.15);
}}

.active {{
    background-color: #ffd166;
    color: #0f2b46 !important;
}}
</style>

<div class="topnav">
    <a href="/" class="{{'active' if page=='dashboard' else ''}}">Dashboard</a>
    <a href="/maps" class="{{'active' if page=='maps' else ''}}">Maps</a>
    <a href="/planning" class="{{'active' if page=='planning' else ''}}">Planning</a>
</div>
""", unsafe_allow_html=True)

# ---------------- PREMIUM UI STYLE ----------------
st.markdown("""
<style>
/* App background */
.stApp {
    background: linear-gradient(135deg, #f5f7fa, #e4ecf7);
    font-family: 'Segoe UI', sans-serif;
}

/* Main title */
h1, h2, h3 {
    color: #1f3b73;
    font-weight: 700;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f3057, #145da0);
    color: white;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Sidebar title */
section[data-testid="stSidebar"] h2 {
    font-size: 20px;
    margin-bottom: 10px;
}

/* Radio buttons */
div[role="radiogroup"] > label {
    padding: 8px;
    border-radius: 8px;
    transition: 0.3s;
}
div[role="radiogroup"] > label:hover {
    background-color: rgba(255,255,255,0.2);
}

/* Data tables */
thead tr th {
    background-color: #1f3b73 !important;
    color: white !important;
    font-weight: 600 !important;
}

/* Metrics */
div[data-testid="metric-container"] {
    background: white;
    border-radius: 12px;
    padding: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Download buttons */
button[kind="secondary"] {
    border-radius: 8px;
    border: none;
    background-color: #1f3b73;
    color: white;
    font-weight: 600;
}
button[kind="secondary"]:hover {
    background-color: #145da0;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("Regenerative Landscape Villages")
st.markdown("""
<div style="
    background: linear-gradient(90deg, #1f3b73, #145da0);
    padding: 12px 20px;
    border-radius: 10px;
    color: white;
    font-size: 18px;
    margin-bottom: 15px;">
    🌿 RLV Monitoring & Planning Portal | Integrated Livelihood & Resource Dashboard
</div>
""", unsafe_allow_html=True)

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

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🏠 Total HH", df["Total HHs"].sum())
    col2.metric("👥 Population", df["population"].sum())
    col3.metric("💉 Animals Immunized", df["Total animals immunized"].sum())
    col4.metric("⚠️ Mortality", df["Mortality"].sum())

    st.markdown("### 📍 GP Wise Summary")

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
    st.subheader("🐟 Fisheries")
    f_profile_ws = client.open_by_key(SHEET_ID).worksheet("village profile")
    f_plan_ws    = client.open_by_key(SHEET_ID).worksheet("village plan")

    df_f_profile = pd.DataFrame(f_profile_ws.get_all_records())
    df_f_plan    = pd.DataFrame(f_plan_ws.get_all_records())
    
    df_f_profile = df_f_profile[[
    "mandal","panchayath","village",
    "Total HHs",
    "HHs owning ponds",
    "No of community ponds",
    "No of ponds under fisheries",
    "How many ponds converted in to eco farmponds",
    "Total water spread are of the ponds_acr"
]]
    df_f_plan = df_f_plan[[
    "mandal","panchayath","village",
    "New farmponds proposed 10x10m (nos)",
    "New farmponds proposed 15x15m (nos)",
    "New farmponds proposed 20x20m (nos)",
    "New farmponds proposed 40x40m (nos)"
]]
    df_fish = df_f_profile.merge(
    df_f_plan,
    on=["mandal","panchayath","village"],
    how="left"
).fillna(0)
    mandal = st.selectbox("Select Mandal",["All"]+sorted(df_fish["mandal"].unique()))
    if mandal!="All":
        df_fish = df_fish[df_fish["mandal"]==mandal]

    st.markdown("### Village Wise")
    st.dataframe(df_fish)
    
    st.markdown("GP Wise Summary")
    
    gp_summary = df_fish.groupby("panchayath").agg({
        "village":"nunique",
        "Total HHs":"sum",
        "HHs owning ponds":"sum",
        "No of community ponds":"sum",
        "No of ponds under fisheries":"sum",
        "How many ponds converted in to eco farmponds":"sum",
        "Total water spread are of the ponds_acr":"sum",
        "New farmponds proposed 10x10m (nos)":"sum",
        "New farmponds proposed 15x15m (nos)":"sum",
        "New farmponds proposed 20x20m (nos)":"sum",
        "New farmponds proposed 40x40m (nos)":"sum"
    }).reset_index()

    st.dataframe(gp_summary)
    st.download_button("Download GP Wise Excel", gp_summary.to_csv(index=False), "fisheries.csv")

    st.markdown("Mandal Wise Summary")                   
    mandal_summary = df_fish.groupby("mandal").agg({
        "panchayath":"nunique",
        "village":"nunique",
        "Total HHs":"sum",
        "HHs owning ponds":"sum",
        "No of community ponds":"sum",
        "No of ponds under fisheries":"sum",
        "How many ponds converted in to eco farmponds":"sum",
        "Total water spread are of the ponds_acr":"sum",
        "New farmponds proposed 10x10m (nos)":"sum",
        "New farmponds proposed 15x15m (nos)":"sum",
        "New farmponds proposed 20x20m (nos)":"sum",
        "New farmponds proposed 40x40m (nos)":"sum"
    }).reset_index()

    st.dataframe(mandal_summary)
    st.download_button("Download Mandal Summary", mandal_summary.to_csv(index=False), "fisheries.csv")
    pass

elif menu == "Land Development":

    st.subheader("🌱 Land Development")

    # --- Load sheets ---
    profile_ws = client.open_by_key(SHEET_ID).worksheet("village profile")
    plan_ws    = client.open_by_key(SHEET_ID).worksheet("village plan")

    df_profile = pd.DataFrame(profile_ws.get_all_records())
    df_plan    = pd.DataFrame(plan_ws.get_all_records())

    # --- Clean column names (removes hidden spaces) ---
    df_profile.columns = df_profile.columns.str.strip()
    df_plan.columns    = df_plan.columns.str.strip()

    # --- Required PROFILE columns ---
    profile_cols = [
        "mandal","panchayath","village",
        "mettu_total_land_acr",
        "coffee_cashew_land_acr",
        "podu_total_land_acr"
    ]

    df_profile = df_profile.reindex(columns=profile_cols)

    # --- Required PLAN columns ---
    plan_cols = [
        "mandal","panchayath","village",

        # METTU
        "mettu_earthen_bunds_cum",
        "mettu_stone_bunding_cum",
        "mettu_wat_cum",
        "mettu_land_leveling_cum",

        # COFFEE
        "coffee_trench_cum",
        "coffee_stone_bunding_cum",
        "coffee_bench_terracing_cum",

        # PODU
        "podu_sgt_cum",
        "podu_cct_cum",
        "podu_pebble_bunding_cum",
        "podu_plantation_acr",

        # PASTURE
        "pasture_land_development_acr",

        # MGNREGA
        "plans_submitted_mgnrega"
    ]

    df_plan = df_plan.reindex(columns=plan_cols)

    # --- Merge profile + plan ---
    df = df_profile.merge(
        df_plan,
        on=["mandal","panchayath","village"],
        how="left"
    ).fillna(0)

    # --- Mandal Filter ---
    mandal = st.selectbox("Select Mandal", ["All"] + sorted(df["mandal"].dropna().unique()))
    if mandal != "All":
        df = df[df["mandal"] == mandal]

    # ======================
    # VILLAGE WISE TABLE
    # ======================
    st.markdown("### 🏘️ Village Wise Land Development")
    st.dataframe(df)

    # ======================
    # PANCHAYATH SUMMARY
    # ======================

    st.markdown("### 🏡 Panchayath Wise Summary")

    df["mgnrega_yes"] = (
        df["plans_submitted_mgnrega"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("yes")
        .astype(int)
    )

    gp_summary = df.groupby("panchayath").agg({
        "village": "nunique",

        "mettu_total_land_acr": "sum",
        "mettu_earthen_bunds_cum": "sum",
        "mettu_stone_bunding_cum": "sum",
        "mettu_wat_cum": "sum",
        "mettu_land_leveling_cum": "sum",

        "coffee_cashew_land_acr": "sum",
        "coffee_trench_cum": "sum",
        "coffee_stone_bunding_cum": "sum",
        "coffee_bench_terracing_cum": "sum",

        "podu_total_land_acr": "sum",
        "podu_sgt_cum": "sum",
        "podu_cct_cum": "sum",
        "podu_pebble_bunding_cum": "sum",
        "podu_plantation_acr": "sum",

        "pasture_land_development_acr": "sum",

        "mgnrega_yes": "sum"
    }).reset_index()

    st.dataframe(gp_summary)

    st.download_button(
        "Download Panchayath Report",
        gp_summary.to_csv(index=False),
        "land_development_gp.csv"
    )

    # ======================
    # MANDAL SUMMARY
    # ======================

    st.markdown("### 🗺️ Mandal Wise Summary")

    mandal_summary = df.groupby("mandal").agg({
        "panchayath": "nunique",
        "village": "nunique",

        "mettu_total_land_acr": "sum",
        "coffee_cashew_land_acr": "sum",
        "podu_total_land_acr": "sum",
        "pasture_land_development_acr": "sum",

        "mettu_earthen_bunds_cum": "sum",
        "coffee_trench_cum": "sum",
        "podu_sgt_cum": "sum",

        "mgnrega_yes": "sum"
    }).reset_index()

    st.dataframe(mandal_summary)

    st.download_button(
        "Download Mandal Report",
        mandal_summary.to_csv(index=False),
        "land_development_mandal.csv"
    )
    pass

elif menu == "Migration":
    st.subheader("🧳 Migration")
        
    mig_ws = client.open_by_key(SHEET_ID).worksheet("village profile")
    df_mig = pd.DataFrame(mig_ws.get_all_records())
    df_mig = df_mig[[
        "mandal","panchayath","village",
        "Total HHs",
        "Total no of land less HHs",
        "No of HHs not having Job cards",
        "HHs going for seasonal migraion",
        "Average no of days in a year going for migraion",
        "Type of work during the migration",
        "Average earning per annum per family"
    ]].fillna(0)

    mandal = st.selectbox("Select Mandal",["All"]+sorted(df_mig["mandal"].unique()))
    if mandal!="All":
        df_mig = df_mig[df_mig["mandal"]==mandal]

    st.markdown("### Village Wise")
    st.dataframe(df_mig)

    st.markdown("### Panchayath Wise Summary")
    
    gp_summary = df_mig.groupby("panchayath").agg({
        "village":"nunique",
        "Total HHs":"sum",
        "Total no of land less HHs":"sum",
        "No of HHs not having Job cards":"sum",
        "HHs going for seasonal migraion":"sum",
        "Average no of days in a year going for migraion":"sum",
        "Average earning per annum per family":"sum"
    }).reset_index()

    st.dataframe(gp_summary)
    st.download_button("Download GP Summary", gp_summary.to_csv(index=False),"migration_gp.csv")

    st.markdown("### Mandal Wise Summary")

    mandal_summary = df_mig.groupby("mandal").agg({
        "panchayath":"nunique",
        "village":"nunique",
        "Total HHs":"sum",
        "Total no of land less HHs":"sum",
        "No of HHs not having Job cards":"sum",
        "HHs going for seasonal migraion":"sum",
        "Average no of days in a year going for migraion":"sum",
        "Average earning per annum per family":"sum"
    }).reset_index()

    st.dataframe(mandal_summary)
    st.download_button("Download Mandal Summary", mandal_summary.to_csv(index=False),"migration_mandal.csv")
    pass

elif menu == "Farm mechanization":

    st.subheader("🚜 Farm Mechanization")

    profile_ws = client.open_by_key(SHEET_ID).worksheet("village profile")
    plan_ws    = client.open_by_key(SHEET_ID).worksheet("village plan")

    df_profile = pd.DataFrame(profile_ws.get_all_records())
    df_plan    = pd.DataFrame(plan_ws.get_all_records())

    df_profile.columns = df_profile.columns.str.strip()
    df_plan.columns    = df_plan.columns.str.strip()

    # Select required columns
    df_profile = df_profile[[
        "mandal","panchayath","village",

        "farmeasy_Power_weeder_available","farmeasy_Power_weeder_users",
        "farmeasy_Cycle_weeder_available","farmeasy_Cycle_weeder_users",
        "farmeasy_Plastic_drums_available","farmeasy_Plastic_drums_users",
        "farmeasy_Cono_Weeder_available","farmeasy_Cono_Weeder_users",
        "farmeasy_Sprayers_available","farmeasy_Sprayers_users",
        "farmeasy_Power_sprayers_available","farmeasy_Power_sprayers_users",
        "farmeasy_Taurpalin_available","farmeasy_Taurpalin_users",
        "farmeasy_Graders_available","farmeasy_Graders_users",
        "farmeasy_Power_tiller_available","farmeasy_Power_tiller_users",
        "farmeasy_Tractor_available","farmeasy_Tractor_users",
        "farmeasy_Coffee_pulper_available","farmeasy_Coffee_pulper_users",
        "farmeasy_Pepper_thresher_available","farmeasy_Pepper_thresher_users",
        "farmeasy_Multigrain_thresher_available","farmeasy_Multigrain_thresher_users",
        "farmeasy_Turmeric_polisher_available","farmeasy_Turmeric_polisher_users",
        "farmeasy_Turmeric_boiler_available","farmeasy_Turmeric_boiler_users",
        "farmeasy_asc_businessplan",
        "farmeasy_asc"
    ]]

    df_plan = df_plan[[
        "mandal","panchayath","village",

        "farmeasy_Power_weeder_required",
        "farmeasy_Cycle_weeder_required",
        "farmeasy_Plastic_drums_required",
        "farmeasy_Cono_Weeder_required",
        "farmeasy_Sprayers_required",
        "farmeasy_Power_sprayers_required",
        "farmeasy_Taurpalin_required",
        "farmeasy_Graders_required",
        "farmeasy_Power_tiller_required",
        "farmeasy_Tractor_required",
        "farmeasy_Coffee_pulper_required",
        "farmeasy_Pepper_thresher_required",
        "farmeasy_Multigrain_thresher_required",
        "farmeasy_Turmeric_polisher_required",
        "farmeasy_Turmeric_boiler_required"
    ]]

    df = df_profile.merge(df_plan, on=["mandal","panchayath","village"], how="left").fillna(0)

    # Convert yes/no to counts
    df["asc_businessplan_yes"] = df["farmeasy_asc_businessplan"].astype(str).str.lower().eq("yes").astype(int)
    df["asc_yes"] = df["farmeasy_asc"].astype(str).str.lower().eq("yes").astype(int)

    mandal = st.selectbox("Select Mandal", ["All"] + sorted(df["mandal"].unique()))
    if mandal != "All":
        df = df[df["mandal"] == mandal]

    st.markdown("### Village Wise")
    st.dataframe(df)

    st.markdown("### Panchayath Wise Summary")

    gp_summary = df.groupby("panchayath").agg({
        "village":"nunique",
        "farmeasy_Power_weeder_available":"sum",
        "farmeasy_Power_weeder_users":"sum",
        "farmeasy_Power_weeder_required":"sum",
        "farmeasy_Tractor_available":"sum",
        "farmeasy_Tractor_users":"sum",
        "farmeasy_Tractor_required":"sum",
        "asc_businessplan_yes":"sum",
        "asc_yes":"sum"
    }).reset_index()

    st.dataframe(gp_summary)
    st.download_button("Download GP Report", gp_summary.to_csv(index=False), "farm_mech_gp.csv")

    st.markdown("### Mandal Wise Summary")

    mandal_summary = df.groupby("mandal").agg({
        "panchayath":"nunique",
        "village":"nunique",
        "farmeasy_Power_weeder_available":"sum",
        "farmeasy_Power_weeder_users":"sum",
        "farmeasy_Power_weeder_required":"sum",
        "farmeasy_Tractor_available":"sum",
        "farmeasy_Tractor_users":"sum",
        "farmeasy_Tractor_required":"sum",
        "asc_businessplan_yes":"sum",
        "asc_yes":"sum"
    }).reset_index()

    st.dataframe(mandal_summary)
    st.download_button("Download Mandal Report", mandal_summary.to_csv(index=False), "farm_mech_mandal.csv")
    pass

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
        "Total land under NF practice_acre",
        "Is business plan developed",
        "Name of the BRC entrepreneur",
        "No of farmers accessing NF inputs",
        "Extent covered under BRC_acres",
        "No of villages accessing NF inputs"
    ]]

    df_nf1 = df_nf1[[
        "mandal","panchayath","village"
    ]]

    df_nf2 = df_nf2[[
        "mandal","panchayath","village"
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
    

    






































































