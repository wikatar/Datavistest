import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gridspec
from kpi_calculations import get_all_kpis

# Set the style for seaborn
sns.set(style="whitegrid")

def create_kpi_dashboard():
    """Create a dashboard with multiple visualizations for KPIs."""
    # Get KPI data
    kpis, df = get_all_kpis()
    
    # Create figure with subplots
    plt.figure(figsize=(20, 16))
    gs = gridspec.GridSpec(3, 3)
    
    # 1. Revenue by Region (Bar Chart)
    ax1 = plt.subplot(gs[0, 0])
    sns.barplot(x=kpis['revenue_by_region'].index, y=kpis['revenue_by_region'].values, palette="viridis", ax=ax1)
    ax1.set_title('Revenue by Region', fontsize=14)
    ax1.set_ylabel('Revenue ($)')
    ax1.set_xlabel('Region')
    
    # 2. Profit by Channel (Bar Chart)
    ax2 = plt.subplot(gs[0, 1])
    sns.barplot(x=kpis['profit_by_channel'].index, y=kpis['profit_by_channel'].values, palette="magma", ax=ax2)
    ax2.set_title('Profit by Channel', fontsize=14)
    ax2.set_ylabel('Profit ($)')
    ax2.set_xlabel('Channel')
    
    # 3. Monthly Revenue Trend (Line Chart)
    ax3 = plt.subplot(gs[0, 2])
    monthly_revenue = kpis['monthly_revenue'].reset_index()
    sns.lineplot(x=monthly_revenue['date'], y=monthly_revenue['sales_amount'], marker='o', ax=ax3)
    ax3.set_title('Monthly Revenue Trend', fontsize=14)
    ax3.set_ylabel('Revenue ($)')
    ax3.set_xlabel('Month')
    plt.xticks(rotation=45)
    
    # 4. Top 5 Products by Revenue (Horizontal Bar Chart)
    ax4 = plt.subplot(gs[1, 0])
    top_products = kpis['top_products_by_revenue'].head(5)
    sns.barplot(y=top_products.index, x=top_products.values, palette="Blues_d", ax=ax4)
    ax4.set_title('Top 5 Products by Revenue', fontsize=14)
    ax4.set_xlabel('Revenue ($)')
    ax4.set_ylabel('Product ID')
    
    # 5. Customer Count by Region (Pie Chart)
    ax5 = plt.subplot(gs[1, 1])
    customers_by_region = kpis['customers_by_region']
    ax5.pie(customers_by_region.values, labels=customers_by_region.index, autopct='%1.1f%%', 
            shadow=True, startangle=90, colors=sns.color_palette("Set3"))
    ax5.set_title('Customer Distribution by Region', fontsize=14)
    
    # 6. Revenue vs Profit by Region (Scatter Plot)
    ax6 = plt.subplot(gs[1, 2])
    region_data = pd.DataFrame({
        'Region': kpis['revenue_by_region'].index,
        'Revenue': kpis['revenue_by_region'].values,
        'Profit': kpis['profit_by_region'].values
    })
    sns.scatterplot(x='Revenue', y='Profit', hue='Region', size='Revenue', 
                   sizes=(100, 500), data=region_data, ax=ax6)
    ax6.set_title('Revenue vs Profit by Region', fontsize=14)
    
    # 7. Sales Distribution (Histogram)
    ax7 = plt.subplot(gs[2, 0])
    sns.histplot(df['sales_amount'], bins=30, kde=True, ax=ax7)
    ax7.set_title('Sales Amount Distribution', fontsize=14)
    ax7.set_xlabel('Sales Amount ($)')
    ax7.set_ylabel('Frequency')
    
    # 8. Sales by Month and Channel (Stacked Bar Chart)
    ax8 = plt.subplot(gs[2, 1:])
    # Extract month and aggregate
    df['month'] = df['date'].dt.strftime('%Y-%m')
    monthly_channel = df.groupby(['month', 'channel'])['sales_amount'].sum().unstack()
    monthly_channel.plot(kind='bar', stacked=True, ax=ax8, colormap='tab10')
    ax8.set_title('Monthly Sales by Channel', fontsize=14)
    ax8.set_xlabel('Month')
    ax8.set_ylabel('Sales ($)')
    plt.xticks(rotation=45)
    
    # Add a big title
    plt.suptitle('Sales & Performance KPI Dashboard', fontsize=24, y=0.98)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Save the dashboard
    plt.savefig('kpi_dashboard.png', dpi=300, bbox_inches='tight')
    print("Dashboard saved as 'kpi_dashboard.png'")
    
    # Display numeric KPIs
    print("\nKey Performance Indicators:")
    print(f"Total Revenue: ${kpis['total_revenue']:.2f}")
    print(f"Total Profit: ${kpis['total_profit']:.2f}")
    print(f"Profit Margin: {kpis['profit_margin']:.2f}%")
    print(f"Average Order Value: ${kpis['average_order_value']:.2f}")
    print(f"Unique Customers: {kpis['unique_customers']}")
    
    plt.show()

