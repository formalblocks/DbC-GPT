"""
Smart Contract Function-by-Function Verification System

This script implements a system for verifying smart contract specifications function by function
using OpenAI's API and solc-verify. It handles the verification process for ERC20, ERC721, and ERC1155
token standards by processing each function independently.

Key Features:
- Function-by-function verification of smart contract specifications
- Support for multiple ERC token standards
- Parallel processing of verification runs
- Detailed logging and result tracking
- Error handling and retry mechanisms
- Function-specific documentation support
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
import textwrap
import tempfile
import shutil

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
    "4.1":"asst_zX20A8d9KI7rIK8lLoRTgHK2",
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
    "erc123": "../assets/file_search/erc123_interface.md",
}

# File paths for EIP documentation
EIP_PATHS = {
    "erc20": "../assets/file_search/erc-20.md",
    "erc721": "../assets/file_search/erc-721.md",
    "erc1155": "../assets/file_search/erc-1155.md",
    "erc123": "../assets/file_search/erc-123.md",
}

# File paths for reference specifications
REFERENCE_SPEC_PATHS = {
    "erc20": "../assets/file_search/erc20_ref_spec.md",
    "erc721": "../assets/file_search/erc721_ref_spec.md",
    "erc1155": "../assets/file_search/erc1155_ref_spec.md",
    "erc123": "../assets/file_search/erc123_ref_spec.md",
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

Requirements:
    - Ensure conditions correctly represent the expected state changes and return values.
    - View functions should relate return values directly to state variables.
    - Postconditions MUST ONLY use state variables exactly as declared. Referencing undeclared variables will fail if they aren't in the contract. For instance, a state variable `uint256 var` can be referenced as `var` only.
    - Postconditions MUST ONLY use parameter names exactly as they appear in function signatures. For instance, `function foo(uint256 bar,  address par)` has parameter names `bar` and `par` only. 
    - Use `__verifier_old_uint(stateVariable)` or `__verifier_old_bool(stateVariable)` to reference values from the start of the function execution.
    - A quantified postcondition MUST start with `forall`. For instance, a quantified postcondition look like `/// @notice postcondition forall (uint x) condition`. Without the `forall` at the beginning, the postcondition is invalid.
    - YOU MUST SPECIFY THE RANGE when postconditions quantify over arrays. For example, for array `arr` a postcondition quantification would look like `/// @notice postcondition forall (uint i) !(0 <= i && i < arr.length) || condition`. Without the range, the postcondition is likely to be invalid.
    - The implication operator "==>" is not valid in solc-verify notation, so it must appear NOWHERE in a postcondition. For instance, a postcondition of the form `/// @notice postcondition condition1 ==> condition2` is invalid. Similarly, a postcondition of the form `/// @notice postcondition (forall uint x) condition1 ==> condition2` is also invalid. You can use instead the notation `!(condition) || condition2` to simulate the implication operator. For instance, `/// @notice postcondition (forall uint x) condition1 ==> condition2` can be written as `/// @notice postcondition !(condition1) || condition2`.

Your task is to annotate the function in the contract below:
"""

# Global state for tracking verification progress
interaction_counter = 0
verification_status = []

