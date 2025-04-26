import logging
import openai
import time
import sys
import re
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import os
import argparse
from dotenv import load_dotenv
import random
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

# Get API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Assistant IDs
ASSISTANT_IDS = {
    # "4.1-mini": "asst_zX20A8d9KI7rIK8lLoRTgHK2",
    # "4o_mini_single": "asst_qsyJh2SEYrnuYDiSs5NgdaXx",
    # "4o_mini_erc20": "asst_UWMifHspYEAkIGyWtHzkWiwD",
    # "4o_mini_erc721": "asst_WgHFp7pTzvutsqYE4zOGRAkc",
    # "4o_mini_erc1155": "asst_lOku2pOPoQ5Kdd2elUlglALf",
    # "4o_mini_erc721_1155": "asst_PgrUKdpgXSrVMyNqDm558yM2",
    # "4o_mini_erc20_1155": "asst_Lvr2qeZs6mMaUmcx40xJGlJS",
    # "4o_mini_erc20_721": "asst_jfH5JELAZxvA75FzwguaZpwL",
    # "4o_mini_erc20_721_1155": "asst_6QvHigvGMTBgAFdmU4gW3QEe",
    # "4o-mini-erc-1155-new": "asst_C2rYMIVOTAiRS2o17e94QGGR"
    "4o_mini": "asst_WRF0J9P9EiZ70DcntBSlapWB",
    "erc20-721-1155-4-o-mini": "asst_PDcb3OR1jFTRQNTFpZgdY9wt",
    "erc20-4-o-mini": "asst_H3M7A5dC7RXLbY49k0GhuCJS",
    "erc721-4-o-mini": "asst_aroYVGYOi4TB4PMsEgEzVfIS",
    "erc1155-4-o-mini": "asst_M0wMZRzDVSdby3CfuMLtgWsc",
    "erc20-721-4-o-mini": "asst_6o09ITzVveX37WwyVz42KhrY",
    "erc20-1155-4-o-mini": "asst_231yQkPjxDM9cBgo76IzQgdh",
    "erc721-1155-4-o-mini": "asst_Qs4WLHGBoP9fAMgbZ6y7gFrX",

}

# Paths to interface templates and EIP docs
INTERFACE_PATHS = {
    "erc20": "../assets/file_search/erc20_interface.md",
    "erc721": "../assets/file_search/erc721_interface.md",
    "erc1155": "../assets/file_search/erc1155_interface.md",
}

EIP_PATHS = {
    "erc20": "../assets/file_search/erc-20.md",
    "erc721": "../assets/file_search/erc-721.md",
    "erc1155": "../assets/file_search/erc-1155.md",
}

REFERENCE_SPEC_PATHS = {
    "erc20": "../assets/file_search/erc20_ref_spec.md",
    "erc721": "../assets/file_search/erc721_ref_spec.md",
    "erc1155": "../assets/file_search/erc1155_ref_spec.md",
    "": ""
}

INSTRUCTIONS = """
    Task:
        - You are given a smart contract interface and need to add formal verification conditions for each function.
        - Read the ERC documentation to understand the contract's behavior.
        - For each function, add postconditions by replacing "$ADD POSTCONDITION HERE" with one or more appropriate postconditions.
        - Use the solc-verify syntax: /// @notice postcondition [condition]
        
    Requirements:
        - Each function must have appropriate postconditions
        - Conditions must correctly represent the expected behavior per the ERC standard
        - Conditions for all functions must be consistent with each other
        - Annotate with postconditions above each function
        
    Verification Guidelines:
        - Use ONLY state variables exactly as declared in the contract (_balances, _allowed, _totalSupply)
        - Use ONLY parameter names exactly as they appear in function signatures (_to, _from, _value, etc.)
        - DO NOT create short variable names like 'bal', 't', 's', 'u', 'v', or 'rem'
        - For referencing previous state values, use __verifier_old_uint(stateVariable)
        - For functions that return success, handle both success and failure cases: (condition && success) || !success
        - For self-transfers, add special handling when sender == recipient
        - View functions should relate return values directly to state variables
        - Ensure consistency between related functions (e.g., transfer and transferFrom)
        
    Your task is to annotate this contract with proper solc-verify postconditions:
"""

