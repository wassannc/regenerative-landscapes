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

1. DEMOGRAPHICS
Total Households: {row.get('Total HHs',0)}

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
    doc.add_heading("Village Development Report", 0)

    # TABLE
    table = doc.add_table(rows=6, cols=2)
    table.style = "Table Grid"

    location = f"{row.get('village_gps-Latitude','')}, {row.get('village_gps-Longitude','')}"

    data = [
        ("Village", village),
        ("Location (Lat, Long)", location),
        ("Mandal", row.get("mandal", "")),
        ("Panchayath", row.get("panchayath", "")),
        ("VO Name", row.get("VO_name", "")),
        ("Raithu Seva Kendra", row.get("RSK_name", "")),
        ("Sachivalayam", row.get("RSK_name", ""))
    ]

    for i, (key, val) in enumerate(data):
        table.rows[i].cells[0].text = str(key)
        table.rows[i].cells[1].text = str(val)

    # ✅ PARAGRAPH (your requirement)
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

    job_yes = row.get("Households-mnregs_cards", 0)
    job_no = row.get("No of HHs not having Job cards", 0)

    # convert safely
    job_yes = int(job_yes) if pd.notna(job_yes) else 0
    job_no = int(job_no) if pd.notna(job_no) else 0

    if school in ["yes", "y"]:
        para = f"""{village} is a small village with a total population of {total_pop} people, comprising {male} males and {female} females across {hh} households. The village has {children_icds} children enrolled in ICDS and {children_school} children attending {school_name}. A kitchen garden is {'available' if kg in ['yes','y'] else 'not available'} at the school. Drinking water in the village is sourced from {water}. In terms of livelihoods, {job_yes} households possess job cards, while {job_no} households do not have access to them."""
    else:
        para = f"""{village} is a small village with a total population of {total_pop} people, comprising {male} males and {female} females across {hh} households. The village has {children_icds} children enrolled in ICDS; however, there is no functioning school currently, and no children are attending school despite the presence of a {school_name}. Drinking water in the village is sourced from {water}. In terms of livelihoods, {job_yes} households possess job cards, while {job_no} households do not have access to them."""

    doc.add_paragraph(para)

    # EXISTING TEXT BELOW
    doc.add_paragraph(text)

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


