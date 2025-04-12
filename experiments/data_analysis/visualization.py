import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def load_and_prepare_data(csv_path="full_model_comparison.csv"):
    """
    Load the CSV data and prepare it for visualization.
    """
    # Load the data
    df = pd.read_csv(csv_path)
    
    # Print basic information
    print(f"Loaded data with {len(df)} rows and {len(df.columns)} columns")
    
    return df

def generate_contract_type_summary(df):
    """
    Generate a summary by contract type across all models.
    """
    # Get all success_rate columns
    rate_cols = [col for col in df.columns if col.endswith('_success_rate')]
    
    # Group by contract_type and calculate mean success rates
    contract_summary = df.groupby('contract_type')[rate_cols].mean().reset_index()
    
    # Calculate overall average per model
    model_avgs = {col: contract_summary[col].mean() for col in rate_cols}
    
    # Create a summary DataFrame for plotting
    plot_data = []
    
    for _, row in contract_summary.iterrows():
        contract = row['contract_type']
        for col in rate_cols:
            model = col.replace('_success_rate', '')
            plot_data.append({
                'contract_type': contract,
                'model': model,
                'success_rate': row[col]
            })
    
    plot_df = pd.DataFrame(plot_data)
    
    # Create the plot
    plt.figure(figsize=(14, 8))
    
    # Create grouped bar chart
    sns.barplot(x='contract_type', y='success_rate', hue='model', data=plot_df)
    
    plt.title('Average Success Rate by Contract Type Across All Models')
    plt.xlabel('Contract Type')
    plt.ylabel('Average Success Rate')
    plt.ylim(0, 1.0)
    plt.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    plt.savefig('contract_type_comparison.png', dpi=300)
    plt.close()
    
    # Print the data
    print("\nAverage Success Rate by Contract Type:")
    print(contract_summary)
    
    print("\nOverall Average Success Rate by Model:")
    for model, avg in model_avgs.items():
        print(f"{model}: {avg:.4f}")
    
    return contract_summary

def generate_context_effectiveness(df):
    """
    Analyze how context affects performance for each contract type.
    """
    # Get unique contract types
    contract_types = df['contract_type'].unique()
    
    # For each contract type, compare performance across different contexts
    for contract_type in contract_types:
        # Filter to the current contract type
        ct_df = df[df['contract_type'] == contract_type]
        
        if len(ct_df) <= 1:
            continue
        
        # Get success rate columns
        rate_cols = [col for col in df.columns if col.endswith('_success_rate')]
        
        # Prepare data for plotting
        plot_data = []
        
        for _, row in ct_df.iterrows():
            context = row['context'] if row['context'] else 'none'
            for col in rate_cols:
                model = col.replace('_success_rate', '')
                plot_data.append({
                    'context': context,
                    'model': model,
                    'success_rate': row[col]
                })
        
        plot_df = pd.DataFrame(plot_data)
        
        # Create plot
        plt.figure(figsize=(16, 10))
        
        # Create grouped bar chart
        sns.barplot(x='context', y='success_rate', hue='model', data=plot_df)
        
        plt.title(f'Success Rate by Context for {contract_type}')
        plt.xlabel('Context')
        plt.ylabel('Success Rate')
        plt.ylim(0, 1.0)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        plt.savefig(f'context_comparison_{contract_type}.png', dpi=300)
        plt.close()
    
    # Create a simplified heatmap showing which contexts are most effective per contract type
    # First, calculate the average success rate across all models for each contract_type/context pair
    rate_cols = [col for col in df.columns if col.endswith('_success_rate')]
    df['avg_success_rate'] = df[rate_cols].mean(axis=1)
    
    # Make sure context is displayed as 'none' instead of empty string
    df['context_display'] = df['context'].apply(lambda x: 'none' if x == '' else x)
    
    # Create a simple pivot table: contract_type × context
    pivot_df = df.pivot_table(
        index='contract_type',
        columns='context_display', 
        values='avg_success_rate',
        aggfunc='mean'
    )
    
    # Increase figure size and adjust font size
    plt.figure(figsize=(16, 8))
    
    # Create the heatmap with improved parameters
    ax = sns.heatmap(
        pivot_df, 
        annot=True,
        cmap="YlGnBu", 
        fmt=".2f", 
        linewidths=1,
        annot_kws={"size": 12},
        vmin=0, 
        vmax=1
    )
    
    # Improve title and labels
    plt.title('Context Effectiveness by Contract Type', fontsize=16, pad=20)
    plt.xlabel('Context', fontsize=14, labelpad=10)
    plt.ylabel('Contract Type', fontsize=14, labelpad=10)
    
    # Ensure x-labels are readable
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    
    # Apply tight layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('context_effectiveness_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return pivot_df

def identify_top_performers(df):
    """
    Identify the top performing model for each contract type and context.
    """
    # Get success rate columns
    rate_cols = [col for col in df.columns if col.endswith('_success_rate')]
    
    # Create a new dataframe to store the top performer for each scenario
    top_performers = pd.DataFrame()
    top_performers['contract_type'] = df['contract_type']
    top_performers['context'] = df['context']
    
    # Find the best model for each row
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
    top_performers.to_csv('top_performers.csv', index=False)
    
    # Create a matrix showing which model is best for each contract/context
    pivot_df = top_performers.pivot_table(index='contract_type', 
                                         columns='context', 
                                         values='best_model', 
                                         aggfunc='first')
    
    # Count how many times each model is the best
    model_counts = {}
    for model in top_performers['best_model']:
        for m in model.split(', '):
            if m in model_counts:
                model_counts[m] += 1
            else:
                model_counts[m] = 1
    
    # Create a bar chart showing the number of "wins" for each model
    plt.figure(figsize=(12, 6))
    models = list(model_counts.keys())
    counts = list(model_counts.values())
    
    # Sort by count
    sorted_indices = np.argsort(counts)[::-1]
    models = [models[i] for i in sorted_indices]
    counts = [counts[i] for i in sorted_indices]
    
    plt.bar(models, counts)
    plt.title('Number of "Best Performance" Scenarios by Model')
    plt.xlabel('Model')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    plt.savefig('best_model_counts.png', dpi=300)
    plt.close()
    
    print("\nTop performer analysis completed. Results saved to 'top_performers.csv'.")
    print("\nModels with most 'best performance' scenarios:")
    for i, model in enumerate(models):
        print(f"{model}: {counts[i]}")
    
    return top_performers

def main():
    """
    Main function to run the visualization analysis
    """
    print("Loading data...")
    df = load_and_prepare_data()
    
    print("\nGenerating contract type summary...")
    generate_contract_type_summary(df)
    
    print("\nAnalyzing context effectiveness...")
    generate_context_effectiveness(df)
    
    print("\nIdentifying top performers...")
    identify_top_performers(df)
    
    print("\nVisualization complete! Check the generated PNG files and CSVs.")

if __name__ == "__main__":
    main() 