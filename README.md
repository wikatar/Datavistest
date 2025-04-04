# KPI Data Visualization Dashboard

This project demonstrates how to create KPI (Key Performance Indicators) visualizations and dashboards using Python, pandas, and seaborn.

## Overview

The project includes:

1. **KPI Calculations**: Various sales and business KPIs calculated from sample data.
2. **Static Dashboard**: A comprehensive static dashboard with multiple visualizations.
3. **Interactive Dashboard**: An interactive web dashboard using Streamlit and Plotly.
4. **Individual KPI Plots**: Separate visualizations for specific KPIs.

## Files

- `kpi_calculations.py`: Functions for generating sample data and calculating KPIs.
- `dashboard.py`: Code for creating the static dashboard and individual visualizations.
- `streamlit_dashboard.py`: Interactive dashboard using Streamlit.
- `requirements.txt`: Required Python packages.

## Setup

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Run the static dashboard:

```bash
python dashboard.py
```

3. Run the interactive Streamlit dashboard:

```bash
streamlit run streamlit_dashboard.py
```

## Generated Outputs

Running the dashboard scripts will generate:

- `kpi_dashboard.png`: A comprehensive dashboard with multiple visualizations.
- Individual visualization files:
  - `revenue_by_region.png`
  - `monthly_revenue.png`
  - `profit_margin_by_channel.png`
  - `sales_distribution.png`
  - `region_channel_heatmap.png`

## Interactive Dashboard Features

The Streamlit dashboard includes:

- **Interactive Filters**: Filter data by region, channel, and date range.
- **Real-time KPI Calculations**: KPIs update automatically based on filtered data.
- **Interactive Charts**: Hover for details, zoom, and more interactive features.
- **Data Table**: View aggregated data in a sortable, filterable table.

## Sample KPIs Included

- Revenue metrics (total, by region, by channel, monthly trends)
- Profitability metrics (total profit, profit margin, profit by region/channel)
- Product performance metrics (top products by revenue and quantity)
- Customer metrics (unique customers, average revenue per customer)

## Customization

You can modify the `generate_sample_sales_data()` function in `kpi_calculations.py` to work with your own data source instead of the generated sample data. 