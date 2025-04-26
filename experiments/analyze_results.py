# Necessary imports
import pandas as pd
import glob
import os
import re
import ast  # For safely evaluating string representations of lists
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import numpy as np

# Define base directory for results - assumes script is run from 'experiments' dir
BASE_RESULTS_DIR = '.'

# Define standard functions for each ERC type (ADJUST THESE IF YOUR INTERFACES DIFFER)
ERC_FUNCTIONS = {
    'erc20': ['totalSupply', 'balanceOf', 'transfer', 'transferFrom', 'approve', 'allowance'],
    'erc721': ['balanceOf', 'ownerOf', 'safeTransferFrom', 'transferFrom', 'approve', 'getApproved', 'setApprovalForAll', 'isApprovedForAll', 'supportsInterface'], # Added supportsInterface based on common implementations
    'erc1155': ['balanceOf', 'balanceOfBatch', 'setApprovalForAll', 'isApprovedForAll', 'safeTransferFrom', 'safeBatchTransferFrom', 'supportsInterface'] # Added supportsInterface
}

# --- 1. Data Loading and Preprocessing ---

def parse_context_from_dir(context_dir):
    """Parses context from the directory name."""
    if context_dir == 'none':
        return 'none'
    # Directory names use underscores
    return context_dir

def load_all_results(base_dir):
    """Loads all CSV results into a single DataFrame."""
    all_files = glob.glob(os.path.join(base_dir, 'results_*', '*', '*', '*.csv'))
    if not all_files:
        print(f"Error: No CSV files found matching the pattern in {base_dir}")
        print("Please ensure you run this script from the 'experiments' directory containing the 'results_*' folders.")
        return pd.DataFrame()

    df_list = []
    print(f"Found {len(all_files)} potential result files. Processing...")
    processed_files = 0
    skipped_files = 0

    for f in all_files:
        try:
            # Extract info from path: ./results_{assistant}/{requested}/{context_dir}/{filename}.csv
            parts = f.split(os.sep)
            if len(parts) < 5:
                 print(f"Warning: Skipping file with unexpected path structure: {f}")
                 skipped_files += 1
                 continue

            filename = parts[-1]
            context_dir = parts[-2]
            requested_type = parts[-3]
            assistant_part = parts[-4]

            # Extract assistant name
            match = re.match(r'results_(.*)', assistant_part)
            if not match:
                print(f"Warning: Could not parse assistant name from directory {assistant_part}. Skipping file {f}")
                skipped_files += 1
                continue
            assistant = match.group(1)

            # Use context_dir for context grouping
            context = parse_context_from_dir(context_dir)

            # Basic check if file looks like a result file before reading
            if not filename.startswith(f"{requested_type}_[") or not filename.endswith("].csv"):
                 print(f"Warning: Skipping file with unexpected name format: {f}")
                 skipped_files += 1
                 continue


            df = pd.read_csv(f)
            # Add columns only if they don't exist (useful if script is rerun)
            if 'assistant' not in df.columns:
                 df['assistant'] = assistant
            if 'requested_type' not in df.columns:
                 df['requested_type'] = requested_type
            if 'context' not in df.columns:
                 df['context'] = context
            df_list.append(df)
            processed_files += 1
        except pd.errors.EmptyDataError:
            print(f"Warning: Skipping empty file: {f}")
            skipped_files += 1
        except Exception as e:
            print(f"Error loading or processing file {f}: {e}")
            skipped_files += 1

    if not df_list:
        print("Error: No dataframes were successfully loaded.")
        return pd.DataFrame()

    print(f"Successfully processed {processed_files} files. Skipped {skipped_files} files.")
    return pd.concat(df_list, ignore_index=True)

# --- 2. Request 1: Model Ranking ---

