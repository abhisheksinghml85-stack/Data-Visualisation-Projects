import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from data_utils import load_data

st.set_page_config(page_title="State Comparison", page_icon="⚖️", layout="wide")
df = load_data()

st.title("State Comparison")
states = sorted(df["State"].unique())
selected_states = st.multiselect(
    "Choose states to compare (up to 4)",
    states,
    default=states[:2],
    max_selections=4,
)

if len(selected_states) < 2:
    st.info("Select at least two states to create a comparison.")
    st.stop()

compare_df = df[df["State"].isin(selected_states)].copy()

x_axis = st.selectbox(
    "X-axis",
    ["Population", "Literacy_Rate", "Worker_Rate", "Sex_Ratio", "Urban_Household_Rate"],
)
y_axis = st.selectbox(
    "Y-axis",
    ["Literacy_Rate", "Worker_Rate", "Sex_Ratio", "Urban_Household_Rate", "Population"],
    index=0,
)

fig = px.scatter(
    compare_df,
    x=x_axis,
    y=y_axis,
    color="State",
    size="Population",
    hover_name="District",
    title=f"{y_axis.replace('_', ' ')} vs {x_axis.replace('_', ' ')}",
)
st.plotly_chart(fig, width="stretch")

summary = (
    compare_df.groupby("State", as_index=False)[["Population", "Male", "Female", "Literate", "Workers", "Households"]].sum()
)
summary["Literacy Rate (%)"] = summary["Literate"] / summary["Population"] * 100
summary["Worker Rate (%)"] = summary["Workers"] / summary["Population"] * 100
summary["Sex Ratio"] = summary["Female"] / summary["Male"] * 100
st.subheader("Comparison summary")
st.dataframe(summary.sort_values("Population", ascending=False), width="stretch", hide_index=True)