def parse_solidity_interface(solidity_code: str):
    """
    Parses Solidity interface code to extract components.
    Returns a dictionary containing 'pragma', 'state_vars', 'events', 'functions'.
    Functions value is a list of {'signature': str, 'body': str}.
    """
    components = {
        'pragma': "pragma solidity ^0.8.0;", # Default pragma if not found
        'state_vars': [],
        'events': [],
        'functions': []
    }

    # Extract pragma
    pragma_match = re.search(r"^\s*pragma solidity[^;]+;", solidity_code, re.MULTILINE)
    if pragma_match:
        components['pragma'] = pragma_match.group(0).strip()
    else:
        logging.warning("No pragma directive found in solidity_code. Using default.")

    # Extract state variables (simple version: assumes they are declared outside functions)
    # Matches lines like: mapping(...) private _variable; string private _uri; uint256 constant VALUE = 10;
    state_var_pattern = re.compile(r"^\s*(mapping\(.+?\)|bytes32|uint\d*|int\d*|string|address|bool|bytes)\s+(public|private|internal|constant)?\s*(\w+)\s*(?:=.*?)?;", re.MULTILINE)
    for match in state_var_pattern.finditer(solidity_code):
      components['state_vars'].append(match.group(0).strip()) # Store the full declaration line

    # Extract events
    event_pattern = re.compile(r"^\s*event\s+(\w+)\((.*?)\);", re.MULTILINE | re.DOTALL)
    for match in event_pattern.finditer(solidity_code):
        components['events'].append(match.group(0).strip())

    # Extract functions (including modifiers and return types)
    # This regex is complex and might need refinement for edge cases
    function_pattern = re.compile(
        r"^\s*function\s+(?P<name>\w+)\s*\((?P<params>.*?)\)\s*(?P<modifiers>.*?)\s*(?:returns\s*\((?P<returns>.*?)\))?\s*;",
        re.MULTILINE | re.DOTALL
    )

    for match in function_pattern.finditer(solidity_code):
        func_dict = match.groupdict()
        signature = f"function {func_dict['name']}({func_dict['params'].strip()}) {func_dict['modifiers'].strip()}"
        if func_dict['returns']:
            signature += f" returns ({func_dict['returns'].strip()})"
        signature += ";"
        # We assume the interface has no body, just the signature ending in ';'
        components['functions'].append({'signature': signature.strip(), 'name': func_dict['name']})

    logging.info(f"Parsed components: {len(components['state_vars'])} state vars, {len(components['events'])} events, {len(components['functions'])} functions. Pragma: {components['pragma']}")

    return components

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
        combo_dir = f"threads_func_by_func/{assistant_key}/{requested_type}/{context_str}"
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
    """Represents an OpenAI Assistant with a specific ID for contract verification."""
    
    def __init__(self, id) -> None:
        self.id = id

class Thread:
    """Manages a conversation thread with an OpenAI Assistant."""
    
    def __init__(self, assistant: Assistant) -> None:
        self.assistant = assistant
        self._thread = self._create_thread()
    
    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError, openai.APIConnectionError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    def _create_thread(self):
        """Creates a new thread with retry logic for API errors."""
        try:
            return openai.beta.threads.create()
        except (openai.RateLimitError, openai.APIError, openai.APIConnectionError) as e:
            logging.error(f"API error: {str(e)}. Retrying...")
            raise
    
    @property
    def id(self):
        """Returns the thread ID."""
        return self._thread.id
    
    def send_message(self, content: str) -> 'Interaction':
        """Sends a message to the thread and returns an Interaction object."""
        interaction = Interaction(self, content)
        return interaction
    
    @property
    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError, openai.APIConnectionError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    def last_message(self) -> str:
        """Retrieves the last message from the thread with retry logic."""
        try:
            response = openai.beta.threads.messages.list(
                thread_id=self.id
            )
            return response.data[0].content[0].text.value
        except (openai.RateLimitError, openai.APIError, openai.APIConnectionError) as e:
            logging.error(f"API error: {str(e)}. Retrying...")
            raise
        except Exception as e:
            logging.error(f"Unexpected error retrieving message: {str(e)}")
            return "Error retrieving message"

class Interaction:
    """Represents a single interaction with the OpenAI Assistant."""
    
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
        """Creates a message in the thread with retry logic."""
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
        """Creates a run for the message with retry logic."""
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
        """Returns the run ID."""
        return self._run.id
    
    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError, openai.APIConnectionError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    def remote_sync(self):
        """Synchronizes the run status with the server with retry logic."""
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
        """Returns the current run status."""
        return self._run.status
    
    def await_for_response(self) -> str:
        """Waits for and returns the assistant's response with error handling."""
        status = self.status
        while (status != "completed"):
            try:
                self.remote_sync()
                status = self.status
                logging.info("awaiting for a response. status: " + str(status))
                
                if status == "failed" or status == "expired":
                    error_info = self._run.last_error if hasattr(self._run, 'last_error') else "Unknown error"
                    logging.error(f"Run {status}: {error_info}")
                    time.sleep(10)
                    self._create_run()
                    status = self.status
                
                sleep_time = 2 + random.uniform(0, 1)
                time.sleep(sleep_time)
            except Exception as e:
                logging.error(f"Error during response wait: {str(e)}")
                time.sleep(5)
        
        return self.thread.last_message

