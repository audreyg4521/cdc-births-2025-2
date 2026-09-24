"""CDC Provisional Natality Dashboard (2025).

A pedagogical Streamlit dashboard designed for undergraduate business analytics students
to explore temporal, geographic, and demographic variation in provisional U.S. birth counts.
"""

from typing import List
import pandas as pd
import streamlit as st

from src.data_loader import MONTH_ORDER, load_data
from src.ui_components import (
    render_empty_state,
    render_filter_summary,
    render_kpi_cards,
)
from src.visualizations import (
    create_choropleth_map,
    create_monthly_trend_chart,
    create_sex_comparison_chart,
    create_state_month_heatmap,
    create_state_ranking_chart,
    create_top_bottom_chart,
)

# Page configuration
st.set_page_config(
    page_title="CDC Provisional Natality Dashboard (2025)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_session_state(all_states: List[str], all_months: List[str]) -> None:
    """Initialize Streamlit session state for filters if not already present."""
    if "state_multiselect" not in st.session_state:
        st.session_state["state_multiselect"] = list(all_states)
    if "month_multiselect" not in st.session_state:
        st.session_state["month_multiselect"] = list(all_months)
    if "sex_radio" not in st.session_state:
        st.session_state["sex_radio"] = "All"


def reset_filters(all_states: List[str], all_months: List[str]) -> None:
    """Reset all sidebar filters to their default values."""
    st.session_state["state_multiselect"] = list(all_states)
    st.session_state["month_multiselect"] = list(all_months)
    st.session_state["sex_radio"] = "All"


def render_header() -> None:
    """Render the dashboard title, source attribution, and statistical guardrails."""
    st.title("CDC Provisional Natality Dashboard (2025)")
    st.caption(
        "A Business Analytics Learning Tool • Dataset: Centers for Disease Control and Prevention (CDC WONDER)"
    )

    # Required notices: Provisional data & Birth counts vs. birth rates
    col_notice1, col_notice2 = st.columns(2)

    with col_notice1:
        st.info(
            "ℹ️ **Provisional Data Notice**: These figures reflect provisional 2025 live birth registrations "
            "reported by the CDC National Center for Health Statistics. Figures are subject to continuous "
            "quality checks and final revision."
        )

    with col_notice2:
        st.warning(
            "⚠️ **Analytical Guardrail (Counts vs. Rates)**: All metrics displayed represent **raw birth counts**, "
            "not birth or fertility rates. Populous states (e.g., California, Texas) naturally have higher totals "
            "due to population scale. Do not infer birth rates without Census denominator data."
        )


def main() -> None:
    # 1. Load data safely
    try:
        raw_df = load_data()
    except Exception as exc:
        st.error(f"Error loading natality dataset: {exc}")
        return

    all_states = sorted(raw_df["State of Residence"].unique().tolist())
    all_months = MONTH_ORDER.copy()
    init_session_state(all_states, all_months)

    # 2. Sidebar Filters
    st.sidebar.title("Dashboard Filters")
    st.sidebar.markdown(
        "Refine observations across geography, calendar months, and infant sex."
    )

    # Reset Filters Button
    if st.sidebar.button("🔄 Reset All Filters", key="btn_reset_all", use_container_width=True):
        reset_filters(all_states, all_months)
        st.rerun()

    st.sidebar.markdown("---")

    # State / Geography Filter
    st.sidebar.subheader("1. Geography")
    geo_col1, geo_col2 = st.sidebar.columns(2)
    if geo_col1.button("Select All", key="select_all_states", use_container_width=True):
        st.session_state["state_multiselect"] = list(all_states)
        st.rerun()
    if geo_col2.button("Clear All", key="clear_all_states", use_container_width=True):
        st.session_state["state_multiselect"] = []
        st.rerun()

    selected_states = st.sidebar.multiselect(
        "Choose Geographies:",
        options=all_states,
        key="state_multiselect",
        help="Select one, several, or all 50 U.S. states plus District of Columbia.",
    )

    # Month Filter (chronological order)
    st.sidebar.subheader("2. Calendar Month")
    mo_col1, mo_col2 = st.sidebar.columns(2)
    if mo_col1.button("Select All", key="select_all_months", use_container_width=True):
        st.session_state["month_multiselect"] = list(all_months)
        st.rerun()
    if mo_col2.button("Clear All", key="clear_all_months", use_container_width=True):
        st.session_state["month_multiselect"] = []
        st.rerun()

    selected_months = st.sidebar.multiselect(
        "Choose Months:",
        options=all_months,
        key="month_multiselect",
        help="Select calendar months (January through December).",
    )

    # Infant Sex Selector
    st.sidebar.subheader("3. Infant Biological Sex")
    sex_options = ["All", "Female", "Male"]
    selected_sex = st.sidebar.radio(
        "Filter by Sex:",
        options=sex_options,
        key="sex_radio",
        help="Filter observations for Female infants, Male infants, or Both combined.",
    )

    # 3. Filter DataFrame
    filtered_df = raw_df.copy()
    if selected_states:
        filtered_df = filtered_df[filtered_df["State of Residence"].isin(selected_states)]
    else:
        filtered_df = filtered_df.iloc[0:0]

    if selected_months:
        filtered_df = filtered_df[filtered_df["Month"].isin(selected_months)]
    else:
        filtered_df = filtered_df.iloc[0:0]

    if selected_sex in ["Female", "Male"]:
        filtered_df = filtered_df[filtered_df["Sex of Infant"] == selected_sex]

    # Active filter summary in sidebar
    render_filter_summary(
        selected_states=selected_states,
        selected_months=selected_months,
        selected_sex=selected_sex,
        total_rows=len(raw_df),
        filtered_rows=len(filtered_df),
    )

    # 4. Render Main Dashboard Header
    render_header()
    st.markdown("---")

    # 5. Empty State Handling
    if filtered_df.empty:
        render_empty_state()
        return

    # 6. KPI Cards
    render_kpi_cards(filtered_df, total_geos_available=len(all_states))
    st.markdown("---")

    # 7. Dashboard Tabs
    tab_overview, tab_geo, tab_trend, tab_data, tab_about = st.tabs([
        "📈 Overview",
        "🗺️ Geographic Analysis",
        "📅 Monthly & Sex Analysis",
        "📋 Data Table & Download",
        "📖 About the Data",
    ])

    # ---------------- TAB 1: OVERVIEW ----------------
    with tab_overview:
        st.subheader("Executive Overview & Distribution")
        st.markdown(
            "This tab provides a high-level statistical summary of the active selection, "
            "contrasting volume across months and extreme geographies."
        )

        ov_col1, ov_col2 = st.columns([3, 2])
        with ov_col1:
            st.plotly_chart(
                create_monthly_trend_chart(filtered_df),
                use_container_width=True,
                key="overview_monthly_trend",
            )
        with ov_col2:
            st.plotly_chart(
                create_top_bottom_chart(filtered_df, n=5),
                use_container_width=True,
                key="overview_top_bottom",
            )

        st.info(
            "💡 **Student Tip**: Look at the contrast between the highest-volume and lowest-volume jurisdictions. "
            "Notice how volume variation spans multiple orders of magnitude across state populations."
        )

    # ---------------- TAB 2: GEOGRAPHIC ANALYSIS ----------------
    with tab_geo:
        st.subheader("Geographic Distribution & State Rankings")
        st.markdown(
            "Explore geographic dispersion across the United States. Hover over states in the map "
            "or review the ranked horizontal bar chart below."
        )

        st.plotly_chart(
            create_choropleth_map(filtered_df),
            use_container_width=True,
            key="geo_choropleth_map",
        )

        st.plotly_chart(
            create_state_ranking_chart(filtered_df),
            use_container_width=True,
            key="geo_state_ranking",
        )

    # ---------------- TAB 3: MONTHLY & SEX ANALYSIS ----------------
    with tab_trend:
        st.subheader("Monthly Seasonality & Infant Sex Comparison")
        st.markdown(
            "Analyze seasonality patterns across calendar months and compare birth counts "
            "between male and female infants."
        )

        trend_col1, trend_col2 = st.columns(2)
        with trend_col1:
            st.plotly_chart(
                create_monthly_trend_chart(filtered_df),
                use_container_width=True,
                key="trend_monthly_trend",
            )
        with trend_col2:
            st.plotly_chart(
                create_sex_comparison_chart(filtered_df),
                use_container_width=True,
                key="trend_sex_comparison",
            )

        st.markdown("#### Geographic Seasonality Matrix")
        st.markdown(
            "The heatmap below illustrates monthly birth counts across all selected geographies, "
            "helping identify regional or seasonal volume clusters."
        )
        st.plotly_chart(
            create_state_month_heatmap(filtered_df),
            use_container_width=True,
            key="trend_state_month_heatmap",
        )

    # ---------------- TAB 4: DATA TABLE & DOWNLOAD ----------------
    with tab_data:
        st.subheader("Filtered Observation Records")
        st.markdown(
            "Search, sort, and inspect the underlying microdata records matching your current filter criteria."
        )

        # Display table formatted cleanly
        display_cols = [
            "State of Residence",
            "State Abbr",
            "Month",
            "Month Code",
            "Year Code",
            "Sex of Infant",
            "Births",
        ]
        formatted_table = filtered_df[display_cols].copy()

        st.dataframe(
            formatted_table.style.format({"Births": "{:,}"}),
            use_container_width=True,
            height=450,
        )

        # CSV Download Button
        csv_data = filtered_df[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_data,
            file_name="cdc_provisional_natality_filtered_2025.csv",
            mime="text/csv",
            help="Download the currently active filtered observations for external statistical analysis.",
        )

    # ---------------- TAB 5: ABOUT THE DATA ----------------
    with tab_about:
        st.subheader("Data Documentation & Learning Guide")

        st.markdown("""
### 1. Data Provenance & Methodology
- **Source**: Centers for Disease Control and Prevention (CDC), National Center for Health Statistics (NCHS).
- **Collection System**: CDC WONDER Provisional Natality Statistics.
- **Reporting Period**: Calendar Year 2025 (Provisional records).
- **Scope**: Live birth certificates registered across the 50 U.S. states and the District of Columbia.

### 2. Analytical Lesson: Birth Counts vs. Birth Rates
A common pitfall in business and public health analytics is confusing **counts** with **rates**:
- **Birth Count (Observed here)**: The absolute frequency of registered births within a jurisdiction over a timeframe.
- **Birth Rate (Not in this dataset)**: Births divided by total population (Crude Birth Rate) or women of childbearing age (General Fertility Rate).
> **Takeaway**: California having the largest birth count does not indicate a higher fertility rate; it primarily reflects that California has the largest base population of any state.

### 3. Data Dictionary
| Variable Name | Storage Type | Conceptual Type | Description |
| :--- | :--- | :--- | :--- |
| `State of Residence` | String | Categorical (Nominal) | U.S. State or District of Columbia (51 entities). |
| `Month` | String | Categorical (Ordinal) | Calendar month (`January` through `December`). |
| `Month Code` | Integer | Discrete Numeric | Chronological month number (`1` to `12`). |
| `Year Code` | Integer | Discrete Numeric | Reporting calendar year (`2025`). |
| `Sex of Infant` | String | Categorical (Nominal) | Infant biological sex (`Female` or `Male`). |
| `Births` | Integer | Continuous Count | Number of live births registered. |

### 4. Data Quality Audit Verification
- **Total Factorial Records**: $51 \\text{ Geographies} \\times 12 \\text{ Months} \\times 2 \\text{ Sex Categories} = 1,224 \\text{ Observations}$.
- **Missing Values**: 0 nulls across all fields.
- **Duplicate Rows**: 0 duplicate records.
- **Unfiltered Total Births**: Exactly **3,604,640** live births.
        """)


if __name__ == "__main__":
    main()
