import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sheets_integration import setup_sheets_connection

def get_sales_data():
    """Get sales data from Google Sheets or generate sample data if not available."""
    try:
        # Try to get data from Google Sheets
        connector = setup_sheets_connection()
        if connector:
            return connector.get_sales_data()
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        print("Falling back to sample data")
    
    # Fall back to sample data if Google Sheets connection fails
    return generate_sample_sales_data()

def generate_sample_sales_data(rows=1000):
    """Generate sample sales data for testing KPIs."""
    np.random.seed(42)
    
    # Date range for the last year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days)]
    
    # Create sample data with more realistic patterns
    data = {
        'date': np.random.choice(dates, size=rows),
        'product_id': np.random.randint(1, 11, size=rows),
        'customer_id': np.random.randint(1, 101, size=rows),
        'sales_amount': np.random.uniform(10, 500, size=rows),
        'quantity': np.random.randint(1, 10, size=rows),
        'region': np.random.choice(['North', 'South', 'East', 'West'], size=rows),
        'channel': np.random.choice(['Online', 'Store', 'Partner'], size=rows)
    }
    
    # Add some seasonality and trends
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Add weekend effect
    df['is_weekend'] = df['date'].dt.dayofweek.isin([5, 6])
    df.loc[df['is_weekend'], 'sales_amount'] *= 1.2
    
    # Add monthly seasonality
    df['month'] = df['date'].dt.month
    monthly_multipliers = {
        12: 1.5,  # December
        11: 1.3,  # November
        7: 1.2,   # July
        8: 1.2,   # August
    }
    for month, multiplier in monthly_multipliers.items():
        df.loc[df['month'] == month, 'sales_amount'] *= multiplier
    
    # Calculate cost with varying margins by product and channel
    base_cost_ratio = np.random.uniform(0.6, 0.8, size=rows)
    channel_multipliers = {'Online': 0.9, 'Store': 1.0, 'Partner': 1.1}
    df['cost'] = df.apply(lambda x: x['sales_amount'] * base_cost_ratio[x.name] * 
                         channel_multipliers[x['channel']], axis=1)
    
    return df

def calculate_revenue_kpis(df):
    """Calculate revenue-related KPIs."""
    kpis = {}
    
    # Total Revenue
    kpis['total_revenue'] = df['sales_amount'].sum()
    
    # Average Order Value
    kpis['average_order_value'] = df['sales_amount'].mean()
    
    # Revenue by Region
    kpis['revenue_by_region'] = df.groupby('region')['sales_amount'].sum()
    
    # Revenue by Channel
    kpis['revenue_by_channel'] = df.groupby('channel')['sales_amount'].sum()
    
    # Daily Revenue
    kpis['daily_revenue'] = df.groupby('date')['sales_amount'].sum()
    
    # Monthly Revenue
    df_monthly = df.set_index('date').resample('M').sum()
    kpis['monthly_revenue'] = df_monthly['sales_amount']
    
    # Revenue Growth Rate
    if len(kpis['daily_revenue']) > 1:
        kpis['revenue_growth_rate'] = (
            (kpis['daily_revenue'].iloc[-1] - kpis['daily_revenue'].iloc[0]) / 
            kpis['daily_revenue'].iloc[0] * 100
        )
    
    return kpis

def calculate_profitability_kpis(df):
    """Calculate profitability-related KPIs."""
    kpis = {}
    
    # Total Profit
    df['profit'] = df['sales_amount'] - df['cost']
    kpis['total_profit'] = df['profit'].sum()
    
    # Profit Margin
    kpis['profit_margin'] = kpis['total_profit'] / df['sales_amount'].sum() * 100
    
    # Profit by Region
    kpis['profit_by_region'] = df.groupby('region')['profit'].sum()
    
    # Profit by Channel
    kpis['profit_by_channel'] = df.groupby('channel')['profit'].sum()
    
    # Daily Profit
    kpis['daily_profit'] = df.groupby('date')['profit'].sum()
    
    # Monthly Profit
    df_monthly = df.set_index('date').resample('M').sum()
    kpis['monthly_profit'] = df_monthly['profit']
    
    # Profit Growth Rate
    if len(kpis['daily_profit']) > 1:
        kpis['profit_growth_rate'] = (
            (kpis['daily_profit'].iloc[-1] - kpis['daily_profit'].iloc[0]) / 
            kpis['daily_profit'].iloc[0] * 100
        )
    
    return kpis