# Initialize the global counter
interaction_counter = 0

# Initialize the global verification status
verification_status = []

def save_thread_to_file(thread_id, requested_type, context_str, assistant_key, run_number):
    """
    Save thread to a file organized in directories by request type and context
    
    Parameters:
        thread_id: The ID of the thread
        requested_type: The contract type being verified (e.g., "erc20")
        context_str: The context string with underscore separators (e.g., "erc721_erc1155")
        run_number: The run number
    """
    try:
        # Create directory structure
        combo_dir = f"threads_{assistant_key}/{requested_type}/{context_str}"
        os.makedirs(combo_dir, exist_ok=True)
        
        # Define filename
        filename = f"{combo_dir}/run_{run_number}.txt"
        
        # Retrieve all messages from the thread
        messages = openai.beta.threads.messages.list(
            thread_id=thread_id,
            order="asc"  # Get messages in chronological order
        )
        
        # Open file for writing
        with open(filename, 'w', encoding='utf-8') as file:
            # Write thread ID as header
            file.write(f"Thread ID: {thread_id}\n")
            file.write(f"Request Type: {requested_type}\n")
            file.write(f"Context: {context_str}\n")
            file.write(f"Run: {run_number}\n\n")
            
            # Write each message to the file
            for message in messages.data:
                role = message.role
                created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message.created_at))
                content = message.content[0].text.value if message.content else "(No content)"
                
                file.write(f"=== {role.upper()} [{created_time}] ===\n")
                file.write(f"{content}\n\n")
                
            file.write("=== END OF THREAD ===\n")
        
        print(f"Thread saved to {filename}")
        return True
    except Exception as e:
        print(f"ERROR saving thread to {filename}: {e}")
        return False

class Assistant:
    
    def __init__(self, id) -> None:
        self.id = id

class Thread:
    
    def __init__(self, assistant: Assistant) -> None:
        self.assistant = assistant
        self._thread = self._create_thread()
    
    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError, openai.APIConnectionError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    def _create_thread(self):
        try:
            return openai.beta.threads.create()
        except (openai.RateLimitError, openai.APIError, openai.APIConnectionError) as e:
            logging.error(f"API error: {str(e)}. Retrying...")
            raise
    
    @property
    def id(self):
        return self._thread.id
    
    def send_message(self, content: str) -> 'Interaction':
        interaction = Interaction(self, content)
        return interaction
    
    @property
    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError, openai.APIConnectionError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    def last_message(self) -> str:
        try:
            response = openai.beta.threads.messages.list(
                thread_id=self.id
            )
            # Returns last response from thread
            return response.data[0].content[0].text.value
        except (openai.RateLimitError, openai.APIError, openai.APIConnectionError) as e:
            logging.error(f"API error: {str(e)}. Retrying...")
            raise
        except Exception as e:
            logging.error(f"Unexpected error retrieving message: {str(e)}")
            return "Error retrieving message"

