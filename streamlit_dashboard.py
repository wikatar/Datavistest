import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from kpi_calculations import get_all_kpis, generate_sample_sales_data
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Add plotly to requirements.txt
with open('requirements.txt', 'a') as f:
    f.write('\nstreamlit==1.23.1\nplotly==5.14.1\n')

def calculate_growth_rate(current, previous):
    """Calculate growth rate between two values."""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

def main():
    # Page config
    st.set_page_config(
        page_title="Advanced Sales Analytics Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Title
    st.title("📊 Advanced Sales Analytics Dashboard")
    st.markdown("Comprehensive analytics platform for detailed business performance insights")
    
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
    
    # Calculate advanced KPIs
    current_period = filtered_df
    previous_period = df[
        (df['date'].dt.date < date_range[0]) &
        (df['date'].dt.date >= (date_range[0] - (date_range[1] - date_range[0])))
    ]
    
    # Current period KPIs
    current_revenue = current_period['sales_amount'].sum()
    current_profit = (current_period['sales_amount'] - current_period['cost']).sum()
    current_customers = current_period['customer_id'].nunique()
    current_orders = len(current_period)
    
    # Previous period KPIs
    prev_revenue = previous_period['sales_amount'].sum()
    prev_profit = (previous_period['sales_amount'] - previous_period['cost']).sum()
    prev_customers = previous_period['customer_id'].nunique()
    prev_orders = len(previous_period)
    
    # Calculate growth rates
    revenue_growth = calculate_growth_rate(current_revenue, prev_revenue)
    profit_growth = calculate_growth_rate(current_profit, prev_profit)
    customer_growth = calculate_growth_rate(current_customers, prev_customers)
    order_growth = calculate_growth_rate(current_orders, prev_orders)
    
    # Top row metrics with growth indicators
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Revenue",
            f"${current_revenue:,.2f}",
            f"{revenue_growth:+.1f}%"
        )
    with col2:
        st.metric(
            "Total Profit",
            f"${current_profit:,.2f}",
            f"{profit_growth:+.1f}%"
        )
    with col3:
        st.metric(
            "Unique Customers",
            f"{current_customers:,}",
            f"{customer_growth:+.1f}%"
        )
    with col4:
        st.metric(
            "Total Orders",
            f"{current_orders:,}",
            f"{order_growth:+.1f}%"
        )
    
    # Advanced Metrics Row
    st.markdown("### Advanced Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate advanced metrics
    avg_order_value = current_revenue / current_orders if current_orders > 0 else 0
    customer_lifetime_value = current_revenue / current_customers if current_customers > 0 else 0
    profit_margin = (current_profit / current_revenue * 100) if current_revenue > 0 else 0
    orders_per_customer = current_orders / current_customers if current_customers > 0 else 0
    
    with col1:
        st.metric("Average Order Value", f"${avg_order_value:,.2f}")
    with col2:
        st.metric("Customer Lifetime Value", f"${customer_lifetime_value:,.2f}")
    with col3:
        st.metric("Profit Margin", f"{profit_margin:.1f}%")
    with col4:
        st.metric("Orders per Customer", f"{orders_per_customer:.1f}")
    
    # Row 1 - Advanced Charts
    st.markdown("### Sales Performance Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by Region with Growth
        revenue_by_region = current_period.groupby('region').agg({
            'sales_amount': 'sum',
            'customer_id': 'nunique'
        }).reset_index()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(
                x=revenue_by_region['region'],
                y=revenue_by_region['sales_amount'],
                name="Revenue",
                marker_color='#1f77b4'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=revenue_by_region['region'],
                y=revenue_by_region['customer_id'],
                name="Customers",
                marker=dict(color='#ff7f0e', size=10)
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title="Revenue and Customer Distribution by Region",
            xaxis_title="Region",
            barmode='group'
        )
        
        fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
        fig.update_yaxes(title_text="Number of Customers", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Channel Performance Analysis
        channel_metrics = current_period.groupby('channel').agg({
            'sales_amount': 'sum',
            'customer_id': 'nunique',
            'quantity': 'sum'
        }).reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=channel_metrics['channel'],
            y=channel_metrics['sales_amount'],
            name='Revenue',
            marker_color='#2ecc71'
        ))
        
        fig.add_trace(go.Scatter(
            x=channel_metrics['channel'],
            y=channel_metrics['customer_id'],
            name='Customers',
            yaxis='y2',
            marker=dict(color='#e74c3c', size=10)
        ))
        
        fig.update_layout(
            title="Channel Performance Analysis",
            yaxis=dict(title="Revenue ($)"),
            yaxis2=dict(title="Number of Customers", overlaying="y", side="right"),
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2 - Time Series Analysis
    st.markdown("### Time Series Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily Revenue Trend with Moving Average
        daily_revenue = current_period.groupby('date')['sales_amount'].sum().reset_index()
        daily_revenue['MA7'] = daily_revenue['sales_amount'].rolling(window=7).mean()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_revenue['date'],
            y=daily_revenue['sales_amount'],
            name='Daily Revenue',
            line=dict(color='#3498db', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_revenue['date'],
            y=daily_revenue['MA7'],
            name='7-day Moving Average',
            line=dict(color='#e74c3c', width=2)
        ))
        
        fig.update_layout(
            title="Daily Revenue Trend with Moving Average",
            xaxis_title="Date",
            yaxis_title="Revenue ($)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Customer Acquisition Trend
        daily_customers = current_period.groupby('date')['customer_id'].nunique().reset_index()
        daily_customers['MA7'] = daily_customers['customer_id'].rolling(window=7).mean()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_customers['date'],
            y=daily_customers['customer_id'],
            name='Daily New Customers',
            line=dict(color='#2ecc71', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_customers['date'],
            y=daily_customers['MA7'],
            name='7-day Moving Average',
            line=dict(color='#f1c40f', width=2)
        ))
        
        fig.update_layout(
            title="Customer Acquisition Trend",
            xaxis_title="Date",
            yaxis_title="Number of New Customers",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3 - Product Analysis
    st.markdown("### Product Performance Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Product Performance Matrix
        product_metrics = current_period.groupby('product_id').agg({
            'sales_amount': 'sum',
            'quantity': 'sum',
            'customer_id': 'nunique'
        }).reset_index()
        
        product_metrics['avg_price'] = product_metrics['sales_amount'] / product_metrics['quantity']
        
        fig = px.scatter(
            product_metrics,
            x="quantity",
            y="avg_price",
            size="sales_amount",
            color="customer_id",
            hover_name="product_id",
            title="Product Performance Matrix",
            labels={
                "quantity": "Quantity Sold",
                "avg_price": "Average Price ($)",
                "sales_amount": "Total Revenue ($)",
                "customer_id": "Number of Customers"
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Product Profitability Analysis
        product_profit = current_period.groupby('product_id').agg({
            'sales_amount': 'sum',
            'cost': 'sum'
        }).reset_index()
        
        product_profit['profit'] = product_profit['sales_amount'] - product_profit['cost']
        product_profit['profit_margin'] = product_profit['profit'] / product_profit['sales_amount'] * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=product_profit['product_id'],
            y=product_profit['profit'],
            name='Profit',
            marker_color='#2ecc71'
        ))
        
        fig.add_trace(go.Scatter(
            x=product_profit['product_id'],
            y=product_profit['profit_margin'],
            name='Profit Margin (%)',
            yaxis='y2',
            marker=dict(color='#e74c3c', size=10)
        ))
        
        fig.update_layout(
            title="Product Profitability Analysis",
            yaxis=dict(title="Profit ($)"),
            yaxis2=dict(title="Profit Margin (%)", overlaying="y", side="right"),
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 4 - Customer Analysis
    st.markdown("### Customer Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer Value Distribution
        customer_value = current_period.groupby('customer_id').agg({
            'sales_amount': ['sum', 'count']
        }).reset_index()
        
        customer_value.columns = ['customer_id', 'total_spent', 'order_count']
        customer_value['avg_order_value'] = customer_value['total_spent'] / customer_value['order_count']
        
        fig = make_subplots(rows=2, cols=1, subplot_titles=("Customer Value Distribution", "Order Count Distribution"))
        
        fig.add_trace(
            go.Histogram(x=customer_value['total_spent'], name="Total Spent", nbinsx=30),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Histogram(x=customer_value['order_count'], name="Order Count", nbinsx=30),
            row=2, col=1
        )
        
        fig.update_layout(height=600, showlegend=False)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Customer Segmentation
        customer_value['segment'] = pd.qcut(
            customer_value['total_spent'],
            q=4,
            labels=['Low Value', 'Medium Value', 'High Value', 'VIP']
        )
        
        segment_metrics = customer_value.groupby('segment').agg({
            'customer_id': 'count',
            'total_spent': 'sum',
            'order_count': 'mean'
        }).reset_index()
        
        fig = go.Figure(data=[
            go.Table(
                header=dict(
                    values=['Segment', 'Customer Count', 'Total Revenue', 'Avg Orders'],
                    fill_color='#2ecc71',
                    align='left'
                ),
                cells=dict(
                    values=[
                        segment_metrics['segment'],
                        segment_metrics['customer_id'],
                        segment_metrics['total_spent'].map('${:,.2f}'.format),
                        segment_metrics['order_count'].map('{:.1f}'.format)
                    ],
                    fill_color='#f8f9fa',
                    align='left'
                )
            )
        ])
        
        fig.update_layout(
            title="Customer Segmentation Analysis",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("Advanced Analytics Dashboard created with Streamlit and Plotly")

if __name__ == "__main__":
    main() 