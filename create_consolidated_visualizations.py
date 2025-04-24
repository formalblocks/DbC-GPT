import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import glob

# Set up plot style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('colorblind')

def create_erc_verification_heatmaps(analysis_dir):
    """Create heatmaps showing verification rates for each ERC standard"""
    # Process for each ERC standard
    for erc_standard in ['erc20', 'erc721', 'erc1155']:
        # Find all summary files for this standard
        summary_files = glob.glob(f"{analysis_dir}/*_{erc_standard}_summary.csv")
        
        if not summary_files:
            continue
            
        # Collect data from all files
        all_data = []
        
        for file in summary_files:
            try:
                # Extract assistant name from filename
                assistant = os.path.basename(file).split('_')[0]
                
                # Read the CSV
                df = pd.read_csv(file)
                
                # Add assistant column
                df['Assistant'] = assistant
                
                all_data.append(df)
            except Exception as e:
                print(f"Error processing {file}: {e}")
        
        if not all_data:
            continue
            
        # Combine all data
        combined_df = pd.concat(all_data)
        
        # Extract function names
        function_cols = [col for col in combined_df.columns if col.endswith('_rate')]
        function_names = [col.replace('_rate', '') for col in function_cols]
        
        # Create a pivot table for verification rates
        pivot_data = []
        
        for _, row in combined_df.iterrows():
            assistant = row['Assistant']
            context = row['Context']
            
            for func in function_names:
                rate_col = f"{func}_rate"
                iter_col = f"{func}_avg_iter"
                
                if rate_col in row and pd.notna(row[rate_col]):
                    pivot_data.append({
                        'Assistant': assistant,
                        'Context': context,
                        'Function': func,
                        'Verification Rate': row[rate_col],
                        'Average Iteration': row[iter_col] if iter_col in row and pd.notna(row[iter_col]) else np.nan
                    })
        
        # Create DataFrame from pivoted data
        pivot_df = pd.DataFrame(pivot_data)
        
        # Generate heatmap
        plt.figure(figsize=(14, 10))
        
        # Create pivot table for heatmap
        heatmap_data = pivot_df.pivot_table(
            index=['Assistant', 'Context'],
            columns='Function',
            values='Verification Rate',
            aggfunc='mean'
        ).fillna(0)
        
        # Sort functions by overall verification rate
        func_order = pivot_df.groupby('Function')['Verification Rate'].mean().sort_values(ascending=False).index.tolist()
        heatmap_data = heatmap_data[func_order]
        
        # Plot heatmap
        ax = sns.heatmap(heatmap_data, annot=True, cmap='YlGnBu', vmin=0, vmax=1, fmt='.2f')
        plt.title(f'Verification Rates for {erc_standard.upper()}')
        plt.tight_layout()
        plt.savefig(f"{analysis_dir}/{erc_standard}_verification_rates.png", dpi=300)
        plt.close()
        
        # Generate average iteration heatmap for verified functions
        plt.figure(figsize=(14, 10))
        
        # Filter data for verified functions
        verified_df = pivot_df[pivot_df['Verification Rate'] > 0]
        
        # Create pivot table for heatmap
        iter_heatmap_data = verified_df.pivot_table(
            index=['Assistant', 'Context'],
            columns='Function',
            values='Average Iteration',
            aggfunc='mean'
        )
        
        # Plot heatmap
        sns.heatmap(iter_heatmap_data, annot=True, cmap='YlOrRd', fmt='.1f')
        plt.title(f'Average Verification Iteration for {erc_standard.upper()}')
        plt.tight_layout()
        plt.savefig(f"{analysis_dir}/{erc_standard}_avg_iterations.png", dpi=300)
        plt.close()