class Interaction:
    
    def __init__(self, thread: Thread, prompt: str) -> None:
        self.thread = thread
        self.prompt = prompt
        self._create_message()
        self._create_run()

    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError, openai.APIConnectionError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    def _create_message(self):
        try:
            openai.beta.threads.messages.create(
                thread_id = self.thread.id,
                role = "user",
                content = self.prompt
            )
        except (openai.RateLimitError, openai.APIError, openai.APIConnectionError) as e:
            logging.error(f"API error: {str(e)}. Retrying...")
            raise
    
    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError, openai.APIConnectionError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    def _create_run(self):
        try:
            self._run = openai.beta.threads.runs.create(
                thread_id = self.thread.id,
                assistant_id = self.thread.assistant.id,
            )
        except (openai.RateLimitError, openai.APIError, openai.APIConnectionError) as e:
            logging.error(f"API error: {str(e)}. Retrying...")
            raise
    
    @property
    def id(self):
        return self._run.id
    
    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError, openai.APIConnectionError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    def remote_sync(self):
        try:
            self._run = openai.beta.threads.runs.retrieve(
                thread_id = self.thread.id,
                run_id = self._run.id
            )
        except (openai.RateLimitError, openai.APIError, openai.APIConnectionError) as e:
            logging.error(f"API error: {str(e)}. Retrying...")
            raise
    
    @property
    def status(self):
        return self._run.status
    
    def await_for_response(self) -> str:
        status = self.status
        while (status != "completed"):
            try:
                self.remote_sync()
                status = self.status
                logging.info("awaiting for a response. status: " + str(status))
                
                if status == "failed" or status == "expired":
                    error_info = self._run.last_error if hasattr(self._run, 'last_error') else "Unknown error"
                    logging.error(f"Run {status}: {error_info}")
                    # Additional wait time if a run fails before retrying
                    time.sleep(10)
                    self._create_run()  # Create a new run after failure or expiration
                    status = self.status
                
                # Add a random sleep time to avoid hitting rate limits
                sleep_time = 2 + random.uniform(0, 1)
                time.sleep(sleep_time)
            except Exception as e:
                logging.error(f"Error during response wait: {str(e)}")
                time.sleep(5)  # Sleep before retry on general errors
        
        return self.thread.last_message

@dataclass
class VerificationResult:
    status: int
    output: str

