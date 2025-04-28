import pandas as pd
import os
import glob

results_base_dir = "experiments/results"
all_data = []

# Find all assistant result directories (e.g., "results_4o_mini")
assistant_dirs = glob.glob(os.path.join(results_base_dir, "results_*"))

for assistant_dir in assistant_dirs:
    assistant_model = os.path.basename(assistant_dir).replace("results_", "")
    
    # Find requested type directories (e.g., "erc20")
    requested_type_dirs = glob.glob(os.path.join(assistant_dir, "*"))
    
    for req_type_dir in requested_type_dirs:
         # Check if it's actually a directory before proceeding
        if not os.path.isdir(req_type_dir):
            continue
        requested_type = os.path.basename(req_type_dir)
        
        # Find context directories (e.g., "erc721_erc1155")
        context_dirs = glob.glob(os.path.join(req_type_dir, "*"))
        
        for ctx_dir in context_dirs:
            # Check if it's actually a directory before proceeding
            if not os.path.isdir(ctx_dir):
                continue
            context_str_dir = os.path.basename(ctx_dir) # e.g., 'erc721_erc1155' or 'none'
            
            # Construct the expected CSV file name pattern
            # Note: The script run_all_combinations.py uses context with commas in the filename [] part
            # Need to handle both comma and underscore separated context in filename pattern
            
            context_in_filename = context_str_dir.replace('_', ',') if context_str_dir != 'none' else 'none'
            # Original script might have used underscores in filename too
            context_in_filename_alt = context_str_dir if context_str_dir != 'none' else 'none'

            csv_pattern = f"{requested_type}_[{context_in_filename}].csv"
            csv_pattern_alt = f"{requested_type}_[{context_in_filename_alt}].csv" # Handle old naming convention if needed

            csv_path = os.path.join(ctx_dir, csv_pattern)
            csv_path_alt = os.path.join(ctx_dir, csv_pattern_alt)

            actual_csv_path = None
            if os.path.exists(csv_path):
                actual_csv_path = csv_path
            elif os.path.exists(csv_path_alt):
                 actual_csv_path = csv_path_alt
            # Add more specific error handling/logging if neither exists

            if actual_csv_path:
                try:
                    df = pd.read_csv(actual_csv_path)
                    df['assistant_model'] = assistant_model
                    df['requested_type'] = requested_type
                    # Store context as derived from directory, handle 'none' case
                    df['context_types'] = context_str_dir 
                    all_data.append(df)
                except Exception as e:
                    print(f"Error reading {actual_csv_path}: {e}") # Log errors

# Concatenate all DataFrames
if all_data:
    master_df = pd.concat(all_data, ignore_index=True)
    print(f"Successfully aggregated data. Initial total runs: {len(master_df)}")
    
    # --- Data Cleaning ---
    print("\\n--- Cleaning Data ---")
    initial_rows = len(master_df)
    master_df.dropna(subset=['verified'], inplace=True)
    rows_after_null_drop = len(master_df)
    print(f"Dropped {initial_rows - rows_after_null_drop} rows with null 'verified' values.")
    
    # Drop potential duplicates (simplified: drop exact duplicates across key columns, keep first)
    key_cols = ['assistant_model', 'requested_type', 'context_types', 'run']
    master_df.drop_duplicates(subset=key_cols, keep='first', inplace=True)
    rows_after_duplicate_drop = len(master_df)
    print(f"Dropped {rows_after_null_drop - rows_after_duplicate_drop} duplicate rows based on keys.")

    # Convert data types
    master_df['iterations'] = pd.to_numeric(master_df['iterations'], errors='coerce')
    master_df['time_taken'] = pd.to_numeric(master_df['time_taken'], errors='coerce')
    # Ensure 'verified' column exists and handle potential errors before converting
    if 'verified' in master_df.columns:
        master_df['verified'] = master_df['verified'].astype(str).str.lower() == 'true'
    else:
        print("Error: 'verified' column not found after cleaning.")

    if master_df['iterations'].isnull().any() or master_df['time_taken'].isnull().any():
        print("Warning: Errors converting iterations or time_taken to numeric. Nulls introduced.")

    print(f"Cleaned data. Final total runs: {len(master_df)}")
    print("\\n--- Runs per Assistant Model (Post-Cleaning) ---")
    print(master_df['assistant_model'].value_counts())

    # --- Task 1 & 2: Success Rates and Ranking ---
    print("\\n--- Success Rate Analysis ---")
    
    # Group by assistant model
    grouped = master_df.groupby('assistant_model')
    
    # Calculate total runs and successful runs
    summary = grouped['verified'].agg(
        total_runs='size',
        successful_runs=lambda x: x.sum() # Boolean True sums to 1
    ).reset_index()
    
    # Calculate success rate
    summary['success_rate'] = (summary['successful_runs'] / summary['total_runs']) * 100
    
    # Sort by success rate (descending) for ranking
    summary_ranked = summary.sort_values(by='success_rate', ascending=False)
    
    print("Overall Success Rate per Model (Ranked):")
    print(summary_ranked.to_string(index=False, formatters={'success_rate': '{:.2f}%'.format}))

    # Just the ranking by total successful runs
    summary_ranked_by_count = summary.sort_values(by='successful_runs', ascending=False)
    print("\\nModel Ranking by Total Successful Runs:")
    print(summary_ranked_by_count[['assistant_model', 'successful_runs']].to_string(index=False))

else:
    print("No data found or loaded.")
