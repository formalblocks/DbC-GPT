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
    
    # Find requested type directories (e.g., "erc20")
    requested_type_dirs = glob.glob(os.path.join(assistant_dir, "*"))
    
    for req_type_dir in requested_type_dirs:
        if not os.path.isdir(req_type_dir):
            continue
        requested_type = os.path.basename(req_type_dir)
        
        # Find context directories (e.g., "erc721_erc1155")
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
        master_df = pd.DataFrame() # Avoid processing if error

    # Drop rows where conversion failed
    master_df.dropna(subset=['iterations', 'time_taken'], inplace=True)
    print(f"Dropped rows where iterations/time_taken conversion failed: {rows_after_duplicate_drop - len(master_df)}")

    print(f"Cleaned data. Final total runs for analysis: {len(master_df)}")

    # --- Efficiency Analysis ---
    if not master_df.empty:
        print("\n--- Efficiency Analysis ---")

        # 1. Overall Averages (Successful vs. Failed)
        print("\n--- Overall Average Iterations and Time ---")
        overall_efficiency = master_df.groupby('verified')[['iterations', 'time_taken']].mean().reset_index()
        overall_efficiency.rename(columns={'verified': 'Run Succeeded'}, inplace=True)
        print(overall_efficiency.to_string(index=False, float_format='{:.2f}'.format))

        # 2. Averages per Model (Successful vs. Failed)
        print("\n--- Average Iterations and Time per Model ---")
        model_efficiency = master_df.groupby(['assistant_model', 'verified'])\
[['iterations', 'time_taken']].agg(['mean', 'count']).unstack(fill_value=0) # Use unstack and fillna
        # Format column names for clarity
        model_efficiency.columns = [f'{stat}_{agg_func}_{("Success" if verified else "Fail")}' \
                                    for stat, agg_func, verified in model_efficiency.columns]
        # Calculate Fail Rate %
        total_runs = model_efficiency['iterations_count_Fail'] + model_efficiency['iterations_count_Success']
        model_efficiency['Fail_Rate'] = (model_efficiency['iterations_count_Fail'] / total_runs) * 100
        model_efficiency.sort_values(by='Fail_Rate', ascending=False, inplace=True)
        print(model_efficiency.to_string(float_format='{:.2f}'.format))

        # 3. Efficiency by Fine-tuning Level (Successful Runs Only)
        print("\n--- Average Iterations and Time for SUCCESSFUL Runs by Fine-tuning Level ---")
        model_sets = {
            'erc20': ['4o_mini', 'erc20-4-o-mini', 'erc20-721-4-o-mini', 'erc20-1155-4-o-mini', 'erc20-721-1155-4-o-mini'],
            'erc721': ['4o_mini', 'erc721-4-o-mini', 'erc20-721-4-o-mini', 'erc721-1155-4-o-mini', 'erc20-721-1155-4-o-mini'],
            'erc1155': ['4o_mini', 'erc1155-4-o-mini', 'erc20-1155-4-o-mini', 'erc721-1155-4-o-mini', 'erc20-721-1155-4-o-mini']
        }
        ft_levels = { 
            '4o_mini': 0,
            'erc20-4-o-mini': 1, 'erc721-4-o-mini': 1, 'erc1155-4-o-mini': 1,
            'erc20-721-4-o-mini': 2, 'erc20-1155-4-o-mini': 2, 'erc721-1155-4-o-mini': 2,
            'erc20-721-1155-4-o-mini': 3
        }

        successful_runs = master_df[master_df['verified']].copy()

        for req_type, relevant_models in model_sets.items():
            print(f"\n--- Efficiency for SUCCESSFUL {req_type.upper()} Task ---")
            df_filtered = successful_runs[
                (successful_runs['requested_type'] == req_type) &
                (successful_runs['assistant_model'].isin(relevant_models))
            ].copy()
            
            if df_filtered.empty:
                print(f"No successful runs found for requested type {req_type} with relevant models.")
                continue

            grouped = df_filtered.groupby('assistant_model')[['iterations', 'time_taken']].mean().reset_index()
            grouped['ft_level'] = grouped['assistant_model'].map(ft_levels)
            grouped_sorted = grouped.sort_values(by=['ft_level', 'iterations'], ascending=[True, True]) # Sort by ft_level, then iterations
            
            print(grouped_sorted[['assistant_model', 'ft_level', 'iterations', 'time_taken']].to_string(index=False, float_format='{:.2f}'.format))

else:
    print("No data found or loaded.") 