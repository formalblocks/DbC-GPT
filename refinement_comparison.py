import pandas as pd
import re

# Define file paths 
file_1_path = "./experiments/refinement_check/erc20/base_llm/refinement_check_erc20_[]_base_llm.csv"
file_2_path = "./experiments/refinement_check/erc20/llm_base/refinement_check_erc20_[]_llm_base.csv"
comparison_by_function_file_path = "comparison_by_function_result.csv"

# Load the two CSV files from the provided paths
df1 = pd.read_csv(file_1_path)
df2 = pd.read_csv(file_2_path)

# Define a function to extract the function names and results from the output column
def extract_function_results(output):
    results = []
    pattern = re.compile(r"Refinement::(\w+_?\w*): (\w+)")
    matches = pattern.findall(output)
    for func, result in matches:
        results.append((func, result))
    return results

# Initialize a list to store the comparison data
comparison_data = []

# Loop through both dataframes and compare the outputs
for index, row in df1.iterrows():
    run = row['run']
    output_1 = row['output']
    output_2 = df2.loc[df2['run'] == run, 'output'].values[0]
    
    functions_1 = extract_function_results(output_1)
    functions_2 = extract_function_results(output_2)
    
    func_dict_2 = dict(functions_2)
    
    for func, result_1 in functions_1:
        result_2 = func_dict_2.get(func, 'N/A')
        comparison_data.append([run, func, 'base_llm', result_1])
        comparison_data.append([run, func, 'llm_base', result_2])

# Create a DataFrame from the comparison data
comparison_df = pd.DataFrame(comparison_data, columns=['run', 'function', 'option', 'result'])

print(comparison_df)

# Save the comparison DataFrame to a new CSV file
comparison_df.to_csv(comparison_by_function_file_path, index=False)