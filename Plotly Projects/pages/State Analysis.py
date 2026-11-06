import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from data_utils import fmt_number, load_data, safe_weighted_rate

st.set_page_config(page_title="State Analysis", page_icon="🗺️", layout="wide")
df = load_data()

st.title("State-wise Analysis")
metric = st.selectbox(
    "Explore indicator",
    ["Population", "Literacy Rate", "Worker Rate", "Sex Ratio", "Households"],
)

if metric in ["Literacy Rate", "Worker Rate", "Sex Ratio"]:
    rows = []
    for state, group in df.groupby("State"):
        if metric == "Literacy Rate":
            value = safe_weighted_rate(group, "Literate", "Population")
        elif metric == "Worker Rate":
            value = safe_weighted_rate(group, "Workers", "Population")
        else:
            value = group["Female"].sum() / group["Male"].sum() * 100
        rows.append({"State": state, metric: value})
    state_data = pd.DataFrame(rows)
else:
    column = "Households" if metric == "Households" else "Population"
    state_data = df.groupby("State", as_index=False)[column].sum().rename(columns={column: metric})

c1, c2, c3 = st.columns(3)
c1.metric("States and union territories", df["State"].nunique())
c2.metric("Districts", df["District"].nunique())
c3.metric("India population", fmt_number(df["Population"].sum()))

fig = px.bar(
    state_data.nlargest(15, metric),
    x=metric,
    y="State",
    orientation="h",
    text_auto=".1s",
    title=f"Top 15 states/territories by {metric.lower()}",
)
fig.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, width="stretch")

st.subheader("Complete state summary")
population_data = df.groupby("State", as_index=False)[["Population", "Households", "Workers", "Male", "Female"]].sum()
population_data["Literacy Rate (%)"] = population_data["State"].map(
    {state: safe_weighted_rate(group, "Literate", "Population")
     for state, group in df.groupby("State")}
)
population_data["Urban Household Rate (%)"] = population_data["State"].map(
    {state: safe_weighted_rate(group, "Urban_Households", "Households")
     for state, group in df.groupby("State")}
)
st.dataframe(
    population_data.sort_values("Population", ascending=False),
    width="stretch",
    hide_index=True,
)