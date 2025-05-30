import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import glob
from pathlib import Path
import datetime

# Configure the visualization settings
plt.style.use('ggplot')
sns.set(font_scale=1.2)
sns.set_style("whitegrid")

class AssistantComparer:
    def __init__(self, results_dir_pattern="experiments/results_entire_contract_base_full_context/*"):
        """
        Initialize the assistant comparer.
        
        Args:
            results_dir_pattern: Pattern to search for results directories
        """
        self.results_dir_pattern = results_dir_pattern
        self.assistant_data = {}
        self.summary_df = None
        
    def extract_assistant_params(self, assistant_name):
        """Extract hyperparameters from assistant name."""
        if assistant_name == "4o-mini":
            return {
                "model": "4o-mini",
                "erc_type": "base",
                "learning_rate": 0,
                "epochs": 0, 
                "batch_size": 0
            }
        
        # Parse names like "erc-1155-001-3-16"
        match = re.match(r"erc-(\d+)-(\d+)-(\d+)-(\d+)", assistant_name)
        if match:
            erc_type, lr_str, epochs, batch_size = match.groups()
            # Convert learning rate string (e.g., '001' to 0.01)
            lr = float("0." + lr_str)
            return {
                "model": assistant_name,
                "erc_type": f"erc{erc_type}",
                "learning_rate": lr,
                "epochs": int(epochs),
                "batch_size": int(batch_size)
            }
        return {
            "model": assistant_name,
            "erc_type": "unknown",
            "learning_rate": 0,
            "epochs": 0,
            "batch_size": 0
        }
    
    def find_results_files(self):
        """Find all results CSV files in the results directories."""
        results_files = []
        for results_dir in glob.glob(self.results_dir_pattern):
            # Get the assistant name directly from the directory name
            assistant_name = os.path.basename(results_dir)
            
            # Skip if not a directory
            if not os.path.isdir(results_dir):
                continue
                
            for root, _, files in os.walk(results_dir):
                for file in files:
                    if file.endswith(".csv"):
                        filepath = os.path.join(root, file)
                        
                        # Extract requested_type and context_type from the path
                        path_parts = filepath.split(os.sep)
                        # Adjust the index calculation to make it more robust
                        results_dir_idx = path_parts.index(os.path.basename(results_dir))
                        if len(path_parts) > results_dir_idx + 2:  # Make sure we have enough parts
                            requested_type = path_parts[results_dir_idx + 1]
                            context_type = path_parts[results_dir_idx + 2]
                        else:
                            requested_type = "unknown"
                            context_type = "unknown"
                        
                        results_files.append({
                            "assistant": assistant_name,
                            "filepath": filepath,
                            "requested_type": requested_type,
                            "context_type": context_type
                        })
        
        print(f"Found {len(results_files)} result files")
        return results_files
    
    def load_and_analyze_data(self):
        """Load results files and analyze performance."""
        results_files = self.find_results_files()
        
        if not results_files:
            print("No result files found. Please check the directory pattern.")
            return pd.DataFrame()
        
        all_results = []
        for file_info in results_files:
            try:
                print(f"Processing {file_info['filepath']}")
                df = pd.read_csv(file_info["filepath"])
                
                # Debug: Print columns to understand the data structure
                print(f"Columns in {os.path.basename(file_info['filepath'])}: {df.columns.tolist()}")
                
                # Extract the assistant parameters
                params = self.extract_assistant_params(file_info["assistant"])
                
                # Make sure the required columns exist
                if "verified" not in df.columns:
                    print(f"Warning: 'verified' column not found in {file_info['filepath']}")
                    continue
                
                # Calculate metrics
                verified_count = df["verified"].sum()
                total_runs = len(df)
                verification_rate = verified_count / total_runs if total_runs > 0 else 0
                
                # Check for other columns, use defaults if not available
                avg_time = df["time_taken"].mean() if "time_taken" in df.columns else 0
                avg_iterations = df["iterations"].mean() if "iterations" in df.columns else 0
                
                # Calculate success and failure metrics separately
                success_df = df[df["verified"] == True]
                fail_df = df[df["verified"] == False]
                
                # Get success/failure specific metrics
                avg_success_time = success_df["time_taken"].mean() if "time_taken" in df.columns and not success_df.empty else 0
                avg_fail_time = fail_df["time_taken"].mean() if "time_taken" in df.columns and not fail_df.empty else 0
                avg_success_iterations = success_df["iterations"].mean() if "iterations" in df.columns and not success_df.empty else 0
                avg_fail_iterations = fail_df["iterations"].mean() if "iterations" in df.columns and not fail_df.empty else 0
                
                # Analyze function-level verification
                function_success_rates = {}
                if "function_status" in df.columns:
                    for i, row in df.iterrows():
                        try:
                            # Try to parse the function_status column
                            if isinstance(row["function_status"], str):
                                # The function_status might be a string representation of a dict
                                func_status = eval(row["function_status"])
                            else:
                                func_status = row["function_status"]
                                
                            for func_name, status in func_status.items():
                                if func_name not in function_success_rates:
                                    function_success_rates[func_name] = {"success": 0, "total": 0}
                                
                                function_success_rates[func_name]["total"] += 1
                                if status == "Verified":
                                    function_success_rates[func_name]["success"] += 1
                        except Exception as e:
                            print(f"Error processing function_status in row {i}: {e}")
                            continue
                
                # Calculate function-level verification rates
                func_verification_rates = {
                    func_name: data["success"] / data["total"] 
                    for func_name, data in function_success_rates.items()
                }
                
                # Create a result entry
                result = {
                    "assistant": file_info["assistant"],
                    "requested_type": file_info["requested_type"],
                    "context_type": file_info["context_type"],
                    "verification_rate": verification_rate,
                    "verified_count": verified_count,
                    "total_runs": total_runs,
                    "avg_time": avg_time,
                    "avg_iterations": avg_iterations,
                    "avg_success_time": avg_success_time,
                    "avg_fail_time": avg_fail_time,
                    "avg_success_iterations": avg_success_iterations,
                    "avg_fail_iterations": avg_fail_iterations,
                    "function_verification_rates": func_verification_rates,
                    **params  # Include the extracted parameters
                }
                
                all_results.append(result)
                
            except Exception as e:
                print(f"Error processing {file_info['filepath']}: {e}")
        
        if not all_results:
            print("No results could be processed. Check the file format.")
            return pd.DataFrame()
            
        # Convert results to DataFrame
        self.summary_df = pd.DataFrame(all_results)
        print(f"Processed {len(all_results)} result files successfully")
        
        # Debug: Print the columns and first few rows
        if not self.summary_df.empty:
            print(f"Summary DataFrame columns: {self.summary_df.columns.tolist()}")
            print("First few rows:")
            print(self.summary_df.head())
        
        return self.summary_df
    
    def create_summary_table(self):
        """Create a summary table of performance metrics."""
        if self.summary_df is None or self.summary_df.empty:
            print("No data available to create summary table")
            return pd.DataFrame()
            
        # To avoid KeyError if columns are missing, let's be defensive
        pivot_columns = ["verification_rate", "avg_time", "avg_iterations"]
        available_columns = [col for col in pivot_columns if col in self.summary_df.columns]
        
        if not available_columns:
            print("No metric columns available for pivot table")
            return self.summary_df
        
        try:
            # Create a pivot table with assistants as rows and metrics as columns
            pivot_df = self.summary_df.pivot_table(
                index=["model", "erc_type", "learning_rate", "epochs", "batch_size"],
                columns=["requested_type", "context_type"],
                values=available_columns,
                aggfunc="mean"
            )
            
            # Flatten the multi-level columns
            pivot_df.columns = [f"{col[0]}_{col[1]}_{col[2]}" for col in pivot_df.columns]
            
            # Reset index to make it a regular DataFrame
            pivot_df = pivot_df.reset_index()
            
            # Calculate overall performance (average across all configurations)
            overall_metrics = {}
            for col in available_columns:
                if col in self.summary_df.columns:
                    overall_metrics[col] = "mean"
            
            if overall_metrics:
                overall_performance = self.summary_df.groupby(["model"]).agg(overall_metrics).reset_index()
                
                # Rename columns for clarity
                rename_dict = {
                    "verification_rate": "overall_verification_rate",
                    "avg_time": "overall_avg_time",
                    "avg_iterations": "overall_avg_iterations"
                }
                
                rename_cols = {k: v for k, v in rename_dict.items() if k in overall_performance.columns}
                if rename_cols:
                    overall_performance = overall_performance.rename(columns=rename_cols)
                
                # Merge with pivot_df
                result_df = pd.merge(pivot_df, overall_performance, on="model")
            else:
                result_df = pivot_df
            
            return result_df
        except Exception as e:
            print(f"Error creating summary table: {e}")
            return self.summary_df
    
    def plot_verification_rates(self, output_file="verification_rates.png"):
        """Plot verification rates for different assistants."""
        if self.summary_df is None or self.summary_df.empty or "verification_rate" not in self.summary_df.columns:
            print("No verification rate data available for plotting")
            return None
        
        plt.figure(figsize=(12, 8))
        
        try:
            # Group by model and calculate mean verification rate
            model_performance = self.summary_df.groupby("model")["verification_rate"].mean().reset_index()
            model_performance = model_performance.sort_values("verification_rate", ascending=False)
            
            # Create bar plot
            sns.barplot(x="model", y="verification_rate", data=model_performance)
            plt.title("Overall Verification Rate by Assistant Model")
            plt.xlabel("Assistant Model")
            plt.ylabel("Verification Rate")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(output_file)
            
            return output_file
        except Exception as e:
            print(f"Error plotting verification rates: {e}")
            return None

    def plot_verification_by_params(self, output_prefix="verification_by"):
        """Plot verification rates grouped by different hyperparameters."""
        if self.summary_df is None or self.summary_df.empty or "verification_rate" not in self.summary_df.columns:
            print("No verification rate data available for plotting by parameters")
            return None
        
        try:
            # Filter out the baseline model
            df = self.summary_df[self.summary_df["learning_rate"] > 0]
            
            if df.empty:
                print("No data with learning rate > 0 for hyperparameter plots")
                return None
            
            # Plot by learning rate
            plt.figure(figsize=(10, 6))
            sns.boxplot(x="learning_rate", y="verification_rate", data=df)
            plt.title("Verification Rate by Learning Rate")
            plt.xlabel("Learning Rate")
            plt.ylabel("Verification Rate")
            plt.tight_layout()
            plt.savefig(f"{output_prefix}_learning_rate.png")
            
            # Plot by epochs
            plt.figure(figsize=(10, 6))
            sns.boxplot(x="epochs", y="verification_rate", data=df)
            plt.title("Verification Rate by Number of Epochs")
            plt.xlabel("Epochs")
            plt.ylabel("Verification Rate")
            plt.tight_layout()
            plt.savefig(f"{output_prefix}_epochs.png")
            
            # Plot by batch size
            plt.figure(figsize=(10, 6))
            sns.boxplot(x="batch_size", y="verification_rate", data=df)
            plt.title("Verification Rate by Batch Size")
            plt.xlabel("Batch Size")
            plt.ylabel("Verification Rate")
            plt.tight_layout()
            plt.savefig(f"{output_prefix}_batch_size.png")
            
            return output_prefix
        except Exception as e:
            print(f"Error plotting verification by parameters: {e}")
            return None

    def plot_heatmap(self, output_file="heatmap.png"):
        """Create a heatmap showing verification rates by epochs and learning rate."""
        if self.summary_df is None or self.summary_df.empty or "verification_rate" not in self.summary_df.columns:
            print("No verification rate data available for heatmap")
            return None
            
        try:
            # Filter out the baseline model and get relevant data
            df = self.summary_df[self.summary_df["learning_rate"] > 0]
            
            if df.empty:
                print("No data with learning rate > 0 for heatmap")
                return None
            
            # For each batch size, create a heatmap
            batch_sizes = df["batch_size"].unique()
            
            for batch_size in batch_sizes:
                # Filter for this batch size
                batch_df = df[df["batch_size"] == batch_size]
                
                if batch_df.empty:
                    print(f"No data for batch size {batch_size}")
                    continue
                
                # Check if we have multiple epochs and learning rates
                if len(batch_df["epochs"].unique()) <= 1 or len(batch_df["learning_rate"].unique()) <= 1:
                    print(f"Not enough variation in epochs or learning rate for batch size {batch_size}")
                    continue
                
                # Create pivot table for heatmap
                heatmap_data = batch_df.pivot_table(
                    index="epochs", 
                    columns="learning_rate",
                    values="verification_rate",
                    aggfunc="mean"
                )
                
                plt.figure(figsize=(10, 8))
                sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", fmt=".2f", linewidths=.5)
                plt.title(f"Verification Rate by Learning Rate and Epochs (Batch Size: {batch_size})")
                plt.xlabel("Learning Rate")
                plt.ylabel("Epochs")
                plt.tight_layout()
                plt.savefig(f"heatmap_batch_{batch_size}.png")
                
            return "Heatmaps generated for each batch size"
        except Exception as e:
            print(f"Error plotting heatmap: {e}")
            return None
    
    def plot_function_verification(self, output_file="function_verification.png"):
        """Plot function-level verification rates."""
        if self.summary_df is None or self.summary_df.empty:
            print("No data available for function verification plot")
            return None
            
        try:
            # Collect function verification rates
            function_data = []
            for i, row in self.summary_df.iterrows():
                assistant = row["model"]
                if "function_verification_rates" not in row:
                    continue
                    
                func_rates = row["function_verification_rates"]
                
                if isinstance(func_rates, str):
                    try:
                        func_rates = eval(func_rates)
                    except:
                        print(f"Could not parse function_verification_rates in row {i}")
                        continue
                        
                if not func_rates:  # Skip if empty
                    continue
                    
                for func_name, rate in func_rates.items():
                    function_data.append({
                        "assistant": assistant,
                        "function": func_name,
                        "verification_rate": rate
                    })
            
            if not function_data:
                print("No function verification data collected")
                return None
                
            func_df = pd.DataFrame(function_data)
            
            # Create a pivot table for heatmap
            pivot_data = func_df.pivot_table(
                index="function",
                columns="assistant",
                values="verification_rate",
                aggfunc="mean"
            )
            
            if pivot_data.empty:
                print("Pivot table for function verification is empty")
                return None
                
            plt.figure(figsize=(14, 10))
            sns.heatmap(pivot_data, annot=True, cmap="YlGnBu", fmt=".2f", linewidths=.5)
            plt.title("Function-level Verification Rate by Assistant")
            plt.xlabel("Assistant")
            plt.ylabel("Function")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(output_file)
            
            return output_file
        except Exception as e:
            print(f"Error plotting function verification: {e}")
            return None
    
    def create_markdown_table(self, data, columns, index_col=None, percentage_cols=None, sort_col=None, sort_ascending=False, precision=2):
        """
        Create a markdown table from a DataFrame
        
        Args:
            data: DataFrame to convert to a table
            columns: List of columns to include
            index_col: Column to use as the index (first column)
            percentage_cols: List of columns to format as percentages
            sort_col: Column to sort by
            sort_ascending: Sort order (True for ascending, False for descending)
            precision: Decimal precision for numeric values
            
        Returns:
            Markdown formatted table string
        """
        if percentage_cols is None:
            percentage_cols = []
            
        # Create a copy to avoid modifying the original
        df = data.copy()
        
        # Filter to only include specified columns
        if index_col:
            cols_to_use = [index_col] + [c for c in columns if c != index_col]
        else:
            cols_to_use = columns
            
        df = df[cols_to_use]
        
        # Sort if specified
        if sort_col:
            df = df.sort_values(by=sort_col, ascending=sort_ascending)
            
        # Format percentage columns
        for col in percentage_cols:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"{x*100:.{precision}f}" if pd.notnull(x) else "")
        
        # Create header row
        header = "| " + " | ".join(df.columns) + " |"
        
        # Create separator row
        separator = "| " + " | ".join([":---" if i == 0 or i-1 not in percentage_cols else ":---:" for i, c in enumerate(df.columns)]) + " |"
        
        # Create data rows
        rows = []
        for _, row in df.iterrows():
            rows.append("| " + " | ".join([str(v) for v in row.values]) + " |")
            
        # Combine all parts
        table = "\n".join([header, separator] + rows)
        return table
    
    def generate_detailed_report(self, output_directory="assistant_comparison_report/entire_contract_base_full_context", output_file="detailed_report.md"):
        """
        Generate a comprehensive detailed report in markdown format similar to the experiment_analysis_summary_latest.md
        """
        if self.summary_df is None or self.summary_df.empty:
            print("No data available to generate detailed report")
            return None
            
        os.makedirs(output_directory, exist_ok=True)
        report_path = os.path.join(output_directory, output_file)
        
        try:
            # Calculate total runs
            total_runs = self.summary_df["total_runs"].sum()
            
            # Create the overall performance section
            overall_performance = self.summary_df.groupby("model").agg({
                "verification_rate": "mean",
                "verified_count": "sum",
                "total_runs": "sum"
            }).reset_index()
            
            overall_performance = overall_performance.sort_values("verification_rate", ascending=False)
            
            # Create the model specificity analysis
            # Group by model and requested_type to see how each model performs on different standards
            model_specificity = self.summary_df.groupby(["model", "requested_type"]).agg({
                "verification_rate": "mean",
                "verified_count": "sum",
                "total_runs": "sum"
            }).reset_index()
            
            # Create pivot tables for model specificity
            specificity_rate_pivot = model_specificity.pivot_table(
                index="model",
                columns="requested_type",
                values="verification_rate",
                aggfunc="mean"
            ).reset_index()
            
            specificity_counts_pivot = model_specificity.pivot_table(
                index="model",
                columns="requested_type",
                values=["verified_count", "total_runs"],
                aggfunc="sum"
            )
            
            # Construct counts as strings "X / Y"
            counts_df = pd.DataFrame(index=specificity_counts_pivot.index)
            for req_type in model_specificity["requested_type"].unique():
                if (("verified_count", req_type) in specificity_counts_pivot.columns and 
                    ("total_runs", req_type) in specificity_counts_pivot.columns):
                    counts_df[req_type] = (
                        specificity_counts_pivot["verified_count"][req_type].astype(str) + 
                        " / " + 
                        specificity_counts_pivot["total_runs"][req_type].astype(str)
                    )
            
            counts_df = counts_df.reset_index()
            
            # Efficiency analysis based on iterations and time
            efficiency_df = self.summary_df.groupby("model").agg({
                "avg_success_iterations": "mean",
                "avg_fail_iterations": "mean",
                "avg_success_time": "mean",
                "avg_fail_time": "mean",
                "verification_rate": lambda x: 1 - x.mean()  # fail rate
            }).reset_index()
            
            efficiency_df = efficiency_df.rename(columns={"verification_rate": "fail_rate"})
            
            # Write the markdown report
            with open(report_path, "w") as f:
                # Report header
                f.write(f"# Assistant Fine-Tuning Performance Analysis\n\n")
                f.write(f"This document summarizes the results of fine-tuning experiments for generating formal postconditions for smart contracts using different GPT models. The analysis is based on {total_runs} total runs.\n\n")
                
                # Overall Performance Section
                f.write("## Overall Performance Analysis\n\n")
                f.write("This section presents the overall success rates of each model across all tasks. Success is defined as generating postconditions that pass verification.\n\n")
                f.write(f"**Total Runs Analyzed:** {total_runs}\n\n")
                f.write("**Overall Success Rates:**\n\n")
                
                # Create markdown table for overall performance
                overall_table = self.create_markdown_table(
                    overall_performance,
                    columns=["model", "verification_rate", "verified_count", "total_runs"],
                    percentage_cols=["verification_rate"],
                    sort_col="verification_rate",
                    sort_ascending=False
                )
                f.write(overall_table + "\n\n")
                
                # Key observations section
                f.write("**Key Observations:**\n\n")
                best_model = overall_performance.iloc[0]["model"]
                worst_model = overall_performance.iloc[-1]["model"]
                avg_rate = overall_performance["verification_rate"].mean()
                
                f.write(f"- The '{best_model}' model achieved the highest overall success rate at {overall_performance.iloc[0]['verification_rate']*100:.2f}%.\n")
                f.write(f"- The average verification rate across all models was {avg_rate*100:.2f}%.\n")
                f.write(f"- The '{worst_model}' model had the lowest success rate at {overall_performance.iloc[-1]['verification_rate']*100:.2f}%.\n\n")
                
                # Add graph reference
                f.write("![Overall Verification Rates](verification_rates.png)\n\n")
                
                # Model Specificity Section
                f.write("## Model Specificity Analysis\n\n")
                f.write("This section examines how well each model performs when requested to generate postconditions for a particular contract standard.\n\n")
                
                # Add the verification rate table
                f.write("**Success Rate (%) for each Model on each Requested Type:**\n\n")
                spec_table = self.create_markdown_table(
                    specificity_rate_pivot,
                    columns=["model"] + list(specificity_rate_pivot.columns[1:]),
                    percentage_cols=list(specificity_rate_pivot.columns[1:]),
                    sort_col="model"
                )
                f.write(spec_table + "\n\n")
                
                # Add the counts table
                f.write("**Successful Runs / Total Runs for each Model on each Requested Type:**\n\n")
                counts_table = self.create_markdown_table(
                    counts_df,
                    columns=["model"] + list(counts_df.columns[1:]),
                    sort_col="model"
                )
                f.write(counts_table + "\n\n")
                
                # Efficiency Analysis Section
                f.write("## Efficiency Analysis\n\n")
                f.write("This section evaluates the efficiency of the models in terms of the number of iterations and time taken to reach a successful verification or exhaust attempts.\n\n")
                
                # Add efficiency tables
                f.write("**Average Iterations and Time per Model:**\n\n")
                efficiency_table = self.create_markdown_table(
                    efficiency_df,
                    columns=["model", "avg_fail_iterations", "avg_success_iterations", "avg_fail_time", "avg_success_time", "fail_rate"],
                    percentage_cols=["fail_rate"],
                    sort_col="fail_rate"
                )
                f.write(efficiency_table + "\n\n")
                
                # Add hyperparameter analysis
                f.write("## Hyperparameter Analysis\n\n")
                f.write("This section analyzes the impact of different hyperparameters (learning rate, epochs, batch size) on model performance.\n\n")
                
                # Add hyperparameter images
                f.write("### By Learning Rate\n\n")
                f.write("![Verification Rate by Learning Rate](verification_by_learning_rate.png)\n\n")
                
                f.write("### By Epochs\n\n")
                f.write("![Verification Rate by Number of Epochs](verification_by_epochs.png)\n\n")
                
                f.write("### By Batch Size\n\n")
                f.write("![Verification Rate by Batch Size](verification_by_batch_size.png)\n\n")
                
                # Function-level verification
                f.write("## Function-level Verification Analysis\n\n")
                f.write("This section examines which specific functions are most successfully verified by each model.\n\n")
                f.write("![Function Verification Rates](function_verification.png)\n\n")
                
                # Overall Conclusion
                f.write("## Overall Conclusion\n\n")
                f.write("Based on the analysis, the following conclusions can be drawn:\n\n")
                
                # Extract insights for the conclusion
                top_models = overall_performance.head(3)["model"].tolist()
                top_models_str = ", ".join([f"`{m}`" for m in top_models[:-1]]) + f" and `{top_models[-1]}`"
                
                baseline_model = "4o-mini"
                baseline_rate = overall_performance[overall_performance["model"] == baseline_model]["verification_rate"].values
                if len(baseline_rate) > 0:
                    baseline_rate = baseline_rate[0] * 100
                else:
                    baseline_rate = "N/A"
                
                # Find the best hyperparameters
                fine_tuned_df = self.summary_df[self.summary_df["learning_rate"] > 0]
                if not fine_tuned_df.empty:
                    best_lr = fine_tuned_df.groupby("learning_rate")["verification_rate"].mean().idxmax()
                    best_epochs = fine_tuned_df.groupby("epochs")["verification_rate"].mean().idxmax()
                    best_batch = fine_tuned_df.groupby("batch_size")["verification_rate"].mean().idxmax()
                    
                    f.write(f"1. The models {top_models_str} demonstrated the highest overall verification rates.\n")
                    f.write(f"2. Fine-tuning generally improved performance compared to the baseline `{baseline_model}` model (verification rate: {baseline_rate:.2f}%).\n")
                    f.write(f"3. The optimal hyperparameters appear to be a learning rate of {best_lr:.3f}, {best_epochs} epochs, and a batch size of {best_batch}.\n")
                    f.write(f"4. Successful verification attempts are significantly faster than failed attempts, suggesting that early success indicators can help determine when a model is likely to produce valid postconditions.\n")
                
                # Generate report date
                f.write(f"\n\n*Report generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
                
            print(f"Detailed report generated at {report_path}")
            return report_path
                
        except Exception as e:
            print(f"Error generating detailed report: {e}")
            return None
            
    def generate_report(self, output_directory="assistant_comparison_report/entire_contract_base_full_context"):
        """Generate a comprehensive report with tables and visualizations."""
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
        
        print(f"Generating report in {output_directory}...")
        
        # Load and analyze data
        self.load_and_analyze_data()
        
        if self.summary_df is None or self.summary_df.empty:
            print("No data available to generate report")
            return None
        
        # Generate summary table
        summary_table = self.create_summary_table()
        if not summary_table.empty:
            summary_table.to_csv(f"{output_directory}/summary_table.csv", index=False)
            
            # Generate HTML table for better visualization
            html_table = summary_table.to_html(index=False)
            with open(f"{output_directory}/summary_table.html", "w") as f:
                f.write(html_table)
        
        # Generate plots
        verification_plot = self.plot_verification_rates(f"{output_directory}/verification_rates.png")
        params_plots = self.plot_verification_by_params(f"{output_directory}/verification_by")
        heatmap_result = self.plot_heatmap(f"{output_directory}/heatmap.png")
        function_plot = self.plot_function_verification(f"{output_directory}/function_verification.png")
        
        # Generate detailed report
        detailed_report = self.generate_detailed_report(output_directory)
        
        # Generate simple markdown report
        with open(f"{output_directory}/report.md", "w") as f:
            f.write("# Assistant Performance Comparison Report\n\n")
            f.write("## Summary Table\n\n")
            f.write("See [summary_table.csv](summary_table.csv) for the detailed metrics.\n\n")
            
            if verification_plot:
                f.write("## Overall Verification Rates\n\n")
                f.write("![Verification Rates](verification_rates.png)\n\n")
            
            if params_plots:
                f.write("## Verification Rates by Hyperparameters\n\n")
                f.write("### By Learning Rate\n\n")
                f.write("![By Learning Rate](verification_by_learning_rate.png)\n\n")
                f.write("### By Epochs\n\n")
                f.write("![By Epochs](verification_by_epochs.png)\n\n")
                f.write("### By Batch Size\n\n")
                f.write("![By Batch Size](verification_by_batch_size.png)\n\n")
            
            if function_plot:
                f.write("## Function-level Verification\n\n")
                f.write("![Function Verification](function_verification.png)\n\n")
            
            if detailed_report:
                f.write("\n\nFor a more detailed analysis, see [Detailed Report](detailed_report.md).\n")
            
        print(f"Report generated in {output_directory}/")
        return output_directory

if __name__ == "__main__":
    comparer = AssistantComparer()
    report_dir = comparer.generate_report()
    print(f"Performance comparison complete. Report available at {report_dir}/") 