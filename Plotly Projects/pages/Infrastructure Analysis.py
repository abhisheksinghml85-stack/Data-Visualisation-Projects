import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from data_utils import load_data

st.set_page_config(page_title="Infrastructure Analysis", page_icon="🏠", layout="wide")
df = load_data()

st.title("Infrastructure and Household Amenities")
st.caption("Explore access to household services across states and districts.")

facilities = {
    "Electric lighting": "Housholds_with_Electric_Lighting",
    "LPG / PNG": "LPG_or_PNG_Households",
    "Internet": "Households_with_Internet",
    "Computer": "Households_with_Computer",
    "Latrine within premises": "Having_latrine_facility_within_the_premises_Total_Households",
}

indicator = st.selectbox("Facility", list(facilities))
column = facilities[indicator]
state_summary = df.groupby("State", as_index=False)[[column, "Households"]].sum()
state_summary["Access Rate (%)"] = (
    state_summary[column] / state_summary["Households"] * 100
).fillna(0)

c1, c2 = st.columns(2)
c1.metric(
    f"Households with {indicator.lower()}",
    f"{df[column].sum():,.0f}",
)
c2.metric(
    "National access rate",
    f"{df[column].sum() / df['Households'].sum() * 100:.1f}%",
)

fig = px.bar(
    state_summary.sort_values("Access Rate (%)", ascending=False),
    x="Access Rate (%)",
    y="State",
    orientation="h",
    title=f"{indicator} access by state",
)
st.plotly_chart(fig, width="stretch")

st.subheader("State access summary")
st.dataframe(
    state_summary.sort_values("Access Rate (%)", ascending=False),
    width="stretch",
    hide_index=True,
)
