import pandas as pd
import os
import glob

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
                    # Explicitly handle potential bad lines if CSV parsing fails
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
    
    # Drop rows with null 'verified' values (and handle potential malformed rows)
    master_df.dropna(subset=['verified'], inplace=True)
    rows_after_null_drop = len(master_df)
    print(f"Dropped {initial_rows - rows_after_null_drop} rows with null 'verified' values.")
    
    # Drop potential duplicates 
    key_cols = ['assistant_model', 'requested_type', 'context_types', 'run']
    # Convert 'run' to numeric temporarily for reliable duplicate check if needed
    master_df['run_num'] = pd.to_numeric(master_df['run'], errors='coerce')
    master_df.dropna(subset=['run_num'], inplace=True) # Drop rows where run isn't numeric
    key_cols_numeric = ['assistant_model', 'requested_type', 'context_types', 'run_num']
    
    master_df.drop_duplicates(subset=key_cols_numeric, keep='first', inplace=True)
    master_df.drop(columns=['run_num'], inplace=True) # Remove temporary column
    
    rows_after_duplicate_drop = len(master_df)
    print(f"Dropped {rows_after_null_drop - rows_after_duplicate_drop} duplicate rows based on keys.")

    # Convert data types
    master_df['iterations'] = pd.to_numeric(master_df['iterations'], errors='coerce')
    master_df['time_taken'] = pd.to_numeric(master_df['time_taken'], errors='coerce')
    if 'verified' in master_df.columns:
        master_df['verified'] = master_df['verified'].astype(str).str.lower() == 'true'
    else:
        print("Error: 'verified' column not found after cleaning.")

    if master_df['iterations'].isnull().any() or master_df['time_taken'].isnull().any():
        print("Warning: Errors converting iterations or time_taken to numeric. Nulls introduced.")

    print(f"Cleaned data. Final total runs: {len(master_df)}")

    # --- Task 3: Fine-tuning Effectiveness Analysis ---
    print("\n--- Task 3: Fine-tuning Effectiveness Analysis ---")

    # Define the models relevant to each requested type based on fine-tuning data
    model_sets = {
        'erc20': ['4o_mini', 'erc20-4-o-mini', 'erc20-721-4-o-mini', 'erc20-1155-4-o-mini', 'erc20-721-1155-4-o-mini'],
        'erc721': ['4o_mini', 'erc721-4-o-mini', 'erc20-721-4-o-mini', 'erc721-1155-4-o-mini', 'erc20-721-1155-4-o-mini'],
        'erc1155': ['4o_mini', 'erc1155-4-o-mini', 'erc20-1155-4-o-mini', 'erc721-1155-4-o-mini', 'erc20-721-1155-4-o-mini']
    }

    # Define fine-tuning data amount (conceptual)
    # This helps order the models for trend analysis
    ft_levels = { 
        '4o_mini': 0,
        'erc20-4-o-mini': 1, 'erc721-4-o-mini': 1, 'erc1155-4-o-mini': 1,
        'erc20-721-4-o-mini': 2, 'erc20-1155-4-o-mini': 2, 'erc721-1155-4-o-mini': 2,
        'erc20-721-1155-4-o-mini': 3
    }

    for req_type, relevant_models in model_sets.items():
        print(f"\n--- Analysis for Requested Type: {req_type.upper()} ---")
        
        # Filter data for the current requested type and relevant models
        df_filtered = master_df[
            (master_df['requested_type'] == req_type) &
            (master_df['assistant_model'].isin(relevant_models))
        ].copy() # Use copy to avoid SettingWithCopyWarning
        
        if df_filtered.empty:
            print(f"No data found for requested type {req_type} with relevant models.")
            continue

        # Calculate success rates for these models on this specific task
        grouped = df_filtered.groupby('assistant_model')['verified'].agg(
            total_runs='size',
            successful_runs=lambda x: x.sum() 
        ).reset_index()
        
        grouped['success_rate'] = (grouped['successful_runs'] / grouped['total_runs']) * 100
        
        # Add fine-tuning level for sorting
        grouped['ft_level'] = grouped['assistant_model'].map(ft_levels)
        
        # Sort by fine-tuning level, then success rate
        grouped_sorted = grouped.sort_values(by=['ft_level', 'success_rate'], ascending=[True, False])
        
        print(f"Success Rate on {req_type.upper()} Task (Sorted by Fine-tuning Amount):")
        print(grouped_sorted[['assistant_model', 'ft_level', 'total_runs', 'successful_runs', 'success_rate']].to_string(index=False, formatters={'success_rate': '{:.2f}%'.format}))

else:
    print("No data found or loaded.") 