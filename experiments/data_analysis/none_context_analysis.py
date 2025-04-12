import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict

def gather_none_context_results(base_dir: str, model_name: str) -> pd.DataFrame:
    """
    Finds CSV files with 'none' context under base_dir, computes verification stats for each file,
    and returns a DataFrame with columns:
      [model, contract_type, total_runs, success_count, success_rate].
    """
    records = []
    print(f"Searching for 'none' context CSV files in: {base_dir}")
    
    # The directory structure is: results_{assistant}/{contract_type}/none/{contract_type}_[none].csv
    for contract_type in ['erc20', 'erc721', 'erc1155']:
        # Use direct file path instead of glob
        csv_path = os.path.join(base_dir, contract_type, "none", f"{contract_type}_[none].csv")
        print(f"Checking file: {csv_path}")
        
        if os.path.exists(csv_path):
            print(f"Found file: {csv_path}")
            # Read the CSV
            try:
                df = pd.read_csv(csv_path)
                # Basic verification stats
                total_runs = len(df)
                success_count = df['verified'].sum() if 'verified' in df.columns else 0
                success_rate = success_count / total_runs if total_runs else 0
                
                # Get error patterns if available
                errors = []
                if 'status' in df.columns:
                    for _, row in df.iterrows():
                        if isinstance(row['status'], str) and row['status'] and row['status'].strip() != '[]':
                            errors.append(row['status'])
                
                record = {
                    "model": model_name,
                    "contract_type": contract_type,
                    "total_runs": total_runs,
                    "success_count": success_count,
                    "success_rate": success_rate,
                    "errors": errors
                }
                records.append(record)
                print(f"Added record: {record}")
            except Exception as e:
                print(f"Error processing {csv_path}: {e}")
        else:
            print(f"File does not exist: {csv_path}")

    return pd.DataFrame(records)

def compare_none_context_models(model_dirs: Dict[str, str]) -> pd.DataFrame:
    """
    Gathers results from multiple model directories (each containing CSVs),
    focusing only on 'none' context files.
    
    Args:
        model_dirs: Dictionary with model_name: directory_path pairs
    """
    # Gather results for each model
    dataframes = []
    for model_name, dir_path in model_dirs.items():
        print(f"\nProcessing model: {model_name}")
        df = gather_none_context_results(dir_path, model_name)
        if not df.empty:
            dataframes.append(df)
        else:
            print(f"No data found for model: {model_name}")
    
    # Combine all dataframes
    if not dataframes:
        print("No data found in any model directory")
        return pd.DataFrame()
    
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Create a pivot table for easier comparison
    pivot_df = combined_df.pivot_table(
        index=["contract_type"],
        columns="model",
        values=["total_runs", "success_count", "success_rate"],
        fill_value=0
    )
    
    # Flatten the multi-index columns
    pivot_df.columns = [f"{col[1]}_{col[0]}" if col[1] else col[0] for col in pivot_df.columns]
    
    # Reset index to get contract_type as a column
    result_df = pivot_df.reset_index()
    
    return result_df

def plot_none_context_success_rates(df: pd.DataFrame, models: List[str]):
    """
    Plots a grouped bar chart comparing success rates across all models for 'none' context.
    
    Args:
        df: DataFrame with success rates
        models: List of model names to include in the plot
    """
    # Prepare data for plotting
    plot_df = df.copy()
    
    # Create figure and axis
    plt.figure(figsize=(14, 8))
    
    # Set up the bar positions
    x = range(len(plot_df))
    width = 0.8 / len(models)
    offsets = [(i - (len(models) - 1) / 2) * width for i in range(len(models))]
    
    # Plot bars for each model
    for model, offset in zip(models, offsets):
        col_name = f"{model}_success_rate"
        if col_name in plot_df.columns:
            plt.bar([pos + offset for pos in x], plot_df[col_name], 
                    width=width, label=model)
    
    # Set labels and title
    plt.xticks(ticks=x, labels=plot_df["contract_type"], rotation=0)
    plt.title("Success Rate Comparison Across Models (No Context)")
    plt.xlabel("Contract Type")
    plt.ylabel("Success Rate (fraction)")
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save figure
    plt.savefig("experiments/none_context_success_rate_comparison.png", dpi=300)
    print("Success rate chart saved to experiments/none_context_success_rate_comparison.png")
    plt.close()

def plot_none_context_heatmap(df: pd.DataFrame, models: List[str]):
    """
    Creates a heatmap of success rates for none context files.
    
    Args:
        df: DataFrame with success rates
        models: List of model names to include in the plot
    """
    # Prepare data for heatmap
    heatmap_df = df.copy()
    
    # Get only the success rate columns for our models
    success_cols = [f"{model}_success_rate" for model in models if f"{model}_success_rate" in df.columns]
    
    # Select only the columns we need
    heatmap_df = heatmap_df[["contract_type"] + success_cols]
    
    # Set the contract_type as index
    heatmap_df = heatmap_df.set_index("contract_type")
    
    # Create figure
    plt.figure(figsize=(12, len(heatmap_df) * 0.8))
    
    # Create heatmap
    sns.heatmap(heatmap_df, annot=True, cmap="YlGnBu", fmt=".2f", 
                linewidths=.5, vmin=0, vmax=1, annot_kws={"size": 12})
    
    plt.title("Success Rate Heatmap (No Context)")
    plt.tight_layout()
    
    # Save figure
    plt.savefig("experiments/none_context_success_rate_heatmap.png", dpi=300)
    print("Heatmap saved to experiments/none_context_success_rate_heatmap.png")
    plt.close()

