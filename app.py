import plotly.express as px
import streamlit as st

from data_utils import fmt_number, load_data, safe_weighted_rate


st.set_page_config(
    page_title="India Census 2011 Explorer",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

df = load_data()

st.title("India District Census 2011")
st.caption("Interactive demographic and social indicators from the Census of India 2011.")

states = sorted(df["State"].dropna().unique())
selected_state = st.sidebar.selectbox("Explore a state", states)
state_df = df[df["State"] == selected_state].copy()

population = state_df["Population"].sum()
st.metric("Districts in selected state", f"{state_df['District'].nunique():,}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Population", fmt_number(population))
c2.metric("Literacy Rate", f"{safe_weighted_rate(state_df, 'Literate', 'Population'):.1f}%")
c3.metric("Households", fmt_number(state_df["Households"].sum()))
c4.metric("Urban Household Rate", f"{safe_weighted_rate(state_df, 'Urban_Households', 'Households'):.1f}%")

st.subheader("Population Overview")
population_chart = px.bar(
    state_df.sort_values("Population", ascending=False),
    x="District",
    y="Population",
    color="Population",
    title=f"District population in {selected_state}",
    color_continuous_scale="Teal",
)
population_chart.update_layout(xaxis_tickangle=-45)
st.plotly_chart(population_chart, width="stretch")

map_df = state_df[
    state_df["Latitude"].between(-90, 90)
    & state_df["Longitude"].between(-180, 180)
    & (state_df["Latitude"] != 0)
    & (state_df["Longitude"] != 0)
]
if not map_df.empty:
    map_chart = px.scatter_map(
        map_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="District",
        hover_data={"Population": ":,.0f", "Literacy_Rate": ":.1f"},
        size="Population",
        color="Literacy_Rate",
        color_continuous_scale="Viridis",
        zoom=4,
        title=f"District locations and literacy in {selected_state}",
        height=560,
    )
    map_chart.update_layout(map_style="open-street-map")
    st.plotly_chart(map_chart, width="stretch")

st.subheader("Census Data")
display_columns = [
    "District", "Population", "Male", "Female", "Literate",
    "Literacy_Rate", "Workers", "Worker_Rate", "Households",
    "Urban_Households", "SC", "ST",
]
st.dataframe(state_df[display_columns].sort_values("Population", ascending=False), width="stretch", hide_index=True)

with st.expander("About this dashboard"):
    st.markdown(
        "This project combines district-level Census 2011 indicators with district coordinates. "
        "Rates are calculated from counts; multi-district totals use population or household weights."
    )