import pandas as pd
import re, sys, os

# Determine the current directory (assuming this is run from the notebook)
current_dir = os.path.dirname(os.path.abspath("__file__"))

# Calculate the relative path to the solc_verify_generator directory
solc_verify_generator_path = os.path.abspath(os.path.join(current_dir, "../../../../../solc_verify_generator"))

# Add the calculated path to sys.path
sys.path.append(solc_verify_generator_path)

ref_spec = "./temp/spec.sol"

experiments_list = ['erc20_[20_721_1155]', 'erc20_[20_721]', 'erc20_[20_1155]', 'erc20_[20]', 'erc20_[721_1155]', 'erc20_[721]', 'erc20_[1155]', 'erc20_[]']

desired_functions = ['transfer', 'approve', 'transferFrom', 'balanceOf', 'totalSupply', 'allowance']

from main import call_solc, parse_ast, process_annotations

def get_ref_annotations(spec: str, function: str) -> dict:
    result = call_solc(spec)
    if result.returncode:
        # Something has gone wrong compiling the solidity code
        raise RuntimeError(result.returncode, result.stdout + result.stderr)
    annotations, state_variables = parse_ast()

    list = {}
    for key, value in annotations.items():
        list[key] = value
    if function in list:
        return list[function]
    
for experiment in experiments_list:

    # Define file paths
    file_1_path = f'../../../erc20/base_llm/refinement_check_{experiment}_base_llm.csv'
    file_2_path = f'../../../erc20/llm_base/refinement_check_{experiment}_llm_base.csv'
    spec_file_path = f'../../../../outputs/{experiment}/{experiment}.csv'
    comparison_table_file_path = f'./{experiment}_comparison_table.csv'

    # Load the two CSV files from the provided paths
    df1 = pd.read_csv(file_1_path)
    df2 = pd.read_csv(file_2_path)
    spec_df = pd.read_csv(spec_file_path)

    # Define a function to extract the function names and results from the output column
    def extract_function_results(output):
        results = []
        pattern = re.compile(r"Refinement::(\w+_?\w*): (\w+)")
        matches = pattern.findall(output)
        for func, result in matches:
            if any(desired_func in func for desired_func in desired_functions):
                results.append((func, result))
        return results

    # Define a function to extract the postcondition specs from the specification file
    def extract_postcondition_specs(run, function):
        spec = spec_df.loc[spec_df['run'] == run, 'annotated_contract'].values[0]
        if not isinstance(spec, str):
            return 'N/A'
        function_name = function.split('_')[0]
        postcondition_pattern = re.compile(rf"(/// @notice postcondition.*\n).*function {function_name}")
        matches = postcondition_pattern.findall(spec)
        return '\n'.join(matches) if matches else 'N/A'

    # Initialize a list to store the comparison data
    comparison_data = []

    # Loop through both dataframes and compare the outputs
    for index, row in df1.iterrows():
        run = row['run']
        output_1 = row['output']
        matching_rows = df2.loc[df2['run'] == run, 'output']
        if len(matching_rows) == 0:
            continue  # Skip this iteration if no matching rows are found
        output_2 = matching_rows.values[0]
        functions_1 = extract_function_results(output_1)
        functions_2 = extract_function_results(output_2)
        func_dict_2 = dict(functions_2)
        for func, result_1 in functions_1:
            if "post" in func:
                result_2 = func_dict_2.get(func, 'N/A')
                if not (result_1 == 'OK' and result_2 == 'OK'):
                    base_llm_spec = get_ref_annotations(ref_spec, func.split('_')[0])  # Correctly calling the function
                    llm_base_spec = extract_postcondition_specs(run, func)
                    comparison_data.append([run, func, 'base_llm', result_1, base_llm_spec])
                    comparison_data.append([run, func, 'llm_base', result_2, llm_base_spec])

    # Create a DataFrame from the comparison data
    comparison_df = pd.DataFrame(comparison_data, columns=['run', 'function', 'option', 'result', 'spec'])

    # Pivot the DataFrame to get the desired table format
    pivot_table = comparison_df.pivot_table(index='run', columns=['function', 'option'], values=['result', 'spec'], aggfunc=lambda x: ' '.join(x))

    # Flatten the MultiIndex columns
    pivot_table.columns = ['_'.join(col).strip() for col in pivot_table.columns.values]

    # Add the "refines all" column
    def check_refines_all(row):
        base_llm_ok = all(row.get(f'result_{func}_base_llm', 'N/A') == 'OK' for func in desired_functions)
        llm_base_ok = all(row.get(f'result_{func}_llm_base', 'N/A') == 'OK' for func in desired_functions)
        return 'Yes' if base_llm_ok and llm_base_ok else 'No'

    pivot_table['refines all'] = pivot_table.apply(check_refines_all, axis=1)

    # Save the pivot table to a new CSV file
    pivot_table.to_csv(comparison_table_file_path)
