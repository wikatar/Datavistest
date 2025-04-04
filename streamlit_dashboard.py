import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from kpi_calculations import get_all_kpis, generate_sample_sales_data
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add plotly to requirements.txt
with open('requirements.txt', 'a') as f:
    f.write('\nstreamlit==1.23.1\nplotly==5.14.1\n')

def main():
    # Page config
    st.set_page_config(
        page_title="Sales KPI Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Title
    st.title("📊 Sales Performance KPI Dashboard")
    st.markdown("An interactive dashboard displaying key sales performance indicators")
    
    # Get data
    kpis, df = get_all_kpis()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Region filter
    selected_regions = st.sidebar.multiselect(
        "Select Regions:",
        options=df['region'].unique(),
        default=df['region'].unique()
    )
    
    # Channel filter
    selected_channels = st.sidebar.multiselect(
        "Select Channels:",
        options=df['channel'].unique(),
        default=df['channel'].unique()
    )
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range:",
        value=(df['date'].min().date(), df['date'].max().date()),
        min_value=df['date'].min().date(),
        max_value=df['date'].max().date()
    )
    
    # Apply filters
    filtered_df = df[
        (df['region'].isin(selected_regions)) &
        (df['channel'].isin(selected_channels)) &
        (df['date'].dt.date >= date_range[0]) &
        (df['date'].dt.date <= date_range[1])
    ]
    
    # Recalculate KPIs based on filtered data
    filtered_kpis = {}
    filtered_kpis['total_revenue'] = filtered_df['sales_amount'].sum()
    filtered_kpis['total_profit'] = (filtered_df['sales_amount'] - filtered_df['cost']).sum()
    filtered_kpis['profit_margin'] = (filtered_kpis['total_profit'] / filtered_kpis['total_revenue'] * 100) if filtered_kpis['total_revenue'] > 0 else 0
    filtered_kpis['average_order_value'] = filtered_df['sales_amount'].mean() if not filtered_df.empty else 0
    filtered_kpis['unique_customers'] = filtered_df['customer_id'].nunique()
    
    # Top row metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Revenue", f"${filtered_kpis['total_revenue']:,.2f}")
    with col2:
        st.metric("Total Profit", f"${filtered_kpis['total_profit']:,.2f}")
    with col3:
        st.metric("Profit Margin", f"{filtered_kpis['profit_margin']:.2f}%")
    with col4:
        st.metric("Unique Customers", f"{filtered_kpis['unique_customers']}")
    
    # Row 1 - Charts
    st.markdown("### Sales Performance by Segment")
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by Region
        revenue_by_region = filtered_df.groupby('region')['sales_amount'].sum().reset_index()
        fig = px.bar(
            revenue_by_region, 
            x='region', 
            y='sales_amount',
            title='Revenue by Region',
            labels={'sales_amount': 'Revenue ($)', 'region': 'Region'},
            color='region',
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue by Channel
        revenue_by_channel = filtered_df.groupby('channel')['sales_amount'].sum().reset_index()
        fig = px.pie(
            revenue_by_channel,
            values='sales_amount',
            names='channel',
            title='Revenue by Channel',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Plasma_r
        )
        fig.update_traces(textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2 - Time series & Distribution
    st.markdown("### Time Trends & Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly Revenue Trend
        filtered_df['month'] = filtered_df['date'].dt.strftime('%Y-%m')
        monthly_revenue = filtered_df.groupby('month')['sales_amount'].sum().reset_index()
        
        fig = px.line(
            monthly_revenue,
            x='month',
            y='sales_amount',
            title='Monthly Revenue Trend',
            labels={'sales_amount': 'Revenue ($)', 'month': 'Month'},
            markers=True,
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sales Amount Distribution
        fig = px.histogram(
            filtered_df,
            x="sales_amount",
            title="Sales Amount Distribution",
            nbins=30,
            color_discrete_sequence=['#22A7F0'],
            labels={'sales_amount': 'Sales Amount ($)'}
        )
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3 - Heatmap & Scatter
    st.markdown("### Cross-Segment Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Heatmap for Region/Channel
        region_channel = pd.crosstab(
            filtered_df['region'], 
            filtered_df['channel'], 
            values=filtered_df['sales_amount'], 
            aggfunc='sum'
        ).fillna(0)
        
        fig = px.imshow(
            region_channel,
            text_auto=True,
            aspect="auto",
            title="Sales Heatmap: Region vs Channel",
            labels=dict(x="Channel", y="Region", color="Sales Amount"),
            color_continuous_scale='YlGnBu'
        )
        fig.update_layout(
            xaxis_title="Channel",
            yaxis_title="Region"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Scatter plot: Quantity vs Sales Amount
        fig = px.scatter(
            filtered_df,
            x="quantity",
            y="sales_amount",
            color="channel",
            title="Quantity vs Sales Amount by Channel",
            labels={
                "quantity": "Quantity",
                "sales_amount": "Sales Amount ($)",
                "channel": "Channel"
            },
            opacity=0.7,
            size_max=15
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 4 - Sales Table
    st.markdown("### Data Table")
    
    # Aggregate data by date, region, channel
    agg_data = filtered_df.groupby(['date', 'region', 'channel']).agg({
        'sales_amount': 'sum',
        'cost': 'sum',
        'quantity': 'sum'
    }).reset_index()
    
    # Calculate profit
    agg_data['profit'] = agg_data['sales_amount'] - agg_data['cost']
    agg_data['profit_margin'] = agg_data['profit'] / agg_data['sales_amount'] * 100
    
    # Format for display
    display_data = agg_data.copy()
    display_data['date'] = display_data['date'].dt.date
    display_data['sales_amount'] = display_data['sales_amount'].map('${:,.2f}'.format)
    display_data['cost'] = display_data['cost'].map('${:,.2f}'.format)
    display_data['profit'] = display_data['profit'].map('${:,.2f}'.format)
    display_data['profit_margin'] = display_data['profit_margin'].map('{:.2f}%'.format)
    
    # Show table
    st.dataframe(display_data, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("Dashboard created with Streamlit and Plotly")

if __name__ == "__main__":
    main() 