@dataclass
class VerificationResult:
    """Represents the result of a contract verification attempt."""
    status: int  # 0 for success, non-zero for failure
    output: str  # Verification output or error message

class SolcVerifyWrapper:
    """Wrapper class for interacting with solc-verify tool for contract verification."""
    
    SOLC_VERIFY_CMD = "solc-verify.py"
    SOLC_VERIFY_TIMEOUT = int(os.getenv("SOLC_VERIFY_TIMEOUT", "120"))
    
    # Template paths for different ERC standards
    TEMPLATE_PATHS = {
        "erc20": './solc_verify_generator/ERC20/templates/imp_spec_merge.template',
        "erc721": './solc_verify_generator/ERC721/templates/imp_spec_merge.template',
        "erc1155": './solc_verify_generator/ERC1155/templates/imp_spec_merge.template',
        "erc123": './solc_verify_generator/ERC123/templates/imp_spec_merge.template',
    }
    
    # Merge paths for different ERC standards
    MERGE_PATHS = {
        "erc20": './solc_verify_generator/ERC20/imp/ERC20_merge.sol',
        "erc721": './solc_verify_generator/ERC721/imp/ERC721_merge.sol',
        "erc1155": './solc_verify_generator/ERC1155/imp/ERC1155_merge.sol',
        "erc123": './solc_verify_generator/ERC123/imp/ERC123_merge.sol',
    }

    @classmethod
    def call_solc(cls, file_path) -> VerificationResult:
        """
        Calls the solc-verify tool on a given file.
        
        Args:
            file_path: Path to the Solidity file to verify
            
        Returns:
            VerificationResult containing the verification status and output
        """
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
    def verify(cls, soldity_spec_str: str, requested_type: str = "erc20") -> VerificationResult:
        """
        Verifies a Solidity specification string against a template.
        
        Args:
            spec_str: Solidity code with function signatures annotated with solc-verify conditions
            requested_type: The ERC standard to verify ("erc20", "erc721", "erc1155")
            
        Returns:
            VerificationResult containing the verification status and output
        """
        original_merge_file_path = cls.MERGE_PATHS.get(requested_type)
        if not original_merge_file_path:
            raise ValueError(f"Unsupported requested_type for SolcVerifyWrapper: {requested_type} - merge path not found.")
        
        dependency_source_dir = os.path.dirname(original_merge_file_path)
        if not os.path.isdir(dependency_source_dir) and requested_type in ["erc20", "erc721", "erc1155"]:
             logging.warning(f"Dependency source directory not found or not a directory: {dependency_source_dir}")

        workdir = tempfile.mkdtemp(prefix="solc_verify_fbf_")
        try:
            spec_file_in_workdir  = os.path.join(workdir, "spec.sol")
            merge_file_basename = os.path.basename(original_merge_file_path)

            Utils.save_string_to_file(spec_file_in_workdir, soldity_spec_str)

            # Create temp directory for AST output
            os.makedirs(os.path.join(workdir, "temp"), exist_ok=True)

            # Copy dependencies from source directory
            if os.path.isdir(dependency_source_dir):
                for item_name in os.listdir(dependency_source_dir):
                    source_item_path = os.path.join(dependency_source_dir, item_name)
                    dest_item_path = os.path.join(workdir, item_name)
                    
                    if os.path.isdir(source_item_path):
                        shutil.copytree(source_item_path, dest_item_path)
                    elif item_name.endswith(".sol") or os.path.isfile(source_item_path):
                        shutil.copy2(source_item_path, dest_item_path)
                logging.debug(f"Copied dependencies from {dependency_source_dir} to {workdir}")

            from solc_verify_generator.main import generate_merge 
            
            original_cwd = os.getcwd()
            os.chdir(workdir)
            try:
                absolute_template_path = os.path.abspath(os.path.join(original_cwd, cls.TEMPLATE_PATHS[requested_type]))
                if not os.path.exists(absolute_template_path):
                    logging.error(f"Template file not found: {absolute_template_path}")
                    return VerificationResult(-1, f"Template file not found: {absolute_template_path}")

                generate_merge(
                  "spec.sol",
                  absolute_template_path, 
                  merge_file_basename
                )
            except RuntimeError as e:
                logging.error(f"Error during generate_merge: {e}")
                return VerificationResult(e.args[0] if len(e.args) > 0 else -1, str(e.args[1] if len(e.args) > 1 else e))
            except Exception as e:
                logging.error(f"Unexpected error during generate_merge: {e}")
                return VerificationResult(-1, f"Unexpected error during generate_merge: {e}")
            finally:
                os.chdir(original_cwd)
            
            # Execute solc-verify in the working directory
            os.chdir(workdir)
            try:
                verification_result = cls.call_solc(merge_file_basename)
            finally:
                os.chdir(original_cwd)
            
            return verification_result
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

