# CDC Provisional Natality 2025 Dashboard

An interactive pedagogical dashboard built with Streamlit, pandas, and Plotly for undergraduate business analytics students.

## Project Overview
This application visualizes provisional 2025 U.S. birth registration data from the Centers for Disease Control and Prevention (CDC WONDER).

### Educational Focus: Birth Counts vs. Birth Rates
A primary learning goal of this dashboard is helping students differentiate between **raw counts** (volume) and **rates** (frequency normalized by population). High-volume states such as California and Texas have high birth counts because of their population size; birth counts alone cannot be used to compare fertility rates without demographic denominator data.

## Features
- **Statistical Guardrails**: Prominently displays provisional status and analytical warnings against conflating counts and rates.
- **Dynamic Multi-criteria Filters**: Geography (51 states/DC), chronological calendar months (Jan–Dec), and infant biological sex (Female, Male, All).
- **KPI Summary Cards**: Real-time updates for Total Births, Selected Geographies, Average Births per Month, Top Geography, and Peak Month.
- **Interactive Visualizations**:
  - Chronological monthly birth trend.
  - Female vs. Male comparative bar chart with accessible palettes.
  - Horizontal geographic ranking with zero-anchored baselines.
  - US state choropleth map.
  - State-by-month volume heatmap.
  - Top 5 vs. Bottom 5 volume contrast.
- **Data Access & Export**: Searchable filtered table with formatted numbers and single-click CSV export.
- **Robust Error & Empty-State Handling**: Clear user feedback if filter combinations yield no records.

## Installation & Running Locally

1. Clone or download the repository.
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## File Structure
- `app.py`: Main dashboard application and page routing.
- `src/data_loader.py`: Cached Excel ingestion, schema validation, and state postal code mapping.
- `src/visualizations.py`: Plotly chart generators using accessible palettes and non-truncated baselines.
- `src/ui_components.py`: KPI cards, filter summary badges, and empty-state notifications.
- `Provisional_Natality_2025_CDC.xlsx`: Raw CDC dataset (strictly read-only).
