import os
import pandas as pd
import numpy as np

def generate_sample_data():
    print("Generating sample CSV files for RetailMart...")
    
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
    df_products = pd.DataFrame(products_data)
    df_products.to_csv('products.csv', index=False)
    print(f"Created products.csv with shape: {df_products.shape}")
    
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
    df_stores = pd.DataFrame(stores_data)
    df_stores.to_csv('stores.csv', index=False)
    print(f"Created stores.csv with shape: {df_stores.shape}")
    
    # 3. sales_data.csv (at least 10-15 rows, with missing values and duplicates)
    # We will construct a list of rows to have precise control over duplicates and missing values
    sales_rows = [
        # sale_id, store_id, product_id, quantity, sale_date, amount
        [1001, 'S001', 'P001', 2.0, '2026-06-01', '110000.0'],  # normal
        [1002, 'S002', 'P002', 1.0, '2026-06-01', '25000.0'],   # normal
        [1003, 'S003', 'P003', None, '2026-06-02', '0.0'],       # quantity is missing (should be filled with 0)
        [1004, 'S004', 'P004', 5.0, '2026-06-02', '4000.0'],    # normal
        [1005, 'S005', 'P005', 3.0, '2026-06-03', None],        # amount is missing (should be dropped)
        [1002, 'S002', 'P002', 1.0, '2026-06-01', '25000.0'],   # duplicate of row 2 (should be removed)
        [1006, 'S006', 'P006', 4.0, '2026-06-03', '14000.0'],   # normal
        [1007, 'S007', 'P007', 2.0, '04-06-2026', '10000.0'],   # raw date format (DD-MM-YYYY)
        [1008, 'S008', 'P008', None, '2026/06/04', '0.0'],      # quantity is missing, raw date format (YYYY/MM/DD)
        [1009, 'S009', 'P009', 1.0, '2026-06-05', '4500.0'],    # normal
        [1010, 'S010', 'P010', 2.0, '2026-06-05', '16000.0'],   # normal
        [1011, 'S001', 'P002', 1.0, '2026-06-06', None],        # amount is missing (should be dropped)
        [1009, 'S009', 'P009', 1.0, '2026-06-05', '4500.0'],    # duplicate of row 10 (should be removed)
        [1012, 'S002', 'P011', 3.0, '2026-06-06', '7500.0'],    # normal
        [1013, 'S003', 'P012', 10.0, '2026-06-07', '12000.0'],  # normal
        [1014, 'S004', 'P001', 1.0, '07-06-2026', '55000.0'],   # raw date format (DD-MM-YYYY)
        [1015, 'S005', 'P003', 2.0, '2026-06-08', '6000.0']     # normal
    ]
    
    df_sales = pd.DataFrame(
        sales_rows, 
        columns=['sale_id', 'store_id', 'product_id', 'quantity', 'sale_date', 'amount']
    )
    df_sales.to_csv('sales_data.csv', index=False)
    print(f"Created sales_data.csv with shape: {df_sales.shape}")
    print("Sample sales data created successfully.")

if __name__ == '__main__':
    generate_sample_data()
