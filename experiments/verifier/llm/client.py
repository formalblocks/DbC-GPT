import openai
import logging
import time
import random
from typing import Optional, Dict, Any, List, Tuple
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..config.config_manager import ConfigManager


class Assistant:
    """
    Wrapper for OpenAI Assistant.
    
    This class provides a simple interface for interacting with an OpenAI Assistant.
    """
    
    def __init__(self, assistant_id: str) -> None:
        """
        Initialize the Assistant.
        
        Args:
            assistant_id: The ID of the OpenAI Assistant.
        """
        self.id = assistant_id


class Thread:
    """
    Wrapper for OpenAI Thread.
    
    This class provides a simple interface for interacting with an OpenAI Thread.
    """
    
    def __init__(self, assistant: Assistant) -> None:
        """
        Initialize the Thread.
        
        Args:
            assistant: The Assistant to use for this Thread.
        """
        self.assistant = assistant
        self._thread = self._create_thread()
    
    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError, openai.APIConnectionError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    def _create_thread(self):
        """
        Create a new Thread.
        
        Returns:
            The created Thread.
            
        Raises:
            Exception: If there was an error creating the Thread.
        """
        try:
            return openai.beta.threads.create()
        except (openai.RateLimitError, openai.APIError, openai.APIConnectionError) as e:
            logging.error(f"API error: {str(e)}. Retrying...")
            raise
    
    @property
    def id(self) -> str:
        """
        Get the ID of the Thread.
        
        Returns:
            The Thread ID.
        """
        return self._thread.id
    
    def send_message(self, content: str) -> 'Interaction':
        """
        Send a message to the Thread.
        
        Args:
            content: The content of the message.
            
        Returns:
            An Interaction object representing the interaction with the Thread.
        """
        interaction = Interaction(self, content)
        return interaction
    
    @property
    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError, openai.APIConnectionError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    def last_message(self) -> str:
        """
        Get the last message from the Thread.
        
        Returns:
            The content of the last message.
        """
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
    """
    Wrapper for an interaction with an OpenAI Thread.
    
    This class provides a simple interface for interacting with an OpenAI Thread.
    """
    
    def __init__(self, thread: Thread, prompt: str) -> None:
        """
        Initialize the Interaction.
        
        Args:
            thread: The Thread to interact with.
            prompt: The prompt to send to the Thread.
        """
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
        """
        Create a message in the Thread.
        
        Raises:
            Exception: If there was an error creating the message.
        """
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
        """
        Create a run in the Thread.
        
        Raises:
            Exception: If there was an error creating the run.
        """
        try:
            self._run = openai.beta.threads.runs.create(
                thread_id = self.thread.id,
                assistant_id = self.thread.assistant.id,
            )
        except (openai.RateLimitError, openai.APIError, openai.APIConnectionError) as e:
            logging.error(f"API error: {str(e)}. Retrying...")
            raise
    
    @property
    def id(self) -> str:
        """
        Get the ID of the Interaction.
        
        Returns:
            The Interaction ID.
        """
        return self._run.id
    
    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError, openai.APIConnectionError)),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    def remote_sync(self):
        """
        Sync the Interaction with the remote state.
        
        Raises:
            Exception: If there was an error syncing the Interaction.
        """
        try:
            self._run = openai.beta.threads.runs.retrieve(
                thread_id = self.thread.id,
                run_id = self._run.id
            )
        except (openai.RateLimitError, openai.APIError, openai.APIConnectionError) as e:
            logging.error(f"API error: {str(e)}. Retrying...")
            raise
    
    @property
    def status(self) -> str:
        """
        Get the status of the Interaction.
        
        Returns:
            The status of the Interaction.
        """
        return self._run.status
    
    def await_for_response(self) -> str:
        """
        Wait for a response from the Interaction.
        
        Returns:
            The response from the Interaction.
        """
        status = self.status
        while (status != "completed"):
            try:
                self.remote_sync()
                status = self.status
                logging.info(f"Awaiting for a response. Status: {status}")
                
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


