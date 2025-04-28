import pandas as pd
import os
import glob
import re
import ast
import numpy as np
from collections import defaultdict

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

    # --- Learning Curve Analysis ---
    if not master_df.empty:
        print("\n--- Learning Curve Analysis ---")

        key_functions = {
            'erc20': ['totalSupply', 'balanceOf', 'allowance', 'transfer', 'approve', 'transferFrom'],
            'erc721': ['balanceOf', 'ownerOf', 'getApproved', 'isApprovedForAll', 'safeTransferFrom', 'transferFrom', 'approve', 'setApprovalForAll'],
            'erc1155': ['balanceOf', 'balanceOfBatch', 'isApprovedForAll', 'safeTransferFrom', 'safeBatchTransferFrom', 'setApprovalForAll']
        }

        # Filter for failed runs that had at least one iteration
        failed_learning_runs = master_df[(~master_df['verified']) & (master_df['iterations'] > 0)].copy()
        print(f"Analyzing learning curve for {len(failed_learning_runs)} failed runs with iterations > 0.")

        # Reusable function to parse status string (slightly modified)
        def count_ok_functions(status_str, functions_to_check, contract_prefix):
            ok_count = 0
            if not isinstance(status_str, str) or not status_str:
                return 0 # Cannot parse non-string or empty string
            
            for func in functions_to_check:
                # Search for the function status line (e.g., "ERC20::transfer: OK")
                pattern = re.compile(rf"^{re.escape(contract_prefix)}::{re.escape(func)}:\s*(OK|OK_Maybe)", re.MULTILINE)
                match = pattern.search(status_str)
                if match:
                    ok_count += 1
                # Add check for OK_Maybe for safety, though pattern includes it
                # elif f"::{func}: OK_Maybe" in status_str: 
                #    ok_count += 1 
            return ok_count

        # Store results: { (model, req_type): { iter_num: [list_of_ok_counts] } }
        learning_data = defaultdict(lambda: defaultdict(list))
        parse_errors = 0

        for index, row in failed_learning_runs.iterrows():
            model = row['assistant_model']
            req_type = row['requested_type']
            status_history_str = row['status']
            
            if req_type not in key_functions:
                continue
            
            functions_to_check = key_functions[req_type]
            contract_prefix = req_type.upper()
            
            try:
                # Evaluate the string representation of the list
                status_history = ast.literal_eval(status_history_str)
                if not isinstance(status_history, list):
                    parse_errors += 1
                    continue
                    
                # Iterate through each status message in the history
                for i, iteration_status in enumerate(status_history):
                    iteration_num = i + 1 # 1-based iteration number
                    ok_count = count_ok_functions(iteration_status, functions_to_check, contract_prefix)
                    learning_data[(model, req_type)][iteration_num].append(ok_count)
                    
            except (ValueError, SyntaxError, TypeError):
                parse_errors += 1
                # print(f"Parse error for row index {index}") # Optional: log specific errors
                continue
            except Exception as e:
                parse_errors += 1
                # print(f"Unknown error processing row {index}: {e}")
                continue

        print(f"Finished processing. Encountered {parse_errors} errors parsing status history.")

        # Calculate and display average OK counts per iteration
        print("\n--- Average Number of OK Functions per Iteration (Failed Runs) ---")

        # Prepare data for display
        analysis_results = []
        for (model, req_type), iter_data in learning_data.items():
            for iteration_num, ok_counts in iter_data.items():
                if ok_counts: # Ensure list is not empty
                    avg_ok = np.mean(ok_counts)
                    num_runs_at_iter = len(ok_counts)
                    analysis_results.append({
                        'assistant_model': model,
                        'requested_type': req_type,
                        'iteration': iteration_num,
                        'avg_ok_functions': avg_ok,
                        'num_runs_at_iter': num_runs_at_iter
                    })
        
        if not analysis_results:
            print("No learning data to analyze.")
        else:
            analysis_df = pd.DataFrame(analysis_results)
            analysis_df.sort_values(by=['assistant_model', 'requested_type', 'iteration'], inplace=True)
            
            # Display pivoted table for better readability
            try:
                pivot_table = pd.pivot_table(analysis_df, 
                                             values='avg_ok_functions', 
                                             index=['assistant_model', 'requested_type'], 
                                             columns='iteration',
                                             aggfunc=np.mean) # Use mean here, already averaged
                print(pivot_table.to_string(float_format='{:.2f}'.format, na_rep='-'))
                # Optional: Print number of runs contributing to each cell for context
                # pivot_counts = pd.pivot_table(analysis_df, values='num_runs_at_iter', index=['assistant_model', 'requested_type'], columns='iteration')
                # print("\nNumber of Runs Contributing to Averages:")
                # print(pivot_counts.to_string(float_format='{:.0f}'.format, na_rep='-'))
            except Exception as e:
                 print(f"Error creating pivot table: {e}")
                 print("\nRaw Analysis Data:")
                 print(analysis_df.to_string(index=False, float_format='{:.2f}'.format)) 

else:
    print("No data found or loaded.") 