#!/usr/bin/env python3

import random
import re
from typing import List, Dict, Tuple, Optional

class ErrorInjector:
    """Class for injecting common errors into formal verification conditions"""
    
    def __init__(self):
        # Common error types and their injection methods
        self.error_types = {
            "missing_condition": self._remove_random_condition,
            "incorrect_comparison": self._change_comparison_operator,
            "incorrect_variable": self._change_variable_name,
            "missing_old_reference": self._remove_old_reference,
            "incorrect_logical_operator": self._change_logical_operator,
            "missing_revert_condition": self._remove_revert_condition,
            "invalid_arithmetic": self._introduce_arithmetic_error,
            "swapped_variables": self._swap_variables
        }
        
        # Track the last error type that was injected
        self.last_error_type = None
        
        # Mapping of function names to common state variables for each ERC standard
        self.function_state_mapping = {
            "erc20": {
                "transfer": ["_balances", "_totalSupply"],
                "transferFrom": ["_balances", "_allowed", "_totalSupply"],
                "approve": ["_allowed"],
                "balanceOf": ["_balances"],
                "allowance": ["_allowed"]
            },
            "erc721": {
                "safeTransferFrom": ["_tokenOwner", "_ownedTokensCount", "_tokenApprovals"],
                "transferFrom": ["_tokenOwner", "_ownedTokensCount", "_tokenApprovals"],
                "approve": ["_tokenApprovals", "_tokenOwner"],
                "setApprovalForAll": ["_operatorApprovals"],
                "balanceOf": ["_ownedTokensCount"],
                "ownerOf": ["_tokenOwner"],
                "getApproved": ["_tokenApprovals"],
                "isApprovedForAll": ["_operatorApprovals"]
            },
            "erc1155": {
                "safeTransferFrom": ["_balances"],
                "safeBatchTransferFrom": ["_balances"],
                "balanceOf": ["_balances"],
                "balanceOfBatch": ["_balances"],
                "setApprovalForAll": ["_operatorApprovals"],
                "isApprovedForAll": ["_operatorApprovals"]
            }
        }

    def inject_error(self, contract: str, erc_standard: str, function_name: str = None) -> str:
        """
        Inject an error into a contract's postconditions
        
        Args:
            contract: The solidity contract code
            erc_standard: The ERC standard (erc20, erc721, erc1155)
            function_name: Target function name (optional)
            
        Returns:
            Modified contract with errors in postconditions
        """
        # Extract all postconditions from the contract
        postconditions = self._extract_postconditions(contract)
        
        # If no postconditions found, return original contract
        if not postconditions:
            return contract
        
        # If function name is not provided, infer it from postconditions
        if not function_name:
            function_name = self._infer_function_name(postconditions, erc_standard)
        
        # Choose an error type to inject
        error_types = list(self.error_types.keys())
        error_type = random.choice(error_types)
        self.last_error_type = error_type
        
        # Apply the error injection
        error_injection_method = self.error_types[error_type]
        modified_contract = error_injection_method(
            contract, 
            postconditions, 
            erc_standard,
            function_name
        )
        
        return modified_contract

    def _extract_postconditions(self, contract: str) -> List[Tuple[str, int]]:
        """
        Extract all postconditions from a contract with their line numbers
        
        Returns:
            List of tuples (postcondition, line_number)
        """
        postconditions = []
        lines = contract.split('\n')
        
        for i, line in enumerate(lines):
            if "@notice postcondition" in line:
                postconditions.append((line, i))
        
        return postconditions

    def _infer_function_name(self, postconditions: List[Tuple[str, int]], erc_standard: str) -> str:
        """Infer function name based on postconditions and ERC standard"""
        # Default fallback
        default_functions = {
            "erc20": "transfer",
            "erc721": "transferFrom",
            "erc1155": "safeTransferFrom"
        }
        
        # Try to infer from postconditions
        for postcondition, _ in postconditions:
            # Check for state variables that are unique to functions
            for function, state_vars in self.function_state_mapping.get(erc_standard, {}).items():
                for var in state_vars:
                    if var in postcondition:
                        return function
        
        # Return default function if we couldn't infer
        return default_functions.get(erc_standard, "transfer")

    def _remove_random_condition(self, contract: str, postconditions: List[Tuple[str, int]], 
                                erc_standard: str, function_name: str) -> str:
        """Remove a random postcondition"""
        if len(postconditions) <= 1:
            # Don't remove the only postcondition
            return contract
        
        # Choose a random postcondition to remove
        post_to_remove, line_num = random.choice(postconditions)
        
        # Remove the line from the contract
        lines = contract.split('\n')
        lines.pop(line_num)
        
        return '\n'.join(lines)

    def _change_comparison_operator(self, contract: str, postconditions: List[Tuple[str, int]], 
                                   erc_standard: str, function_name: str) -> str:
        """Change a comparison operator in a postcondition"""
        # Map of operators and their replacements
        operators = {
            "==": "!=",
            "!=": "==",
            "<=": ">",
            ">=": "<",
            ">": "<=",
            "<": ">="
        }
        
        # Choose a random postcondition
        if not postconditions:
            return contract
        
        post, line_num = random.choice(postconditions)
        
        # Find all operators in the postcondition
        all_operators = []
        for op in operators.keys():
            matches = re.finditer(r'(?<![=!<>])' + re.escape(op) + r'(?![=!<>])', post)
            all_operators.extend([(op, m.start()) for m in matches])
        
        if not all_operators:
            return contract  # No operators found
        
        # Choose an operator to replace
        op_to_replace, start_pos = random.choice(all_operators)
        replacement = operators[op_to_replace]
        
        # Replace the operator
        modified_post = post[:start_pos] + replacement + post[start_pos + len(op_to_replace):]
        
        # Update the contract
        lines = contract.split('\n')
        lines[line_num] = modified_post
        
        return '\n'.join(lines)

    def _change_variable_name(self, contract: str, postconditions: List[Tuple[str, int]], 
                             erc_standard: str, function_name: str) -> str:
        """Change a variable name in a postcondition"""
        if not postconditions:
            return contract
        
        # Get common variables for this function
        common_vars = self.function_state_mapping.get(erc_standard, {}).get(function_name, [])
        if not common_vars:
            return contract
        
        # Choose a random postcondition
        post, line_num = random.choice(postconditions)
        
        # Find variables in the postcondition that match our common vars
        found_vars = []
        for var in common_vars:
            if var in post:
                found_vars.append(var)
        
        if not found_vars:
            return contract  # No matching variables found
        
        # Choose a variable to replace
        var_to_replace = random.choice(found_vars)
        
        # Generate an incorrect version of the variable
        if var_to_replace.startswith('_'):
            replacement = var_to_replace[1:]  # Remove underscore
        else:
            replacement = '_' + var_to_replace  # Add underscore
        
        # Replace the variable
        modified_post = post.replace(var_to_replace, replacement)
        
        # Update the contract
        lines = contract.split('\n')
        lines[line_num] = modified_post
        
        return '\n'.join(lines)

    def _remove_old_reference(self, contract: str, postconditions: List[Tuple[str, int]], 
                             erc_standard: str, function_name: str) -> str:
        """Remove __verifier_old_uint reference from a postcondition"""
        if not postconditions:
            return contract
        
        # Filter postconditions containing __verifier_old_uint
        old_refs = [(p, ln) for p, ln in postconditions if "__verifier_old_uint" in p]
        
        if not old_refs:
            return contract  # No __verifier_old_uint references found
        
        # Choose a random postcondition with an old reference
        post, line_num = random.choice(old_refs)
        
        # Replace __verifier_old_uint([var]) with just [var]
        modified_post = re.sub(r'__verifier_old_uint\(([^)]+)\)', r'\1', post)
        
        # Update the contract
        lines = contract.split('\n')
        lines[line_num] = modified_post
        
        return '\n'.join(lines)

    def _change_logical_operator(self, contract: str, postconditions: List[Tuple[str, int]], 
                                erc_standard: str, function_name: str) -> str:
        """Change a logical operator (&&, ||) in a postcondition"""
        # Map of operators and their replacements
        operators = {
            "&&": "||",
            "||": "&&"
        }
        
        # Choose a random postcondition
        if not postconditions:
            return contract
        
        post, line_num = random.choice(postconditions)
        
        # Find all logical operators in the postcondition
        all_operators = []
        for op in operators.keys():
            matches = re.finditer(r'(?<![&|])' + re.escape(op) + r'(?![&|])', post)
            all_operators.extend([(op, m.start()) for m in matches])
        
        if not all_operators:
            return contract  # No logical operators found
        
        # Choose an operator to replace
        op_to_replace, start_pos = random.choice(all_operators)
        replacement = operators[op_to_replace]
        
        # Replace the operator
        modified_post = post[:start_pos] + replacement + post[start_pos + len(op_to_replace):]
        
        # Update the contract
        lines = contract.split('\n')
        lines[line_num] = modified_post
        
        return '\n'.join(lines)

    def _remove_revert_condition(self, contract: str, postconditions: List[Tuple[str, int]], 
                                erc_standard: str, function_name: str) -> str:
        """Remove revert or success condition from a postcondition"""
        if not postconditions:
            return contract
        
        # Filter postconditions containing success/revert conditions
        success_refs = [(p, ln) for p, ln in postconditions if "success" in p or "revert" in p or "!success" in p]
        
        if not success_refs:
            return contract  # No success/revert conditions found
        
        # Choose a random postcondition with success/revert
        post, line_num = random.choice(success_refs)
        
        # Remove "|| !success" or "&& success" or similar patterns
        patterns = [
            r'\s*\|\|\s*!success', 
            r'\s*&&\s*success',
            r'\s*\|\|\s*revert',
            r'revert\s*'
        ]
        
        for pattern in patterns:
            if re.search(pattern, post):
                modified_post = re.sub(pattern, '', post)
                
                # Update the contract
                lines = contract.split('\n')
                lines[line_num] = modified_post
                
                return '\n'.join(lines)
        
        return contract

    def _introduce_arithmetic_error(self, contract: str, postconditions: List[Tuple[str, int]], 
                                   erc_standard: str, function_name: str) -> str:
        """Change arithmetic operators or introduce incorrect math in a postcondition"""
        if not postconditions:
            return contract
        
        # Choose a random postcondition
        post, line_num = random.choice(postconditions)
        
        # Look for subtraction patterns like "var - value"
        subtract_match = re.search(r'([_a-zA-Z0-9\[\]]+)\s*-\s*([_a-zA-Z0-9\[\]]+)', post)
        if subtract_match:
            # Replace subtraction with addition
            modified_post = post.replace(
                f"{subtract_match.group(1)} - {subtract_match.group(2)}", 
                f"{subtract_match.group(1)} + {subtract_match.group(2)}"
            )
            
            # Update the contract
            lines = contract.split('\n')
            lines[line_num] = modified_post
            
            return '\n'.join(lines)
        
        # Look for addition patterns like "var + value"
        add_match = re.search(r'([_a-zA-Z0-9\[\]]+)\s*\+\s*([_a-zA-Z0-9\[\]]+)', post)
        if add_match:
            # Replace addition with subtraction
            modified_post = post.replace(
                f"{add_match.group(1)} + {add_match.group(2)}", 
                f"{add_match.group(1)} - {add_match.group(2)}"
            )
            
            # Update the contract
            lines = contract.split('\n')
            lines[line_num] = modified_post
            
            return '\n'.join(lines)
        
        return contract

    def _swap_variables(self, contract: str, postconditions: List[Tuple[str, int]], 
                       erc_standard: str, function_name: str) -> str:
        """Swap two variables in a postcondition"""
        if not postconditions:
            return contract
        
        # Choose a random postcondition
        post, line_num = random.choice(postconditions)
        
        # Match variables that could be swapped
        # Look for patterns like state[addrA] == state[addrB] or similar
        match = re.search(r'([_a-zA-Z0-9\[\]]+)(\[[_a-zA-Z0-9\[\]]+\])(\[\S+\])?\s*==\s*([_a-zA-Z0-9\[\]]+)(\[[_a-zA-Z0-9\[\]]+\])(\[\S+\])?', post)
        if match:
            # Check if we can swap address indices
            if match.group(2) and match.group(5):
                # Swap the address indices
                left_var = f"{match.group(1)}{match.group(5)}"
                if match.group(3):
                    left_var += match.group(3)
                
                right_var = f"{match.group(4)}{match.group(2)}"
                if match.group(6):
                    right_var += match.group(6)
                
                modified_post = post.replace(
                    f"{match.group(1)}{match.group(2)}{match.group(3) or ''} == {match.group(4)}{match.group(5)}{match.group(6) or ''}",
                    f"{left_var} == {right_var}"
                )
                
                # Update the contract
                lines = contract.split('\n')
                lines[line_num] = modified_post
                
                return '\n'.join(lines)
        
        return contract 