def calculate_product_kpis(df):
    """Calculate product-related KPIs."""
    kpis = {}
    
    # Product Performance Metrics
    product_metrics = df.groupby('product_id').agg({
        'sales_amount': 'sum',
        'quantity': 'sum',
        'customer_id': 'nunique',
        'cost': 'sum'
    }).reset_index()
    
    product_metrics['profit'] = product_metrics['sales_amount'] - product_metrics['cost']
    product_metrics['profit_margin'] = product_metrics['profit'] / product_metrics['sales_amount'] * 100
    product_metrics['avg_price'] = product_metrics['sales_amount'] / product_metrics['quantity']
    
    kpis['product_metrics'] = product_metrics
    
    # Top Selling Products
    kpis['top_products_by_revenue'] = product_metrics.sort_values('sales_amount', ascending=False)
    
    # Top Products by Quantity
    kpis['top_products_by_quantity'] = product_metrics.sort_values('quantity', ascending=False)
    
    # Most Profitable Products
    kpis['top_products_by_profit'] = product_metrics.sort_values('profit', ascending=False)
    
    # Products by Profit Margin
    kpis['products_by_margin'] = product_metrics.sort_values('profit_margin', ascending=False)
    
    return kpis

def calculate_customer_kpis(df):
    """Calculate customer-related KPIs."""
    kpis = {}
    
    # Customer Value Metrics
    customer_metrics = df.groupby('customer_id').agg({
        'sales_amount': 'sum',
        'customer_id': 'count',
        'date': ['min', 'max']
    }).reset_index()
    
    customer_metrics.columns = ['customer_id', 'total_spent', 'order_count', 'first_purchase', 'last_purchase']
    customer_metrics['avg_order_value'] = customer_metrics['total_spent'] / customer_metrics['order_count']
    customer_metrics['customer_lifetime_days'] = (
        customer_metrics['last_purchase'] - customer_metrics['first_purchase']
    ).dt.days
    
    # Customer Segmentation
    customer_metrics['segment'] = pd.qcut(
        customer_metrics['total_spent'],
        q=4,
        labels=['Low Value', 'Medium Value', 'High Value', 'VIP']
    )
    
    kpis['customer_metrics'] = customer_metrics
    
    # Total Unique Customers
    kpis['unique_customers'] = df['customer_id'].nunique()
    
    # Average Revenue per Customer
    kpis['avg_revenue_per_customer'] = customer_metrics['total_spent'].mean()
    
    # Customer Lifetime Value
    kpis['customer_lifetime_value'] = kpis['avg_revenue_per_customer']
    
    # Orders per Customer
    kpis['orders_per_customer'] = customer_metrics['order_count'].mean()
    
    # Customer Count by Region
    kpis['customers_by_region'] = df.groupby('region')['customer_id'].nunique()
    
    # Customer Count by Channel
    kpis['customers_by_channel'] = df.groupby('channel')['customer_id'].nunique()
    
    # Customer Segmentation Metrics
    segment_metrics = customer_metrics.groupby('segment').agg({
        'customer_id': 'count',
        'total_spent': 'sum',
        'order_count': 'mean',
        'avg_order_value': 'mean'
    }).reset_index()
    
    kpis['segment_metrics'] = segment_metrics
    
    return kpis

def calculate_operational_kpis(df):
    """Calculate operational KPIs."""
    kpis = {}
    
    # Daily Orders
    kpis['daily_orders'] = df.groupby('date').size()
    
    # Average Order Value by Channel
    kpis['avg_order_value_by_channel'] = df.groupby('channel')['sales_amount'].mean()
    
    # Average Order Value by Region
    kpis['avg_order_value_by_region'] = df.groupby('region')['sales_amount'].mean()
    
    # Orders per Day
    kpis['orders_per_day'] = len(df) / df['date'].nunique()
    
    # Peak Sales Hours (if time data available)
    if 'date' in df.columns:
        df['hour'] = df['date'].dt.hour
        kpis['sales_by_hour'] = df.groupby('hour')['sales_amount'].sum()
    
    return kpis

def get_all_kpis():
    """Get sales data and calculate all KPIs."""
    df = get_sales_data()
    
    all_kpis = {}
    all_kpis.update(calculate_revenue_kpis(df))
    all_kpis.update(calculate_profitability_kpis(df))
    all_kpis.update(calculate_product_kpis(df))
    all_kpis.update(calculate_customer_kpis(df))
    all_kpis.update(calculate_operational_kpis(df))
    
    return all_kpis, df

if __name__ == "__main__":
    kpis, df = get_all_kpis()
    
    # Print some KPIs as a test
    print(f"Total Revenue: ${kpis['total_revenue']:.2f}")
    print(f"Average Order Value: ${kpis['average_order_value']:.2f}")
    print(f"Total Profit: ${kpis['total_profit']:.2f}")
    print(f"Profit Margin: {kpis['profit_margin']:.2f}%")
    print(f"Unique Customers: {kpis['unique_customers']}")
    print(f"Customer Lifetime Value: ${kpis['customer_lifetime_value']:.2f}")
    print("\nRevenue by Region:")
    print(kpis['revenue_by_region'])
    print("\nCustomer Segments:")
    print(kpis['segment_metrics']) 