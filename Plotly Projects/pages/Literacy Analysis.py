import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from data_utils import load_data, safe_weighted_rate

st.set_page_config(page_title="Literacy Analysis", page_icon="📚", layout="wide")
df = load_data()

st.title("Literacy Analysis")
rows = []
for state, group in df.groupby("State"):
    rows.append({
        "State": state,
        "Literacy_Rate": safe_weighted_rate(group, "Literate", "Population"),
        "Male_Rate": safe_weighted_rate(group, "Male_Literate", "Male"),
        "Female_Rate": safe_weighted_rate(group, "Female_Literate", "Female"),
        "Population": group["Population"].sum(),
    })
state_literacy = pd.DataFrame(rows)

selected_states = st.multiselect(
    "Filter states",
    sorted(state_literacy["State"]),
    default=[],
    placeholder="All states",
)
shown = state_literacy[
    state_literacy["State"].isin(selected_states)
] if selected_states else state_literacy

top_col, gap_col, bottom_col = st.columns([1, 0.15, 1])
top_col.metric("Highest literacy rate", shown.loc[shown["Literacy_Rate"].idxmax(), "State"])
top_col.metric("National weighted rate", f"{safe_weighted_rate(df, 'Literate', 'Population'):.1f}%")
bottom_col.metric("Lowest literacy rate", shown.loc[shown["Literacy_Rate"].idxmin(), "State"])

rate_long = shown.melt(
    id_vars="State",
    value_vars=["Male_Rate", "Female_Rate"],
    var_name="Gender",
    value_name="Literacy Rate",
)
rate_long["Gender"] = rate_long["Gender"].str.replace("_Rate", "")
fig = px.bar(
    rate_long.sort_values(["State", "Literacy Rate"]),
    x="State",
    y="Literacy Rate",
    color="Gender",
    barmode="group",
    title="Male and female literacy by state",
)
fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)
left.plotly_chart(
    px.histogram(df, x="Literacy_Rate", nbins=20, title="District literacy distribution"),
    width="stretch",
)
right.plotly_chart(
    px.scatter(
        df,
        x="Literate_Education",
        y="Illiterate_Education",
        color="State",
        hover_name="District",
        size="Population",
        title="Literate vs illiterate population by district",
    ),
    width="stretch",
)

st.subheader("State literacy summary")
st.dataframe(shown.sort_values("Literacy_Rate", ascending=False), width="stretch", hide_index=True)