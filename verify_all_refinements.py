import logging
import sys
import re
import pandas as pd
from dataclasses import dataclass
from typing import List
import os
import glob # Import glob

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@dataclass
class VerificationResult:
    status: int
    output: str

class SolcVerifyWrapper:

    SOLC_VERIFY_CMD = "solc-verify.py"
    SPEC_FILE_PATH = './temp/spec.sol'
    
    TEMPLATE_PATHS = {
        "erc20": './experiments/solc_verify_generator/ERC20/templates/spec_refinement.template',
        "erc721": './experiments/solc_verify_generator/ERC721/templates/spec_refinement.template',
        "erc1155": './experiments/solc_verify_generator/ERC1155/templates/spec_refinement.template'
    }
    MERGE_PATHS = {
        "erc20": './experiments/solc_verify_generator/ERC20/imp/ERC20_merge.sol',
        "erc721": './experiments/solc_verify_generator/ERC721/imp/ERC721_merge.sol',
        "erc1155": './experiments/solc_verify_generator/ERC1155/imp/ERC1155_merge.sol'
    }

    @classmethod
    def call_solc(cls, file_path) -> VerificationResult:
        from subprocess import PIPE, run
        os.makedirs(os.path.dirname(cls.SPEC_FILE_PATH), exist_ok=True)
        command = [cls.SOLC_VERIFY_CMD, file_path]
        try:
            result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, check=False)
            return VerificationResult(result.returncode, result.stdout + result.stderr)
        except FileNotFoundError:
            logging.error(f"Command not found: {cls.SOLC_VERIFY_CMD}. Make sure solc-verify.py is installed and in PATH.")
            return VerificationResult(-1, f"Command not found: {cls.SOLC_VERIFY_CMD}")
        except Exception as e:
             logging.error(f"Error running solc-verify: {e}")
             return VerificationResult(-1, f"Error running solc-verify: {e}")

    @classmethod
    def verify(cls, solidity_spec_str: str, erc_type: str) -> VerificationResult:
        if erc_type not in cls.TEMPLATE_PATHS or erc_type not in cls.MERGE_PATHS:
            logging.error(f"Unsupported ERC type for refinement verification: {erc_type}")
            return VerificationResult(-1, f"Unsupported ERC type: {erc_type}")

        template_path = cls.TEMPLATE_PATHS[erc_type]
        merge_path = cls.MERGE_PATHS[erc_type]

        os.makedirs(os.path.dirname(merge_path), exist_ok=True)

        if not os.path.exists(template_path):
             logging.error(f"Refinement template not found: {template_path}")
             return VerificationResult(-1, f"Template not found: {template_path}")

        Utils.save_string_to_file(cls.SPEC_FILE_PATH, solidity_spec_str)
        
        try:
            # Assuming generate_merge is correctly located relative to this script
            # Adjust import path if necessary
            from experiments.solc_verify_generator.main import generate_merge 
        except ImportError:
            logging.error("Module 'experiments.solc_verify_generator.main' not found. Check PYTHONPATH.")
            return VerificationResult(-1, "solc_verify_generator not found")
        
        try:
            generate_merge(cls.SPEC_FILE_PATH, template_path, merge_path, prefix='nw')
        except RuntimeError as e:
            # Specific error from generate_merge (like solc not found)
            logging.error(f"RuntimeError during generate_merge for {erc_type}: {e}")
            # Return status reflecting generator error, e.g., -2
            return VerificationResult(-2, f"Generator Error: {e}") 
        except Exception as e:
             logging.error(f"Unexpected error during generate_merge for {erc_type}: {e}")
             return VerificationResult(-1, f"Unexpected error in generate_merge: {e}")
             
        return cls.call_solc(merge_path)

class Utils:

    @staticmethod
    def save_string_to_file(file_name, content):
        try:
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            with open(file_name, 'w') as file:
                file.write(content)
        except IOError as e:
            logging.error(f"An error occurred while writing to the file {file_name}: {e}")

    @staticmethod
    def save_results_to_csv(file_name: str, results: List[dict]):
        if not results:
            logging.warning("No results to save.")
            return
        df = pd.DataFrame(results)
        try:
            df.to_csv(file_name, index=False)
            logging.info(f"Results successfully saved to {file_name}")
        except IOError as e:
            logging.error(f"An error occurred while writing to the file {file_name}: {e}")
    
    @staticmethod
    def extract_annotated_code_from_csv(csv_file: str) -> pd.DataFrame:
        if not os.path.exists(csv_file):
            # Don't log warning here, handled in the main loop
            # logging.warning(f"Input CSV file not found: {csv_file}")
            return pd.DataFrame() 
        try:
            df = pd.read_csv(csv_file)
            # Ensure column exists before filtering
            if 'annotated_contract' not in df.columns:
                logging.warning(f"'annotated_contract' column not found in {csv_file}. Skipping.")
                return pd.DataFrame()
            if 'run' not in df.columns:
                 logging.warning(f"'run' column not found in {csv_file}. Skipping.")
                 return pd.DataFrame()
                 
            # Convert to string before filtering, handle potential non-string data causing errors
            df['annotated_contract'] = df['annotated_contract'].astype(str)
            filtered_df = df[df['annotated_contract'].notna() & df['annotated_contract'].str.strip().ne('')]
            result_df = filtered_df[['run', 'annotated_contract']].copy()
            return result_df
        except Exception as e:
            logging.error(f"Error reading or processing CSV file {csv_file}: {e}")
            return pd.DataFrame()