def identify_top_performers_none_context(df: pd.DataFrame, all_models: List[str]):
    """
    Identify top performing models for each contract type with no context.
    Creates a visualization showing success rates for all models across contract types.
    
    Args:
        df: DataFrame with success rates
        all_models: Complete list of all available models to include in visualization
    """
    # Get success rate columns
    rate_cols = [col for col in df.columns if col.endswith('_success_rate')]
    
    # Create a new dataframe to store the top performer for each contract type
    top_performers = pd.DataFrame()
    top_performers['contract_type'] = df['contract_type']
    
    # Find the best model for each contract type
    best_models = []
    best_rates = []
    
    for _, row in df.iterrows():
        rates = [row[col] for col in rate_cols]
        max_rate = max(rates)
        
        # Find which model(s) achieved this rate
        best_model_indices = [i for i, r in enumerate(rates) if r == max_rate]
        best_model_names = [rate_cols[i].replace('_success_rate', '') for i in best_model_indices]
        
        best_models.append(', '.join(best_model_names))
        best_rates.append(max_rate)
    
    top_performers['best_model'] = best_models
    top_performers['best_rate'] = best_rates
    
    # Save to CSV
    top_performers.to_csv('experiments/none_context_top_performers.csv', index=False)
    
    # Create a plot showing success rates for all models across contract types
    plt.figure(figsize=(18, 10))
    
    # Extract data for plotting
    contract_types = df['contract_type'].unique()
    
    # Set width of bars
    n_models = len(all_models)
    width = 0.8 / n_models
    
    # Set up positions
    positions = np.arange(len(contract_types))
    
    # Colors for bars
    colors = plt.cm.viridis(np.linspace(0, 1, n_models))
    
    # Plot each model's success rate for each contract type
    for i, model in enumerate(sorted(all_models)):
        # Find success rates for this model across contract types
        model_rates = []
        for ct in contract_types:
            # Find the row for this contract type
            row = df[df['contract_type'] == ct]
            if len(row) > 0:
                col_name = f"{model}_success_rate"
                if col_name in row.columns:
                    rate = row[col_name].values[0]
                else:
                    rate = 0.0
            else:
                rate = 0.0
            model_rates.append(rate)
        
        # Plot the bars for this model
        offset = (i - n_models/2) * width + width/2
        plt.bar(positions + offset, model_rates, width=width, color=colors[i], 
                label=model, alpha=0.8)
    
    # Labels and formatting
    plt.xlabel('Contract Type')
    plt.ylabel('Success Rate')
    plt.title('Model Success Rates by Contract Type (No Context)')
    plt.xticks(positions, contract_types)
    plt.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.ylim(0, 1.0)
    plt.tight_layout()
    
    # Add value labels on the bars
    for i, model in enumerate(sorted(all_models)):
        for j, ct in enumerate(contract_types):
            row = df[df['contract_type'] == ct]
            if len(row) > 0:
                col_name = f"{model}_success_rate"
                if col_name in row.columns:
                    rate = row[col_name].values[0]
                else:
                    rate = 0.0
            else:
                rate = 0.0
                
            offset = (i - n_models/2) * width + width/2
            plt.text(j + offset, rate + 0.02, f'{rate:.1f}', 
                     ha='center', va='bottom', fontsize=8, rotation=90)
    
    plt.savefig('experiments/none_context_success_rates.png', dpi=300)
    plt.close()
    
    print("\nTop performer analysis completed. Results saved to 'experiments/none_context_top_performers.csv'.")
    print("\nModels success rates visualization saved to 'experiments/none_context_success_rates.png'.")
    
    return top_performers

def main():
    """
    This script analyzes models' performance on 'none' context files only.
    1) Gathers stats for all available models for 'none' context,
    2) Combines them into a single DataFrame,
    3) Print & save that table to none_context_comparison.csv,
    4) Create visualizations specific to 'none' context performance.
    """
    # All available assistants from loop_contract_verifier.py
    available_models = [
        "4o_mini",
        "4o_mini_single",
        "4o_mini_erc20",
        "4o_mini_erc721",
        "4o_mini_erc1155",
        "4o_mini_erc721_1155",
        "4o_mini_erc20_1155",
        "4o_mini_erc20_721",
        "4o_mini_erc20_721_1155"
    ]
    
    # Create directory paths for each model
    model_dirs = {model: f"experiments/results_{model}" for model in available_models}
    
    # Filter to only include directories that exist
    model_dirs = {model: dir_path for model, dir_path in model_dirs.items() 
                  if os.path.exists(dir_path)}
    
    if not model_dirs:
        print("No result directories found!")
        return
    
    print(f"Found result directories for models: {list(model_dirs.keys())}")
    
    # Compare all models on none context only
    df_comparison = compare_none_context_models(model_dirs)
    
    if df_comparison.empty:
        print("No results found for 'none' context in the directories.")
        return
    
    # Print basic stats
    print("\n=== Comparison of success rates for 'none' context ===")
    
    # Create a list of cols to display
    display_cols = ["contract_type"]
    success_rate_cols = [col for col in df_comparison.columns if col.endswith("_success_rate")]
    display_cols.extend(success_rate_cols)
    
    print(df_comparison[display_cols])
    
    # Save to CSV
    csv_name = "experiments/none_context_comparison.csv"
    df_comparison.to_csv(csv_name, index=False)
    print(f"\nSaved comparison to '{csv_name}'")
    
    # Generate plots
    plot_none_context_success_rates(df_comparison, list(model_dirs.keys()))
    plot_none_context_heatmap(df_comparison, list(model_dirs.keys()))
    
    # Identify top performers - pass both df and complete list of models
    identify_top_performers_none_context(df_comparison, list(model_dirs.keys()))
    
    print("\nNone context analysis complete! Check the generated PNG files and CSVs.")

if __name__ == "__main__":
    main() 