import pandas as pd
import os
import glob
import numpy as np

# --- Data Loading ---
results_base_dir = "experiments/results"
all_data = []

# Find all assistant result directories (e.g., "results_4o_mini")
assistant_dirs = glob.glob(os.path.join(results_base_dir, "results_*"))

for assistant_dir in assistant_dirs:
    assistant_model = os.path.basename(assistant_dir).replace("results_", "")
    requested_type_dirs = glob.glob(os.path.join(assistant_dir, "*"))
    for req_type_dir in requested_type_dirs:
        if not os.path.isdir(req_type_dir):
            continue
        requested_type = os.path.basename(req_type_dir)
        context_dirs = glob.glob(os.path.join(req_type_dir, "*"))
        for ctx_dir in context_dirs:
            if not os.path.isdir(ctx_dir):
                continue
            context_str_dir = os.path.basename(ctx_dir)
            context_in_filename = context_str_dir.replace('_', ',') if context_str_dir != 'none' else 'none'
            context_in_filename_alt = context_str_dir if context_str_dir != 'none' else 'none'
            csv_pattern = f"{requested_type}_[{context_in_filename}].csv"
            csv_pattern_alt = f"{requested_type}_[{context_in_filename_alt}].csv"
            csv_path = os.path.join(ctx_dir, csv_pattern)
            csv_path_alt = os.path.join(ctx_dir, csv_pattern_alt)
            actual_csv_path = None
            if os.path.exists(csv_path):
                actual_csv_path = csv_path
            elif os.path.exists(csv_path_alt):
                 actual_csv_path = csv_path_alt
            if actual_csv_path:
                try:
                    df = pd.read_csv(actual_csv_path, on_bad_lines='skip') 
                    df['assistant_model'] = assistant_model
                    df['requested_type'] = requested_type
                    df['context_types'] = context_str_dir 
                    all_data.append(df)
                except Exception as e:
                    print(f"Error reading {actual_csv_path}: {e}")

# --- Data Aggregation and Cleaning ---
if all_data:
    master_df = pd.concat(all_data, ignore_index=True)
    print(f"Successfully aggregated data. Initial total runs: {len(master_df)}")
    print("\n--- Cleaning Data ---")
    initial_rows = len(master_df)
    master_df.dropna(subset=['verified'], inplace=True)
    rows_after_null_drop = len(master_df)
    print(f"Dropped {initial_rows - rows_after_null_drop} rows with null 'verified' values.")
    key_cols = ['assistant_model', 'requested_type', 'context_types', 'run']
    master_df['run_num'] = pd.to_numeric(master_df['run'], errors='coerce')
    master_df.dropna(subset=['run_num'], inplace=True)
    key_cols_numeric = ['assistant_model', 'requested_type', 'context_types', 'run_num']
    master_df.drop_duplicates(subset=key_cols_numeric, keep='first', inplace=True)
    master_df.drop(columns=['run_num'], inplace=True)
    rows_after_duplicate_drop = len(master_df)
    print(f"Dropped {rows_after_null_drop - rows_after_duplicate_drop} duplicate rows based on keys.")
    master_df['iterations'] = pd.to_numeric(master_df['iterations'], errors='coerce')
    master_df['time_taken'] = pd.to_numeric(master_df['time_taken'], errors='coerce')
    if 'verified' in master_df.columns:
        master_df['verified'] = master_df['verified'].astype(str).str.lower() == 'true'
    else:
        print("Error: 'verified' column not found after cleaning.")
        master_df = pd.DataFrame()
    master_df.dropna(subset=['iterations', 'time_taken'], inplace=True)
    print(f"Dropped rows where iterations/time_taken conversion failed: {rows_after_duplicate_drop - len(master_df)}")
    print(f"Cleaned data. Final total runs for analysis: {len(master_df)}")

    # --- Model Specificity Analysis ---
    if not master_df.empty:
        print("\n--- Model Specificity Analysis (Performance per Requested Type) ---")

        # Group by assistant model and requested type
        grouped_specificity = master_df.groupby(['assistant_model', 'requested_type'])
        
        # Calculate total runs and successful runs for each group
        summary_specificity = grouped_specificity['verified'].agg(
            total_runs='size',
            successful_runs=lambda x: x.sum() # Boolean True sums to 1
        ).reset_index()
        
        # Calculate success rate
        summary_specificity['success_rate'] = (summary_specificity['successful_runs'] / summary_specificity['total_runs']) * 100
        
        # Pivot the table for better comparison across requested types for each model
        try:
            pivot_specificity = pd.pivot_table(summary_specificity, 
                                               values='success_rate', 
                                               index='assistant_model', 
                                               columns='requested_type',
                                               aggfunc=np.mean) # Already calculated
            
            print("\nSuccess Rate (%) for each Model on each Requested Type:")
            print(pivot_specificity.to_string(float_format='{:.2f}'.format, na_rep='-'))

            # Optional: Show counts as well
            pivot_counts = pd.pivot_table(summary_specificity, 
                                           values='successful_runs', 
                                           index='assistant_model', 
                                           columns='requested_type',
                                           aggfunc=np.sum) # Sum successful runs
            pivot_total = pd.pivot_table(summary_specificity, 
                                           values='total_runs', 
                                           index='assistant_model', 
                                           columns='requested_type',
                                           aggfunc=np.sum) # Sum total runs 

            print("\nSuccessful Runs / Total Runs for each Model on each Requested Type:")
            # Combine counts into a string format like "success/total"
            count_str_df = pivot_counts.astype(str) + " / " + pivot_total.astype(str)
            print(count_str_df.to_string(na_rep='-'))

        except Exception as e:
             print(f"Error creating pivot table: {e}")
             print("\nRaw Specificity Analysis Data:")
             print(summary_specificity.to_string(index=False, float_format='{:.2f}'.format))

else:
    print("No data found or loaded.") 