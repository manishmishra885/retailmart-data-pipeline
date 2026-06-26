import os
import sqlite3
import pandas as pd
import numpy as np

def generate_data():
    """Generates the three raw CSV files with some intentional errors (duplicates, nulls)."""
    # 1. products.csv (at least 10-15 rows)
    products_data = {
        'product_id': [f'P{i:03d}' for i in range(1, 13)],
        'product_name': [
            'Laptop', 'Smartphone', 'Headphones', 'T-Shirt', 'Jeans', 
            'Running Shoes', 'Watch', 'Backpack', 'Coffee Maker', 
            'Vacuum Cleaner', 'Blender', 'Desk Lamp'
        ],
        'category': [
            'Electronics', 'Electronics', 'Electronics', 'Apparel', 'Apparel', 
            'Footwear', 'Accessories', 'Accessories', 'Appliances', 
            'Appliances', 'Appliances', 'Home Decor'
        ],
        'price': [55000.0, 25000.0, 3000.0, 800.0, 1500.0, 3500.0, 5000.0, 2000.0, 4500.0, 8000.0, 2500.0, 1200.0]
    }
    pd.DataFrame(products_data).to_csv('products.csv', index=False)
    
    # 2. stores.csv (at least 10-15 rows)
    stores_data = {
        'store_id': [f'S{i:03d}' for i in range(1, 11)],
        'store_name': [
            'RetailMart Delhi', 'RetailMart Mumbai', 'RetailMart Bengaluru', 
            'RetailMart Kolkata', 'RetailMart Chennai', 'RetailMart Hyderabad', 
            'RetailMart Pune', 'RetailMart Ahmedabad', 'RetailMart Jaipur', 'RetailMart Lucknow'
        ],
        'city': ['Delhi', 'Mumbai', 'Bengaluru', 'Kolkata', 'Chennai', 'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'],
        'region': ['North', 'West', 'South', 'East', 'South', 'South', 'West', 'West', 'North', 'North']
    }
    pd.DataFrame(stores_data).to_csv('stores.csv', index=False)
    
    # 3. sales_data.csv (at least 10-15 rows, with missing values and duplicates)
    sales_rows = [
        [1001, 'S001', 'P001', 2.0, '2026-06-01', 110000.0],
        [1002, 'S002', 'P002', 1.0, '2026-06-01', 25000.0],
        [1003, 'S003', 'P003', None, '2026-06-02', 0.0],
        [1004, 'S004', 'P004', 5.0, '2026-06-02', 4000.0],
        [1005, 'S005', 'P005', 3.0, '2026-06-03', None],
        [1002, 'S002', 'P002', 1.0, '2026-06-01', 25000.0],
        [1006, 'S006', 'P006', 4.0, '2026-06-03', 14000.0],
        [1007, 'S007', 'P007', 2.0, '04-06-2026', 10000.0],
        [1008, 'S008', 'P008', None, '2026/06/04', 0.0],
        [1009, 'S009', 'P009', 1.0, '2026-06-05', 4500.0],
        [1010, 'S010', 'P010', 2.0, '2026-06-05', 16000.0],
        [1011, 'S001', 'P002', 1.0, '2026-06-06', None],
        [1009, 'S009', 'P009', 1.0, '2026-06-05', 4500.0],
        [1012, 'S002', 'P011', 3.0, '2026-06-06', 7500.0],
        [1013, 'S003', 'P012', 10.0, '2026-06-07', 12000.0],
        [1014, 'S004', 'P001', 1.0, '07-06-2026', 55000.0],
        [1015, 'S005', 'P003', 2.0, '2026-06-08', 6000.0]
    ]
    pd.DataFrame(sales_rows, columns=['sale_id', 'store_id', 'product_id', 'quantity', 'sale_date', 'amount']).to_csv('sales_data.csv', index=False)
    return "Sample CSV files generated successfully."

def task1_ingest():
    """Loads CSV files and counts missing values."""
    df_sales = pd.read_csv('sales_data.csv')
    df_products = pd.read_csv('products.csv')
    df_stores = pd.read_csv('stores.csv')
    null_summary = {
        'sales_data': df_sales.isnull().sum().to_dict(),
        'products': df_products.isnull().sum().to_dict(),
        'stores': df_stores.isnull().sum().to_dict()
    }
    return df_sales, df_products, df_stores, null_summary

