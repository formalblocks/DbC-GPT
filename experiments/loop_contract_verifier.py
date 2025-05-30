"""
Smart Contract Verification System

This script implements a system for verifying smart contract specifications using OpenAI's API
and solc-verify. It handles the verification process for ERC20, ERC721, and ERC1155 token standards.

Key Features:
- Automated verification of smart contract specifications
- Support for multiple ERC token standards
- Parallel processing of verification runs
- Detailed logging and result tracking
- Error handling and retry mechanisms
"""

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
import tempfile
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed

# Load environment variables and configure API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# OpenAI Assistant IDs for different model configurations
# ASSISTANT_IDS = {
#     "4o-mini": "asst_uMJ30gjHtG1VIBnqJFKpR6gm",
#     "erc-1155-001-3-16": "asst_uMYPmlxmT9ppnPKZQ8ZTyfYb",
#     "erc-1155-005-3-16": "asst_nsa6edZTsNNWj4SBFSPeFYPq",
#     "erc-1155-010-3-16": "asst_BsZDuAHsmBfrlimXinHt96Cb",
#     "erc-1155-001-5-16": "asst_Mkq2y7mUxjusd47rPSGXrrCM",
#     "erc-1155-005-5-16": "asst_8ZL8R3zwXyurmmjkFX14kcuS",
#     "erc-1155-010-5-16": "asst_wOnRMvawOAI1sO83lfRWWBLu",
#     "erc-1155-001-7-16": "asst_sZLa64l2Xrb1zNhogDl7RXap",
#     "erc-1155-005-7-16": "asst_m8y0QMRJVtvDRYcPZLVIcHW6",
#     "erc-1155-010-7-16": "asst_MRg3E5ds4NRfFKPTPqLsx9rS",
#     "erc-20-001-3-16": "asst_wn9R7oQTUr60VpfvvaZ5asBa",
#     "erc-20-005-3-16": "asst_3pHhhAMFwXi9JCVPOvftRQJU",
#     "erc-20-010-3-16": "asst_OZk81q3HVr1mrGXCfOiVKaku",
#     "erc-20-001-5-16": "asst_M6Q7TjZTC5wLDXdA88kCre7o",
#     "erc-20-005-5-16": "asst_XFsmrlLmDMcbQ8uPeG4EVGA0",
#     "erc-20-010-5-16": "asst_d1TPZLOP9HSmJq0va4vD2rcW",
#     "erc-20-001-7-16": "asst_M8jjeryyXFYdnGSiQuyOB4ij",
#     "erc-20-005-7-16": "asst_w98aowF6diNCOJxaM9li84Hi",
#     "erc-20-010-7-16": "asst_FEGX60kN1RpiFGQP3CaQI6vO",
#     "erc-721-001-3-16": "asst_nPqcpEo7lJnH4nmX9sNSBmfX",
#     "erc-721-005-3-16": "asst_wipOM1IWYzuK1jyqwqRJmDic",
#     "erc-721-010-3-16": "asst_MnKQphy1oPqu7QUWah63JFJk",
#     "erc-721-001-5-16": "asst_kjoZHBonf5tXKpuiJ6Z4T3Gv",
#     "erc-721-005-5-16": "asst_u2r0eDkkqERqTmOY5soRPU7n",
#     "erc-721-010-5-16": "asst_YNv1CBWWYuzTg4D7rRK7JVL6",
#     "erc-721-001-7-16": "asst_odutVf248qCN3C9zlFKLNd9a",
#     "erc-721-005-7-16": "asst_HdOeD4DYTJAHfluUAeu6cwNJ",
#     "erc-721-010-7-16": "asst_JNnQFWooGybyzS3juCJT5GQg",
# }

ASSISTANT_IDS = {
    "4o-mini": "asst_uMJ30gjHtG1VIBnqJFKpR6gm",
    "erc-1155-001-5-16": "asst_Mkq2y7mUxjusd47rPSGXrrCM",
    "erc-20-001-5-16": "asst_M6Q7TjZTC5wLDXdA88kCre7o",
    "erc-721-001-5-16": "asst_kjoZHBonf5tXKpuiJ6Z4T3Gv",
    "erc-20-721-001-5-16": "asst_waYnC3Fcp2JVmsShGUkz9o5y",
    "erc-20-1155-001-5-16": "asst_xiVobEjKhGFhIFIPw3EySfsf",
    "erc-721-1155-001-5-16": "asst_YsmuTcAJW179xCxAufROe2k1",
    "erc-20-721-1155-001-5-16": "asst_0JMCtwBpCeOHZ1lWmy4nErjB",
}

