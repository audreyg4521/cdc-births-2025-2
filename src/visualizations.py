"""Interactive visualization components built with Plotly.

Strictly adheres to:
- Accessible, colorblind-friendly palettes
- Thousands separators on numbers and tooltips
- Strict non-truncated zero baselines for bar charts
- Chronological month order
"""

from typing import List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.data_loader import MONTH_ORDER

# Accessible color palette tokens
COLOR_PRIMARY = "#1D4ED8"       # Deep Blue
COLOR_FEMALE = "#D95F02"        # Accessible Warm Coral/Amber
COLOR_MALE = "#2B5C8F"          # Accessible Deep Slate Navy
COLOR_ACCENT = "#0D9488"        # Accessible Teal
COLOR_MUTED = "#64748B"         # Slate Muted
COLOR_LIGHT_BG = "#F8FAFC"      # Clean Card BG

CHART_LAYOUT_DEFAULTS = dict(
    font=dict(family="sans-serif", color="#1E293B", size=12),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=40, t=50, b=40),
    hoverlabel=dict(bgcolor="white", font_size=12, font_family="sans-serif"),
)


def create_monthly_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Create a chronological monthly birth trend chart with zero-anchored Y-axis."""
    monthly = (
        df.groupby(["Month Code", "Month"], observed=True)["Births"]
        .sum()
        .reset_index()
        .sort_values("Month Code")
    )

    max_val = monthly["Births"].max() if not monthly.empty else 1000

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=monthly["Month"],
            y=monthly["Births"],
            name="Monthly Births",
            marker_color=COLOR_PRIMARY,
            hovertemplate="<b>%{x}</b><br>Births: %{y:,}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["Births"],
            mode="lines+markers",
            name="Trend Line",
            line=dict(color="#0F172A", width=2.5),
            marker=dict(size=7, color="#0F172A"),
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(text="<b>Monthly Birth Trend (2025 Provisional)</b>", x=0.0),
        xaxis=dict(title="Month", categoryorder="array", categoryarray=MONTH_ORDER),
        yaxis=dict(
            title="Total Birth Count",
            range=[0, max_val * 1.15],
            tickformat=",",
            gridcolor="#E2E8F0",
        ),
        showlegend=False,
    )
    return fig


def create_sex_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """Create a grouped bar chart comparing Female and Male births across months."""
    sex_month = (
        df.groupby(["Month Code", "Month", "Sex of Infant"], observed=True)["Births"]
        .sum()
        .reset_index()
        .sort_values(["Month Code", "Sex of Infant"])
    )

    max_val = sex_month["Births"].max() if not sex_month.empty else 1000

    fig = go.Figure()

    for sex, color in [("Female", COLOR_FEMALE), ("Male", COLOR_MALE)]:
        sub = sex_month[sex_month["Sex of Infant"] == sex]
        fig.add_trace(
            go.Bar(
                x=sub["Month"],
                y=sub["Births"],
                name=f"{sex} Births",
                marker_color=color,
                hovertemplate=f"<b>%{{x}} ({sex})</b><br>Births: %{{y:,}}<extra></extra>",
            )
        )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(text="<b>Birth Counts by Infant Sex Across Months</b>", x=0.0),
        xaxis=dict(title="Month", categoryorder="array", categoryarray=MONTH_ORDER),
        yaxis=dict(
            title="Birth Count",
            range=[0, max_val * 1.18],
            tickformat=",",
            gridcolor="#E2E8F0",
        ),
        barmode="group",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=None,
        ),
    )
    return fig


def create_state_ranking_chart(df: pd.DataFrame, top_n: Optional[int] = None) -> go.Figure:
    """Create a horizontal ranking bar chart with a strict zero baseline."""
    state_totals = (
        df.groupby("State of Residence", observed=True)["Births"]
        .sum()
        .reset_index()
        .sort_values("Births", ascending=True)
    )

    if top_n is not None and top_n < len(state_totals):
        state_totals = state_totals.tail(top_n)

    max_val = state_totals["Births"].max() if not state_totals.empty else 1000

    fig = go.Figure(
        go.Bar(
            x=state_totals["Births"],
            y=state_totals["State of Residence"],
            orientation="h",
            marker=dict(
                color=state_totals["Births"],
                colorscale="Blues",
                showscale=False,
            ),
            hovertemplate="<b>%{y}</b><br>Total Births: %{x:,}<extra></extra>",
        )
    )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(
            text=f"<b>Geographic Rankings by Birth Count {'(Top ' + str(top_n) + ')' if top_n else ''}</b>",
            x=0.0,
        ),
        xaxis=dict(
            title="Total Birth Count",
            range=[0, max_val * 1.12],
            tickformat=",",
            gridcolor="#E2E8F0",
        ),
        yaxis=dict(title="", tickfont=dict(size=11)),
        height=max(400, len(state_totals) * 18),
    )
    return fig


def create_choropleth_map(df: pd.DataFrame) -> go.Figure:
    """Create a US Choropleth map illustrating birth counts across all 51 jurisdictions."""
    state_summary = (
        df.groupby(["State of Residence", "State Abbr"], observed=True)["Births"]
        .sum()
        .reset_index()
    )

    fig = px.choropleth(
        state_summary,
        locations="State Abbr",
        locationmode="USA-states",
        color="Births",
        scope="usa",
        color_continuous_scale="Blues",
        hover_name="State of Residence",
        hover_data={"Births": ":,", "State Abbr": False},
        labels={"Births": "Birth Count"},
    )

    layout_dict = {**CHART_LAYOUT_DEFAULTS, "margin": dict(l=0, r=0, t=50, b=0)}
    fig.update_layout(
        **layout_dict,
        title=dict(text="<b>Geographic Distribution of Birth Counts (U.S.)</b>", x=0.0),
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            lakecolor="#F1F5F9",
            showlakes=True,
            landcolor="#F8FAFC",
            subunitcolor="#CBD5E1",
        ),
        coloraxis_colorbar=dict(
            title="Births",
            tickformat=",",
            len=0.75,
            y=0.5,
        ),
    )
    return fig


def create_state_month_heatmap(df: pd.DataFrame) -> go.Figure:
    """Create a 2D Heatmap showing birth volume by State and Month."""
    pivot = (
        df.pivot_table(
            index="State of Residence",
            columns="Month",
            values="Births",
            aggfunc="sum",
            observed=True,
        )
        .reindex(columns=MONTH_ORDER)
    )

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="Viridis",
            hovertemplate="<b>State:</b> %{y}<br><b>Month:</b> %{x}<br><b>Births:</b> %{z:,}<extra></extra>",
            colorbar=dict(title="Births", tickformat=","),
        )
    )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(text="<b>State × Month Birth Count Heatmap</b>", x=0.0),
        xaxis=dict(title="Month", categoryorder="array", categoryarray=MONTH_ORDER),
        yaxis=dict(title="", autorange="reversed", tickfont=dict(size=10)),
        height=max(500, len(pivot) * 16),
    )
    return fig


def create_top_bottom_chart(df: pd.DataFrame, n: int = 5) -> go.Figure:
    """Create a comparison chart of the Top N and Bottom N geographies."""
    totals = (
        df.groupby("State of Residence", observed=True)["Births"]
        .sum()
        .reset_index()
        .sort_values("Births", ascending=True)
    )

    if len(totals) <= n * 2:
        # If selection has fewer states, show all
        comparison_df = totals.copy()
        comparison_df["Group"] = "Selected Geographies"
    else:
        bottom_n = totals.head(n).copy()
        bottom_n["Group"] = f"Bottom {n}"
        top_n = totals.tail(n).copy()
        top_n["Group"] = f"Top {n}"
        comparison_df = pd.concat([bottom_n, top_n]).sort_values("Births")

    max_val = comparison_df["Births"].max() if not comparison_df.empty else 1000

    color_map = {
        f"Top {n}": COLOR_PRIMARY,
        f"Bottom {n}": COLOR_ACCENT,
        "Selected Geographies": COLOR_PRIMARY,
    }

    fig = go.Figure()
    for grp in comparison_df["Group"].unique():
        sub = comparison_df[comparison_df["Group"] == grp]
        fig.add_trace(
            go.Bar(
                x=sub["Births"],
                y=sub["State of Residence"],
                orientation="h",
                name=grp,
                marker_color=color_map.get(grp, COLOR_PRIMARY),
                hovertemplate="<b>%{y}</b> (%{data.name})<br>Births: %{x:,}<extra></extra>",
            )
        )

    fig.update_layout(
        **CHART_LAYOUT_DEFAULTS,
        title=dict(text=f"<b>Volume Contrast: Top {n} vs. Bottom {n} Geographies</b>", x=0.0),
        xaxis=dict(
            title="Total Birth Count",
            range=[0, max_val * 1.15],
            tickformat=",",
            gridcolor="#E2E8F0",
        ),
        yaxis=dict(title=""),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=None,
        ),
        height=400,
    )
    return fig