class Utils:
    """Utility class for file operations and data processing."""

    @staticmethod
    def extract_solidity_code(markdown_text):
        """
        Extracts Solidity code from markdown text.
        
        Args:
            markdown_text: Text containing markdown-formatted Solidity code
            
        Returns:
            Extracted Solidity code or None if not found
        """
        pattern = r'```solidity\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)
        try:
            return matches[0]
        except IndexError:
            return None
    
    @staticmethod
    def read_file_content(file_path):
        """
        Reads content from a file.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File contents or None if read fails
        """
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except IOError as e:
            print(f"An error occurred while reading the file {file_path}: {e}")
            return None

    @staticmethod
    def save_string_to_file(file_name, content):
        """
        Saves string content to a file.
        
        Args:
            file_name: Path where to save the content
            content: String content to save
        """
        try:
            with open(file_name, 'w') as file:
                file.write(content)
            print(f"Content successfully saved to {file_name}")
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")

    @staticmethod
    def save_results_to_csv(file_name: str, results: List[dict]):
        """
        Saves verification results to a CSV file.
        
        Args:
            file_name: Path where to save the CSV file
            results: List of dictionaries containing verification results
        """
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        df = pd.DataFrame(results)
        try:
            df.to_csv(file_name, index=False)
            print(f"Results successfully saved to {file_name}")
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")

    @staticmethod
    def extract_content_from_markdown(file_path):
        """
        Extracts code block or content from a markdown file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            Extracted content or empty string if file not found
        """
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
    """
    Loads example reference specifications for the given context types.
    
    Args:
        context_types: List of contract types to load examples for
        
    Returns:
        List of example contract specifications in markdown format
    """
    examples = []
    
    for contract_type in context_types:
        if contract_type in REFERENCE_SPEC_PATHS:
            content = Utils.extract_content_from_markdown(REFERENCE_SPEC_PATHS[contract_type])
            if content:
                examples.append(f"```solidity\n{content}\n```")
    
    return examples

def load_target_interface(requested_type):
    """
    Loads the interface that needs to be annotated.
    
    Args:
        requested_type: The type of contract interface to load
        
    Returns:
        Interface content or None if not found
    """
    if requested_type in INTERFACE_PATHS:
        return Utils.extract_content_from_markdown(INTERFACE_PATHS[requested_type])
    return None

def assemble_partial_contract(pragma_str: str, contract_name: str, components: dict, current_annotations: dict):
    """
    Assembles a partial contract string for verification.
    
    Args:
        pragma_str: Solidity pragma directive
        contract_name: Name of the contract
        components: Dictionary containing contract components (events, state vars, functions)
        current_annotations: Dictionary mapping function signatures to their annotations
        
    Returns:
        Complete contract string with annotations
    """
    code = f"{pragma_str}\n\ncontract {contract_name} {{\n\n"

    # Add Events
    code += "    // Events\n"
    for event in components.get('events', []):
        code += f"    {event}\n"
    code += "\n"

    # Add State Variables
    code += "    // State Variables\n"
    for var in components.get('state_vars', []):
        code += f"    {var}\n"
    code += "\n"

    # Add Functions with annotations
    code += "    // Functions\n"
    for func_info in components.get('functions', []):
        func_sig = func_info['signature']
        annotations = current_annotations.get(func_sig)
        if annotations:
            for line in annotations.split('\n'):
                 code += f"    {line}\n"
        else:
            code += "    /// @notice postcondition true\n"

        code += f"    {func_sig}\n\n"

    code += "}\n"
    return code