class SolcVerifyWrapper:

    SOLC_VERIFY_CMD = "solc-verify.py"
    SPEC_FILE_PATH = '../temp/spec.sol'
    
    # Template paths for different ERC standards
    TEMPLATE_PATHS = {
        "erc20": './solc_verify_generator/ERC20/templates/imp_spec_merge.template',
        "erc721": './solc_verify_generator/ERC721/templates/imp_spec_merge.template',
        "erc1155": './solc_verify_generator/ERC1155/templates/imp_spec_merge.template',
    }
    
    # Merge paths for different ERC standards
    MERGE_PATHS = {
        "erc20": './solc_verify_generator/ERC20/imp/ERC20_merge.sol',
        "erc721": './solc_verify_generator/ERC721/imp/ERC721_merge.sol',
        "erc1155": './solc_verify_generator/ERC1155/imp/ERC1155_merge.sol',
    }

    @classmethod
    def call_solc(cls, file_path) -> VerificationResult:
        from subprocess import PIPE, run
        command = [cls.SOLC_VERIFY_CMD, file_path]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        return VerificationResult(result.returncode, result.stdout + result.stderr)
    
    @classmethod
    def verify(cls, soldity_spec_str: str, requested_type: str = "erc20") -> VerificationResult:
        """
        Parameters
            spec_str: Solidity code with only the function signatures
                annotated with solc-verify conditions
            requested_type: The ERC standard to verify ("erc20", "erc721", "erc1155")
        """
        # Use appropriate template and merge paths based on requested_type
        template_path = cls.TEMPLATE_PATHS.get(requested_type, cls.TEMPLATE_PATHS[requested_type])
        merge_path = cls.MERGE_PATHS.get(requested_type, cls.MERGE_PATHS[requested_type])

        
        # Make sure directories exist
        os.makedirs(os.path.dirname(cls.SPEC_FILE_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(merge_path), exist_ok=True)
        
        Utils.save_string_to_file(cls.SPEC_FILE_PATH, soldity_spec_str)
        from solc_verify_generator.main import generate_merge
        try:
            generate_merge(cls.SPEC_FILE_PATH, template_path, merge_path)
        except RuntimeError as e:
            return VerificationResult(*e.args)
        return cls.call_solc(merge_path)

class Utils:

    @staticmethod
    def extract_solidity_code(markdown_text):
        # Regex pattern to match code blocks with "solidity" as the language identifier
        pattern = r'```solidity\n(.*?)```'
        
        # Use re.DOTALL to match newline characters in the code block
        matches = re.findall(pattern, markdown_text, re.DOTALL)
        
        # Try to return first match
        try:
            return matches[0]
        except IndexError:
            return None
    
    @staticmethod
    def read_file_content(file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except IOError as e:
            print(f"An error occurred while reading the file {file_path}: {e}")
            return None

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
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        
        # Convert list of dictionaries to pandas DataFrame
        df = pd.DataFrame(results)
        
        try:
            # Save DataFrame to CSV
            df.to_csv(file_name, index=False)
            print(f"Results successfully saved to {file_name}")
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")

    @staticmethod
    def extract_content_from_markdown(file_path):
        """Extract code block or content from a markdown file"""
        if file_path == "":
            return ""
        content = Utils.read_file_content(file_path)
        if content:
            code_match = re.search(r'```solidity\n(.*?)```', content, re.DOTALL)
            if code_match:
                return code_match.group(1)
            return content
        return None

def load_example_contracts(context_types):
    """Load example reference specifications for the given context types"""
    examples = []
    
    for contract_type in context_types:
        if contract_type in REFERENCE_SPEC_PATHS:
            content = Utils.extract_content_from_markdown(REFERENCE_SPEC_PATHS[contract_type])
            if content:
                examples.append(f"```solidity\n{content}\n```")
    
    return examples

def load_target_interface(requested_type):
    """Load the interface that needs to be annotated"""
    if requested_type in INTERFACE_PATHS:
        return Utils.extract_content_from_markdown(INTERFACE_PATHS[requested_type])
    return None

def generate_prompt(requested_type, context_types):
    """
    Generate the prompt with examples based on the requested type and context types
    """
    # Load the target interface and eip document
    target_interface = load_target_interface(requested_type)
    eip_doc = Utils.extract_content_from_markdown(EIP_PATHS.get(requested_type, ""))
    
    # Build examples section from context types
    examples_text = ""
    for ctx_type in context_types:
        # Skip empty context
        if not ctx_type:
            continue
        
        ref_spec = Utils.extract_content_from_markdown(REFERENCE_SPEC_PATHS[ctx_type])
        if ref_spec:
            examples_text += f"\nExample ERC {ctx_type.upper()} specification:\n\n```solidity\n{ref_spec}\n```\n"
    
    # Build the prompt
    prompt = f"""
    {INSTRUCTIONS}
    
    ```solidity
    {target_interface}
    ```
    """
    
    if examples_text:
        prompt += f"\nHere are examples of similar ERC formal specifications:{examples_text}"
    
    if eip_doc:
        prompt += f"\nEIP {requested_type.upper()} markdown below:\n\n<eip>\n{eip_doc}\n</eip>\n"
    
    return prompt

def loop(thread: Thread, message: str, max_iterations=10, requested_type="erc20") -> bool:
    global interaction_counter
    interaction_counter += 1
    
    # Break the loop if the counter exceeds the max iterations
    if (interaction_counter > max_iterations):
        print(f"Counter exceeded {max_iterations}, breaking the loop")
        return False
    
    print('COUNTER', interaction_counter)
    interaction: Interaction = thread.send_message(message)
    response: str = interaction.await_for_response()
    solidity_code = Utils.extract_solidity_code(response)

    if not solidity_code:
        print("ERROR - No Solidity code found in the response.")
        return False
    try:
        # Pass the requested_type to the verify method
        verification_result: VerificationResult = SolcVerifyWrapper.verify(solidity_code, requested_type)
    except Exception as e:
        print(f"An error occurred during verification: {e}")
        return False

    if verification_result.status:
        global verification_status
        if "OK" in verification_result.output and "ERROR" in verification_result.output:
            verification_status.append(f'Interaction: {interaction_counter}\n{verification_result.output}\n')

        # Get the appropriate contract template based on requested_type
        target_interface = load_target_interface(requested_type)
        if not target_interface:
            print(f"ERROR - Interface template for {requested_type} not found.")
            return False

        instructions = f"""
        {INSTRUCTIONS}
        
        ```solidity
            {target_interface}
        ```
        """
        verification_result.output = instructions + verification_result.output
        logging.info("trying again with solc-verify output: " + str(verification_result.output))
        return loop(thread, verification_result.output, max_iterations, requested_type)
    else:
        print("Verified!")
        return solidity_code

def run_verification_process(requested_type, context_types, assistant_key="4o_mini", num_runs=10, max_iterations=10):
    """
    Run the verification process
    
    Parameters:
        requested_type: String indicating which contract to verify (e.g., "erc20")
        context_types: List of strings indicating which contract types to include as examples
        assistant_key: String key for selecting the assistant ID
        num_runs: Number of times to run the verification
        max_iterations: Maximum iterations per run
    """
    # Validate inputs
    if requested_type not in INTERFACE_PATHS:
        raise ValueError(f"Requested type '{requested_type}' not supported. Available types: {list(INTERFACE_PATHS.keys())}")
    
    for ctx_type in context_types:
        if ctx_type and ctx_type not in REFERENCE_SPEC_PATHS:
            raise ValueError(f"Context type '{ctx_type}' not supported. Available types: {list(REFERENCE_SPEC_PATHS.keys())}")
    
    if assistant_key not in ASSISTANT_IDS:
        raise ValueError(f"Assistant key '{assistant_key}' not found. Available keys: {list(ASSISTANT_IDS.keys())}")
    
    # Select the assistant ID
    assistant_id = ASSISTANT_IDS[assistant_key]
    
    # Generate the output file name - filter out empty context types
    valid_contexts = [ct for ct in context_types if ct]
    context_str = '_'.join(valid_contexts) if valid_contexts else "none"
    file_prefix = f"{requested_type}_[{context_str}]"
    
    # Create results directory
    results_dir = f"results_{assistant_key}/{requested_type}/{context_str}"
    os.makedirs(results_dir, exist_ok=True)
    
    # Generate the prompt
    prompt = generate_prompt(requested_type, context_types)
    
    results = []
    for i in range(num_runs):
        global interaction_counter
        global verification_status
        
        interaction_counter = 0 
        start_time = time.time()
        assistant = Assistant(assistant_id)
        thread = Thread(assistant)
        result = loop(thread, prompt, max_iterations, requested_type)
        end_time = time.time()
        duration = end_time - start_time
        annotated_contract = ""

        # Save thread to file
        save_result = save_thread_to_file(thread.id, requested_type, context_str, assistant_key, i+1)
        if not save_result:
            print(f"WARNING: Failed to save thread file for run {i+1}")
        
        if result:
            annotated_contract = result

        results.append({
            "run": i + 1,
            "time_taken": duration,
            "iterations": interaction_counter - 1,
            "verified": result != False,
            "annotated_contract": annotated_contract,
            "status": verification_status
        })
        verification_status = []
    
    # Save results to CSV
    csv_filename = f"{results_dir}/{file_prefix}.csv"
    Utils.save_results_to_csv(csv_filename, results)
    return results

def main():
    parser = argparse.ArgumentParser(description='Run contract verification with different contexts')
    parser.add_argument('--requested', type=str, required=True, 
                        choices=['erc20', 'erc721', 'erc1155'],
                        help='The contract type to verify')
    parser.add_argument('--context', type=str, required=True,
                        help='Comma-separated list of context contract types (e.g., "erc20,erc721,erc1155")')
    parser.add_argument('--assistant', type=str, default='4o_mini',
                        choices=['4o_mini', 'erc20-721-1155-4-o-mini', 'erc20-4-o-mini', 'erc721-4-o-mini', 'erc1155-4-o-mini', 'erc20-721-4-o-mini', 'erc20-1155-4-o-mini', 'erc721-1155-4-o-mini'],
                        help='The assistant to use')
    parser.add_argument('--runs', type=int, default=10,
                        help='Number of verification runs')
    parser.add_argument('--max-iterations', type=int, default=10,
                        help='Maximum iterations per run')
    
    args = parser.parse_args()
    
    # Parse the context types
    if not args.context.strip():
        # Handle empty context string
        context_types = [""]
    else:
        context_types = [ctx.strip().lower() for ctx in args.context.split(',')]
    
    # Run the verification process
    run_verification_process(
        requested_type=args.requested.lower(),
        context_types=context_types,
        assistant_key=args.assistant,
        num_runs=args.runs,
        max_iterations=args.max_iterations
    )

if __name__ == "__main__":
    main() 