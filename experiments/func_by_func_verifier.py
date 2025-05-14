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
    # "erc20-721-1155-4-o-mini": "asst_PDcb3OR1jFTRQNTFpZgdY9wt",
    # "erc20-4-o-mini": "asst_H3M7A5dC7RXLbY49k0GhuCJS",
    # "erc721-4-o-mini": "asst_aroYVGYOi4TB4PMsEgEzVfIS",
    # "erc1155-4-o-mini": "asst_M0wMZRzDVSdby3CfuMLtgWsc",
    # "erc20-721-4-o-mini": "asst_6o09ITzVveX37WwyVz42KhrY",
    # "erc20-1155-4-o-mini": "asst_231yQkPjxDM9cBgo76IzQgdh",
    # "erc721-1155-4-o-mini": "asst_Qs4WLHGBoP9fAMgbZ6y7gFrX",
    "4o-mini": "asst_WRF0J9P9EiZ70DcntBSlapWB",
    "erc-1155-001-3-16": "asst_uMYPmlxmT9ppnPKZQ8ZTyfYb",
    "erc-1155-005-3-16": "asst_tsqw3GcFG1kyPz9rNkqkIYAU",
    "erc-1155-010-3-16": "asst_BsZDuAHsmBfrlimXinHt96Cb",
    "erc-1155-001-5-16": "asst_Mkq2y7mUxjusd47rPSGXrrCM",
    "erc-1155-005-5-16": "asst_8ZL8R3zwXyurmmjkFX14kcuS",
    "erc-1155-010-5-16": "asst_wOnRMvawOAI1sO83lfRWWBLu",
    "erc-1155-001-7-16": "asst_sZLa64l2Xrb1zNhogDl7RXap",
    "erc-1155-005-7-16": "asst_m8y0QMRJVtvDRYcPZLVIcHW6",
    "erc-1155-001-7-16": "asst_MRg3E5ds4NRfFKPTPqLsx9rS",
}

# Paths to interface templates and EIP docs
INTERFACE_PATHS = {
    "erc20": "../assets/file_search/erc20_interface.md",
    "erc721": "../assets/file_search/erc721_interface.md",
    "erc1155": "../assets/file_search/erc1155_interface.md",
    "erc123": "../assets/file_search/erc123_interface.md",
}

EIP_PATHS = {
    "erc20": "../assets/file_search/erc-20.md",
    "erc721": "../assets/file_search/erc-721.md",
    "erc1155": "../assets/file_search/erc-1155.md",
    "erc123": "../assets/file_search/erc-123.md",
}

REFERENCE_SPEC_PATHS = {
    "erc20": "../assets/file_search/erc20_ref_spec.md",
    "erc721": "../assets/file_search/erc721_ref_spec.md",
    "erc1155": "../assets/file_search/erc1155_ref_spec.md",
    "erc123": "../assets/file_search/erc123_ref_spec.md",
    "": ""
}

