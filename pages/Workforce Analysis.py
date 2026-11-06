import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from data_utils import fmt_number, load_data, safe_weighted_rate

st.set_page_config(page_title="Workforce Analysis", page_icon="👷", layout="wide")
df = load_data()

st.title("Workforce Analysis")
st.caption("Compare worker participation and employment composition across states and districts.")

state_data = []
for state, group in df.groupby("State"):
    state_data.append({
        "State": state,
        "Workers": group["Workers"].sum(),
        "Main Workers": group["Main_Workers"].sum(),
        "Marginal Workers": group["Marginal_Workers"].sum(),
        "Worker Rate (%)": safe_weighted_rate(group, "Workers", "Population"),
    })
summary = pd.DataFrame(state_data)

c1, c2, c3 = st.columns(3)
c1.metric("Working population", fmt_number(df["Workers"].sum()))
c2.metric("Main workers", fmt_number(df["Main_Workers"].sum()))
c3.metric("Marginal workers", fmt_number(df["Marginal_Workers"].sum()))

composition = pd.DataFrame({
    "Worker type": ["Main workers", "Marginal workers"],
    "Population": [df["Main_Workers"].sum(), df["Marginal_Workers"].sum()],
})

left, right = st.columns(2)
left.plotly_chart(
    px.pie(composition, names="Worker type", values="Population", hole=0.55,
           title="Worker composition"),
    width="stretch",
)
right.plotly_chart(
    px.bar(summary.sort_values("Worker Rate (%)", ascending=False),
           x="Worker Rate (%)", y="State", orientation="h",
           title="Worker participation rate by state"),
    width="stretch",
)

st.subheader("State workforce summary")
st.dataframe(
    summary.sort_values("Worker Rate (%)", ascending=False),
    width="stretch",
    hide_index=True,
)
