import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="RLV Planning", layout="wide")

st.title("RLV – Village Planning & Budget")

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(st.secrets["gcp"], scopes=scope)
client = gspread.authorize(creds)

SHEET_ID = "1pq1_1H3Y87D2jWGaOMVM9ypR0039RkQnaW0h2pFAxqs"

profile = pd.DataFrame(client.open_by_key(SHEET_ID).worksheet("village profile").get_all_records())
plan    = pd.DataFrame(client.open_by_key(SHEET_ID).worksheet("village plan").get_all_records())
epra    = pd.DataFrame(client.open_by_key(SHEET_ID).worksheet("epra").get_all_records())
budget  = pd.DataFrame(client.open_by_key(SHEET_ID).worksheet("budget").get_all_records())

st.subheader("Village Wise Livestock Development Plan")

mandal = st.selectbox("Select Mandal", sorted(plan["mandal"].dropna().unique()))
panchayath = st.selectbox("Select Panchayath", sorted(plan[plan["mandal"]==mandal]["panchayath"].unique()))
village = st.selectbox("Select Village", sorted(plan[(plan["mandal"]==mandal) & (plan["panchayath"]==panchayath)]["village"].unique()))

village_plan = plan[(plan["mandal"]==mandal) & (plan["panchayath"]==panchayath) & (plan["village"]==village)]

livestock_budget = budget[budget["Thematic"]=="Large Ruminants"]

final_plan = []

for _,row in livestock_budget.iterrows():
    col = row["Source Column"]
    if col in village_plan.columns:
        qty = village_plan[col].sum()
        if qty > 0:
            cost = qty * row["Unit Cost (Rs)"]
            final_plan.append([row["Name of the work"], row["Unit"], qty, row["Unit Cost (Rs)"], cost])

final_df = pd.DataFrame(final_plan, columns=["Work","Unit","Quantity","Unit Cost","Total Cost"])

st.dataframe(final_df)

st.metric("Total Livestock Budget (₹)", int(final_df["Total Cost"].sum()))

st.download_button("Download Village Livestock DPR", final_df.to_csv(index=False), f"{village}_livestock_dpr.csv")

budget_ws = client.open_by_key(SHEET_ID).worksheet("budget")
df_budget = pd.DataFrame(budget_ws.get_all_records())

plan_ws = client.open_by_key(SHEET_ID).worksheet("village plan")
df_plan = pd.DataFrame(plan_ws.get_all_records())

budget_rows = []

for _, row in df_budget.iterrows():
    source_col = row["Source Column"]
    unit_cost  = row["Unit Cost (Rs)"]
    work_name  = row["Name of the work"]
    thematic   = row["Thematic"]

    if source_col not in df_plan.columns:
        continue

    temp = df_plan.copy()
    temp["Units"] = pd.to_numeric(temp[source_col], errors="coerce").fillna(0)
    temp["Total Cost"] = temp["Units"] * unit_cost
    temp["Work"] = work_name
    temp["Thematic"] = thematic

    budget_rows.append(temp[[
        "mandal","panchayath","village",
        "Work","Thematic","Units","Total Cost"
    ]])

df_budget_calc = pd.concat(budget_rows, ignore_index=True)

theme_budget = df_budget_calc.groupby("Thematic").agg(
    Total_Cost=("Total Cost","sum")
).reset_index()

fig_theme = px.pie(theme_budget,
                   names="Thematic",
                   values="Total_Cost",
                   title="Budget Share by Thematic")
st.plotly_chart(fig_theme, use_container_width=True)

top10 = df_budget_calc.groupby("Work").agg(
    Total_Cost=("Total Cost","sum")
).reset_index().sort_values("Total_Cost", ascending=False).head(10)

fig_top = px.bar(top10,
                 x="Work",
                 y="Total_Cost",
                 title="Top 10 High Cost Interventions")
st.plotly_chart(fig_top, use_container_width=True)

village_budget = df_budget_calc.groupby("village").agg(
    Budget=("Total Cost","sum")
).reset_index()

fig_village = px.bar(village_budget,
                     x="village", y="Budget",
                     title="Village-wise Budget Distribution")
st.plotly_chart(fig_village, use_container_width=True)

# -------------------------------
# THEME FILTER (APPLIES TO ALL BELOW)
# -------------------------------
st.markdown("---")
st.subheader("Filter Budget by Thematic")

theme_selected = st.selectbox(
    "Select Thematic",
    ["All"] + sorted(df_budget_calc["Thematic"].dropna().unique())
)

if theme_selected != "All":
    df_budget_calc = df_budget_calc[df_budget_calc["Thematic"] == theme_selected]

gp_budget = df_budget_calc.groupby("panchayath").agg(
    Budget=("Total Cost","sum"),
    Villages=("village","nunique")
).reset_index()

fig_gp = px.scatter(gp_budget,
                    x="Villages", y="Budget",
                    size="Budget",
                    hover_name="panchayath",
                    title="GP Coverage vs Budget")
st.plotly_chart(fig_gp, use_container_width=True)

st.subheader("Village Wise Budget")
st.dataframe(df_budget_calc)

gp_budget = df_budget_calc.groupby(["mandal","panchayath","Work"]).agg(
    Units=("Units","sum"),
    Total_Cost=("Total Cost","sum")
).reset_index()

st.subheader("GP Wise Budget Summary")
st.dataframe(gp_budget)
st.download_button("Download GP Budget", gp_budget.to_csv(index=False), "gp_budget.csv")

mandal_budget = df_budget_calc.groupby(["mandal","Work"]).agg(
    Units=("Units","sum"),
    Total_Cost=("Total Cost","sum")
).reset_index()

st.subheader("Mandal Wise Budget Summary")
st.dataframe(mandal_budget)
st.download_button("Download Mandal Budget", mandal_budget.to_csv(index=False), "mandal_budget.csv")
