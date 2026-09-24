"""UI components including KPI cards, filter summaries, and empty-state messaging."""

from typing import List
import pandas as pd
import streamlit as st


def render_kpi_cards(df: pd.DataFrame, total_geos_available: int = 51) -> None:
    """Render 5 primary KPI cards based on current filtered data."""
    if df.empty:
        return

    total_births = int(df["Births"].sum())
    num_geos = df["State of Residence"].nunique()
    num_months = df["Month Code"].nunique()

    # Average monthly births in this selection
    avg_per_month = int(total_births / num_months) if num_months > 0 else 0

    # Top Geography and its births
    geo_totals = df.groupby("State of Residence")["Births"].sum()
    top_geo_name = geo_totals.idxmax() if not geo_totals.empty else "N/A"
    top_geo_count = int(geo_totals.max()) if not geo_totals.empty else 0

    # Top Month and its births
    month_totals = df.groupby("Month", observed=True)["Births"].sum()
    top_month_name = month_totals.idxmax() if not month_totals.empty else "N/A"
    top_month_count = int(month_totals.max()) if not month_totals.empty else 0

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="Total Births",
            value=f"{total_births:,}",
            help="Total live birth count in the current filtered selection.",
        )
    with col2:
        st.metric(
            label="Geographies",
            value=f"{num_geos} of {total_geos_available}",
            help="Count of active states or territories included in selection.",
        )
    with col3:
        st.metric(
            label="Avg. Births / Month",
            value=f"{avg_per_month:,}",
            help="Average birth count per active month in current selection.",
        )
    with col4:
        st.metric(
            label="Top Geography",
            value=top_geo_name,
            delta=f"{top_geo_count:,} births",
            delta_color="off",
            help="Jurisdiction with the highest aggregated birth count in selection.",
        )
    with col5:
        st.metric(
            label="Peak Month",
            value=str(top_month_name),
            delta=f"{top_month_count:,} births",
            delta_color="off",
            help="Calendar month with the highest aggregated birth count in selection.",
        )


def render_filter_summary(
    selected_states: List[str],
    selected_months: List[str],
    selected_sex: str,
    total_rows: int,
    filtered_rows: int,
) -> None:
    """Render a concise status badge summarizing active filters."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Active Filter Summary")

    state_desc = (
        "All 51 Geographies"
        if len(selected_states) == 51
        else f"{len(selected_states)} Geographies"
    )
    month_desc = (
        "All 12 Months"
        if len(selected_months) == 12
        else f"{len(selected_months)} Months"
    )

    st.sidebar.info(
        f"**States:** {state_desc}\n\n"
        f"**Months:** {month_desc}\n\n"
        f"**Infant Sex:** {selected_sex}\n\n"
        f"**Records:** {filtered_rows:,} / {total_rows:,}"
    )


def render_empty_state() -> None:
    """Display a friendly, instructional message when no records match filter criteria."""
    st.warning(
        "⚠️ **No records match your selected filter criteria.**\n\n"
        "Please adjust your sidebar filters (such as re-selecting states, months, "
        "or infant sex), or click **'Reset Filters'** in the sidebar to restore the default view."
    )
