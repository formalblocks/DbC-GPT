import pandas as pd
import os
import glob
import re
import ast # For safely evaluating the string representation of lists

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

    if not master_df.empty and (master_df['iterations'].isnull().any() or master_df['time_taken'].isnull().any()):
        print("Warning: Errors converting iterations or time_taken to numeric. Nulls introduced.")

    print(f"Cleaned data. Final total runs: {len(master_df)}")

    # --- Task 4: Partial Verification Analysis ---
    if not master_df.empty:
        print("\n--- Task 4: Partial Verification Analysis ---")

        # Define key functions per standard (adjust based on actual solc-verify output)
        key_functions = {
            'erc20': ['totalSupply', 'balanceOf', 'allowance', 'transfer', 'approve', 'transferFrom'],
            'erc721': ['balanceOf', 'ownerOf', 'getApproved', 'isApprovedForAll', 'safeTransferFrom', 'transferFrom', 'approve', 'setApprovalForAll'],
            'erc1155': ['balanceOf', 'balanceOfBatch', 'isApprovedForAll', 'safeTransferFrom', 'safeBatchTransferFrom', 'setApprovalForAll']
        }

        # Filter for failed runs
        failed_runs_df = master_df[~master_df['verified']].copy()
        print(f"Analyzing {len(failed_runs_df)} failed runs for partial verification.")

        # Function to parse status and extract function results
        def get_function_status(status_str, function_name, contract_prefix):
            try:
                # Safely evaluate the string representation of the list
                status_list = ast.literal_eval(status_str)
                if not isinstance(status_list, list) or not status_list:
                    return 'ParseError' # Or 'NoStatus'
                
                # Get the last recorded status message
                last_status = status_list[-1]
                if not isinstance(last_status, str):
                    return 'ParseError'

                # Search for the function status line (e.g., "ERC20::transfer:")
                # Allow for different contract prefixes (e.g., ERC20::, IERC20::)
                pattern = re.compile(rf"^{re.escape(contract_prefix)}::{re.escape(function_name)}:\s*(\w+)", re.MULTILINE)
                match = pattern.search(last_status)
                
                if match:
                    return match.group(1) # OK, ERROR, TIMEOUT
                else:
                    # Handle cases like safeTransferFrom which might have different prefixes or overloads
                    # Basic check for now: if function name appears with OK status anywhere
                    if f"::{function_name}: OK" in last_status:
                         return "OK_Maybe"
                    return 'NotFound'
            except (ValueError, SyntaxError, TypeError):
                return 'ParseError' # Error parsing the status string
            except Exception:
                return 'UnknownError' # Catch any other unexpected errors

        # Process each row to extract status for relevant functions
        partial_results = []
        for index, row in failed_runs_df.iterrows():
            req_type = row['requested_type']
            status_data = {'assistant_model': row['assistant_model'], 'requested_type': req_type}
            if req_type in key_functions:
                 # Determine contract prefix (e.g., ERC20, ERC721)
                contract_prefix = req_type.upper()
                for func in key_functions[req_type]:
                    status_data[func] = get_function_status(row['status'], func, contract_prefix)
            partial_results.append(status_data)
        
        if not partial_results:
            print("No failed runs found or unable to parse status for analysis.")
        else:
            partial_df = pd.DataFrame(partial_results)

            # --- Aggregate and Display Results ---
            print("\n--- Partial Verification Success Rate (Percentage of Failed Runs where Function was OK) ---")
            
            summary_partial = {}            
            all_functions = set(f for funcs in key_functions.values() for f in funcs)

            for model in partial_df['assistant_model'].unique():
                model_df = partial_df[partial_df['assistant_model'] == model]
                summary_partial[model] = {'total_failed_runs': len(model_df)}
                for func in all_functions:
                    if func in model_df.columns:
                        # Count occurrences where status is 'OK' or 'OK_Maybe' 
                        ok_count = model_df[func].isin(['OK', 'OK_Maybe']).sum()
                        total_relevant_runs = len(model_df[model_df[func] != 'NotFound']) # Runs where function was expected/found
                        
                        if total_relevant_runs > 0:
                            rate = (ok_count / total_relevant_runs) * 100
                            summary_partial[model][f'{func}_OK_Rate'] = f"{rate:.2f}% ({ok_count}/{total_relevant_runs})"
                        else:
                            # Check if the function belongs to any requested type processed for this model
                            # Avoid showing 0% for functions never expected for this model's runs
                             if any(func in key_functions.get(rt, []) for rt in model_df['requested_type'].unique()):
                                 summary_partial[model][f'{func}_OK_Rate'] = "0.00% (0/0)"
                             else:
                                 summary_partial[model][f'{func}_OK_Rate'] = "N/A"
                    else:
                         summary_partial[model][f'{func}_OK_Rate'] = "N/A" # Function not applicable/found

            summary_partial_df = pd.DataFrame.from_dict(summary_partial, orient='index')
            # Reorder columns for readability if needed
            print(summary_partial_df)

else:
    print("No data found or loaded.") 