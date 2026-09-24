"""Data loading, caching, validation, and geographic mapping utilities."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import streamlit as st

# Comprehensive 51-jurisdiction mapping (50 US States + District of Columbia)
STATE_TO_ABBR: Dict[str, str] = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

# Standard chronological calendar month order
MONTH_ORDER: List[str] = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

REQUIRED_COLUMNS: List[str] = [
    "State of Residence",
    "Month",
    "Month Code",
    "Year Code",
    "Sex of Infant",
    "Births",
]


def resolve_data_path() -> Path:
    """Locate the Excel file across local environments and Streamlit Cloud."""
    current_dir = Path.cwd()
    script_dir = Path(__file__).resolve().parent.parent

    candidate_paths = [
        current_dir / "Provisional_Natality_2025_CDC.xlsx",
        current_dir / "data" / "Provisional_Natality_2025_CDC.xlsx",
        script_dir / "Provisional_Natality_2025_CDC.xlsx",
        script_dir / "data" / "Provisional_Natality_2025_CDC.xlsx",
    ]

    for path in candidate_paths:
        if path.is_file():
            return path

    raise FileNotFoundError(
        "Could not find 'Provisional_Natality_2025_CDC.xlsx'. "
        f"Checked candidate locations: {[str(p) for p in candidate_paths]}"
    )


def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Perform data-quality checks on the loaded dataset.

    Returns:
        (is_valid, list_of_warning_or_error_messages)
    """
    messages: List[str] = []

    # Check required columns
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        messages.append(f"Missing required columns: {missing_cols}")

    # Check non-empty
    if df.empty:
        messages.append("The dataset is empty.")

    # Check non-negative births
    if "Births" in df.columns and (df["Births"] < 0).any():
        messages.append("Found negative birth counts in the dataset.")

    # Check state mapping completeness
    if "State of Residence" in df.columns:
        unmapped_states = [
            s for s in df["State of Residence"].unique() if s not in STATE_TO_ABBR
        ]
        if unmapped_states:
            messages.append(f"Unmapped geographies found: {unmapped_states}")

    is_valid = len(messages) == 0
    return is_valid, messages


@st.cache_data(show_spinner="Loading provisional natality dataset...")
def load_data() -> pd.DataFrame:
    """Load and prepare the 2025 CDC Provisional Natality dataset.

    Applies caching to ensure instantaneous dashboard interactions.
    """
    file_path = resolve_data_path()

    # Read the first worksheet
    df = pd.read_excel(file_path, sheet_name=0)

    # Validate schema
    is_valid, validation_errors = validate_dataframe(df)
    if not is_valid:
        raise ValueError(f"Data validation failed: {'; '.join(validation_errors)}")

    # Add 2-letter state postal abbreviation for choropleth mapping
    df["State Abbr"] = df["State of Residence"].map(STATE_TO_ABBR)

    # Ensure categorical sorting for calendar months
    df["Month"] = pd.Categorical(df["Month"], categories=MONTH_ORDER, ordered=True)

    # Sort strictly chronologically and by geography
    df = df.sort_values(by=["State of Residence", "Month Code", "Sex of Infant"]).reset_index(drop=True)

    return df
