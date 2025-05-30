import os
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

# Configure the visualization settings
plt.style.use('ggplot')
sns.set(font_scale=1.2)
sns.set_style("whitegrid")

class ContextComparer:
    def __init__(self, mode="entire_contract", contract_name="erc1155"):
        self.mode = mode
        self.contract_name = contract_name
        if self.mode == "func_by_func":
            self.results_root = f"experiments/results_func_by_func_base_full_context/4o-mini/{self.contract_name}/"
            self.output_dir_base = f"context_comparison_report/func_by_func/{self.contract_name}"
        elif self.mode == "entire_contract":
            self.results_root = f"experiments/results_entire_contract_base_full_context/4o-mini/{self.contract_name}/"
            self.output_dir_base = f"context_comparison_report/entire_contract/{self.contract_name}"
        else:
            raise ValueError(f"Invalid mode: {self.mode}. Choose 'func_by_func' or 'entire_contract'.")
        
        os.makedirs(self.output_dir_base, exist_ok=True)
        self.summary_df = None
        self.function_context_matrix = {}

    def find_context_files(self):
        context_files = []
        if not os.path.exists(self.results_root) or not os.path.isdir(self.results_root):
            print(f"Results root directory not found: {self.results_root}")
            return []
        for context_dir in os.listdir(self.results_root):
            context_path = os.path.join(self.results_root, context_dir)
            if not os.path.isdir(context_path):
                continue
            for file in os.listdir(context_path):
                if file.endswith('.csv'):
                    context_files.append({
                        "context": context_dir,
                        "filepath": os.path.join(context_path, file)
                    })
        return context_files

    def load_and_analyze_data(self):
        context_files = self.find_context_files()
        if not context_files:
            print("No context result files found. Please check the directory.")
            return pd.DataFrame()
        all_results = []
        for file_info in context_files:
            try:
                df = pd.read_csv(file_info["filepath"])
                if "verified" not in df.columns:
                    continue
                verified_count = df["verified"].sum()
                total_runs = len(df)
                verification_rate = verified_count / total_runs if total_runs > 0 else 0
                avg_time = df["time_taken"].mean() if "time_taken" in df.columns else 0
                avg_iterations = df["iterations"].mean() if "iterations" in df.columns else 0
                min_success_iterations = (
                    df[df["verified"] == True]["iterations"].min()
                    if not df[df["verified"] == True].empty else np.nan
                )
                max_iterations = df["iterations"].max() if "iterations" in df.columns else np.nan
                success_df = df[df["verified"] == True]
                fail_df = df[df["verified"] == False]
                avg_success_time = success_df["time_taken"].mean() if "time_taken" in df.columns and not success_df.empty else 0
                avg_fail_time = fail_df["time_taken"].mean() if "time_taken" in df.columns and not fail_df.empty else 0
                avg_success_iterations = success_df["iterations"].mean() if "iterations" in df.columns and not success_df.empty else 0
                avg_fail_iterations = fail_df["iterations"].mean() if "iterations" in df.columns and not fail_df.empty else 0
                function_success_rates = {}
                if self.mode == "func_by_func" and "function_status" in df.columns:
                    for i, row in df.iterrows():
                        try:
                            func_status = row["function_status"]
                            if isinstance(func_status, str):
                                func_status = eval(func_status)
                            for func_name, status in func_status.items():
                                if func_name not in function_success_rates:
                                    function_success_rates[func_name] = {"success": 0, "total": 0}
                                function_success_rates[func_name]["total"] += 1
                                if status == "Verified":
                                    function_success_rates[func_name]["success"] += 1
                        except Exception as e:
                            print(f"Error processing function_status in row {i} of {file_info['filepath']}: {e}")
                            continue
                    for func_name, stat in function_success_rates.items():
                        if func_name not in self.function_context_matrix:
                            self.function_context_matrix[func_name] = {}
                        self.function_context_matrix[func_name][file_info["context"]] = stat["success"] / stat["total"] if stat["total"] > 0 else 0
                result = {
                    "context": file_info["context"],
                    "verification_rate": verification_rate,
                    "verified_count": verified_count,
                    "total_runs": total_runs,
                    "avg_time": avg_time,
                    "avg_iterations": avg_iterations,
                    "avg_success_time": avg_success_time,
                    "avg_fail_time": avg_fail_time,
                    "avg_success_iterations": avg_success_iterations,
                    "avg_fail_iterations": avg_fail_iterations,
                    "min_success_iterations": min_success_iterations,
                    "max_iterations": max_iterations
                }
                all_results.append(result)
            except Exception as e:
                print(f"Error processing {file_info['filepath']}: {e}")
        if not all_results:
            print("No results could be processed. Check the file format.")
            return pd.DataFrame()
        self.summary_df = pd.DataFrame(all_results)
        return self.summary_df

    def create_markdown_table(self, data, columns, percentage_cols=None, sort_col=None, sort_ascending=False, precision=2):
        if percentage_cols is None:
            percentage_cols = []
        df = data.copy()
        df = df[columns]
        if sort_col:
            df = df.sort_values(by=sort_col, ascending=sort_ascending)
        for col in percentage_cols:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: f"{x*100:.{precision}f}" if pd.notnull(x) else "")
        # Replace nan values with "-"
        df = df.fillna("-")
        header = "| " + " | ".join(df.columns) + " |"
        separator = "| " + " | ".join([":---" for _ in df.columns]) + " |"
        rows = ["| " + " | ".join([str(v) for v in row.values]) + " |" for _, row in df.iterrows()]
        table = "\n".join([header, separator] + rows)
        return table

    def plot_function_heatmap(self, output_file=None):
        """Plot a heatmap of function-level verification rates by context."""
        if output_file is None:
            output_file = os.path.join(self.output_dir_base, "function_verification_heatmap.png")

        if not hasattr(self, 'function_context_matrix') or not self.function_context_matrix:
            print("No function-level data available for function heatmap.")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(self.function_context_matrix).T  # Transpose to have functions as rows, contexts as columns
        df = df.fillna(0) # Fill NaNs with 0 for functions not present in some contexts or no successful runs

        if df.empty:
            print("Function-level data is empty after processing.")
            return None

        plt.figure(figsize=(max(10, len(df.columns) * 1.2), max(8, len(df.index) * 0.6)))
        sns.heatmap(df, annot=True, cmap="YlGnBu", fmt=".2f", linewidths=.5, vmin=0, vmax=1)
        plt.title(f"Function-level Verification Rate by Context ({self.mode} - {self.contract_name})")
        plt.xlabel("Context")
        plt.ylabel("Function")
        plt.xticks(rotation=45, ha="right")
        plt.yticks(rotation=0)
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        plt.savefig(output_file)
        plt.close()
        print(f"Function-level heatmap saved to {output_file}")
        return output_file

    def generate_markdown_table(self, output_file=None):
        if output_file is None:
            output_file = os.path.join(self.output_dir_base, "markdown_table.md")

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        self.load_and_analyze_data()
        if self.summary_df is None or self.summary_df.empty:
            print("No data available to generate markdown table")
            return None
        summary_table_df = self.summary_df.sort_values("verification_rate", ascending=False)
        md_table = self.create_markdown_table(
            summary_table_df,
            columns=[
                "context", "verification_rate", "verified_count", "total_runs", "avg_time", "avg_iterations", "min_success_iterations", "max_iterations"
            ],
            percentage_cols=["verification_rate"],
            sort_col="verification_rate",
            sort_ascending=False
        )
        explanation = (
            f"# Context Combination Verification Report ({self.mode} - {self.contract_name})\n\n"
            f"This table summarizes the performance of different context combinations for the assistant on the {self.contract_name.upper()} contract verification task, using the '{self.mode}' approach.\n\n"
            "- **context**: The context combination used for the run.\n"
            "- **verification_rate**: Fraction of runs that were successfully verified (higher is better).\n"
            "- **min_success_iterations**: Minimum number of iterations needed to achieve a successful verification (lower is better).\n"
            "- **max_iterations**: Maximum number of iterations used in any run.\n"
            "- Other columns show averages and counts for each context.\n\n"
        )
        with open(output_file, "w") as f:
            f.write(explanation)
            f.write(md_table + "\n")
            
            if self.mode == "func_by_func":
                f.write("\n## Function-level Verification Rate Heatmap\n\n")
                f.write("The heatmap below shows the verification rates for each function across different context combinations:\n\n")
                f.write("![Function-level Verification Rate Heatmap](function_verification_heatmap.png)\n")
            
        print(f"Markdown table generated at {output_file}")
        return output_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare context performance for smart contract verification.")
    parser.add_argument("--mode", type=str, choices=["func_by_func", "entire_contract"], required=True,
                        help="Analysis mode: 'func_by_func' or 'entire_contract'.")
    parser.add_argument("--contract", type=str, default="erc1155", 
                        help="Contract name (e.g., erc20, erc721, erc1155) to specify results subdirectory. Default: erc1155")
    args = parser.parse_args()

    comparer = ContextComparer(mode=args.mode, contract_name=args.contract)
    markdown_file = comparer.generate_markdown_table()
    
    # Generate function-level heatmap only for func_by_func mode
    if args.mode == "func_by_func":
        comparer.plot_function_heatmap()
    
    print(f"Processing complete for mode '{args.mode}' and contract '{args.contract}'. Reports generated in {comparer.output_dir_base}") 