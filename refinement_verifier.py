import logging
import sys
import pandas as pd
from dataclasses import dataclass
from typing import List

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Initialize the global verification status
verification_status = []

@dataclass
class VerificationResult:
    status: int
    output: str

class SolcVerifyWrapper:

    SOLC_VERIFY_CMD = "solc-verify.py"
    SPEC_FILE_PATH = './temp/spec.sol'
    # ERC20_TEMPLATE_PATH = './solc_verify_generator/ERC20/templates/spec_refinement_base_llm.template'
    # ERC20_TEMPLATE_PATH = './solc_verify_generator/ERC20/templates/spec_refinement_llm_base.template'
    ERC20_TEMPLATE_PATH = './solc_verify_generator/ERC20/templates/spec_refinement_trivial.template'
    ERC20_MERGE_PATH = './solc_verify_generator/ERC20/imp/ERC20_merge.sol'

    ERC721_TEMPLATE_PATH = './solc_verify_generator/ERC721/templates/spec_refinement_base_llm.template'
    ERC721_MERGE_PATH = './solc_verify_generator/ERC721/imp/ERC721_merge.sol'

    @classmethod
    def call_solc(cls, file_path) -> VerificationResult:
        from subprocess import PIPE, run
        command = [cls.SOLC_VERIFY_CMD, file_path]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        return VerificationResult(result.returncode, result.stdout + result.stderr)
    
    @classmethod
    def verify(cls, solidity_spec_str: str, option: str) -> VerificationResult:
        """
        Parameters
            solidity_spec_str: Solidity code with only the function signatures
            annotated with solc-verify conditions
        """
        Utils.save_string_to_file(cls.SPEC_FILE_PATH, solidity_spec_str)
        from solc_verify_generator.main import generate_merge
        try:
            generate_merge(cls.SPEC_FILE_PATH, cls.ERC721_TEMPLATE_PATH, cls.ERC721_MERGE_PATH, option, prefix='con')
        except RuntimeError as e:
            return VerificationResult(*e.args)
        return cls.call_solc(cls.ERC721_MERGE_PATH)

class Utils:

    @staticmethod
    def save_string_to_file(file_name, content):
        try:
            with open(file_name, 'w') as file:
                file.write(content)
            print(f"Content successfully saved to {file_name}")
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")

    @staticmethod
    def save_results_to_csv(file_name: str, results: List[dict]):
        # Convert list of dictionaries to pandas DataFrame
        df = pd.DataFrame(results)
        
        try:
            # Save DataFrame to CSV
            df.to_csv(file_name, index=False)
            print(f"Results successfully saved to {file_name}")
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")
    
    @staticmethod
    def extract_annotated_code_from_csv(csv_file: str) -> pd.DataFrame:
        # Read the CSV file
        df = pd.read_csv(csv_file)

        # Filter rows where 'annotated_contract' column has a value
        filtered_df = df[df['annotated_contract'].notna()]

        # Create a new DataFrame with 'run' and 'annotated_contract' columns
        result_df = filtered_df[['run', 'annotated_contract']]
        return result_df

def run_refinement_verification_process(experiment_name: str, option: str):
    # Extract annotated code from CSV
    annotated_code_df = Utils.extract_annotated_code_from_csv(f'./experiments/outputs/{experiment_name}/{experiment_name}.csv')
    
    verification_results = []

    for index, row in annotated_code_df.iterrows():
        run_number = row['run']
        solidity_code = row['annotated_contract']

        try:
            verification_result = SolcVerifyWrapper.verify(solidity_code, option)
        except Exception as e:
            print(f"An error occurred during verification for run {run_number}: {e}")
            verification_results.append({
                'run': run_number,
                'status': -1,
                'output': str(e)
            })
            continue

        verification_results.append({
            'run': run_number,
            'status': verification_result.status,
            'output': verification_result.output
        })

    # Save all results to a CSV file
    Utils.save_results_to_csv(f'refinement_check_{experiment_name}_{option}.csv', verification_results)

experiments_list_ERC20 = ['erc20_[20_721_1155]', 'erc20_[20_721]', 'erc20_[20_1155]', 'erc20_[20]', 'erc20_[721_1155]', 'erc20_[721]', 'erc20_[1155]', 'erc_20_[]']

experiments_list_ERC721 = ['erc721_[721_20_1155]', 'erc721_[721_20]', 'erc721_[20_1155]', 'erc721_[20]', 'erc721_[721_1155]', 'erc721_[721]', 'erc721_[1155]', 'erc721_[]']

# Run the verification process
for experiment in experiments_list_ERC721:
    print(f"Running verification process for {experiment}")
    run_refinement_verification_process(experiment, option='base_llm')