def extract_annotations_for_function(llm_response: str, target_func_sig: str):
    """
    Extracts annotations from an LLM response.
    
    Args:
        llm_response: Response from the language model
        target_func_sig: Function signature to extract annotations for
        
    Returns:
        Extracted annotations or None if not found
    """
    if not llm_response or not llm_response.strip():
        print(f"LLM response for {target_func_sig} is empty or whitespace.")
        return None

    processed_llm_response = llm_response.strip()
    postcondition_lines = [line.strip().rstrip(";") for line in processed_llm_response.split('\n') if "@notice postcondition" in line.strip()]
    final_annotations_str = "\n".join(postcondition_lines)
    return final_annotations_str

def process_single_function(thread: Thread, func_info: dict, components: dict, pragma_str: str, verified_annotations: dict, eip_doc: str, base_instructions: str, examples_text: str, max_iterations_per_function: int, requested_type: str):
    """
    Processes a single function for verification.
    
    Args:
        thread: Thread object for communication
        func_info: Dictionary containing function information
        components: Dictionary containing contract components
        pragma_str: Solidity pragma directive
        verified_annotations: Dictionary of verified annotations
        eip_doc: EIP documentation
        base_instructions: Base instructions for the model
        examples_text: Example specifications
        max_iterations_per_function: Maximum number of verification attempts
        requested_type: Type of contract being verified
        
    Returns:
        Tuple of (annotations, interaction_count) or (None, interaction_count) if verification fails
    """
    func_sig = func_info['signature']
    func_name = func_info['name']
    contract_name = requested_type.upper()
    logging.info(f"Processing function: {func_name} ({func_sig})")

    func_interactions = 0
    verified_ann_str = "\n".join([f'{fs}\n{fa}' for fs, fa in verified_annotations.items()])
    state_vars_str = "\n".join(components.get('state_vars', []))
    events_str = "\n".join(components.get('events', []))

    # Extract EIP snippet specific to the current function
    specific_eip_snippet = "No specific EIP segment found for this function."
    if eip_doc and func_name:
        pattern = rf"(/\*\*(?:[^*]|\*(?!/))*?\*/\s*function\s+{re.escape(func_name)}\s*\(.*\).*?;)"
        match = re.search(pattern, eip_doc, re.DOTALL)
        if match:
            specific_eip_snippet = match.group(1).strip()

    indented_state_vars = "\n".join([f"    {var}" for var in components.get('state_vars', [])])

    # Check for function-specific documentation
    func_md_path = f"../assets/file_search/{requested_type.lower()}/{func_name}.md"
    func_md_content = ""
    try:
        with open(func_md_path, 'r') as f:
            func_md_content = f.read()
        logging.info(f"Found function-specific file for {func_name} at {func_md_path}")
    except:
        logging.info(f"No function-specific file found for {func_name} at {func_md_path}")

    # Format prompt based on available documentation
    if func_md_content:
        current_prompt = textwrap.dedent(f"""{base_instructions}

```solidity
pragma solidity >= 0.5.0;

contract {contract_name} {{
{func_md_content}
}}
```

EIP markdown below:
<eip>
{specific_eip_snippet}
</eip>
""").lstrip()
    else:
        current_prompt = textwrap.dedent(f"""{base_instructions}

```solidity
pragma solidity >= 0.5.0;

contract {contract_name} {{
{indented_state_vars}

{func_sig}
}}
```

EIP Documentation Snippet (if relevant to `{func_name}`):
<eip>
{specific_eip_snippet}
</eip>
""").lstrip()

    if examples_text:
        current_prompt += f"\n**Examples:**\n{examples_text}"

    for attempt in range(max_iterations_per_function):
        logging.info(f"Attempt {attempt + 1}/{max_iterations_per_function} for function {func_name}")
        interaction: Interaction = thread.send_message(current_prompt)
        response = interaction.await_for_response()
        func_interactions += 1

        proposed_annotations = extract_annotations_for_function(response, func_sig)

        if not proposed_annotations:
            logging.error(f"No annotations extracted for {func_name}. LLM response: {response[:500]}")
            current_prompt = f"Your previous response did not seem to contain just the annotations for `{func_sig}`. Please provide ONLY the `/// @notice postcondition ...` lines for this function. Do not include the function signature or any other text."
            continue

        # Assemble contract with proposed annotations
        temp_annotations = verified_annotations.copy()
        temp_annotations[func_sig] = proposed_annotations
        partial_contract_code = assemble_partial_contract(pragma_str, contract_name, components, temp_annotations)

        try:
            verification_result: VerificationResult = SolcVerifyWrapper.verify(
                partial_contract_code, 
                requested_type=requested_type
            )
        except Exception as e:
            logging.error(f"Verification failed for {func_name} with exception: {e}")
            return None, func_interactions

        verification_passed = verification_result.status == 0
        error_output = verification_result.output

        if verification_passed:
            logging.info(f"Successfully verified annotations for function {func_name}.")
            return proposed_annotations, func_interactions
        else:
            logging.warning(f"Verification failed for function {func_name} (Attempt {attempt + 1}). Error: {error_output[:500]}...")
            current_prompt = f"""
            Verification failed for function `{func_sig}`

            The verifier found the following errors:
            ```
            {error_output}
            ```

            Can you fix the specification accordingly?
            """

    logging.error(f"Failed to verify annotations for function {func_name} after {max_iterations_per_function} attempts.")
    return None, func_interactions

