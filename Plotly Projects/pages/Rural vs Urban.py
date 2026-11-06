import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from data_utils import fmt_number, load_data

st.set_page_config(page_title="Rural and Urban Analysis", page_icon="🏘️", layout="wide")
df = load_data()

st.title("Rural vs Urban Households")
st.caption("This dataset reports household counts in rural and urban areas, not urban or rural population.")

rural = df["Rural_Households"].sum()
urban = df["Urban_Households"].sum()
c1, c2, c3 = st.columns(3)
c1.metric("Rural households", fmt_number(rural))
c2.metric("Urban households", fmt_number(urban))
c3.metric("Urban share", f"{urban / (rural + urban) * 100:.1f}%")

households = pd.DataFrame({"Area": ["Rural", "Urban"], "Households": [rural, urban]})
left, right = st.columns(2)
left.plotly_chart(
    px.pie(households, names="Area", values="Households", hole=0.45, title="Household distribution"),
    width="stretch",
)

state_households = df.groupby("State", as_index=False)[["Rural_Households", "Urban_Households"]].sum()
state_households["Urban Share (%)"] = (
    state_households["Urban_Households"]
    / (state_households["Rural_Households"] + state_households["Urban_Households"])
    * 100
)
right.plotly_chart(
    px.bar(
        state_households.sort_values("Urban Share (%)"),
        x="Urban Share (%)",
        y="State",
        orientation="h",
        title="Urban share by state",
    ),
    width="stretch",
)

districts = df.assign(
    Urban_Household_Rate=df["Urban_Household_Rate"]
).sort_values("Urban_Household_Rate", ascending=False)
st.plotly_chart(
    px.scatter(
        districts.head(100),
        x="Population",
        y="Urban_Household_Rate",
        size="Households",
        color="State",
        hover_name="District",
        title="Population and urban household rate (highest urban districts shown)",
    ),
    width="stretch",
)