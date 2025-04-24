import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import glob

# Set up plot style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('colorblind')
plt.rcParams['figure.figsize'] = (16, 12)

def extract_verification_status(status_entry):
    """Extract verification statuses from status field in CSV"""
    if not status_entry or status_entry == '[]':
        return None
    
    result = {}
    
    # Extract interaction number and function statuses
    for entry in status_entry:
        if not entry:
            continue
            
        # Extract interaction number
        interaction_match = re.search(r'Interaction: (\d+)', entry)
        if not interaction_match:
            continue
        
        interaction_num = int(interaction_match.group(1))
        
        # Extract function verification statuses
        function_statuses = re.findall(r'(\w+(?:::\w+)?): (OK|ERROR)', entry)
        
        for func, status in function_statuses:
            if '::' in func:
                # Clean up function name
                func = func.split('::')[1]
            result[func] = {'status': status, 'iteration': interaction_num}
    
    return result

def aggregate_results_by_contract_type(results_dir):
    """Aggregate results for all contract types"""
    all_results = {}
    
    # Find all result directories
    result_dirs = glob.glob(f"{results_dir}/results_*")
    
    for result_dir in result_dirs:
        assistant = os.path.basename(result_dir).replace('results_', '')
        all_results[assistant] = {}
        
        # Process each contract type (erc20, erc721, erc1155)
        for contract_type in ['erc20', 'erc721', 'erc1155']:
            contract_dir = os.path.join(result_dir, contract_type)
            if not os.path.exists(contract_dir):
                continue
                
            all_results[assistant][contract_type] = {}
            
            # Process each context directory
            for context_dir in os.listdir(contract_dir):
                if not os.path.isdir(os.path.join(contract_dir, context_dir)):
                    continue
                
                csv_files = glob.glob(f"{contract_dir}/{context_dir}/*.csv")
                if not csv_files:
                    continue
                
                # Process each run in the CSV file
                for csv_file in csv_files:
                    try:
                        df = pd.read_csv(csv_file)
                        
                        # Extract information from each run
                        for _, row in df.iterrows():
                            run = row['run']
                            status_data = row['status']
                            
                            if isinstance(status_data, str):
                                # Sometimes status is a string representation of a list
                                try:
                                    status_data = eval(status_data)
                                except:
                                    continue
                            
                            # Extract verification statuses
                            verification_results = extract_verification_status(status_data)
                            
                            if verification_results:
                                if context_dir not in all_results[assistant][contract_type]:
                                    all_results[assistant][contract_type][context_dir] = []
                                
                                all_results[assistant][contract_type][context_dir].append({
                                    'run': run,
                                    'verification_results': verification_results
                                })
                    except Exception as e:
                        print(f"Error processing {csv_file}: {e}")
    
    return all_results

def plot_function_verification_distribution(results, output_dir):
    """Plot function verification distribution across iterations"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each assistant
    for assistant, assistant_data in results.items():
        # Process each contract type
        for contract_type, contract_data in assistant_data.items():
            # Get all unique functions across all contexts
            all_functions = set()
            for context, runs in contract_data.items():
                for run in runs:
                    for func in run['verification_results'].keys():
                        all_functions.add(func)
            
            # Sort functions for consistent plotting
            all_functions = sorted(list(all_functions))
            
            if not all_functions:
                continue
                
            # Create subplot grid
            n_funcs = len(all_functions)
            n_cols = 2
            n_rows = (n_funcs + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 3*n_rows))
            if n_rows == 1 and n_cols == 1:
                axes = np.array([axes])
            axes = axes.flatten()
            
            # Plot each function
            for i, func in enumerate(all_functions):
                ax = axes[i]
                
                # Data structure to hold counts for each iteration/context
                data = defaultdict(lambda: defaultdict(int))
                
                # Count verified functions per iteration per context
                for context, runs in contract_data.items():
                    for run in runs:
                        if func in run['verification_results']:
                            result = run['verification_results'][func]
                            if result['status'] == 'OK':
                                data[context][result['iteration']] += 1
                
                # Plot the data
                for context, iterations in data.items():
                    # Create x and y data
                    x = list(iterations.keys())
                    y = list(iterations.values())
                    
                    # Use a readable context label
                    context_label = context if context != 'none' else 'No Context'
                    
                    ax.plot(x, y, 'o-', label=context_label, alpha=0.7)
                
                ax.set_title(func)
                ax.set_xlabel('Interaction Count')
                ax.set_ylabel('Verified Count')
                ax.set_xlim(0, 10)
                ax.set_xticks(range(11))
                
                # Add legend if there's data
                if data:
                    ax.legend(fontsize='small')
            
            # Hide unused subplots
            for j in range(i+1, len(axes)):
                axes[j].axis('off')
            
            # Set a tight layout and save
            plt.tight_layout()
            plt.savefig(f"{output_dir}/{assistant}_{contract_type}_functions.png", dpi=300)
            plt.close()

def create_verification_summary_tables(results, output_dir):
    """Create summary tables of verification results"""
    os.makedirs(output_dir, exist_ok=True)
    
    # For each assistant and contract type
    for assistant, assistant_data in results.items():
        for contract_type, contract_data in assistant_data.items():
            # Create summary data
            summary_data = []
            
            for context, runs in contract_data.items():
                context_summary = {'Context': context}
                
                # Aggregate function verification stats
                func_stats = defaultdict(lambda: {'verified': 0, 'total': 0, 'avg_iteration': []})
                
                for run in runs:
                    for func, result in run['verification_results'].items():
                        func_stats[func]['total'] += 1
                        if result['status'] == 'OK':
                            func_stats[func]['verified'] += 1
                            func_stats[func]['avg_iteration'].append(result['iteration'])
                
                # Calculate verification rates and average iterations
                for func, stats in func_stats.items():
                    verification_rate = stats['verified'] / stats['total'] if stats['total'] > 0 else 0
                    avg_iteration = np.mean(stats['avg_iteration']) if stats['avg_iteration'] else np.nan
                    
                    context_summary[f"{func}_rate"] = verification_rate
                    context_summary[f"{func}_avg_iter"] = avg_iteration
                
                summary_data.append(context_summary)
            
            # Create DataFrame and save to CSV
            if summary_data:
                df = pd.DataFrame(summary_data)
                df.to_csv(f"{output_dir}/{assistant}_{contract_type}_summary.csv", index=False)

if __name__ == "__main__":
    # Set the experiments directory
    experiments_dir = './experiments'
    output_dir = './analysis_results'
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Aggregate results
    print("Aggregating results...")
    results = aggregate_results_by_contract_type(experiments_dir)
    
    # Plot function verification distribution
    print("Plotting function verification distribution...")
    plot_function_verification_distribution(results, output_dir)
    
    # Create summary tables
    print("Creating summary tables...")
    create_verification_summary_tables(results, output_dir)
    
    print("Analysis complete. Results saved to", output_dir) 