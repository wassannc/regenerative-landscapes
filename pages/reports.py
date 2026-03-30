import streamlit as st
import pandas as pd
from docx import Document
from io import BytesIO
from dashboard import load_sheet

st.title("📄 Village Reports")

df_profile = load_sheet("village profile")
df_plan = load_sheet("village plan")

village_list = sorted(df_profile["village"].dropna().unique())
selected_village = st.selectbox("Select Village", village_list)

df_v = df_profile[df_profile["village"] == selected_village]
df_p = df_plan[df_plan["village"] == selected_village]


# ---------------- REPORT TEXT ----------------
def generate_report(df_v, df_p, village):

    text = f"""
----------------------------------------

2. AGRICULTURE & LAND
The village depends on agriculture and allied activities.

----------------------------------------

3. NATURAL RESOURCES
Water bodies, land, and vegetation support livelihoods.

----------------------------------------

4. IRRIGATION
Limited irrigation sources are available.

----------------------------------------

5. MIGRATION
Seasonal migration exists due to lack of employment.

----------------------------------------

6. LIVESTOCK
Livestock contributes to income.

----------------------------------------

7. REQUIRED WORKS
"""

    for col in df_p.columns:
        if "required" in col.lower():
            val = df_p[col].sum()
            if val > 0:
                text += f"\n- {col.replace('_',' ')}: {int(val)}"

    text += "\n\n----------------------------------------\nConclusion: Development interventions required."

    return text


# ---------------- DOC CREATION ----------------
def create_doc(text, df_v, village):

    doc = Document()
    row = df_v.iloc[0]

    # TITLE
    doc.add_heading("Village Report", 0)

    # LOCATION
    location = f"{row.get('village_gps-Latitude','')}, {row.get('village_gps-Longitude','')}"

    # TABLE
    data = [
        ("Village", village),
        ("Location (Lat, Long)", location),
        ("Mandal", row.get("mandal", "")),
        ("Panchayath", row.get("panchayath", "")),
        ("VO Name", row.get("VO_name", "")),
        ("Raithu Seva Kendra", row.get("RSK_name", "")),
        ("Sachivalayam", row.get("RSK_name", ""))
    ]

    table = doc.add_table(rows=len(data), cols=2)
    table.style = "Table Grid"

    for i, (key, val) in enumerate(data):
        table.rows[i].cells[0].text = str(key)
        table.rows[i].cells[1].text = str(val)

    # SPACE
    doc.add_paragraph("")

    # -------- VALUES --------
    total_pop = row.get("population", "NA")
    male = row.get("Households-male", "NA")
    female = row.get("Households-femlae", "NA")
    hh = row.get("Total HHs", "NA")

    children_icds = row.get("children_icds", "NA")
    children_school = row.get("children_school", "NA")

    school = str(row.get("school", "")).strip().lower()
    school_name = row.get("school_name", "")
    kg = str(row.get("kg_school", "")).strip().lower()

    water = row.get("drinking_water_source", "NA")

    # JOB CARDS
    job_yes = pd.to_numeric(row.get("Households-mnregs_cards", 0), errors="coerce")
    job_no = pd.to_numeric(row.get("No of HHs not having Job cards", 0), errors="coerce")

    job_yes = int(job_yes) if pd.notna(job_yes) else 0
    job_no = int(job_no) if pd.notna(job_no) else 0

    # MIGRATION
    mig_hhs = pd.to_numeric(row.get("HHs going for seasonal migraion", 0), errors="coerce")
    mig_members = pd.to_numeric(row.get("Households-migration_members", 0), errors="coerce")
    mig_days = pd.to_numeric(row.get("Average no of days in a year going for migraion", 0), errors="coerce")
    mig_income = pd.to_numeric(row.get("Average earning per annum per family", 0), errors="coerce")

    mig_hhs = int(mig_hhs) if pd.notna(mig_hhs) else 0
    mig_members = int(mig_members) if pd.notna(mig_members) else 0
    mig_days = int(mig_days) if pd.notna(mig_days) else 0
    mig_income = int(mig_income) if pd.notna(mig_income) else 0

    # -------- PARAGRAPH --------
    if school in ["yes", "y"]:
        para = f"""{village} is a small village with a total population of {total_pop} people, comprising {male} males and {female} females across {hh} households. The village has {children_icds} children enrolled in ICDS and {children_school} children attending {school_name}. A kitchen garden is {'available' if kg in ['yes','y'] else 'not available'} at the school. Drinking water in the village is sourced from {water}. In terms of livelihoods, {job_yes} households possess job cards, while {job_no} households do not have access to them.

{mig_hhs} households undertake seasonal migration involving {mig_members} members. On average, migration lasts for about {mig_days} days per year, with an average annual earning of ₹{mig_income} per family."""
    else:
        para = f"""{village} is a small village with a total population of {total_pop} people, comprising {male} males and {female} females across {hh} households. The village has {children_icds} children enrolled in ICDS; however, there is no functioning school currently, and no children are attending school despite the presence of a {school_name}. Drinking water in the village is sourced from {water}. In terms of livelihoods, {job_yes} households possess job cards, while {job_no} households do not have access to them.

{mig_hhs} households undertake seasonal migration involving {mig_members} members. On average, migration lasts for about {mig_days} days per year, with an average annual earning of ₹{mig_income} per family."""

    doc.add_paragraph(para)
    # -------- COMMUNITY TABLE --------
    doc.add_heading("Community-wise Households", 1)

    others_name = row.get("Households-community_others", "Others")

    raw_data = [
        ("Kotia", row.get("Households-Kotia", 0)),
        ("Porja", row.get("Households-Porja", 0)),
        ("Kondadora", row.get("Households-Kondadora", 0)),
        ("Nookadora", row.get("Households-Nookadora", 0)),
        ("Kammari", row.get("Households-Kammari", 0)),
        ("Bhagatha", row.get("Households-Bhagatha", 0)),
        ("Valmiki", row.get("Households-Valmiki", 0)),
        ("Kondhu PVTG", row.get("Households-Kondu_PVTG", 0)),
        (others_name, row.get("Households-community_others_hhs", 0)),
    ]

    clean_data = []
    total = 0

    for name, val in raw_data:
        val = pd.to_numeric(val, errors="coerce")
        val = int(val) if pd.notna(val) else 0

        if val > 0:   # ✅ skip zero rows
            clean_data.append((name, val))
            total += val

    # always add total
    clean_data.append(("Total", total))

    # create table
    table2 = doc.add_table(rows=len(clean_data), cols=2)
    table2.style = "Table Grid"

    for i, (name, val) in enumerate(clean_data):
        table2.rows[i].cells[0].text = str(name)
        table2.rows[i].cells[1].text = str(val)