def run_verification_process(requested_type, context_types, assistant_key="4o-mini", num_runs=10, max_iterations=10):
    """
    Runs the function-by-function verification process.
    
    Args:
        requested_type: Type of contract to verify (e.g., "erc20")
        context_types: List of context contract types
        assistant_key: Key for the OpenAI assistant to use
        num_runs: Number of verification runs to perform
        max_iterations: Maximum number of iterations per function
        
    Returns:
        List of dictionaries containing verification results
    """
    global verification_status
    if requested_type not in INTERFACE_PATHS:
        raise ValueError(f"Requested type '{requested_type}' not supported.")
    for ct in context_types:
        if ct and ct not in REFERENCE_SPEC_PATHS:
            raise ValueError(f"Context type '{ct}' not found in REFERENCE_SPEC_PATHS.")
    if assistant_key not in ASSISTANT_IDS:
        raise ValueError(f"Assistant key '{assistant_key}' not found in ASSISTANT_IDS.")

    assistant_id = ASSISTANT_IDS[assistant_key]
    valid_contexts = [ct for ct in context_types if ct]
    context_str = '_'.join(valid_contexts) if valid_contexts else "none"
    
    results_base_dir = "results_func_by_func"
    results_dir = os.path.join(results_base_dir, assistant_key, requested_type, context_str)
    os.makedirs(results_dir, exist_ok=True)

    csv_file_name = f"fbf_{requested_type}_[{context_str if context_str else 'none'}].csv"
    csv_file_path = os.path.join(results_dir, csv_file_name)

    # Load contract interface and parse components
    target_interface_content = Utils.extract_content_from_markdown(INTERFACE_PATHS[requested_type])
    if not target_interface_content:
         raise ValueError(f"Could not load interface content for {requested_type}")

    parsed_components = parse_solidity_interface(target_interface_content)
    if not parsed_components['functions']:
        raise ValueError("No functions found in the interface file.")

    pragma_str = parsed_components.get('pragma', "pragma solidity ^0.8.0;")
    contract_name = requested_type.upper()
    eip_doc = Utils.extract_content_from_markdown(EIP_PATHS.get(requested_type, ""))
    base_instructions = INSTRUCTIONS

    # Generate example texts from context types
    raw_examples_content = ""
    for ctx_type in context_types:
        if not ctx_type:
            continue
        
        ref_spec_content = Utils.extract_content_from_markdown(REFERENCE_SPEC_PATHS.get(ctx_type, ""))
        if ref_spec_content:
            raw_examples_content += f"\nExample ERC {ctx_type.upper()} specification:\n\n```solidity\n{ref_spec_content}\n```\n"

    examples_section_for_prompt = ""
    if raw_examples_content:
        examples_section_for_prompt = f"\nHere are examples of similar ERC formal specifications:{raw_examples_content}"

    results = []
    max_iterations_per_function = max_iterations

    for i in range(num_runs):
        current_run_number = i + 1
        print(f"\n--- Starting Func-by-Func Run {current_run_number}/{num_runs} --- ")
        run_start_time = time.time()
        
        verified_annotations = {}
        function_verification_status = {}
        verification_status = []
        total_interactions = 0
        threads_info = []

        for func_info in parsed_components.get('functions', []):
            assistant = Assistant(assistant_id)
            thread = Thread(assistant)
            threads_info.append((func_info['name'], thread.id))
            
            func_annotations, func_interactions_count = process_single_function(
                thread=thread,
                func_info=func_info,
                components=parsed_components,
                pragma_str=pragma_str,
                verified_annotations=verified_annotations,
                eip_doc=eip_doc,
                base_instructions=base_instructions,
                examples_text=examples_section_for_prompt,
                max_iterations_per_function=max_iterations_per_function,
                requested_type=requested_type
            )
            total_interactions += func_interactions_count

            if func_annotations:
                verified_annotations[func_info['signature']] = func_annotations
                function_verification_status[func_info['name']] = "Verified"
            else:
                function_verification_status[func_info['name']] = "Failed"
            
            thread_save_result = save_thread_to_file(thread.id, requested_type, f"{context_str}_{func_info['name']}", assistant_key, current_run_number)
            if not thread_save_result:
                print(f"WARNING: Failed to save thread file for function {func_info['name']} in run {current_run_number}")

        run_end_time = time.time()
        duration = run_end_time - run_start_time

        final_contract_code = assemble_partial_contract(pragma_str, contract_name, parsed_components, verified_annotations)
        all_functions_verified = all(status == "Verified" for status in function_verification_status.values())

        print(f"Run {current_run_number} used {len(threads_info)} threads: {', '.join([f'{name}:{tid}' for name, tid in threads_info])}")

        results.append({
            "run": current_run_number,
            "time_taken": duration,
            "iterations": total_interactions,
            "verified": all_functions_verified,
            "annotated_contract": final_contract_code,
            "function_status": function_verification_status, 
            "status": verification_status, 
            "threads": [tid for _, tid in threads_info] 
        })

    results_df = pd.DataFrame(results)
    if 'run' in results_df.columns:
        results_df = results_df.sort_values(by='run').reset_index(drop=True)
        
    Utils.save_results_to_csv(csv_file_path, results_df.to_dict(orient='records'))
    logging.info(f"All func_by_func results saved to {csv_file_path}")
    return results_df.to_dict(orient='records')