class LLMClient:
    """
    Client for interacting with OpenAI's API.
    
    This class provides methods for generating annotations for functions
    using OpenAI's API.
    """
    
    # Instructions for the LLM
    BASE_INSTRUCTIONS = """
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
    
    def __init__(self, config: ConfigManager):
        """
        Initialize the LLMClient.
        
        Args:
            config: The configuration for the client.
        """
        self.config = config
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        openai.api_key = self.openai_api_key
    
    def create_assistant(self, assistant_key: str) -> Assistant:
        """
        Create an Assistant.
        
        Args:
            assistant_key: The key for the assistant to create.
            
        Returns:
            The created Assistant.
        """
        assistant_id = self.config.get_assistant_id(assistant_key)
        return Assistant(assistant_id)
    
    def create_thread(self, assistant: Assistant) -> Thread:
        """
        Create a Thread.
        
        Args:
            assistant: The Assistant to use for the Thread.
            
        Returns:
            The created Thread.
        """
        return Thread(assistant)
    
    def generate_function_annotations(
        self, 
        thread: Thread, 
        func_info: Dict[str, str],
        contract_components: Dict[str, Any],
        eip_doc: str,
        examples_text: str,
        requested_type: str,
        verified_annotations: Dict[str, str] = None
    ) -> Tuple[Optional[str], int]:
        """
        Generate annotations for a function.
        
        Args:
            thread: The Thread to use for generating annotations.
            func_info: Information about the function.
            contract_components: Components of the contract.
            eip_doc: EIP documentation.
            examples_text: Examples of annotations.
            requested_type: The type of contract (e.g., "erc20").
            verified_annotations: Dictionary of already verified annotations.
            
        Returns:
            A tuple of (proposed_annotations, interaction_count).
                proposed_annotations: The proposed annotations for the function, or None if no annotations could be generated.
                interaction_count: The number of interactions with the LLM.
        """
        from ..utils.file_utils import FileUtils
        from ..core.solidity_parser import SolidityParser
        from ..core.verification_wrapper import SolcVerifyWrapper
        
        func_sig = func_info['signature']
        func_name = func_info['name']
        contract_name = requested_type.upper()
        logging.info(f"Processing function: {func_name} ({func_sig})")
        
        # Ensure we have a dictionary of verified annotations
        if verified_annotations is None:
            verified_annotations = {}
            
        # Track interactions for this function
        interaction_count = 0
        
        # Indent state variables for contract display
        indented_state_vars = "\n".join([f"    {var}" for var in contract_components.get('state_vars', [])])
        
        # Extract EIP snippet specific to the current function
        specific_eip_snippet = "No specific EIP segment found for this function."
        if eip_doc and func_name:
            # Regex to find the function-specific documentation
            import re
            pattern = rf"(/\*\*(?:[^*]|\*(?!/))*?\*/\s*function\s+{re.escape(func_name)}\s*\(.*\).*?;)"
            match = re.search(pattern, eip_doc, re.DOTALL)
            if match:
                specific_eip_snippet = match.group(1).strip()
        
        # Check for a function-specific markdown file
        func_md_content = FileUtils.load_function_template(requested_type, func_name)
        
        # Format prompt based on whether a function-specific file exists
        if func_md_content:
            logging.info(f"Found function-specific file for {func_name}")
            prompt = f"""{self.BASE_INSTRUCTIONS}

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
</eip>"""
        else:
            logging.info(f"No function-specific file found for {func_name}")
            prompt = f"""{self.BASE_INSTRUCTIONS}

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
</eip>"""
        
        if examples_text:
            prompt += f"\n**Examples:**\n{examples_text}"
        
        # Send the prompt to the LLM and verify the results in a loop
        max_attempts = self.config.verifier.max_iterations_per_function
        
        for attempt in range(max_attempts):
            logging.info(f"Attempt {attempt + 1}/{max_attempts} for function {func_name}")
            
            # Send the prompt to the LLM
            interaction = thread.send_message(prompt)
            response = interaction.await_for_response()
            interaction_count += 1
            
            # Extract annotations from the response
            proposed_annotations = SolidityParser.extract_annotations_for_function(response, func_sig)
            
            if not proposed_annotations:
                logging.error(f"No annotations extracted for {func_name}. LLM response: {response[:500]}")
                
                # Ask LLM to provide only annotations
                prompt = f"Your previous response did not seem to contain just the annotations for `{func_sig}`. Please provide ONLY the `/// @notice postcondition ...` lines for this function. Do not include the function signature or any other text."
                continue
            
            # Assemble the contract with proposed annotations for verification
            temp_annotations = verified_annotations.copy()
            temp_annotations[func_sig] = proposed_annotations
            
            # Assemble the partial contract for verification
            partial_contract = self._assemble_partial_contract(
                contract_name, 
                contract_components, 
                temp_annotations, 
                func_sig
            )
            
            try:
                # Verify the contract
                verification_result = SolcVerifyWrapper.verify(
                    partial_contract,
                    requested_type=requested_type
                )
                
                # Check if verification passed
                verification_passed = False
                error_output = verification_result.output
                
                if verification_result.status == 0:
                    verification_passed = True
                else:
                    # Filter out benign warnings
                    benign_warning_patterns = [
                        r'Warning: Unused function parameter',
                        r'Warning: Unused local variable',
                        r'Warning: Function state mutability can be restricted',
                        r'Warning: This is a pre-release compiler version'
                    ]
                    
                    # Check for actual errors
                    critical_errors = []
                    for line in error_output.strip().split('\n'):
                        is_benign = False
                        for pattern in benign_warning_patterns:
                            if re.search(pattern, line):
                                is_benign = True
                                break
                        
                        if not is_benign and line.strip():
                            if f"::{func_name}:" in line or f"Annotation for {func_name}" in line or "solc-verify error:" in line:
                                critical_errors.append(line)
                    
                    # If only benign warnings, treat as success
                    if not critical_errors:
                        logging.warning(f"Verification status non-zero, but only benign warnings detected for {func_name}. Treating as success.")
                        verification_passed = True
                    else:
                        logging.warning(f"Verification failed for {func_name} with critical errors/warnings:")
                        for err_line in critical_errors:
                            logging.warning(f"  - {err_line}")
                
                if verification_passed:
                    logging.info(f"Successfully verified annotations for function {func_name}.")
                    return proposed_annotations, interaction_count
                else:
                    # Verification failed, provide feedback to the LLM
                    logging.warning(f"Verification failed for function {func_name} (Attempt {attempt + 1}). Error: {error_output[:500]}...")
                    
                    # Construct feedback prompt
                    prompt = f"""