def calculate_overall_performance(df):
    """Calculates success rate and average iterations."""
    if df.empty:
        return pd.DataFrame()
    if 'verified' not in df.columns or 'iterations' not in df.columns:
        print("Error: DataFrame missing required 'verified' or 'iterations' columns.")
        return pd.DataFrame()

    # Ensure 'verified' is boolean
    df['verified'] = df['verified'].astype(bool)

    # Group by assistant and requested type, aggregating across contexts and runs
    performance = df.groupby(['assistant', 'requested_type']).agg(
        total_runs=('run', 'count'),
        successful_runs=('verified', 'sum'), # Sum boolean True values
        avg_iterations_success=('iterations', lambda x: x[df.loc[x.index, 'verified']].mean()), # Mean where verified is True
        avg_iterations_overall=('iterations', 'mean'),
        avg_time_taken=('time_taken', 'mean')
    ).reset_index()

    # Avoid division by zero if total_runs is 0 for a group (shouldn't happen with count)
    performance['success_rate'] = (performance['successful_runs'] / performance['total_runs'].replace(0, 1)) * 100
    # Handle cases where there were no successful runs (NaN avg_iterations_success)
    performance['avg_iterations_success'] = performance['avg_iterations_success'].fillna(0).round(2)
    performance['avg_iterations_overall'] = performance['avg_iterations_overall'].round(2)
    performance['avg_time_taken'] = performance['avg_time_taken'].round(2)
    performance['success_rate'] = performance['success_rate'].round(2)


    # Sort for ranking (e.g., by success rate desc, then avg iterations asc)
    performance = performance.sort_values(
        by=['requested_type', 'success_rate', 'avg_iterations_success'],
        ascending=[True, False, True]
    )

    return performance

