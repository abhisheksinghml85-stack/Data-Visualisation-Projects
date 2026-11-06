import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from data_utils import fmt_number, load_data

st.set_page_config(page_title="District Explorer", page_icon="🏙️", layout="wide")
df = load_data()

st.title("District Explorer")
st.caption("Search and compare the demographic profile of one district.")

selected_state = st.selectbox("State", sorted(df["State"].unique()))
state_df = df[df["State"] == selected_state]
selected_district = st.selectbox("District", sorted(state_df["District"].unique()))
row = state_df[state_df["District"] == selected_district].iloc[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Population", fmt_number(row["Population"]))
c2.metric("Literacy Rate", f"{row['Literacy_Rate']:.1f}%")
c3.metric("Sex Ratio", f"{row['Sex_Ratio']:.0f} females / 100 males")
c4.metric("Worker Rate", f"{row['Worker_Rate']:.1f}%")

demographics = {
    "Male": row["Male"],
    "Female": row["Female"],
}
education = {
    "Literate": row["Literate"],
    "Illiterate Education": row["Illiterate_Education"],
}
workers = {
    "Main Workers": row["Main_Workers"],
    "Marginal Workers": row["Marginal_Workers"],
}

left, middle, right = st.columns(3)
left.plotly_chart(px.pie(names=demographics.keys(), values=demographics.values(), hole=.55, title="Gender composition"), width="stretch")
middle.plotly_chart(px.pie(names=education.keys(), values=education.values(), hole=.55, title="Literacy composition"), width="stretch")
right.plotly_chart(px.pie(names=workers.keys(), values=workers.values(), hole=.55, title="Worker composition"), width="stretch")

st.subheader("Infrastructure and household access")
facility_columns = [
    ("Electric lighting", "Housholds_with_Electric_Lighting"),
    ("LPG / PNG cooking", "LPG_or_PNG_Households"),
    ("Internet", "Households_with_Internet"),
    ("Computer", "Households_with_Computer"),
    ("Latrine facility", "Having_latrine_facility_within_the_premises_Total_Households"),
]
facility_df = __import__("pandas").DataFrame({
    "Facility": [name for name, _ in facility_columns],
    "Households": [row[column] for _, column in facility_columns],
})
st.bar_chart(facility_df.set_index("Facility"))

selected_columns = [
    "Population", "Male", "Female", "Literate", "Workers", "Main_Workers",
    "Marginal_Workers", "SC", "ST", "Households", "Rural_Households",
    "Urban_Households", "Latitude", "Longitude",
]
st.subheader("District details")
st.dataframe(row[selected_columns].to_frame("Value"), width="stretch")