def create_individual_kpi_plots():
    """Create individual plots for specific KPIs."""
    # Get KPI data
    kpis, df = get_all_kpis()
    
    # 1. Revenue by Region
    plt.figure(figsize=(10, 6))
    sns.barplot(x=kpis['revenue_by_region'].index, y=kpis['revenue_by_region'].values, palette="viridis")
    plt.title('Revenue by Region', fontsize=16)
    plt.ylabel('Revenue ($)')
    plt.xlabel('Region')
    plt.tight_layout()
    plt.savefig('revenue_by_region.png', dpi=200)
    
    # 2. Monthly Revenue Trend
    plt.figure(figsize=(12, 6))
    monthly_revenue = kpis['monthly_revenue'].reset_index()
    sns.lineplot(x=monthly_revenue['date'], y=monthly_revenue['sales_amount'], marker='o', linewidth=2)
    plt.title('Monthly Revenue Trend', fontsize=16)
    plt.ylabel('Revenue ($)')
    plt.xlabel('Month')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('monthly_revenue.png', dpi=200)
    
    # 3. Profit Margin by Channel
    plt.figure(figsize=(10, 6))
    # Calculate profit margin by channel
    channel_profit = df.groupby('channel')['profit'].sum()
    channel_revenue = df.groupby('channel')['sales_amount'].sum()
    channel_margin = (channel_profit / channel_revenue * 100).reset_index()
    channel_margin.columns = ['Channel', 'Profit Margin (%)']
    
    sns.barplot(x='Channel', y='Profit Margin (%)', data=channel_margin, palette="magma")
    plt.title('Profit Margin by Channel', fontsize=16)
    plt.ylabel('Profit Margin (%)')
    plt.tight_layout()
    plt.savefig('profit_margin_by_channel.png', dpi=200)
    
    # 4. Sales Amount Distribution by Channel
    plt.figure(figsize=(12, 6))
    sns.histplot(data=df, x='sales_amount', hue='channel', bins=30, kde=True, multiple='stack')
    plt.title('Sales Amount Distribution by Channel', fontsize=16)
    plt.xlabel('Sales Amount ($)')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig('sales_distribution.png', dpi=200)
    
    # 5. Region and Channel Heatmap
    plt.figure(figsize=(10, 8))
    region_channel = pd.crosstab(df['region'], df['channel'], values=df['sales_amount'], aggfunc='sum')
    sns.heatmap(region_channel, annot=True, fmt='.0f', cmap='YlGnBu', linewidths=0.5)
    plt.title('Sales by Region and Channel', fontsize=16)
    plt.tight_layout()
    plt.savefig('region_channel_heatmap.png', dpi=200)
    
    print("Individual KPI plots saved as separate PNG files.")

if __name__ == "__main__":
    create_kpi_dashboard()
    create_individual_kpi_plots() 