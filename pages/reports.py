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

    # ✅ TITLE
    doc.add_heading("Village Development Report", 0)

    # ✅ TABLE (TOP SECTION)
    table = doc.add_table(rows=6, cols=2)
    table.style = "Table Grid"

    location = f"{row.get('village_gps-Latitude','')}, {row.get('village_gps-Longitude','')}"

    data = [
        ("Village", village),
        ("Location (Lat, Long)", location),
        ("Mandal", row.get("mandal", "")),
        ("Panchayath", row.get("panchayath", "")),
        ("Raithu Seva Kendra", row.get("RSK_name", "")),
        ("Sachivalayam", row.get("RSK_name", ""))
    ]

    for i, (key, val) in enumerate(data):
        table.rows[i].cells[0].text = str(key)
        table.rows[i].cells[1].text = str(val)

    # ✅ ADD TEXT BELOW TABLE
    doc.add_paragraph(text)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer
# button
if st.button("Generate Report"):

    report = generate_report(df_v, df_p, selected_village)
    file = create_doc(report)

    st.download_button(
        "Download Report",
        data=file,
        file_name=f"{selected_village}_report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    st.text_area("Preview", report, height=400)