def main():
    """
    Main entry point for the function-by-function verification process.
    Parses command line arguments and initiates the verification process.
    """
    parser = argparse.ArgumentParser(description='Run contract verification with different contexts')
    parser.add_argument('--requested', type=str, required=True, 
                        choices=['erc20', 'erc721', 'erc1155', 'erc123'],
                        help='The contract type to verify')
    parser.add_argument('--context', type=str, required=True,
                        help='Comma-separated list of context contract types (e.g., "erc20,erc721,erc1155,erc123")')
    parser.add_argument('--assistant', type=str, default='4o-mini',
                        choices=list(ASSISTANT_IDS.keys()),
                        help='The assistant to use')
    parser.add_argument('--runs', type=int, default=10,
                        help='Number of verification runs')
    parser.add_argument('--max-iterations', type=int, default=10,
                        help='Maximum iterations per run')
    
    args = parser.parse_args()
    
    if not args.context.strip():
        context_types = [""]
    else:
        context_types = [ctx.strip().lower() for ctx in args.context.split(',')]
    
    run_verification_process(
        requested_type=args.requested.lower(),
        context_types=context_types,
        assistant_key=args.assistant,
        num_runs=args.runs,
        max_iterations=args.max_iterations
    )

if __name__ == "__main__":
    main() 
