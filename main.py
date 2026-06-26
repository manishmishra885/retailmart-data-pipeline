import os
import shutil
from generate_data import generate_sample_data
from pipeline import run_pipeline

def main():
    print("=" * 70)
    print("               RETAILMART DATA PIPELINE RUNNER               ")
    print("=" * 70)
    
    # Step 1: Generate sample data
    generate_sample_data()
    print("\nSample datasets ready. Starting the data pipeline...\n")
    
    # Step 2: Run the data pipeline
    success = run_pipeline()
    
    if not success:
        print("[FAIL] The pipeline did not complete successfully.")
        return

    # Step 3: Demonstrate Error Handling (Task 6 - step 14)
    print("=" * 70)
    print("             DEMONSTRATING PIPELINE ERROR HANDLING             ")
    print("=" * 70)
    print("We will temporarily rename 'sales_data.csv' to 'sales_data_temp.csv'")
    print("and run the pipeline to verify that it handles the missing file gracefully.")
    print("-" * 70)
    
    # Rename file to simulate missing file
    original_sales = 'sales_data.csv'
    temp_sales = 'sales_data_temp.csv'
    
    if os.path.exists(original_sales):
        os.rename(original_sales, temp_sales)
        print(f"Renamed {original_sales} -> {temp_sales}")
        
        # Run pipeline with the original name (which is now missing)
        print("\nRunning pipeline with missing sales_data.csv...")
        run_pipeline(sales_path=original_sales)
        
        # Restore the file
        os.rename(temp_sales, original_sales)
        print("-" * 70)
        print(f"Restored {temp_sales} -> {original_sales}")
        print("Error handling demonstration complete.\n")
    else:
        print("[WARNING] Could not run error handling demo: sales_data.csv not found.")
        
    print("=" * 70)
    print("                    ALL RUNS COMPLETED                    ")
    print("=" * 70)

if __name__ == '__main__':
    main()
