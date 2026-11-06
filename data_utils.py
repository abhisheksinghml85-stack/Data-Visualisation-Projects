from pathlib import Path
from difflib import get_close_matches

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
CENSUS_FILE = BASE_DIR / "india-districts-census-2011.csv"
LOCATION_FILE = BASE_DIR / "district wise population and centroids.csv"
REQUIRED_CENSUS_COLUMNS = {
    "State name",
    "District name",
    "Population",
    "Male",
    "Female",
    "Literate",
    "Male_Literate",
    "Female_Literate",
    "Workers",
    "Main_Workers",
    "Marginal_Workers",
    "Households",
    "Rural_Households",
    "Urban_Households",
}


def _safe_rate(numerator, denominator):
    numerator = pd.to_numeric(numerator, errors="coerce").fillna(0)
    denominator = pd.to_numeric(denominator, errors="coerce").fillna(0)
    return numerator.div(denominator.where(denominator.ne(0))).mul(100).fillna(0)


def _location_key(value):
    return " ".join(str(value).strip().upper().split())


def _district_key(value):
    key = _location_key(value)
    replacements = (
        (" AND ", " & "),
        ("DISTRICT", ""),
        ("(BHABUA)", ""),
    )
    for old, new in replacements:
        key = key.replace(old, new)
    return "".join(character for character in key if character.isalnum())


@st.cache_data(ttl="1h", show_spinner=False)
def load_data():
    census = pd.read_csv(CENSUS_FILE)
    locations = pd.read_csv(LOCATION_FILE)

    missing = REQUIRED_CENSUS_COLUMNS.difference(census.columns)
    if missing:
        raise ValueError(
            "The census file is missing required columns: "
            + ", ".join(sorted(missing))
        )

    census["State"] = census["State name"].astype(str).str.strip().str.title()
    census["District"] = census["District name"].astype(str).str.strip()
    census["_State_Key"] = census["State"].map(_location_key)
    census["_District_Key"] = census["District"].map(_district_key)

    locations["State"] = locations["State"].astype(str).str.strip()
    locations["District"] = locations["District"].astype(str).str.strip()
    locations["_State_Key"] = locations["State"].map(_location_key)
    locations["_District_Key"] = locations["District"].map(_district_key)
    locations = locations.drop_duplicates(
        subset=["_State_Key", "_District_Key"], keep="first"
    )

    location_columns = [
        "_State_Key",
        "_District_Key",
        "Latitude",
        "Longitude",
        "Population in 2001",
        "Population in 2011",
    ]
    data = census.merge(
        locations[location_columns],
        on=["_State_Key", "_District_Key"],
        how="left",
        validate="one_to_one",
    )

    unmatched = data["Latitude"].isna() | data["Longitude"].isna()
    if unmatched.any():
        location_lookup = {}
        for state_key, state_locations in locations.groupby("_State_Key"):
            location_lookup[state_key] = dict(
                zip(state_locations["_District_Key"], state_locations["District"])
            )

        for index in data.index[data["Latitude"].isna() | data["Longitude"].isna()]:
            district_key = data.at[index, "_District_Key"] if "_District_Key" in data else _district_key(data.at[index, "District"])
            census_state_key = _location_key(data.at[index, "State"])
            candidates = location_lookup.get(census_state_key, {})
            match = get_close_matches(district_key, candidates, n=1, cutoff=0.88)
            if match:
                match_row = locations[
                    (locations["_State_Key"] == census_state_key)
                    & (locations["_District_Key"] == match[0])
                ]
                if not match_row.empty:
                    data.at[index, ["Latitude", "Longitude"]] = match_row.iloc[0][
                        ["Latitude", "Longitude"]
                    ].values
    numeric_columns = data.select_dtypes(include="number").columns
    data[numeric_columns] = data[numeric_columns].fillna(0)

    data["Literacy_Rate"] = _safe_rate(data["Literate"], data["Population"])
    data["Sex_Ratio"] = _safe_rate(data["Female"], data["Male"])
    data["Worker_Rate"] = _safe_rate(data["Workers"], data["Population"])
    data["Female_Literacy_Rate"] = _safe_rate(data["Female_Literate"], data["Female"])
    data["Male_Literacy_Rate"] = _safe_rate(data["Male_Literate"], data["Male"])
    data["SC_Rate"] = _safe_rate(data["SC"], data["Population"])
    data["ST_Rate"] = _safe_rate(data["ST"], data["Population"])
    data["Urban_Household_Rate"] = _safe_rate(
        data["Urban_Households"], data["Households"]
    )

    data["Growth_2001_2011"] = _safe_rate(
        data["Population in 2011"] - data["Population in 2001"],
        data["Population in 2001"],
    )
    data = data.drop(columns=["_State_Key", "_District_Key"])
    return data


def fmt_number(value):
    return f"{float(value):,.0f}"


def safe_weighted_rate(df, numerator, denominator):
    denominator_total = df[denominator].sum()
    if denominator_total == 0:
        return 0.0
    return df[numerator].sum() / denominator_total * 100
