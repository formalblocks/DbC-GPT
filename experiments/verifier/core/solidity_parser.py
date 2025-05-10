import re
import logging
from typing import Dict, List, Any, Optional, Tuple


class SolidityParser:
    """
    Parser for Solidity code.
    
    This class provides methods for parsing Solidity code and extracting components.
    """
    
    @staticmethod
    def parse_solidity_interface(solidity_code: str) -> Dict[str, Any]:
        """
        Parse Solidity interface code to extract components.
        
        Args:
            solidity_code: The Solidity code to parse.
            
        Returns:
            A dictionary containing 'state_vars', 'events', 'functions'.
            Functions value is a list of {'signature': str, 'name': str}.
        """
        if not solidity_code:
            logging.error("No Solidity code provided for parsing")
            return {
                'state_vars': [],
                'events': [],
                'functions': []
            }
            
        components = {
            'state_vars': [],
            'events': [],
            'functions': []
        }

        # Extract state variables
        # Matches lines like: mapping(...) private _variable; string private _uri; uint256 constant VALUE = 10;
        state_var_pattern = re.compile(
            r"^\s*(mapping\(.+?\)|bytes32|uint\d*|int\d*|string|address|bool|bytes)\s+"
            r"(public|private|internal|constant)?\s*(\w+)\s*(?:=.*?)?;", 
            re.MULTILINE
        )
        
        for match in state_var_pattern.finditer(solidity_code):
            components['state_vars'].append(match.group(0).strip())

        # Extract events
        event_pattern = re.compile(r"^\s*event\s+(\w+)\((.*?)\);", re.MULTILINE | re.DOTALL)
        for match in event_pattern.finditer(solidity_code):
            components['events'].append(match.group(0).strip())

        # Extract functions (including modifiers and return types)
        function_pattern = re.compile(
            r"^\s*function\s+(?P<name>\w+)\s*\((?P<params>.*?)\)\s*(?P<modifiers>.*?)\s*"
            r"(?:returns\s*\((?P<returns>.*?)\))?\s*;",
            re.MULTILINE | re.DOTALL
        )

        for match in function_pattern.finditer(solidity_code):
            func_dict = match.groupdict()
            signature = f"function {func_dict['name']}({func_dict['params'].strip()}) {func_dict['modifiers'].strip()}"
            if func_dict['returns']:
                signature += f" returns ({func_dict['returns'].strip()})"
            signature += ";"
            
            components['functions'].append({
                'signature': signature.strip(), 
                'name': func_dict['name']
            })

        logging.info(
            f"Parsed components: {len(components['state_vars'])} state vars, "
            f"{len(components['events'])} events, {len(components['functions'])} functions."
        )
        
        return components
    
    @staticmethod
    def extract_annotations_for_function(llm_response: str, target_func_sig: str) -> Optional[str]:
        """
        Extract annotations from an LLM response.
        
        The LLM response might include a complete contract snippet, markdown, etc.
        This function will extract ONLY the lines starting with "///" or "/*".
        
        Args:
            llm_response: The LLM response.
            target_func_sig: The target function signature.
            
        Returns:
            The extracted annotations, or None if no annotations were found.
        """
        if not llm_response or not llm_response.strip():
            logging.warning(f"LLM response for {target_func_sig} is empty or whitespace.")
            return None

        processed_llm_response = llm_response.strip()
        
        # Check for markdown code blocks
        code_block_match = re.search(r"```(?:solidity)?\s*(.*?)```", processed_llm_response, re.DOTALL)
        if code_block_match:
            # Extract content from the code block
            content_to_process = code_block_match.group(1).strip()
            logging.debug("Extracted content from markdown code block")
        else:
            # No code block found, process the entire response
            content_to_process = processed_llm_response
            logging.debug("No markdown code block found, processing entire response")
        
        # Split the content into lines
        all_lines = content_to_process.split('\n')
        
        # Only collect lines that start with /// or /*
        annotation_lines = []
        for line in all_lines:
            stripped_line = line.strip()  # Remove leading/trailing whitespace
            logging.debug(f"Processing line: {repr(stripped_line)}")
            
            if stripped_line.startswith("///") or stripped_line.startswith("/*"):
                logging.debug(f"Found annotation line: {repr(stripped_line)}")
                # Remove any trailing semicolon
                if stripped_line.endswith(';'):
                    annotation_lines.append(stripped_line[:-1])
                else:
                    annotation_lines.append(stripped_line)
        
        if not annotation_lines:
            logging.warning(f"No annotation lines found in the response for {target_func_sig}")
            return None
        
        # Join the annotation lines with newlines
        final_annotations_str = "\n".join(annotation_lines)
        logging.debug(f"Final annotations string: {repr(final_annotations_str)}")
        return final_annotations_str
    
    @staticmethod
    def assemble_partial_contract(
        contract_name: str, 
        components: Dict[str, Any], 
        current_annotations: Dict[str, str], 
        target_func_sig: Optional[str] = None
    ) -> str:
        """
        Assemble a partial contract string for verification.
        
        Args:
            contract_name: The name of the contract.
            components: The components of the contract.
            current_annotations: The current annotations for functions.
            target_func_sig: The target function signature.
            
        Returns:
            The assembled contract code.
        """
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
                # Placeholder for the function being actively verified
                pass  # Annotations will be added just before verification call
            else:
                # Add placeholder for functions not yet processed or failed
                code += "    /// @notice postcondition true\n"

            code += f"    {func_sig}\n\n"  # Add function signature

        code += "}\n"
        return code 