def task2_clean(df_sales):
    """Cleans sales data by removing duplicates, filling nulls, and formatting columns."""
    initial_len = len(df_sales)
    df_cleaned = df_sales.drop_duplicates()
    duplicates_removed = initial_len - len(df_cleaned)
    
    df_cleaned = df_cleaned.copy()
    df_cleaned['quantity'] = df_cleaned['quantity'].fillna(0)
    df_cleaned = df_cleaned.dropna(subset=['amount'])
    
    df_cleaned['sale_date'] = pd.to_datetime(df_cleaned['sale_date'], format='mixed')
    df_cleaned['amount'] = df_cleaned['amount'].astype(float)
    return df_cleaned, duplicates_removed

def task3_transform(df_sales_cleaned, df_products, df_stores):
    """Merges all datasets, calculates total revenue, and computes stats."""
    df_merged = df_sales_cleaned.merge(df_stores, on='store_id', how='inner')
    df_merged = df_merged.merge(df_products, on='product_id', how='inner')
    
    df_merged['total_revenue'] = df_merged['quantity'] * df_merged['price']
    stats = {
        'mean': float(np.mean(df_merged['total_revenue'])),
        'max': float(np.max(df_merged['total_revenue'])),
        'min': float(np.min(df_merged['total_revenue']))
    }
    df_city_revenue = df_merged.groupby('city')['total_revenue'].sum().reset_index()
    df_city_revenue = df_city_revenue.sort_values(by='total_revenue', ascending=False)
    return df_merged, stats, df_city_revenue

def task4_load_db(df_merged):
    """Loads the merged DataFrame into a SQLite database and queries top 3 products."""
    conn = sqlite3.connect('retail_mart.db')
    df_merged.to_sql('retail_sales', conn, if_exists='replace', index=False)
    
    top_query = """
    SELECT product_name, SUM(quantity) as total_quantity
    FROM retail_sales
    GROUP BY product_name
    ORDER BY total_quantity DESC
    LIMIT 3
    """
    df_top = pd.read_sql_query(top_query, conn)
    conn.close()
    return df_top

def task5_report():
    """Queries daily store revenue from the database and returns overall summary numbers."""
    conn = sqlite3.connect('retail_mart.db')
    daily_query = """
    SELECT store_name, sale_date, SUM(total_revenue) as daily_revenue
    FROM retail_sales
    GROUP BY store_name, sale_date
    ORDER BY sale_date ASC, daily_revenue DESC
    """
    df_daily = pd.read_sql_query(daily_query, conn)
    
    # Summary calculations
    df_all = pd.read_sql_query("SELECT * FROM retail_sales", conn)
    total_tx = len(df_all)
    total_rev = df_all['total_revenue'].sum()
    
    # Top city
    city_revenue = df_all.groupby('city')['total_revenue'].sum().reset_index()
    top_city = city_revenue.sort_values(by='total_revenue', ascending=False).iloc[0]['city'] if len(city_revenue) > 0 else "N/A"
    
    # Top product
    product_sales = df_all.groupby('product_name')['quantity'].sum().reset_index()
    top_prod = product_sales.sort_values(by='quantity', ascending=False).iloc[0]['product_name'] if len(product_sales) > 0 else "N/A"
    
    conn.close()
    summary = {
        'transactions': total_tx,
        'revenue': total_rev,
        'top_city': top_city,
        'top_product': top_prod
    }
    return df_daily, summary

def run_pipeline():
    """Runs all tasks in one function call with basic try-except error handling."""
    try:
        # Check files
        for f in ['sales_data.csv', 'products.csv', 'stores.csv']:
            if not os.path.exists(f):
                raise FileNotFoundError(f"Missing file: {f}")
        df_sales, df_products, df_stores, nulls = task1_ingest()
        df_clean, dups = task2_clean(df_sales)
        df_merged, stats, city_rev = task3_transform(df_clean, df_products, df_stores)
        df_top = task4_load_db(df_merged)
        df_daily, summary = task5_report()
        return {
            'status': 'Success',
            'summary': summary,
            'stats': stats,
            'top_products': df_top,
            'city_revenue': city_rev
        }
    except Exception as e:
        return {'status': 'Error', 'message': str(e)}