def run_refinement_verification_process():
    results_base_dir = "experiments/results"
    all_verification_results = []

    logging.info(f"Starting refinement verification for all models and contexts...")

    # Iterate through assistant model directories
    assistant_dirs = glob.glob(os.path.join(results_base_dir, "results_*"))
    for assistant_dir in assistant_dirs:
        assistant_model = os.path.basename(assistant_dir).replace("results_", "")
        logging.info(f"== Processing Model: {assistant_model} ==")

        # Iterate through requested type directories (erc20, erc721, etc.)
        requested_type_dirs = glob.glob(os.path.join(assistant_dir, "*"))
        for req_type_dir in requested_type_dirs:
            if not os.path.isdir(req_type_dir):
                continue
            requested_type = os.path.basename(req_type_dir) # This is the ERC type
            
            # Check if requested_type is one we can verify refinement for
            if requested_type not in SolcVerifyWrapper.TEMPLATE_PATHS:
                 logging.warning(f"Skipping directory {req_type_dir}, not a recognized ERC type for refinement.")
                 continue

            # Iterate through context directories (none, erc20, etc.)
            context_dirs = glob.glob(os.path.join(req_type_dir, "*"))
            for ctx_dir in context_dirs:
                if not os.path.isdir(ctx_dir):
                    continue
                context_type_name = os.path.basename(ctx_dir) # e.g., erc721_erc1155, none
                
                logging.info(f"-- Processing Type: {requested_type.upper()}, Context: {context_type_name} --")

                # Construct the expected CSV file name
                context_in_filename = context_type_name.replace('_', ',') if context_type_name != 'none' else 'none'
                context_in_filename_alt = context_type_name # Handle potential old naming
                csv_pattern = f"{requested_type}_[{context_in_filename}].csv"
                csv_pattern_alt = f"{requested_type}_[{context_in_filename_alt}].csv"
                csv_path = os.path.join(ctx_dir, csv_pattern)
                csv_path_alt = os.path.join(ctx_dir, csv_pattern_alt)
                actual_csv_path = None
                if os.path.exists(csv_path):
                    actual_csv_path = csv_path
                elif os.path.exists(csv_path_alt):
                    actual_csv_path = csv_path_alt
                
                if not actual_csv_path:
                    logging.warning(f"CSV file not found for model={assistant_model}, type={requested_type}, context={context_type_name}. Searched: {csv_pattern}, {csv_pattern_alt}")
                    continue
                    
                annotated_code_df = Utils.extract_annotated_code_from_csv(actual_csv_path)
                
                if annotated_code_df.empty:
                    # Warning already logged by extract function if file not found
                    if os.path.exists(actual_csv_path):
                        logging.warning(f"No valid annotated contracts found in {actual_csv_path}. Skipping.")
                    continue
                
                logging.info(f"Found {len(annotated_code_df)} contracts to verify in {os.path.basename(actual_csv_path)}.")

                for index, row in annotated_code_df.iterrows():
                    run_number = row['run']
                    solidity_code = row['annotated_contract']
                    
                    if not isinstance(solidity_code, str) or not solidity_code.strip():
                        logging.warning(f"Skipping run {run_number} for {assistant_model}/{requested_type}/{context_type_name} due to empty/invalid code.")
                        continue

                    try:
                        # Pass the requested_type as erc_type for refinement check
                        verification_result = SolcVerifyWrapper.verify(solidity_code, requested_type)
                    except Exception as e:
                        logging.error(f"Unexpected error during verification for run {run_number} ({assistant_model}/{requested_type}/{context_type_name}): {e}")
                        verification_result = VerificationResult(-1, f"Script Error: {e}")

                    all_verification_results.append({
                        'assistant_model': assistant_model,
                        'requested_type': requested_type,
                        'context': context_type_name,
                        'run': run_number,
                        'refinement_status': verification_result.status, # Renamed for clarity
                        'refinement_output': verification_result.output  # Renamed for clarity
                    })

    # Save all combined results to a new CSV file
    Utils.save_results_to_csv('all_refinement_results.csv', all_verification_results)
    logging.info("--- Refinement verification process completed. ---")

# Run the verification process
if __name__ == "__main__":
    run_refinement_verification_process() 