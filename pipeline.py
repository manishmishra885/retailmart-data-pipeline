import os
import sqlite3
import pandas as pd
import numpy as np

def run_pipeline(sales_path='sales_data.csv', products_path='products.csv', stores_path='stores.csv', db_path='retail_mart.db'):
    """
    RetailMart Data Pipeline: Ingests, cleans, transforms, and loads sales data.
    Includes comprehensive error handling for missing files and database issues.
    """
    print("=" * 60)
    print("           RETAILMART DATA PIPELINE RUN           ")
    print("=" * 60)
    
    # -------------------------------------------------------------------------
    # Task 6: Error Handling - Verify files exist before loading
    # -------------------------------------------------------------------------
    missing_files = []
    for path, name in [(sales_path, 'Sales Data'), (products_path, 'Products'), (stores_path, 'Stores')]:
        if not os.path.exists(path):
            missing_files.append(f"{name} ({path})")
            
    if missing_files:
        print("\n[ERROR] Pipeline execution failed due to missing files:")
        for mf in missing_files:
            print(f"  - Missing: {mf}")
        print("\nPlease ensure all source CSV files are present before running the pipeline.\n")
        return False

    try:
        # =========================================================================
        # TASK 1: DATA INGESTION
        # =========================================================================
        print("\n--- TASK 1: DATA INGESTION ---")
        
        # 1. Load CSVs into pandas DataFrames and print shape/first 5 rows
        print(f"Loading {sales_path}...")
        df_sales = pd.read_csv(sales_path)
        print(f"  Shape: {df_sales.shape}")
        print("  First 5 rows:")
        print(df_sales.head())
        print("-" * 50)
        
        print(f"Loading {products_path}...")
        df_products = pd.read_csv(products_path)
        print(f"  Shape: {df_products.shape}")
        print("  First 5 rows:")
        print(df_products.head())
        print("-" * 50)
        
        print(f"Loading {stores_path}...")
        df_stores = pd.read_csv(stores_path)
        print(f"  Shape: {df_stores.shape}")
        print("  First 5 rows:")
        print(df_stores.head())
        print("-" * 50)
        
        # 2. Check for missing values in all three DataFrames
        print("Checking for missing values in DataFrames:")
        for df, name in [(df_sales, 'sales_data'), (df_products, 'products'), (df_stores, 'stores')]:
            print(f"\nMissing values in '{name}':")
            null_summary = df.isnull().sum()
            print(null_summary[null_summary > 0] if null_summary.sum() > 0 else "No missing values found.")
            
        # =========================================================================
        # TASK 2: DATA CLEANING
        # =========================================================================
        print("\n--- TASK 2: DATA CLEANING ---")
        
        # 3. Remove all duplicate rows from sales_data
        initial_sales_shape = df_sales.shape
        # Identify duplicates (for printing)
        duplicates = df_sales[df_sales.duplicated()]
        num_duplicates = len(duplicates)
        
        df_sales_cleaned = df_sales.drop_duplicates()
        print(f"Found and removed {num_duplicates} duplicate rows from sales_data.")
        if num_duplicates > 0:
            print("Removed Duplicate Rows:")
            print(duplicates)
            
        # 4. Fill missing values in 'quantity' with 0 and drop rows where 'amount' is NULL
        # Before filling, keep track of rows with null quantity for transparency
        null_qty_count = df_sales_cleaned['quantity'].isnull().sum()
        df_sales_cleaned = df_sales_cleaned.copy() # Avoid SettingWithCopyWarning
        df_sales_cleaned['quantity'] = df_sales_cleaned['quantity'].fillna(0)
        print(f"Filled {null_qty_count} missing values in 'quantity' with 0.")
        
        # Drop rows where 'amount' is NULL
        null_amount_count = df_sales_cleaned['amount'].isnull().sum()
        df_sales_cleaned = df_sales_cleaned.dropna(subset=['amount'])
        print(f"Dropped {null_amount_count} rows where 'amount' was NULL.")
        print(f"Cleaned sales_data shape: {df_sales_cleaned.shape}")
        
        # 5. Convert 'sale_date' to proper datetime and 'amount' to float
        # Convert sale_date using mixed format handling
        df_sales_cleaned['sale_date'] = pd.to_datetime(df_sales_cleaned['sale_date'], format='mixed')
        # Clean amount if there are any formatting issues (e.g. whitespace), then cast to float
        df_sales_cleaned['amount'] = df_sales_cleaned['amount'].astype(str).str.strip().astype(float)
        print("Data types converted successfully:")
        print(df_sales_cleaned.dtypes[['sale_date', 'amount']])
        
        # =========================================================================
        # TASK 3: DATA TRANSFORMATION
        # =========================================================================
        print("\n--- TASK 3: DATA TRANSFORMATION ---")
        
        # 6. Merge all three DataFrames into one final DataFrame (Inner join)
        # Using inner join to match sales with their respective products and stores
        df_merged = df_sales_cleaned.merge(df_stores, on='store_id', how='inner')
        df_merged = df_merged.merge(df_products, on='product_id', how='inner')
        print("Final merged DataFrame:")
        print(f"  Shape: {df_merged.shape}")
        print(df_merged.head())
        print("-" * 50)
        
        # 7. Add a new column 'total_revenue' = quantity * price
        df_merged['total_revenue'] = df_merged['quantity'] * df_merged['price']
        
        # Use NumPy to calculate and print mean, max, and min of total_revenue
        mean_revenue = np.mean(df_merged['total_revenue'])
        max_revenue = np.max(df_merged['total_revenue'])
        min_revenue = np.min(df_merged['total_revenue'])
        print("NumPy Revenue Statistics:")
        print(f"  Mean Total Revenue: {mean_revenue:.2f}")
        print(f"  Max Total Revenue:  {max_revenue:.2f}")
        print(f"  Min Total Revenue:  {min_revenue:.2f}")
        print("-" * 50)
        
        # 8. Group by 'city' and find total revenue per city, sorted descending
        city_revenue = df_merged.groupby('city')['total_revenue'].sum().reset_index()
        city_revenue = city_revenue.sort_values(by='total_revenue', ascending=False)
        print("Total Revenue by City (Descending):")
        print(city_revenue.to_string(index=False))
        
        # =========================================================================
        # TASK 4: DATA LOADING (SQL)
        # =========================================================================
        print("\n--- TASK 4: DATA LOADING (SQL) ---")
        
        # 9. Load final cleaned and merged DataFrame into SQLite table 'retail_sales'
        print(f"Connecting to SQLite database: {db_path}...")
        conn = sqlite3.connect(db_path)
        
        # Load the data, replacing the table if it already exists
        df_merged.to_sql('retail_sales', conn, if_exists='replace', index=False)
        print("Loaded data successfully into table 'retail_sales'.")
        
        # 10. SQL query to find the Top 3 best-selling products by total quantity sold
        top_products_query = """
        SELECT product_name, SUM(quantity) as total_quantity_sold
        FROM retail_sales
        GROUP BY product_name
        ORDER BY total_quantity_sold DESC
        LIMIT 3
        """
        print("\nExecuting SQL Query: Top 3 best-selling products by total quantity sold...")
        df_top_products = pd.read_sql_query(top_products_query, conn)
        print(df_top_products.to_string(index=False))
        
        # =========================================================================
        # TASK 5: REPORTING & INSIGHTS
        # =========================================================================
        print("\n--- TASK 5: REPORTING & INSIGHTS ---")
        
        # 11. SQL query to find total revenue per store per day
        store_daily_revenue_query = """
        SELECT store_name, sale_date, SUM(total_revenue) as daily_revenue
        FROM retail_sales
        GROUP BY store_name, sale_date
        ORDER BY sale_date ASC, daily_revenue DESC
        """
        print("Executing SQL Query: Total revenue per store per day...")
        df_daily_revenue = pd.read_sql_query(store_daily_revenue_query, conn)
        # Format the sale_date column in the output for better readability
        df_daily_revenue['sale_date'] = pd.to_datetime(df_daily_revenue['sale_date']).dt.strftime('%Y-%m-%d')
        print(df_daily_revenue.to_string(index=False))
        print("-" * 50)
        
        # 12. Using Python, print a summary report showing:
        # Total transactions, Total revenue, Top selling city, and Top selling product
        total_transactions = len(df_merged)
        total_revenue_sum = df_merged['total_revenue'].sum()
        
        # Top selling city (by total revenue)
        top_city_row = city_revenue.iloc[0]
        top_city_name = top_city_row['city']
        top_city_rev = top_city_row['total_revenue']
        
        # Top selling product by total quantity sold
        product_sales = df_merged.groupby('product_name')['quantity'].sum().reset_index()
        top_product_row = product_sales.sort_values(by='quantity', ascending=False).iloc[0]
        top_product_name = top_product_row['product_name']
        top_product_qty = top_product_row['quantity']
        
        # Top selling product by total revenue generated (as alternative insight)
        product_revenue = df_merged.groupby('product_name')['total_revenue'].sum().reset_index()
        top_prod_rev_row = product_revenue.sort_values(by='total_revenue', ascending=False).iloc[0]
        top_prod_rev_name = top_prod_rev_row['product_name']
        top_prod_rev_val = top_prod_rev_row['total_revenue']
        
        print("                 RETAILMART SUMMARY REPORT                ")
        print("=" * 50)
        print(f"Total Transactions Processed : {total_transactions}")
        print(f"Total Revenue Generated      : INR {total_revenue_sum:,.2f}")
        print(f"Top Selling City             : {top_city_name} (INR {top_city_rev:,.2f})")
        print(f"Top Selling Product (Qty)    : {top_product_name} ({int(top_product_qty)} units sold)")
        print(f"Top Selling Product (Revenue): {top_prod_rev_name} (INR {top_prod_rev_val:,.2f})")
        print("=" * 50)
        
        # Close database connection
        conn.close()
        print("\nDatabase connection closed. Pipeline run completed successfully.")
        print("=" * 60 + "\n")
        return True
        
    except sqlite3.Error as se:
        print(f"\n[ERROR] Database error occurred: {se}")
        return False
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred in the pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    run_pipeline()
