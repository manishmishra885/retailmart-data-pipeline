import streamlit as st
import os
import pandas as pd
import simple_pipeline as sp

# Set page title and layout
st.set_page_config(page_title="RetailMart Data Pipeline", layout="wide")

st.title("🛒 RetailMart Data Pipeline Control Panel")
st.write("This simple application allows you to run each data engineering task step-by-step using buttons.")

# =========================================================================
# STEP 0: Generate Data
# =========================================================================
st.header("Step 0: Generate Raw Sample Data")
st.write("First, generate the raw CSV files (`sales_data.csv`, `products.csv`, `stores.csv`). These contain duplicate rows and missing values to simulate real-world data issues.")

if st.button("Generate Sample CSV Files", key="btn_gen"):
    msg = sp.generate_data()
    st.success(msg)
    
    # Show what files were created
    if os.path.exists('sales_data.csv'):
        st.write("Created files:")
        st.write("- `sales_data.csv` (Transactions)")
        st.write("- `products.csv` (Product Catalog)")
        st.write("- `stores.csv` (Store Directory)")

st.markdown("---")

# =========================================================================
# TASK 1: DATA INGESTION
# =========================================================================
st.header("Task 1: Data Ingestion")
st.write("Load the three raw CSV files into pandas DataFrames and inspect them for missing values.")

if st.button("Run Task 1: Load Data", key="btn_task1"):
    try:
        # Run ingestion
        df_sales, df_products, df_stores, nulls = sp.task1_ingest()
        
        # Save to session state so next buttons can use them
        st.session_state['df_sales'] = df_sales
        st.session_state['df_products'] = df_products
        st.session_state['df_stores'] = df_stores
        
        st.success("Data successfully loaded!")
        
        # Display shapes and data
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader(f"Sales Data {df_sales.shape}")
            st.dataframe(df_sales.head(8))
        with col2:
            st.subheader(f"Products {df_products.shape}")
            st.dataframe(df_products.head(8))
        with col3:
            st.subheader(f"Stores {df_stores.shape}")
            st.dataframe(df_stores.head(8))
            
        # Display missing values
        st.subheader("Missing Values (Nulls) Summary:")
        st.write("**Sales Data Nulls:**", nulls['sales_data'])
        st.write("**Products Data Nulls:**", nulls['products'])
        st.write("**Stores Data Nulls:**", nulls['stores'])
        
    except FileNotFoundError:
        st.error("Error: CSV files not found. Please click 'Generate Sample CSV Files' in Step 0 first.")
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("---")

# =========================================================================
# TASK 2: DATA CLEANING
# =========================================================================
st.header("Task 2: Data Cleaning")
st.write("Remove duplicates from sales data, fill missing quantities with 0, drop rows where amount is missing, and convert columns to proper types.")

if st.button("Run Task 2: Clean Sales Data", key="btn_task2"):
    if 'df_sales' not in st.session_state:
        st.warning("Please run **Task 1: Load Data** first so we have data to clean!")
    else:
        # Run cleaning
        df_sales_cleaned, duplicates_removed = sp.task2_clean(st.session_state['df_sales'])
        
        # Save cleaned data
        st.session_state['df_sales_cleaned'] = df_sales_cleaned
        
        st.success(f"Cleaning complete! Removed {duplicates_removed} duplicate rows.")
        
        # Display before and after shapes
        st.write(f"Original Sales Rows: {len(st.session_state['df_sales'])} | Cleaned Sales Rows: {len(df_sales_cleaned)}")
        
        st.subheader("Cleaned Sales DataFrame:")
        st.dataframe(df_sales_cleaned)
        
        # Display data types
        st.write("Converted Data Types:")
        st.write(df_sales_cleaned.dtypes[['sale_date', 'amount']].astype(str).to_dict())

st.markdown("---")

# =========================================================================
# TASK 3: DATA TRANSFORMATION
# =========================================================================
st.header("Task 3: Data Transformation")
st.write("Merge sales, products, and stores into one DataFrame. Calculate total revenue and find sales performance by city.")

