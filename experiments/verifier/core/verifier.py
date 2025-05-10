import logging
import time
import os
from typing import Dict, List, Any, Optional, Tuple

from ..config.config_manager import ConfigManager
from ..utils.file_utils import FileUtils
from ..llm.client import LLMClient, Thread
from .solidity_parser import SolidityParser
from .verification_wrapper import SolcVerifyWrapper, VerificationResult


class Verifier:
    """
    Coordinates the verification process for a contract.
    
    This class provides methods for verifying functions in a contract
    using a language model to generate annotations and a verifier to
    check the annotations.
    """
    
    def __init__(self, config: ConfigManager):
        """
        Initialize the Verifier.
        
        Args:
            config: The configuration for the verifier.
        """
        self.config = config
        self.llm_client = LLMClient(config)
    
    def verify_contract(
        self,
        requested_type: str,
        context_types: List[str],
        assistant_key: str = "4o-mini",
        num_runs: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Verify a contract.
        
        Args:
            requested_type: The type of contract to verify (e.g., "erc20").
            context_types: The context types for verification.
            assistant_key: The key for the assistant to use.
            num_runs: The number of verification runs to perform.
            
        Returns:
            A list of results, one for each run.
        """
        # Validate inputs
        if requested_type not in self.config.contract.interface_paths:
            raise ValueError(f"Requested type '{requested_type}' not supported.")
        
        valid_contexts = [ct for ct in context_types if ct]
        context_str = '_'.join(valid_contexts) if valid_contexts else "none"
        
        # Define output paths and create directories
        file_prefix = f"fbf_{requested_type}_[{context_str}]"  # Prefix for function-by-function
        results_dir = f"results_{assistant_key}/{requested_type}/{context_str}"
        os.makedirs(results_dir, exist_ok=True)
        
        # Load interface content
        interface_path = self.config.contract.interface_paths.get(requested_type)
        if not interface_path:
            raise ValueError(f"Interface path for {requested_type} not found in configuration.")
            
        interface_content = FileUtils.extract_content_from_markdown(interface_path)
        if not interface_content:
            raise ValueError(f"Could not load interface content for {requested_type}")
        
        # Parse interface
        parsed_components = SolidityParser.parse_solidity_interface(interface_content)
        if not parsed_components['functions']:
            raise ValueError("No functions found in the interface file.")
        
        # Set contract name
        contract_name = requested_type.upper()
        
        # Load EIP documentation
        eip_doc = ""
        eip_path = self.config.contract.eip_paths.get(requested_type, "")
        if eip_path:
            eip_doc = FileUtils.extract_content_from_markdown(eip_path)
        
        # Generate examples from reference specifications
        examples_text = self._load_examples(context_types)
        
        # Run verification for the specified number of runs
        results = []
        for run_num in range(num_runs):
            logging.info(f"\n--- Starting Run {run_num + 1}/{num_runs} --- ")
            
            run_start_time = time.time()
            
            # Create assistant and thread
            assistant = self.llm_client.create_assistant(assistant_key)
            thread = self.llm_client.create_thread(assistant)
            
            # Reset for each run
            verified_annotations = {}
            function_verification_status = {}
            total_interactions = 0
            
            # Process each function
            for func_info in parsed_components.get('functions', []):
                func_result = self._process_function(
                    thread=thread,
                    func_info=func_info,
                    components=parsed_components,
                    verified_annotations=verified_annotations,
                    eip_doc=eip_doc,
                    examples_text=examples_text,
                    requested_type=requested_type,
                    contract_name=contract_name
                )
                
                # Update total interactions
                total_interactions += func_result["interactions"]
                
                # Update verified annotations and status
                if func_result["success"]:
                    verified_annotations[func_info['signature']] = func_result["annotations"]
                    function_verification_status[func_info['name']] = "Verified"
                else:
                    function_verification_status[func_info['name']] = "Failed"
            
            # Calculate run duration
            run_end_time = time.time()
            duration = run_end_time - run_start_time
            
            # Assemble final contract (potentially partial)
            final_contract_code = SolidityParser.assemble_partial_contract(
                contract_name=contract_name,
                components=parsed_components,
                current_annotations=verified_annotations
            )
            
            # Check if all functions were verified
            all_functions_verified = all(status == "Verified" for status in function_verification_status.values())
            
            # Save thread log
            FileUtils.save_thread_to_file(
                thread_id=thread.id,
                requested_type=requested_type,
                context_str=context_str,
                assistant_key=assistant_key,
                run_number=run_num+1
            )
            
            # Store results
            results.append({
                "run": run_num + 1,
                "time_taken": duration,
                "iterations": total_interactions,
                "verified": all_functions_verified,
                "annotated_contract": final_contract_code,
                "function_status": function_verification_status,
                "status": []  # Placeholder for error status
            })
        
        # Save results to CSV
        csv_filename = f"{results_dir}/{file_prefix}.csv"
        FileUtils.save_results_to_csv(csv_filename, results)
        
        return results
    
    def _load_examples(self, context_types: List[str]) -> str:
        """
        Load example specifications for context types.
        
        Args:
            context_types: The context types.
            
        Returns:
            A string with example specifications.
        """
        raw_examples_content = ""
        
        for ctx_type in context_types:
            if not ctx_type:
                continue
                
            ref_spec_path = self.config.contract.reference_spec_paths.get(ctx_type, "")
            if not ref_spec_path:
                continue
                
            ref_spec_content = FileUtils.extract_content_from_markdown(ref_spec_path)
            if ref_spec_content:
                raw_examples_content += f"\nExample ERC {ctx_type.upper()} specification:\n\n```solidity\n{ref_spec_content}\n```\n"
        
        if raw_examples_content:
            return f"\nHere are examples of similar ERC formal specifications:{raw_examples_content}"
        
        return ""
    
    def _process_function(
        self,
        thread: Thread,
        func_info: Dict[str, str],
        components: Dict[str, Any],
        verified_annotations: Dict[str, str],
        eip_doc: str,
        examples_text: str,
        requested_type: str,
        contract_name: str
    ) -> Dict[str, Any]:
        """
        Process a single function to generate and verify annotations.
        
        Args:
            thread: The thread to use for the LLM interaction.
            func_info: Information about the function.
            components: Components of the contract.
            verified_annotations: Dictionary of verified annotations.
            eip_doc: EIP documentation.
            examples_text: Examples of annotations.
            requested_type: The type of contract (e.g., "erc20").
            contract_name: The name of the contract.
            
        Returns:
            A dictionary with information about the function processing.
        """
        logging.info(f"Processing function: {func_info['name']}")
        
        # Use the LLM client to generate annotations for the function
        annotations, interaction_count = self.llm_client.generate_function_annotations(
            thread=thread,
            func_info=func_info,
            contract_components=components,
            eip_doc=eip_doc,
            examples_text=examples_text,
            requested_type=requested_type,
            verified_annotations=verified_annotations
        )
        
        if not annotations:
            return {
                "success": False,
                "function": func_info['name'],
                "signature": func_info['signature'],
                "annotations": None,
                "interactions": interaction_count,
                "verification_result": None,
                "error_message": "Failed to generate annotations"
            }
        
        # Assemble contract with proposed annotations for verification
        temp_annotations = verified_annotations.copy()
        temp_annotations[func_info['signature']] = annotations
        
        partial_contract = SolidityParser.assemble_partial_contract(
            contract_name=contract_name,
            components=components,
            current_annotations=temp_annotations
        )
        
        # Verify the contract
        try:
            verification_result = SolcVerifyWrapper.verify(
                partial_contract, 
                requested_type=requested_type
            )
            
            # Analyze the verification result
            verification_passed, error_message = SolcVerifyWrapper.analyze_verification_result(
                verification_result, 
                func_info['name']
            )
            
            if verification_passed:
                logging.info(f"Successfully verified annotations for function {func_info['name']}.")
                return {
                    "success": True,
                    "function": func_info['name'],
                    "signature": func_info['signature'],
                    "annotations": annotations,
                    "interactions": interaction_count,
                    "verification_result": verification_result,
                    "error_message": None
                }
            else:
                logging.warning(f"Verification failed for function {func_info['name']}: {error_message}")
                return {
                    "success": False,
                    "function": func_info['name'],
                    "signature": func_info['signature'],
                    "annotations": annotations,
                    "interactions": interaction_count,
                    "verification_result": verification_result,
                    "error_message": error_message
                }
                
        except Exception as e:
            logging.error(f"Verification failed for {func_info['name']} with exception: {e}")
            return {
                "success": False,
                "function": func_info['name'],
                "signature": func_info['signature'],
                "annotations": annotations,
                "interactions": interaction_count,
                "verification_result": None,
                "error_message": str(e)
            } 