import streamlit as st
import pandas as pd
from docx import Document
from io import BytesIO

st.title("📄 Village Reports")
df_profile = load_sheet("village profile")
df_plan = load_sheet("village plan")

village_list = sorted(df_profile["village"].dropna().unique())

selected_village = st.selectbox("Select Village", village_list)
village_list = sorted(df_profile["village"].dropna().unique())

selected_village = st.selectbox("Select Village", village_list)

def generate_report(df_v, df_p, village):

    row = df_v.iloc[0]

    text = f"""
VILLAGE DEVELOPMENT REPORT

Village: {village}
Mandal: {row.get('mandal','')}
Panchayath: {row.get('panchayath','')}

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

def create_doc(text):
    doc = Document()

    for line in text.split("\n"):
        doc.add_paragraph(line)

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