def create_function_complexity_charts(analysis_dir):
    """Create charts showing function verification difficulty across ERC standards"""
    # Find all summary files
    summary_files = glob.glob(f"{analysis_dir}/*_summary.csv")
    
    if not summary_files:
        return
        
    # Collect data from all files
    all_data = []
    
    for file in summary_files:
        try:
            # Extract standard name from filename
            parts = os.path.basename(file).split('_')
            assistant = parts[0]
            standard = parts[1]
            
            # Read the CSV
            df = pd.read_csv(file)
            
            # Add assistant and standard columns
            df['Assistant'] = assistant
            df['Standard'] = standard
            
            all_data.append(df)
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    if not all_data:
        return
        
    # Combine all data
    combined_df = pd.concat(all_data)
    
    # Extract function names
    function_cols = [col for col in combined_df.columns if col.endswith('_rate')]
    function_names = [col.replace('_rate', '') for col in function_cols]
    
    # Create a pivot table for function complexity
    pivot_data = []
    
    for _, row in combined_df.iterrows():
        assistant = row['Assistant']
        standard = row['Standard']
        context = row['Context']
        
        for func in function_names:
            rate_col = f"{func}_rate"
            iter_col = f"{func}_avg_iter"
            
            if rate_col in row and pd.notna(row[rate_col]) and row[rate_col] > 0:
                pivot_data.append({
                    'Assistant': assistant,
                    'Standard': standard,
                    'Context': context,
                    'Function': func,
                    'Average Iteration': row[iter_col] if iter_col in row and pd.notna(row[iter_col]) else np.nan
                })
    
    # Create DataFrame from pivoted data
    pivot_df = pd.DataFrame(pivot_data)
    
    # Calculate average iteration by function across all contexts
    func_complexity = pivot_df.groupby('Function')['Average Iteration'].mean().sort_values(ascending=False)
    
    # Plot function complexity
    plt.figure(figsize=(12, 8))
    sns.barplot(x=func_complexity.index, y=func_complexity.values)
    plt.xticks(rotation=45, ha='right')
    plt.title('Average Verification Iteration by Function (Higher = More Complex)')
    plt.tight_layout()
    plt.savefig(f"{analysis_dir}/function_complexity.png", dpi=300)
    plt.close()
    
    # Calculate verification iteration distribution for complex functions
    complex_functions = func_complexity.head(5).index.tolist()
    
    # Filter data for complex functions
    complex_df = pivot_df[pivot_df['Function'].isin(complex_functions)]
    
    # Plot boxplot for complex functions
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='Function', y='Average Iteration', data=complex_df)
    plt.xticks(rotation=45, ha='right')
    plt.title('Verification Iteration Distribution for Complex Functions')
    plt.tight_layout()
    plt.savefig(f"{analysis_dir}/complex_function_distribution.png", dpi=300)
    plt.close()
    
    # Plot verification distribution for transferFrom
    if 'transferFrom' in function_names:
        transferfrom_df = pivot_df[pivot_df['Function'] == 'transferFrom']
        
        plt.figure(figsize=(12, 8))
        sns.boxplot(x='Standard', y='Average Iteration', data=transferfrom_df)
        plt.title('Verification Iteration Distribution for transferFrom')
        plt.tight_layout()
        plt.savefig(f"{analysis_dir}/transferFrom_distribution.png", dpi=300)
        plt.close()

def create_context_impact_charts(analysis_dir):
    """Create charts showing the impact of context on verification performance"""
    # Find all summary files
    summary_files = glob.glob(f"{analysis_dir}/*_summary.csv")
    
    if not summary_files:
        return
        
    # Collect data from all files
    all_data = []
    
    for file in summary_files:
        try:
            # Extract standard name from filename
            parts = os.path.basename(file).split('_')
            assistant = parts[0]
            standard = parts[1]
            
            # Read the CSV
            df = pd.read_csv(file)
            
            # Add assistant and standard columns
            df['Assistant'] = assistant
            df['Standard'] = standard
            
            all_data.append(df)
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    if not all_data:
        return
        
    # Combine all data
    combined_df = pd.concat(all_data)
    
    # Extract function names
    function_cols = [col for col in combined_df.columns if col.endswith('_rate')]
    
    # Calculate average verification rate for each context
    combined_df['avg_verification_rate'] = combined_df[function_cols].mean(axis=1)
    
    # Generate context labels
    combined_df['Context_Type'] = combined_df['Context'].apply(lambda x: 'None' if x == 'none' else (
        'Same Standard' if x == combined_df['Standard'].iloc[0] else (
        'Multiple Standards' if '_' in x else 'Different Standard'
    )))
    
    # Plot verification rate by context type
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='Context_Type', y='avg_verification_rate', data=combined_df)
    plt.title('Verification Rate by Context Type')
    plt.ylabel('Average Verification Rate')
    plt.tight_layout()
    plt.savefig(f"{analysis_dir}/context_impact.png", dpi=300)
    plt.close()
    
    # Calculate average iterations for each standard and context
    iter_cols = [col for col in combined_df.columns if col.endswith('_avg_iter')]
    combined_df['avg_iteration'] = combined_df[iter_cols].mean(axis=1, skipna=True)
    
    # Plot average iterations by context type
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='Context_Type', y='avg_iteration', data=combined_df)
    plt.title('Average Verification Iteration by Context Type')
    plt.ylabel('Average Verification Iteration')
    plt.tight_layout()
    plt.savefig(f"{analysis_dir}/context_impact_iterations.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    # Set the analysis results directory
    analysis_dir = './analysis_results'
    
    # Create visualizations
    print("Creating ERC verification heatmaps...")
    create_erc_verification_heatmaps(analysis_dir)
    
    print("Creating function complexity charts...")
    create_function_complexity_charts(analysis_dir)
    
    print("Creating context impact charts...")
    create_context_impact_charts(analysis_dir)
    
    print("Visualization generation complete.") 