# File paths for contract interfaces and documentation
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

# Instructions for the AI model to generate contract specifications
INSTRUCTIONS = """
Task:
    - You are given a smart contract interface and need to add formal postconditions to a function using solc-verify syntax (`/// @notice postcondition condition`). Postconditions must not end with a semicolon (";").
    - You MUST use the EIP documentation below to understand the required behavior.
    - Replace `$ADD POSTCONDITION HERE` with appropriate postconditions above each function. Postconditions placed below the function signature are invalid. For instance:
    ```/// @notice postcondition condition1\\n
    /// @notice postcondition condition2\\n
    function foo(uint256 bar, address par) public;```
    - Return the entire contract interface, inside ```solidity``` tags, with no implementation code, just the interface with the postconditions added and function signatures.

Requirements:
    - Ensure conditions correctly represent the expected state changes and return values.
    - View functions should relate return values directly to state variables.
    - Postconditions MUST ONLY use state variables exactly as declared. Referencing undeclared variables will fail if they aren't in the contract. For instance, a state variable `uint256 var` can be referenced as `var` only.
    - Postconditions MUST ONLY use parameter names exactly as they appear in function signatures. For instance, `function foo(uint256 bar,  address par)` has parameter names `bar` and `par` only. 
    - Use `__verifier_old_uint(stateVariable)` or `__verifier_old_bool(stateVariable)` to reference values from the start of the function execution.
    - A quantified postcondition MUST start with `forall`. For instance, a quantified postcondition look like `/// @notice postcondition forall (uint x) condition`. Without the `forall` at the beginning, the postcondition is invalid.
    - YOU MUST SPECIFY THE RANGE when postconditions quantify over arrays. For example, for array `arr` a postcondition quantification would look like `/// @notice postcondition forall (uint i) !(0 <= i && i < arr.length) || condition`. Without the range, the postcondition is likely to be invalid.
    - The implication operator "==>" is not valid in solc-verify notation, so it must appear NOWHERE in a postcondition. For instance, a postcondition of the form `/// @notice postcondition condition1 ==> condition2` is invalid. Similarly, a postcondition of the form `/// @notice postcondition (forall uint x) condition1 ==> condition2` is also invalid. You can use instead the notation `!(condition) || condition2` to simulate the implication operator. For instance, `/// @notice postcondition (forall uint x) condition1 ==> condition2` can be written as `/// @notice postcondition !(condition1) || condition2`.
    - Return the entire contract interface, inside ```solidity``` tags, with no implementation code, just the interface with the postconditions added and function signatures.

Your task is to annotate the functions in the contract below:
"""

# Global state for tracking verification progress
interaction_counter = 0
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
        combo_dir = f"threads_entire_contract/{assistant_key}/{requested_type}/{context_str}"
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
    """Represents the result of a contract verification attempt"""
    status: int  # 0 for success, non-zero for failure
    output: str  # Verification output or error message

