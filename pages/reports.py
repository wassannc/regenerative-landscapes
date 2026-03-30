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

def generate_report(df_v, df_p, village):

    row = df_v.iloc[0]

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
    
def create_doc(text, df_v, village):

    doc = Document()

    row = df_v.iloc[0]

    # TITLE
    doc.add_heading("Village Report", 0)

    # LOCATION
    location = f"{row.get('village_gps-Latitude','')}, {row.get('village_gps-Longitude','')}"

    # TABLE DATA
    data = [
        ("Village", village),
        ("Location (Lat, Long)", location),
        ("Mandal", row.get("mandal", "")),
        ("Panchayath", row.get("panchayath", "")),
        ("VO Name", row.get("VO_name", "")),
        ("Raithu Seva Kendra", row.get("RSK_name", "")),
        ("Sachivalayam", row.get("RSK_name", ""))
    ]

    # CREATE TABLE
    table = doc.add_table(rows=len(data), cols=2)
    table.style = "Table Grid"

    for i, (key, val) in enumerate(data):
        table.rows[i].cells[0].text = str(key)
        table.rows[i].cells[1].text = str(val)

    # PARAGRAPH
    doc.add_paragraph("")

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
    mig_hhs = pd.to_numeric(row.get("HHs going for seasonal migraion", 0), errors="coerce")
    mig_members = pd.to_numeric(row.get("Households-migration_members", 0), errors="coerce")
    mig_days = pd.to_numeric(row.get("Average no of days in a year going for migraion", 0), errors="coerce")
    mig_income = pd.to_numeric(row.get("Average earning per annum per family", 0), errors="coerce")

    mig_hhs = int(mig_hhs) if pd.notna(mig_hhs) else 0
    mig_members = int(mig_members) if pd.notna(mig_members) else 0
    mig_days = int(mig_days) if pd.notna(mig_days) else 0
    mig_income = int(mig_income) if pd.notna(mig_income) else 0
    
    job_yes = row.get("Households-mnregs_cards", 0)
    job_no = row.get("No of HHs not having Job cards", 0)

    job_yes = pd.to_numeric(row.get("Households-mnregs_cards", 0), errors="coerce")
    job_no = pd.to_numeric(row.get("No of HHs not having Job cards", 0), errors="coerce")

    job_yes = int(job_yes) if pd.notna(job_yes) else 0
    job_no = int(job_no) if pd.notna(job_no) else 0
    
    if school in ["yes", "y"]:
        para = f"""{village} is a small village with a total population of {total_pop} people, comprising {male} males and {female} females across {hh} households. The village has {children_icds} children enrolled in ICDS and {children_school} children attending {school_name}. A kitchen garden is {'available' if kg in ['yes','y'] else 'not available'} at the school. Drinking water in the village is sourced from {water}. In terms of livelihoods, {job_yes} households possess job cards, while {job_no} households do not have access to them."""
        {mig_hhs} households undertake seasonal migration involving {mig_members} members. On average, migration lasts for about {mig_days} days per year, with an average annual earning of ₹{mig_income} per family."""
    else:
        
    # EXISTING TEXT
    doc.add_paragraph(text)

    # SAVE
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer
# button
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


        
    # EXISTING TEXT
    doc.add_paragraph(text)

    # SAVE
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer
# button
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