INSTRUCTIONS = """
    Task:
        - You are given a smart contract interface and need to add formal postconditions to a function using solc-verify syntax (`/// @notice postcondition condition`). Postconditions must not end with a semicolon (";").
        - You MUST use the EIP documentation below to understand the required behavior.
        - Replace `$ADD POSTCONDITION HERE` with appropriate postconditions above each function. Postconditions placed below the function signature are invalid. For instance:
        ``` 
        /// @notice postcondition condition1\n
        /// @notice postcondition condition2\n
        function foo(uint256 bar, address par) public;
        ```

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

# Initialize the global counter
interaction_counter = 0

# Initialize the global verification status
verification_status = []

def parse_solidity_interface(solidity_code: str):
    """
    Parses Solidity interface code to extract components.
    Returns a dictionary containing 'state_vars', 'events', 'functions'.
    Functions value is a list of {'signature': str, 'body': str}.
    """
    components = {
        'state_vars': [],
        'events': [],
        'functions': []
    }

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

    logging.info(f"Parsed components: {len(components['state_vars'])} state vars, {len(components['events'])} events, {len(components['functions'])} functions.")

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
            print("GENERATING MERGE")
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

def assemble_partial_contract(contract_name: str, components: dict, current_annotations: dict, target_func_sig: str = None):
    """Assembles a partial contract string for verification."""
    code = f"pragma solidity >= 0.5.0;\n\ncontract {contract_name} {{\n\n"

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
            # Add existing/verified annotations
            for line in annotations.split('\n'):
                 code += f"    {line}\n"
        elif func_sig == target_func_sig:
             # Placeholder for the function being actively verified if its annotations aren't ready
             pass # Annotations will be added just before verification call
        else:
            # Add placeholder for functions not yet processed or failed
            code += "    /// @notice postcondition true\n"

        code += f"    {func_sig}\n\n" # Add function signature

    code += "}\n"
    return code

def extract_annotations_for_function(llm_response: str, target_func_sig: str):
    """
    Extracts annotations from an LLM response.
    This function will extract ONLY the lines starting with "@notice postcondition".
    Trailing semicolons on annotation lines are removed.
    """

    if not llm_response or not llm_response.strip():
        print(f"LLM response for {target_func_sig} is empty or whitespace.")
        return None

    processed_llm_response = llm_response.strip()
    
    # Only collect lines that contain @notice postcondition
    postcondition_lines = [line.strip().rstrip(";") for line in processed_llm_response.split('\n') if "@notice postcondition" in line.strip()]
    
    # Join the postcondition lines with newlines
    final_annotations_str = "\n".join(postcondition_lines)
    return final_annotations_str
    

def process_single_function(thread: Thread, func_info: dict, components: dict, verified_annotations: dict, eip_doc: str, base_instructions: str, examples_text: str, max_iterations_per_function: int, requested_type: str):
    """Tries to generate and verify annotations for a single function."""
    func_sig = func_info['signature']
    func_name = func_info['name']
    contract_name = requested_type.upper()
    logging.info(f"Processing function: {func_name} ({func_sig})")

    # Track interactions within this function context
    func_interactions = 0

    # Pre-format verified annotations to avoid nested f-string issues
    verified_ann_str = "\n".join([f'{fs}\n{fa}' for fs, fa in verified_annotations.items()])
    # Pre-format state vars and events
    state_vars_str = "\n".join(components.get('state_vars', []))
    events_str = "\n".join(components.get('events', []))

    # Extract EIP snippet specific to the current function
    specific_eip_snippet = "No specific EIP segment found for this function."
    if eip_doc and func_name:
        # Regex to find the Javadoc-style comment and the function signature for the specific function name
        # It captures the comment block and the function line associated with func_name
        pattern = rf"(/\*\*(?:[^*]|\*(?!/))*?\*/\s*function\s+{re.escape(func_name)}\s*\(.*\).*?;)"
        match = re.search(pattern, eip_doc, re.DOTALL)
        if match:
            specific_eip_snippet = match.group(1).strip()

    # Indent state variables for placement within the contract block - do this BEFORE checking for function-specific files
    indented_state_vars = "\n".join([f"    {var}" for var in components.get('state_vars', [])])

    # Check for a function-specific markdown file
    func_md_path = f"../assets/file_search/{requested_type.lower()}/{func_name}.md"
    func_md_content = ""
    try:
        with open(func_md_path, 'r') as f:
            func_md_content = f.read().strip()
        logging.info(f"Found function-specific file for {func_name} at {func_md_path}")
    except:
        logging.info(f"No function-specific file found for {func_name} at {func_md_path}")
        # We already defined indented_state_vars above, so we don't need to do it again here

    # Format the current prompt based on whether we have a function-specific markdown file
    if func_md_content:
        print("FOUND FUNCTION-SPECIFIC FILE")
        current_prompt = f"""
        
        {base_instructions}

        ```solidity
        pragma solidity >= 0.5.0;

        contract {contract_name} {{
        {indented_state_vars}

        {func_md_content}
        }}
        ```

        EIP Documentation Snippet (if relevant to `{func_name}`):
        <eip>
        {specific_eip_snippet}
        </eip>
        """
    else:
        print("NO FUNCTION-SPECIFIC FILE FOUND")
        # Use the original formatting as a fallback
        current_prompt = f"""
        {base_instructions}

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
        """

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
            # Ask LLM to provide only annotations
            current_prompt = f"Your previous response did not seem to contain just the annotations for `{func_sig}`. Please provide ONLY the `/// @notice postcondition ...` lines for this function. Do not include the function signature or any other text."
            continue # Try again with the feedback

        # Assemble the contract with *proposed* annotations for the current function
        temp_annotations = verified_annotations.copy()
        temp_annotations[func_sig] = proposed_annotations
        partial_contract_code = assemble_partial_contract(contract_name, components, temp_annotations)

        # Verify the partially assembled contract
        try:
            verification_result: VerificationResult = SolcVerifyWrapper.verify(
                partial_contract_code, 
                requested_type=requested_type
            )
        except Exception as e:
            logging.error(f"Verification failed for {func_name} with exception: {e}")
            return None, func_interactions

        # --- Verification Result Analysis --- 
        verification_passed = False
        error_output = verification_result.output

        if verification_result.status != 0:
            error_output = verification_result.output
            verification_passed = False
        else:
            verification_passed = True

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
    return None, func_interactions # Failed after max attempts

def run_verification_process(requested_type, context_types, assistant_key="4o-mini", num_runs=10, max_iterations=10):
    """
    Run the function-by-function verification process
    """
    global verification_status # Use the global list to store errors across function calls within a run
    # Validate inputs
    if requested_type not in INTERFACE_PATHS:
        raise ValueError(f"Requested type '{requested_type}' not supported.")
    # ... (rest of validation)

    assistant_id = ASSISTANT_IDS[assistant_key]
    valid_contexts = [ct for ct in context_types if ct]
    context_str = '_'.join(valid_contexts) if valid_contexts else "none"
    file_prefix = f"fbf_{requested_type}_[{context_str}]" # Prefix for function-by-function
    results_dir = f"results_{assistant_key}/{requested_type}/{context_str}"
    os.makedirs(results_dir, exist_ok=True)

    # Load common resources
    target_interface_content = Utils.extract_content_from_markdown(INTERFACE_PATHS[requested_type])
    if not target_interface_content:
         raise ValueError(f"Could not load interface content for {requested_type}")

    parsed_components = parse_solidity_interface(target_interface_content)
    if not parsed_components['functions']:
        raise ValueError("No functions found in the interface file.")

    contract_name = requested_type.upper()

    eip_doc = Utils.extract_content_from_markdown(EIP_PATHS.get(requested_type, ""))

    base_instructions = INSTRUCTIONS

    # Generate example texts (reference specifications) based on context_types
    raw_examples_content = ""
    for ctx_type in context_types: # Iterate over the original context_types list
        if not ctx_type: # Skip if context type string is empty
            continue
        
        ref_spec_content = Utils.extract_content_from_markdown(REFERENCE_SPEC_PATHS.get(ctx_type, ""))
        if ref_spec_content:
            raw_examples_content += f"\nExample ERC {ctx_type.upper()} specification:\n\n```solidity\n{ref_spec_content}\n```\n"

    examples_section_for_prompt = ""
    if raw_examples_content:
        examples_section_for_prompt = f"\nHere are examples of similar ERC formal specifications:{raw_examples_content}"

    results = []
    max_iterations_per_function = 10 # Limit attempts per function

    for i in range(num_runs):
        print(f"\n--- Starting Run {i + 1}/{num_runs} --- ")
        run_start_time = time.time()
        
        verified_annotations = {} # Reset for each run
        function_verification_status = {} # Track status per function for this run
        verification_status = [] # Reset global error list for this run
        total_interactions = 0
        threads_info = [] # Store thread info for logging

        for func_info in parsed_components.get('functions', []):
            # Create a new thread for each function
            assistant = Assistant(assistant_id)
            thread = Thread(assistant)
            threads_info.append((func_info['name'], thread.id))
            
            # Process the function with its own dedicated thread
            func_annotations, func_interactions_count = process_single_function(
                thread=thread,
                func_info=func_info,
                components=parsed_components,
                verified_annotations=verified_annotations,
                eip_doc=eip_doc,
                base_instructions=base_instructions,
                examples_text=examples_section_for_prompt, # Pass the examples
                max_iterations_per_function=max_iterations_per_function,
                requested_type=requested_type
            )
            total_interactions += func_interactions_count

            if func_annotations:
                verified_annotations[func_info['signature']] = func_annotations
                function_verification_status[func_info['name']] = "Verified"
            else:
                function_verification_status[func_info['name']] = "Failed"
            
            # Save individual thread log for this function
            thread_save_result = save_thread_to_file(thread.id, requested_type, f"{context_str}_{func_info['name']}", assistant_key, i+1)
            if not thread_save_result:
                print(f"WARNING: Failed to save thread file for function {func_info['name']} in run {i+1}")

        run_end_time = time.time()
        duration = run_end_time - run_start_time

        # Assemble final contract (potentially partial)
        final_contract_code = assemble_partial_contract(contract_name, parsed_components, verified_annotations)
        all_functions_verified = all(status == "Verified" for status in function_verification_status.values())

        # Log information about all threads used in this run
        print(f"Run {i+1} used {len(threads_info)} threads: {', '.join([f'{name}:{tid}' for name, tid in threads_info])}")

        results.append({
            "run": i + 1,
            "time_taken": duration,
            "iterations": total_interactions,
            "verified": all_functions_verified,
            "annotated_contract": final_contract_code,
            "function_status": function_verification_status, # Add function status
            "status": verification_status, # Append the collected errors for this run
            "threads": [tid for _, tid in threads_info] # Store thread IDs
        })

    # Save results to CSV
    csv_filename = f"{results_dir}/{file_prefix}.csv"
    # Adjust save function if needed for the new structure (e.g., function_status)
    Utils.save_results_to_csv(csv_filename, results)
    return results

def main():
    parser = argparse.ArgumentParser(description='Run contract verification with different contexts')
    parser.add_argument('--requested', type=str, required=True, 
                        choices=['erc20', 'erc721', 'erc1155', 'erc123'],
                        help='The contract type to verify')
    parser.add_argument('--context', type=str, required=True,
                        help='Comma-separated list of context contract types (e.g., "erc20,erc721,erc1155,erc123")')
    parser.add_argument('--assistant', type=str, default='4o-mini',
                        choices=['4o-mini', 'erc-1155-001-3-16', 'erc-1155-005-3-16', 'erc-1155-010-3-16', 'erc-1155-001-5-16', 'erc-1155-005-5-16', 'erc-1155-010-5-16', 'erc-1155-001-7-16', 'erc-1155-005-7-16', 'erc-1155-001-7-16'],
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