class SolcVerifyWrapper:
    """Wrapper class for interacting with solc-verify tool"""
    
    SOLC_VERIFY_CMD = "solc-verify.py"
    SOLC_VERIFY_TIMEOUT = int(os.getenv("SOLC_VERIFY_TIMEOUT", "120"))

    # Template and merge file paths for different ERC standards
    TEMPLATE_PATHS = {
        "erc20": './solc_verify_generator/ERC20/templates/imp_spec_merge.template',
        "erc721": './solc_verify_generator/ERC721/templates/imp_spec_merge.template',
        "erc1155": './solc_verify_generator/ERC1155/templates/imp_spec_merge.template',
    }
    
    MERGE_PATHS = {
        "erc20": './solc_verify_generator/ERC20/imp/ERC20_merge.sol',
        "erc721": './solc_verify_generator/ERC721/imp/ERC721_merge.sol',
        "erc1155": './solc_verify_generator/ERC1155/imp/ERC1155_merge.sol',
    }

    @classmethod
    def call_solc(cls, file_path) -> VerificationResult:
        from subprocess import PIPE, run, TimeoutExpired
        timeout = cls.SOLC_VERIFY_TIMEOUT
        # Pass --timeout to solc-verify and also enforce Python-level kill
        command = [
            cls.SOLC_VERIFY_CMD,
            "--timeout", str(timeout),
            "--show-warnings",
            file_path
        ]
        logging.info(f"Invoking solc-verify: {' '.join(command)}")

        try:
            result = run(
                command,
                stdout=PIPE, stderr=PIPE,
                universal_newlines=True,
                check=False,
                timeout=timeout + 10
            )
            return VerificationResult(result.returncode, result.stdout + result.stderr)
        except FileNotFoundError:
            logging.error(f"Command not found: {cls.SOLC_VERIFY_CMD}. Make sure solc-verify.py is installed and in PATH.")
            return VerificationResult(-1, f"Command not found: {cls.SOLC_VERIFY_CMD}")
        except TimeoutExpired:
            logging.error(f"solc-verify timed out after {timeout}s")
            return VerificationResult(-1, f"solc-verify TIMEOUT after {timeout}s")
        except Exception as e:
            logging.error(f"Error running solc-verify: {e} on file {file_path}")
            return VerificationResult(-1, f"Error running solc-verify: {e}")

    
    @classmethod
    def verify(cls,
               solidity_spec_str: str,
               requested_type: str = "erc20") -> VerificationResult:
        
        original_merge_file_path = cls.MERGE_PATHS.get(requested_type)
        if not original_merge_file_path:
            raise ValueError(f"Unsupported requested_type for SolcVerifyWrapper: {requested_type} - merge path not found.")
        dependency_source_dir = os.path.dirname(original_merge_file_path)
        if not os.path.isdir(dependency_source_dir):
             logging.warning(f"Dependency source directory not found or not a directory: {dependency_source_dir}") # Changed to warning
             # Proceeding as some simple cases might not have external dependencies in that specific dir.

        workdir = tempfile.mkdtemp(prefix="solc_verify_")
        try:
            spec_file_in_workdir  = os.path.join(workdir, "spec.sol")
            merge_file_basename = os.path.basename(original_merge_file_path)
            merge_file_in_workdir = os.path.join(workdir, merge_file_basename)
            
            Utils.save_string_to_file(spec_file_in_workdir, solidity_spec_str)

            # Create the 'temp/' subdirectory inside workdir for AST output by solc_verify_generator.main.call_solc
            os.makedirs(os.path.join(workdir, "temp"), exist_ok=True)

            # Copy dependencies from dependency_source_dir to workdir
            if os.path.isdir(dependency_source_dir): # Check again before copying
                for item_name in os.listdir(dependency_source_dir):
                    source_item_path = os.path.join(dependency_source_dir, item_name)
                    dest_item_path = os.path.join(workdir, item_name)
                    
                    if os.path.isdir(source_item_path):
                        shutil.copytree(source_item_path, dest_item_path)
                    elif item_name.endswith(".sol") or os.path.isfile(source_item_path): # Copy .sol files and other files
                        shutil.copy2(source_item_path, dest_item_path)
                logging.info(f"Copied dependencies from {dependency_source_dir} to {workdir}")

            from solc_verify_generator.main import generate_merge # Keep import here to avoid issues if this class moves
            
            original_cwd = os.getcwd()
            os.chdir(workdir)
            try:
                # Template path should be resolved relative to the original CWD or be absolute.
                absolute_template_path = os.path.abspath(os.path.join(original_cwd, cls.TEMPLATE_PATHS[requested_type]))
                if not os.path.exists(absolute_template_path):
                    logging.error(f"Template file not found: {absolute_template_path}")
                    return VerificationResult(-1, f"Template file not found: {absolute_template_path}")

                # generate_merge will operate in workdir. 
                # spec_file_in_workdir is relative to new CWD (workdir) so just "spec.sol"
                # merge_file_in_workdir is also relative, e.g. "ERC1155_merge.sol"
                generate_merge(
                  "spec.sol", 
                  absolute_template_path, 
                  merge_file_basename 
                )
            except RuntimeError as e:
                 # generate_merge raises RuntimeError if solc fails on spec
                logging.error(f"Error during generate_merge: {e}")
                # e.args already contains (returncode, output)
                return VerificationResult(e.args[0] if len(e.args) > 0 else -1, str(e.args[1] if len(e.args) > 1 else e))
            except Exception as e:
                logging.error(f"Unexpected error during generate_merge: {e}")
                return VerificationResult(-1, f"Unexpected error during generate_merge: {e}")
            finally:
                os.chdir(original_cwd)

            # Execute solc-verify in the working directory to ensure proper path resolution
            # The tool requires relative paths to be resolved from the working directory
            os.chdir(workdir)
            try:
                verification_result = cls.call_solc(merge_file_basename)
            finally:
                os.chdir(original_cwd)
            
            return verification_result
        finally:
            shutil.rmtree(workdir, ignore_errors=True)