Verification failed for function `{func_sig}` with your proposed annotations:

The verifier found the following errors:
```
{error_output}
```

Can you fix the specification accordingly?
"""
            except Exception as e:
                logging.error(f"Verification process failed with exception: {str(e)}")
                # Provide error feedback to the LLM
                prompt = f"""
An error occurred during verification:
```
{str(e)}
```

Please revise your annotations for `{func_sig}` to address this issue.
"""
        
        # Failed after max attempts
        logging.error(f"Failed to verify annotations for function {func_name} after {max_attempts} attempts.")
        return None, interaction_count
    
    def _assemble_partial_contract(
        self, 
        contract_name: str, 
        components: Dict[str, Any], 
        current_annotations: Dict[str, str], 
        target_func_sig: str = None
    ) -> str:
        """
        Assembles a partial contract string for verification.
        
        Args:
            contract_name: The name of the contract.
            components: The components of the contract.
            current_annotations: Dictionary of function signatures to annotations.
            target_func_sig: Optional signature of the function being actively verified.
            
        Returns:
            A string containing the assembled contract.
        """
        code = f"pragma solidity >= 0.5.0;\n\ncontract {contract_name} {{\n\n"

        # Add Events
        if components.get('events', []):
            code += "    // Events\n"
            for event in components.get('events', []):
                code += f"    {event}\n"
            code += "\n"

        # Add State Variables
        if components.get('state_vars', []):
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
                pass
            else:
                # Add placeholder for functions not yet processed or failed
                code += "    /// @notice postcondition true\n"

            code += f"    {func_sig}\n\n"  # Add function signature

        code += "}\n"
        return code 