if st.button("Run Task 3: Transform & Merge Data", key="btn_task3"):
    if 'df_sales_cleaned' not in st.session_state:
        st.warning("Please run **Task 2: Clean Sales Data** first!")
    else:
        # Run transformation
        df_merged, stats, df_city_revenue = sp.task3_transform(
            st.session_state['df_sales_cleaned'],
            st.session_state['df_products'],
            st.session_state['df_stores']
        )
        
        # Save merged data
        st.session_state['df_merged'] = df_merged
        
        st.success("Merging and transformations complete!")
        
        st.subheader("Merged Final DataFrame:")
        st.dataframe(df_merged)
        
        # Display NumPy stats
        st.subheader("NumPy Revenue Statistics:")
        st.write(f"- **Mean Revenue:** INR {stats['mean']:.2f}")
        st.write(f"- **Max Revenue:** INR {stats['max']:.2f}")
        st.write(f"- **Min Revenue:** INR {stats['min']:.2f}")
        
        # Display city revenue
        st.subheader("Total Revenue per City (Sorted Descending):")
        st.dataframe(df_city_revenue)

st.markdown("---")

# =========================================================================
# TASK 4: DATA LOADING (SQL)
# =========================================================================
st.header("Task 4: Data Loading (SQL)")
st.write("Load the final merged data into a SQLite database table called `retail_sales` and query the top 3 best-selling products.")

if st.button("Run Task 4: Load to SQLite Database", key="btn_task4"):
    if 'df_merged' not in st.session_state:
        st.warning("Please run **Task 3: Transform & Merge Data** first!")
    else:
        # Run loading to SQLite and querying
        df_top_products = sp.task4_load_db(st.session_state['df_merged'])
        
        st.success("Successfully loaded data into database table 'retail_sales' inside 'retail_mart.db'!")
        
        st.subheader("SQL Query Result: Top 3 Best-Selling Products (by Quantity Sold):")
        st.dataframe(df_top_products)

st.markdown("---")

# =========================================================================
# TASK 5: REPORTING & INSIGHTS
# =========================================================================
st.header("Task 5: Reporting & Insights")
st.write("Generate daily store revenue reports from the database and print an executive summary report.")

if st.button("Run Task 5: Generate Reports", key="btn_task5"):
    if not os.path.exists('retail_mart.db'):
        st.warning("Please run **Task 4: Load to SQLite Database** first to create the database table!")
    else:
        # Run reporting
        df_daily_store_revenue, summary = sp.task5_report()
        
        st.success("Reports generated successfully from SQLite database!")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("SQL Query Result: Daily Store Revenue:")
            # Format sale_date for better readability
            df_daily_store_revenue['sale_date'] = pd.to_datetime(df_daily_store_revenue['sale_date']).dt.strftime('%Y-%m-%d')
            st.dataframe(df_daily_store_revenue)
            
        with col2:
            st.subheader("RetailMart Summary Report:")
            st.info(
                f"**Total Transactions:** {summary['transactions']}\n\n"
                f"**Total Revenue:** INR {summary['revenue']:,.2f}\n\n"
                f"**Top Selling City:** {summary['top_city']}\n\n"
                f"**Top Selling Product:** {summary['top_product']}"
            )

st.markdown("---")

# =========================================================================
# TASK 6: PIPELINE & ERROR HANDLING
# =========================================================================
st.header("Task 6: Pipeline & Error Handling (All-in-One)")
st.write("Run the entire data pipeline (Load ➡️ Clean ➡️ Transform ➡️ Load DB) in a single click with robust error handling.")

if st.button("Run Task 6: Execute Full Pipeline", key="btn_task6"):
    # Generate data if missing
    if not os.path.exists('sales_data.csv'):
        sp.generate_data()
    result = sp.run_pipeline()
    
    if result['status'] == 'Success':
        st.success("Pipeline executed successfully without any errors!")
        
        # Display overall summary in UI
        summary = result['summary']
        stats = result['stats']
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Executive Report Summary:")
            st.info(
                f"**Total Transactions:** {summary['transactions']}\n\n"
                f"**Total Revenue:** INR {summary['revenue']:,.2f}\n\n"
                f"**Top Selling City:** {summary['top_city']}\n\n"
                f"**Top Selling Product:** {summary['top_product']}"
            )
        with col2:
            st.subheader("NumPy Revenue Stats:")
            st.write(f"- **Mean:** INR {stats['mean']:.2f}")
            st.write(f"- **Max:** INR {stats['max']:.2f}")
            st.write(f"- **Min:** INR {stats['min']:.2f}")
            
        st.subheader("Top 3 Products by Quantity:")
        st.dataframe(result['top_products'])
        
        st.subheader("City Revenue Distribution:")
        st.dataframe(result['city_revenue'])
        
    else:
        st.error(result['message'])
        st.info("Ensure that 'sales_data.csv', 'products.csv', and 'stores.csv' are present by clicking 'Generate Sample CSV Files' at the top.")