def plot_overall_performance(perf_df, metric='success_rate', title_suffix='Success Rate (%)'):
    """Plots the chosen performance metric."""
    if perf_df.empty:
        print("Cannot plot empty performance dataframe.")
        return

    plt.figure(figsize=(15, 8))
    # Using dodge to separate bars for different assistants within the same requested_type
    sns.barplot(data=perf_df, x='requested_type', y=metric, hue='assistant', palette='viridis', dodge=True)

    plt.title(f'Model Performance Comparison ({title_suffix}) across Requested Contract Types')
    plt.ylabel(title_suffix)
    plt.xlabel('Requested Contract Type')
    plt.xticks(rotation=0)
    plt.legend(title='Assistant Model', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
    plt.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make space for legend
    plt.grid(axis='y', linestyle='--')
    # Add value labels on bars
    ax = plt.gca()
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f', label_type='edge', fontsize=8, padding=2)

    plt.show()


# --- 3. Request 2: Per-Function Verification Analysis ---

def safe_literal_eval(val):
    """Safely evaluate a string representation of a list."""
    if isinstance(val, list): # Already a list
        return val
    if pd.isna(val): # Handle NaN
        return []
    if isinstance(val, str):
        try:
            # Basic check for list-like string
            stripped_val = val.strip()
            if stripped_val.startswith('[') and stripped_val.endswith(']'):
                 evaluated = ast.literal_eval(stripped_val)
                 if isinstance(evaluated, list):
                     # Ensure elements within the list are strings
                     return [str(item) for item in evaluated]
            # If not a list string, treat as single entry
            return [val]
        except (ValueError, SyntaxError, TypeError, MemoryError):
             # If parsing fails, return the original string within a list
             print(f"Warning: Could not parse status string as list: '{val[:100]}...'. Treating as single entry.")
             return [val]
    # Handle other types
    return [] # Return empty list if input is not string, list, or NaN


def parse_solc_verify_status(status_list, functions_to_check):
    """
    Parses the list of status strings from solc-verify output for function success.
    Returns a dictionary: {interaction_num: {function_name: status ('OK'/'ERROR'/None)}}
    """
    interaction_results = defaultdict(lambda: {func: None for func in functions_to_check})
    current_interaction = 0

    # Regex patterns (adjust if solc-verify output format differs):
    # Looks for [OK] or [ERROR] followed by optional text, then FunctionName(
    # Captures the FunctionName. Case-insensitive.
    status_pattern = re.compile(r'\[(OK|ERROR)\].*?(\b(?:' + '|'.join(functions_to_check) + r')\b)\s*\(', re.IGNORECASE | re.DOTALL)
    # Extracts interaction number
    interaction_pattern = re.compile(r'^Interaction:\s*(\d+)', re.MULTILINE)

    for entry_index, entry in enumerate(status_list):
        if not isinstance(entry, str): continue # Skip non-string entries

        # Find interaction number for this entry
        interaction_match = interaction_pattern.search(entry)
        if interaction_match:
            current_interaction = int(interaction_match.group(1))
        else:
            # If no marker found, maybe log a warning or skip?
            # For now, assume it belongs to the previous interaction if index > 0, otherwise skip.
            if entry_index == 0:
                 print(f"Warning: Status entry missing 'Interaction:' marker: {entry[:100]}...")
                 continue # Cannot associate with an interaction

        if current_interaction == 0: continue # Should not happen if marker is found

        # Find all status markers and associated functions in this interaction block
        matches = status_pattern.findall(entry)
        for status_marker, func_name in matches:
            # Normalize function name case if needed (though pattern is case-insensitive)
            matched_func = next((f for f in functions_to_check if f.lower() == func_name.lower()), None)
            if matched_func:
                 # Record the status ('OK' or 'ERROR')
                 # Prioritize ERROR if both somehow appear for the same function? Or first found? Let's take first found.
                 if interaction_results[current_interaction][matched_func] is None:
                     interaction_results[current_interaction][matched_func] = status_marker.upper() # Store as 'OK' or 'ERROR'

    return interaction_results


def analyze_function_verification(df):
    """Analyzes when each function gets verified correctly."""
    if df.empty:
        print("Input DataFrame for function analysis is empty.")
        return pd.DataFrame()
    if 'status' not in df.columns:
        print("Error: DataFrame missing required 'status' column for function analysis.")
        return pd.DataFrame()

    # Apply safe evaluation to the status column
    print("Parsing 'status' column...")
    df['parsed_status_list'] = df['status'].apply(safe_literal_eval)
    print("Finished parsing 'status' column.")

    function_verification_data = []

    print("Analyzing function verification status per run...")
    # Iterate through each row (each run)
    for index, row in df.iterrows():
        # Print progress occasionally
        if index % 100 == 0:
            print(f"Processing run {index+1}/{len(df)}...")

        requested_type = row['requested_type']
        if requested_type not in ERC_FUNCTIONS:
            # print(f"Warning: Skipping run {row['run']} for assistant {row['assistant']} - Unknown requested_type '{requested_type}'")
            continue # Skip if we don't have a function list for this type

        functions_to_check = ERC_FUNCTIONS[requested_type]
        run_status_list = row['parsed_status_list']

        # If the run was successful (verified=True) and status list is empty,
        # it means it succeeded on the first try (interaction 1 implied).
        # If verified=False and status list is empty, something is odd, maybe verification failed immediately.
        if row['verified'] and not run_status_list:
             # Assume success at interaction 1 for all functions
             for func in functions_to_check:
                 function_verification_data.append({
                     'assistant': row['assistant'],
                     'requested_type': requested_type,
                     'context': row['context'],
                     'run': row['run'],
                     'interaction': 1, # Implied success at interaction 1
                     'function': func,
                     'status': 'OK',
                     'first_ok_iter': 1,
                     'ever_ok_in_run': True,
                     'final_run_status': 'Verified'
                 })
             continue # Move to next run

        # Parse the list of status strings for this run if it wasn't immediately successful
        interaction_statuses = parse_solc_verify_status(run_status_list, functions_to_check)

        # Track first OK iteration for each function in this run
        first_ok_iteration = {func: float('inf') for func in functions_to_check}
        # Track the status in the last observed interaction
        last_interaction_status = {func: None for func in functions_to_check}
        max_interaction_in_log = 0

        sorted_interactions = sorted(interaction_statuses.keys())
        if sorted_interactions:
            max_interaction_in_log = max(sorted_interactions)

        for interaction_num in sorted_interactions:
            for func, status in interaction_statuses[interaction_num].items():
                if status == 'OK' and interaction_num < first_ok_iteration[func]:
                    first_ok_iteration[func] = interaction_num
                # Update last known status
                if status is not None:
                    last_interaction_status[func] = status


        # Determine final status for the run
        final_run_status = 'Verified' if row['verified'] else 'Failed'

        # Store data points for each function based on the analysis
        for func in functions_to_check:
            first_ok = first_ok_iteration[func]
            ever_ok = first_ok != float('inf')
            last_status = last_interaction_status[func]

            # If the run was verified, the final status for all functions is implicitly OK
            # at an interaction <= row['iterations'] + 1
            # The 'iterations' column counts *failed* attempts. Success is the next step.
            final_ok_interaction = row['iterations'] + 1 if row['verified'] else np.nan

            # If it was ever OK, record the first time.
            # If it was never OK in the logs, but the run succeeded, it became OK at final_ok_interaction.
            # If it was never OK and the run failed, it remained not OK.

            if ever_ok:
                 iter_to_report = first_ok
                 status_to_report = 'OK' # Report based on first success
            elif row['verified']: # Never OK in logs, but run succeeded
                 iter_to_report = final_ok_interaction
                 status_to_report = 'OK' # Implicitly OK at the end
                 ever_ok = True # It did become OK eventually
            else: # Never OK in logs and run failed
                 iter_to_report = np.nan # No specific OK iteration
                 status_to_report = last_status if last_status else 'ERROR' # Last known status or assume ERROR

            function_verification_data.append({
                 'assistant': row['assistant'],
                 'requested_type': requested_type,
                 'context': row['context'],
                 'run': row['run'],
                 # 'interaction': interaction_num, # This level of detail might be too much, focus on summary
                 'function': func,
                 'status_last_log': last_status, # Status in the last interaction recorded in logs
                 'first_ok_iter': iter_to_report if ever_ok else np.nan,
                 'ever_ok_in_run': ever_ok,
                 'final_run_status': final_run_status,
                 'run_iterations': row['iterations'] # Number of failed iterations before success/stop
             })


    print("Finished analyzing function verification status.")
    if not function_verification_data:
         print("Warning: No function verification data could be extracted.")
         return pd.DataFrame()

    func_df = pd.DataFrame(function_verification_data)
    # Remove potential duplicates if logic added redundant rows (e.g., per interaction)
    # Grouping by run and function should give one summary row per function per run
    func_df = func_df.drop_duplicates(subset=['assistant', 'requested_type', 'context', 'run', 'function'])
    print(f"Generated function analysis dataframe with {len(func_df)} rows.")
    return func_df


def plot_function_verification_progress(func_df, requested_type_filter):
    """Plots the cumulative probability of a function being verified by a certain interaction."""
    if func_df.empty:
        print("Cannot plot empty function verification dataframe.")
        return

    df_filtered = func_df[(func_df['requested_type'] == requested_type_filter) & (func_df['ever_ok_in_run'])].copy()

    if df_filtered.empty:
        print(f"No successfully verified functions found for requested type: {requested_type_filter}")
        return

    # --- Plotting Cumulative Success ---
    plt.figure(figsize=(15, 8))

    # Use seaborn's ecdfplot (Empirical Cumulative Distribution Function)
    sns.ecdfplot(data=df_filtered, x='first_ok_iter', hue='function', stat='proportion', palette='tab10', lw=2)

    plt.title(f'Cumulative Probability of Function Verification ({requested_type_filter}) - Aggregated Across Assistants & Contexts')
    plt.xlabel('Interaction Count (First Successful Verification)')
    plt.ylabel('Proportion of Runs Verified')
    # Determine max iterations from data, add buffer
    max_iter = int(df_filtered['first_ok_iter'].max(skipna=True)) if not df_filtered['first_ok_iter'].isna().all() else 10
    plt.xticks(range(1, max_iter + 2))
    plt.xlim(0.5, max_iter + 1.5)
    plt.ylim(0, 1.05)
    plt.grid(axis='both', linestyle='--')
    plt.legend(title='Function', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.show()

    # --- Plotting Faceted by Assistant ---
    g = sns.FacetGrid(df_filtered, col="assistant", col_wrap=4, height=4, aspect=1.2, sharey=True, sharex=True)
    g.map(sns.ecdfplot, "first_ok_iter", hue=df_filtered['function'], stat='proportion', lw=2) # Pass hue data explicitly
    g.add_legend(title="Function")
    g.set_axis_labels("Interaction Count (First Success)", "Proportion Verified")
    g.set_titles(col_template="{col_name}")
    plt.suptitle(f'Cumulative Function Verification ({requested_type_filter}) by Assistant', y=1.02)
    # Adjust x-axis limits for all facets
    max_iter_overall = int(func_df['first_ok_iter'].max(skipna=True)) if not func_df['first_ok_iter'].isna().all() else 10
    g.set(xticks=range(1, max_iter_overall + 2), xlim=(0.5, max_iter_overall + 1.5))
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.show()


def create_function_summary_table(func_df):
    """Creates tables summarizing function verification."""
    if func_df.empty:
        print("Cannot create summary table from empty dataframe.")
        return {}

    summary_tables = {}
    for r_type in sorted(func_df['requested_type'].unique()):
        df_type = func_df[func_df['requested_type'] == r_type].copy()
        if df_type.empty: continue

        # Calculate Avg. First OK Iteration (only for runs where it was ever OK)
        # Group by assistant, context, function and calculate mean of 'first_ok_iter'
        avg_first_ok = df_type[df_type['ever_ok_in_run']].groupby(
            ['assistant', 'context', 'function']
        )['first_ok_iter'].mean().round(2).reset_index()
        # Pivot for table format
        avg_first_ok_pivot = avg_first_ok.pivot_table(index=['assistant', 'context'], columns='function', values='first_ok_iter')

        # Calculate Percentage of Runs where Function was Ever OK
        # Group by assistant, context, function and calculate mean of 'ever_ok_in_run' (boolean -> mean is proportion)
        perc_ever_ok = df_type.groupby(
            ['assistant', 'context', 'function']
        )['ever_ok_in_run'].mean().round(3) * 100 # Convert proportion to percentage
        perc_ever_ok = perc_ever_ok.reset_index()
        # Pivot for table format
        perc_ever_ok_pivot = perc_ever_ok.pivot_table(index=['assistant', 'context'], columns='function', values='ever_ok_in_run')

        summary_tables[f'{r_type}_avg_first_ok_iteration'] = avg_first_ok_pivot.fillna('-')
        summary_tables[f'{r_type}_perc_runs_func_ever_ok'] = perc_ever_ok_pivot.fillna(0.0)

    return summary_tables


# --- Main Execution ---
if __name__ == "__main__":
    print("Starting analysis...")
    print("Loading results...")
    master_df = load_all_results(BASE_RESULTS_DIR)

    if master_df.empty:
        print("Exiting: No data loaded.")
    else:
        print(f"\nLoaded {len(master_df)} total run records across all experiments.")
        print("Columns:", master_df.columns.tolist())
        print("Assistants found:", sorted(master_df['assistant'].unique()))
        print("Requested types found:", sorted(master_df['requested_type'].unique()))
        print("Contexts found:", sorted(master_df['context'].unique()))

        # --- Data Cleaning Step ---
        print("\nCleaning 'iterations' column...")
        if 'iterations' in master_df.columns:
            # Convert to numeric, coercing errors to NaN
            master_df['iterations'] = pd.to_numeric(master_df['iterations'], errors='coerce')
            # Fill NaN values resulting from coercion with 0
            original_nan_count = master_df['iterations'].isna().sum()
            if original_nan_count > 0:
                print(f"Warning: Found {original_nan_count} non-numeric entries in 'iterations'. Converting them to 0.")
                master_df['iterations'] = master_df['iterations'].fillna(0)
            # Ensure the column is integer type if possible (or float if NaNs were introduced)
            master_df['iterations'] = master_df['iterations'].astype(int) # Or float if NaNs were important
            print("Finished cleaning 'iterations' column.")
        else:
            print("Warning: 'iterations' column not found in the loaded data.")

        print("\nCleaning 'time_taken' column...")
        if 'time_taken' in master_df.columns:
            master_df['time_taken'] = pd.to_numeric(master_df['time_taken'], errors='coerce')
            original_nan_count_time = master_df['time_taken'].isna().sum()
            if original_nan_count_time > 0:
                print(f"Warning: Found {original_nan_count_time} non-numeric entries in 'time_taken'. Converting them to 0.0.")
                master_df['time_taken'] = master_df['time_taken'].fillna(0.0)
            # Ensure the column is float type
            master_df['time_taken'] = master_df['time_taken'].astype(float)
            print("Finished cleaning 'time_taken' column.")
        else:
            print("Warning: 'time_taken' column not found in the loaded data.")
        # --- End Data Cleaning ---


        print("\n--- Request 1: Model Ranking ---")
        overall_performance = calculate_overall_performance(master_df.copy()) # Pass copy to avoid modifying original

        if not overall_performance.empty:
            print("\nOverall Performance Summary (Aggregated across Contexts):")
            # Increase display options for pandas
            with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 120):
                 print(overall_performance)

            # Plot Success Rate
            print("\nPlotting Success Rate...")
            plot_overall_performance(overall_performance, metric='success_rate', title_suffix='Success Rate (%)')

            # Plot Average Iterations on Success
            print("\nPlotting Average Iterations (Successful Runs)...")
            plot_overall_performance(overall_performance, metric='avg_iterations_success', title_suffix='Avg. Iterations (Successful Runs)')
        else:
            print("Could not calculate overall performance.")


        print("\n--- Request 2: Per-Function Verification Analysis ---")
        # Use a copy for analysis to avoid modifying the original df
        function_analysis_df = analyze_function_verification(master_df.copy())

        if not function_analysis_df.empty:
            print(f"\nExtracted {len(function_analysis_df)} function summary records.")
            # Display sample rows
            print("\nSample function analysis data:")
            print(function_analysis_df.head())


            # Generate plots for each requested type
            for req_type in sorted(master_df['requested_type'].unique()):
                 print(f"\nGenerating function verification plots for: {req_type}")
                 plot_function_verification_progress(function_analysis_df, req_type)

            # Generate summary tables
            print("\nGenerating function verification summary tables...")
            summary_tables = create_function_summary_table(function_analysis_df)
            for name, table in summary_tables.items():
                print(f"\n--- Summary Table: {name} ---")
                with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
                    print(table)
        else:
            print("Could not perform function verification analysis (no data extracted).")

        print("\nAnalysis complete.")