import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("sheet-access.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_key("1pq1_1H3Y87D2jWGaOMVM9ypR0039RkQnaW0h2pFAxqs").sheet1
df = pd.DataFrame(sheet.get_all_records())

st.title("Habitation-wise Livestock MEL Dashboard")

mandal = st.selectbox("Select Mandal", ["All"] + sorted(df["Mandal name"].unique()))

if mandal != "All":
    df = df[df["Mandal name"] == mandal]

st.dataframe(df)

st.metric("Total HH", df["no of HH"].sum())
st.metric("Total Population", df["population"].sum())
st.metric("Animals Immunized", df["Total animals immunized"].sum())
st.metric("Animals Dewormed", df["Total animals Dewormed"].sum())
st.metric("Total Mortality", df["Mortality"].sum())
st.subheader("GP Wise Summary")

gp_summary = df.groupby("Panchayath name").agg({
    "no of HH":"sum",
    "population":"sum",
    "Total animals immunized":"sum",
    "Total animals Dewormed":"sum",
    "Mortality":"sum",
    "no of cattle sheds":"sum",
    "no of sheds rennovated":"sum",
    "no of sheds to be rennovated":"sum"
}).reset_index()
st.dataframe(gp_summary)
st.download_button("Download GP Wise Excel", gp_summary.to_csv(index=False), "GP_Wise_Report.csv")

st.subheader("Mandal Wise Summary")

mandal_summary = df.groupby("Mandal name").agg({
    "no of HH":"sum",
    "population":"sum",
    "Total animals immunized":"sum",
    "Total animals Dewormed":"sum",
    "Mortality":"sum",
    "no of cattle sheds":"sum",
    "no of sheds rennovated":"sum",
    "no of sheds to be rennovated":"sum"
}).reset_index()
st.dataframe(mandal_summary)
st.download_button("Download Mandal Wise Excel", mandal_summary.to_csv(index=False), "Mandal_Wise_Report.csv")