class Utils:
    """Utility class for file operations and data processing"""
    
    @staticmethod
    def extract_solidity_code(markdown_text):
        """Extract Solidity code from markdown text"""
        pattern = r'```solidity\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)
        try:
            return matches[0]
        except IndexError:
            return None
    
    @staticmethod
    def read_file_content(file_path):
        """Read content from a file"""
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except IOError as e:
            print(f"An error occurred while reading the file {file_path}: {e}")
            return None

    @staticmethod
    def save_string_to_file(file_name, content):
        """Save string content to a file"""
        try:
            with open(file_name, 'w') as file:
                file.write(content)
            print(f"Content successfully saved to {file_name}")
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")

    @staticmethod
    def save_results_to_csv(file_name: str, results: List[dict]):
        """Save verification results to a CSV file"""
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        df = pd.DataFrame(results)
        try:
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
    global verification_status

    # Store the initial prompt if it's the first interaction
    initial_prompt = ""
    if interaction_counter == 0:
        initial_prompt = message

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
        feedback_prompt = "Please provide the full Solidity code block with your annotations. Your previous response did not contain a ```solidity ... ``` block."
        return loop(thread, feedback_prompt, max_iterations, requested_type)

    try:
        # Pass the requested_type to the verify method
        verification_result: VerificationResult = SolcVerifyWrapper.verify(solidity_code, requested_type)
    except Exception as e:
        print(f"An error occurred during verification: {e}")
        return False

    if verification_result.status != 0: # Check if status is non-zero (indicates an error)
        error_output = verification_result.output
        if interaction_counter > 1 and "OK" in error_output and "ERROR" in error_output:
            verification_status.append(f'Interaction: {interaction_counter}\n{error_output}\n')


        # Load the target interface again to provide context
        target_interface = load_target_interface(requested_type)
        if not target_interface:
            print(f"ERROR - Interface template for {requested_type} not found.")
            return False # Cannot proceed without the interface

        feedback_prompt = f"""
            Verification failed, the verifier found the following errors:
            ```
            {error_output}
            ```

            Can you fix the specification accordingly?
            """

        logging.info("Verification failed. Trying again with specific error feedback.")
        logging.info(f"ERROR OUTPUT: \n\n {error_output} \n\n END ERROR OUTPUT")
        return loop(thread, feedback_prompt, max_iterations, requested_type)
    else:
        logging.info("########################################################")
        logging.info("VERIFIED SUCCESSFULLY!")
        logging.info("########################################################")
        return solidity_code

def run_verification_process(requested_type, context_types, assistant_key="4o-mini", num_runs=10, max_iterations=10):
    # Argument checks and initial setup
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    if assistant_key not in ASSISTANT_IDS:
        raise ValueError(f"Assistant key '{assistant_key}' not found in ASSISTANT_IDS.")
    if requested_type not in INTERFACE_PATHS:
        raise ValueError(f"Requested type '{requested_type}' not found in INTERFACE_PATHS.")
    # Ensure os is imported if not already at the top level of the module
    import os 
    # Validate context types
    for ct in context_types:
        if ct and ct not in REFERENCE_SPEC_PATHS: # Allow empty string for "none" context
            raise ValueError(f"Context type '{ct}' not found in REFERENCE_SPEC_PATHS.")

    logging.info(f"Running verification for: Requested Type='{requested_type}', Context Types={context_types}, Assistant Key='{assistant_key}', Target Runs={num_runs}, Max Iterations={max_iterations}")

    prompt = generate_prompt(requested_type, context_types)
    context_str = "_".join([c for c in context_types if c]) if any(c for c in context_types) else "none" # Ensure "none" if context_types is empty or just [""]
    
    results_base_dir = "results_entire_contract"
    results_dir = os.path.join(results_base_dir, assistant_key, requested_type, context_str)
    os.makedirs(results_dir, exist_ok=True)
    
    csv_file_name = f"{requested_type}_[{context_str if context_str else 'none'}].csv"
    csv_file_path = os.path.join(results_dir, csv_file_name)

    thread_base_dir = "threads_loop_contract" 
    
    futures = []
    # Avoid oversubscription: do inner runs sequentially by default
    import multiprocessing
    inner_workers = int(os.getenv("INNER_MAX_WORKERS", "1"))
    with ProcessPoolExecutor(max_workers=inner_workers) as executor:
        for i in range(num_runs):
            futures.append(
                executor.submit(
                    _one_run,
                    i,
                    requested_type,
                    context_types,
                    assistant_key,
                    max_iterations,
                    prompt,
                    ASSISTANT_IDS[assistant_key],
                    thread_base_dir
                )
            )

    new_results_list = []
    for fut in as_completed(futures):
        try:
            result_dict = fut.result()
            new_results_list.append(result_dict)
        except Exception as e:
            logging.error(f"A run generated an exception: {e}", exc_info=True)
            new_results_list.append({
                "run": -1, # Placeholder for failed run index
                "time_taken": 0,
                "iterations": 0,
                "verified": "ERROR_IN_FUTURE",
                "annotated_contract": str(e),
                "status": [{"error": str(e)}]
            })

    # Create DataFrame from results
    results_df = pd.DataFrame(new_results_list)
    
    # Sort by run index to keep CSV ordered
    if 'run' in results_df.columns:
        results_df = results_df.sort_values(by='run').reset_index(drop=True)
    
    Utils.save_results_to_csv(csv_file_path, results_df.to_dict(orient='records'))
    logging.info(f"All results saved to {csv_file_path}")
    return results_df.to_dict(orient='records')