# -------- AGRICULTURE: LAND DETAILS --------
    doc.add_heading("Agriculture - Land Details", 1)

    land_data_raw = [
        ("Mettu Land (acres)", row.get("mettu_total_land_acr", 0)),
        ("Pallam Land (acres)", row.get("Total pallam land", 0)),
        ("Podu Land (acres)", row.get("podu_total_land_acr", 0)),
        ("Banjaru Land (acres)", row.get("banjaru-acres", 0)),
        ("Coffee/Cashew Land (acres)", row.get("coffee_cashew_land_acr", 0)),
        ("Total Land (acres)", row.get("Total land in the village_acre", 0)),
    ]

    land_data = []

    for name, val in land_data_raw:
        val = pd.to_numeric(val, errors="coerce")
        val = int(val) if pd.notna(val) else 0

        if val > 0:
            land_data.append((name, val))

    # create table only if data exists
    if land_data:
        table3 = doc.add_table(rows=len(land_data), cols=2)
        table3.style = "Table Grid"

        for i, (name, val) in enumerate(land_data):
            table3.rows[i].cells[0].text = name
            table3.rows[i].cells[1].text = str(val)
    else:
        doc.add_paragraph("No land data available.")

    # -------- AGRICULTURE PARAGRAPH --------
    doc.add_paragraph("")

    farming_hhs = pd.to_numeric(row.get("Households-farming_hhs", 0), errors="coerce")
    landless = pd.to_numeric(row.get("Total no of land less HHs", 0), errors="coerce")

    kharif_farmers = pd.to_numeric(row.get("Crops-kharif_farmers", 0), errors="coerce")
    kharif_acres = pd.to_numeric(row.get("Crops-kharif_acres", 0), errors="coerce")

    rabi_farmers = pd.to_numeric(row.get("Crops-rabi_farmers", 0), errors="coerce")
    rabi_acres = pd.to_numeric(row.get("Crops-rabi_acres", 0), errors="coerce")

    irrig_sources = row.get("Crops-irrigation_sources", "NA")
    kharif_crops = row.get("Crops-crops_kharif", "NA")
    rabi_crops = row.get("Crops-crops_rabi", "NA")

    rainfed = pd.to_numeric(row.get("Crops-rainfed_acrs", 0), errors="coerce")
    irrigated = pd.to_numeric(row.get("Crops-irrigated_acrs", 0), errors="coerce")

    new_irrig = row.get("Crops-new_irrigation_source", "NA")
    irrig_type = row.get("Crops-potential_irrigation", "NA")

    grazing = row.get("Crops-Grazing", "NA")
    ntfp = row.get("Crops-NTFP", "NA")

# safe int conversion
    def safe_int(val):
        return int(val) if pd.notna(val) else 0

    farming_hhs = safe_int(farming_hhs)
    landless = safe_int(landless)
    kharif_farmers = safe_int(kharif_farmers)
    kharif_acres = safe_int(kharif_acres)
    rabi_farmers = safe_int(rabi_farmers)
    rabi_acres = safe_int(rabi_acres)
    rainfed = safe_int(rainfed)
    irrigated = safe_int(irrigated)

    agri_para = f"""Agriculture is the primary livelihood activity in the village, with {farming_hhs} households engaged in farming, while {landless} households are landless. 

    During the Kharif season, {kharif_farmers} farmers cultivate crops over an extent of {kharif_acres} acres, mainly growing {kharif_crops}. In the Rabi season, {rabi_farmers} farmers cultivate crops over {rabi_acres} acres, with crops such as {rabi_crops}. 

    The village largely depends on rainfed agriculture covering {rainfed} acres, with only {irrigated} acres under irrigation. Major irrigation sources include {irrig_sources}. There is {'availability' if str(new_irrig).lower()=='yes' else 'no availability'} of new irrigation sources, and potential irrigation options include {irrig_type}. 

    Livestock grazing follows a {grazing} system, and Non-Timber Forest Products (NTFP) such as {ntfp} are available in the village, contributing to livelihoods."""

    doc.add_paragraph(agri_para)
    
    # -------- OTHER SECTIONS --------
    doc.add_paragraph(text)

    # SAVE
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# ---------------- BUTTON ----------------
if st.button("Generate Report"):

    report = generate_report(df_v, df_p, selected_village)
    file = create_doc(report, df_v, selected_village)

    st.download_button(
        "Download Report",
        data=file,
        file_name=f"{selected_village}_report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    st.text_area("Preview", report, height=400)
