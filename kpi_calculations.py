import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_sales_data(rows=1000):
    """Generate sample sales data for testing KPIs."""
    np.random.seed(42)
    
    # Date range for the last year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days)]
    
    # Create sample data
    data = {
        'date': np.random.choice(dates, size=rows),
        'product_id': np.random.randint(1, 11, size=rows),
        'customer_id': np.random.randint(1, 101, size=rows),
        'sales_amount': np.random.uniform(10, 500, size=rows),
        'quantity': np.random.randint(1, 10, size=rows),
        'region': np.random.choice(['North', 'South', 'East', 'West'], size=rows),
        'channel': np.random.choice(['Online', 'Store', 'Partner'], size=rows)
    }
    
    # Calculate cost (60-80% of sales amount)
    cost_ratio = np.random.uniform(0.6, 0.8, size=rows)
    data['cost'] = data['sales_amount'] * cost_ratio
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    
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
    
    # Monthly Revenue
    df_monthly = df.set_index('date').resample('M').sum()
    kpis['monthly_revenue'] = df_monthly['sales_amount']
    
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
    
    # Monthly Profit
    df_monthly = df.set_index('date').resample('M').sum()
    kpis['monthly_profit'] = df_monthly['profit']
    
    return kpis

def calculate_product_kpis(df):
    """Calculate product-related KPIs."""
    kpis = {}
    
    # Top Selling Products
    kpis['top_products_by_revenue'] = df.groupby('product_id')['sales_amount'].sum().sort_values(ascending=False)
    
    # Top Products by Quantity
    kpis['top_products_by_quantity'] = df.groupby('product_id')['quantity'].sum().sort_values(ascending=False)
    
    # Product Profitability
    product_profit = df.groupby('product_id').apply(lambda x: (x['sales_amount'].sum() - x['cost'].sum()))
    kpis['product_profitability'] = product_profit.sort_values(ascending=False)
    
    return kpis

def calculate_customer_kpis(df):
    """Calculate customer-related KPIs."""
    kpis = {}
    
    # Total Unique Customers
    kpis['unique_customers'] = df['customer_id'].nunique()
    
    # Average Revenue per Customer
    customer_revenue = df.groupby('customer_id')['sales_amount'].sum()
    kpis['avg_revenue_per_customer'] = customer_revenue.mean()
    
    # Top Customers
    kpis['top_customers'] = customer_revenue.sort_values(ascending=False).head(10)
    
    # Customer Count by Region
    kpis['customers_by_region'] = df.groupby('region')['customer_id'].nunique()
    
    return kpis

def get_all_kpis():
    """Generate sample data and calculate all KPIs."""
    df = generate_sample_sales_data()
    
    all_kpis = {}
    all_kpis.update(calculate_revenue_kpis(df))
    all_kpis.update(calculate_profitability_kpis(df))
    all_kpis.update(calculate_product_kpis(df))
    all_kpis.update(calculate_customer_kpis(df))
    
    return all_kpis, df

if __name__ == "__main__":
    kpis, df = get_all_kpis()
    
    # Print some KPIs as a test
    print(f"Total Revenue: ${kpis['total_revenue']:.2f}")
    print(f"Average Order Value: ${kpis['average_order_value']:.2f}")
    print(f"Total Profit: ${kpis['total_profit']:.2f}")
    print(f"Profit Margin: {kpis['profit_margin']:.2f}%")
    print(f"Unique Customers: {kpis['unique_customers']}")
    print("\nRevenue by Region:")
    print(kpis['revenue_by_region']) 