def _one_run(run_index, requested_type, context_types, assistant_key_name, max_iterations, prompt_content, assistant_id, thread_base_dir_for_saving):
    """
    Executes a single verification run. This function is designed to be called by ProcessPoolExecutor.
    It handles its own OpenAI client initialization if necessary, or assumes it's configured.
    """
    # Each process should have its own interaction_counter and verification_status
    # These cannot be shared directly as globals across processes.
    local_interaction_counter = 0
    local_verification_status = []

    # Ensure OpenAI API key is available in the new process if not inherited
    if not openai.api_key:
        load_dotenv() # Try loading .env again
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            logging.error("OpenAI API key not found in _one_run process.")
            return {
                "run": run_index + 1,
                "time_taken": 0,
                "iterations": 0,
                "verified": "ERROR",
                "annotated_contract": "OpenAI API key not configured in process.",
                "status": [{"error": "OpenAI API key not configured"}]
            }

    start_time = time.time()

    # Create Assistant and Thread objects for this run
    assistant_obj = Assistant(assistant_id)
    thread_obj = Thread(assistant_obj)
    
    # Resetting globals for this process/run
    global interaction_counter, verification_status
    interaction_counter = 0
    verification_status = []

    annotated_contract_result = loop(thread_obj, prompt_content, max_iterations, requested_type)

    # After loop, retrieve the values from the globals of this process
    final_interaction_counter = interaction_counter
    final_verification_status = verification_status

    duration = time.time() - start_time
    
    # Define context_str for saving thread file
    context_str_for_save = "_".join([c for c in context_types if c]) if context_types else "none"

    # Save thread to file
    save_thread_to_file(
        thread_id=thread_obj.id,
        requested_type=requested_type,
        context_str=context_str_for_save,
        assistant_key=assistant_key_name,
        run_number=run_index + 1
    )

    is_verified = isinstance(annotated_contract_result, str) # Assuming string means verified contract
    
    return {
        "run": run_index + 1,
        "time_taken": duration,
        "iterations": max(0, final_interaction_counter -1),
        "verified": is_verified,
        "annotated_contract": annotated_contract_result if is_verified else "",
        "status": final_verification_status
    }


def main():
    """Main entry point for the verification process"""
    parser = argparse.ArgumentParser(description='Run contract verification with different contexts')
    parser.add_argument('--requested', type=str, required=True, 
                        choices=['erc20', 'erc721', 'erc1155'],
                        help='The contract type to verify')
    parser.add_argument('--context', type=str, required=True,
                        help='Comma-separated list of context contract types (e.g., "erc20,erc721,erc1155")')
    parser.add_argument('--assistant', type=str, default='4o-mini',
                        choices=list(ASSISTANT_IDS.keys()),
                        help='The assistant to use')
    parser.add_argument('--runs', type=int, default=10,
                        help='Number of verification runs')
    parser.add_argument('--max-iterations', type=int, default=10,
                        help='Maximum number of iterations for each run (default: 10)')
    
    args = parser.parse_args()
    context_list = [c.strip() for c in args.context.split(',') if c.strip()] if args.context else []

    run_verification_process(
        requested_type=args.requested,
        context_types=context_list,
        assistant_key=args.assistant,
        num_runs=args.runs,
        max_iterations=args.max_iterations
    )

if __name__ == "__main__":
    main() 