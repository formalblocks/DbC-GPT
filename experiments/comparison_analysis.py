import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict

def gather_results(base_dir: str, model_name: str) -> pd.DataFrame:
    """
    Recursively finds CSV files under base_dir, computes verification stats for each file,
    and returns a DataFrame with columns:
      [model, contract_type, context, total_runs, success_count, success_rate].
    """
    records = []
    print(f"Searching for CSV files in: {base_dir}")
    
    # The directory structure is: results_{assistant}/{requested}/{context}/{requested}_[{context}].csv
    # We'll glob for all CSV files below base_dir
    pattern = os.path.join(base_dir, "**", "*.csv")
    csv_files = glob.glob(pattern, recursive=True)
    
    print(f"Found {len(csv_files)} CSV files")

    for csv_path in csv_files:
        print(f"Processing: {csv_path}")
        # Parse out the contract_type and context from the path
        parts = csv_path.split(os.sep)
        if len(parts) < 3:
            # If path is too short or not structured, skip it
            print(f"Skipping {csv_path}: path too short")
            continue

        # Typically:
        #   parts[-3] -> contract_type (like 'erc20', 'erc721', 'erc1155')
        #   parts[-2] -> context (like 'erc20', 'erc721', 'none', etc.)
        # Example: results_4o_mini/erc20/erc20/erc20_[erc20].csv
        contract_type = parts[-3]
        context_dir = parts[-2]
        
        # Convert 'none' context to empty string
        context = "" if context_dir == "none" else context_dir
        
        # Try to extract context from filename as well
        filename = os.path.basename(csv_path)
        if '[' in filename and ']' in filename:
            # Extract context from filename pattern: {requested}_[{context}].csv
            parts = filename.split('[')
            if len(parts) > 1:
                context_from_file = parts[1].split(']')[0]
                # If context from directory is 'none' but filename has a context, use that
                if context == "" and context_from_file != "":
                    context = context_from_file
                # If context from file has underscores, it indicates multiple contexts
                elif '_' in context_from_file:
                    context = context_from_file.replace('_', ',')

        # Read the CSV
        try:
            df = pd.read_csv(csv_path)
            # Basic verification stats
            total_runs = len(df)
            success_count = df['verified'].sum() if 'verified' in df.columns else 0
            success_rate = success_count / total_runs if total_runs else 0
    
            record = {
                "model": model_name,
                "contract_type": contract_type,
                "context": context,
                "total_runs": total_runs,
                "success_count": success_count,
                "success_rate": success_rate
            }
            records.append(record)
            print(f"Added record: {record}")
        except Exception as e:
            print(f"Error processing {csv_path}: {e}")

    return pd.DataFrame(records)

def compare_models(model_dirs: Dict[str, str]) -> pd.DataFrame:
    """
    Gathers results from multiple model directories (each containing CSVs),
    merges them on (contract_type, context),
    and returns a combined DataFrame.
    
    Args:
        model_dirs: Dictionary with model_name: directory_path pairs
    """
    # Gather results for each model
    dataframes = []
    for model_name, dir_path in model_dirs.items():
        print(f"\nProcessing model: {model_name}")
        df = gather_results(dir_path, model_name)
        if not df.empty:
            dataframes.append(df)
        else:
            print(f"No data found for model: {model_name}")
    
    # Combine all dataframes
    if not dataframes:
        return pd.DataFrame()
    
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Create a pivot table for easier comparison
    pivot_df = combined_df.pivot_table(
        index=["contract_type", "context"],
        columns="model",
        values=["total_runs", "success_count", "success_rate"],
        fill_value=0
    )
    
    # Flatten the multi-index columns
    pivot_df.columns = [f"{col[1]}_{col[0]}" if col[1] else col[0] for col in pivot_df.columns]
    
    # Reset index to get contract_type and context as columns
    result_df = pivot_df.reset_index()
    
    return result_df

def plot_success_rates(df: pd.DataFrame, models: List[str]):
    """
    Plots a grouped bar chart comparing success rates across all models.
    
    Args:
        df: DataFrame with success rates
        models: List of model names to include in the plot
    """
    # Prepare data for plotting
    plot_df = df.copy()
    plot_df["label"] = plot_df["contract_type"] + " | " + plot_df["context"]
    
    # Sort by contract_type and context
    plot_df = plot_df.sort_values(by=["contract_type", "context"]).reset_index(drop=True)
    
    # Create figure and axis
    plt.figure(figsize=(18, 10))
    
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
    plt.xticks(ticks=x, labels=plot_df["label"], rotation=45, ha="right")
    plt.title("Success Rate Comparison Across All Models")
    plt.xlabel("Contract Type | Context")
    plt.ylabel("Success Rate (fraction)")
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save figure
    plt.savefig("success_rate_comparison.png", dpi=300)
    print("Success rate chart saved to success_rate_comparison.png")
    plt.close()

def plot_heatmap(df: pd.DataFrame, models: List[str]):
    """
    Creates a heatmap of success rates for easier visual comparison.
    
    Args:
        df: DataFrame with success rates
        models: List of model names to include in the plot
    """
    # Prepare data for heatmap
    heatmap_df = df.copy()
    
    # Get only the success rate columns for our models
    success_cols = [f"{model}_success_rate" for model in models if f"{model}_success_rate" in df.columns]
    
    # Create label column
    heatmap_df["label"] = heatmap_df["contract_type"] + " | " + heatmap_df["context"]
    
    # Select only the columns we need
    heatmap_df = heatmap_df[["label"] + success_cols]
    
    # Set the label as index
    heatmap_df = heatmap_df.set_index("label")
    
    # Create figure
    plt.figure(figsize=(16, len(heatmap_df) * 0.4))
    
    # Create heatmap
    sns.heatmap(heatmap_df, annot=True, cmap="YlGnBu", fmt=".2f", 
                linewidths=.5, vmin=0, vmax=1)
    
    plt.title("Success Rate Heatmap")
    plt.tight_layout()
    
    # Save figure
    plt.savefig("success_rate_heatmap.png", dpi=300)
    print("Heatmap saved to success_rate_heatmap.png")
    plt.close()

def main():
    """
    This script will:
      1) Gather stats for all available models,
      2) Combine them into a single DataFrame,
      3) Print & save that table to full_model_comparison.csv,
      4) Create various visualizations for the data.
    """
    # All available assistants from loop_contract_verifier.py
    available_models = [
        "4o_mini",
        "erc20-721-1155-4-o-mini",
        "erc20-4-o-mini",
        "erc721-4-o-mini",
        "erc1155-4-o-mini",
        "erc20-721-4-o-mini",
        "erc20-1155-4-o-mini",
        "erc721-1155-4-o-mini",
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
    
    # Compare all models
    df_comparison = compare_models(model_dirs)
    
    if df_comparison.empty:
        print("No results found in the directories.")
        return
    
    # Print basic stats
    print("\n=== Comparison of success rates ===")
    
    # Create a list of cols to display
    display_cols = ["contract_type", "context"]
    success_rate_cols = [col for col in df_comparison.columns if col.endswith("_success_rate")]
    display_cols.extend(success_rate_cols)
    
    print(df_comparison[display_cols])
    
    # Save to CSV
    csv_name = "full_model_comparison.csv"
    df_comparison.to_csv(csv_name, index=False)
    print(f"\nSaved comparison to '{csv_name}'")
    
    # Generate plots
    plot_success_rates(df_comparison, list(model_dirs.keys()))
    plot_heatmap(df_comparison, list(model_dirs.keys()))

if __name__ == "__main__":
    main() 