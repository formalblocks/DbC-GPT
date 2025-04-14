#!/usr/bin/env python3

import os
import json
import random
from typing import Dict, List, Any, Tuple
import re
from jinja2 import Template

class ERC20Generator:
    """Generator for ERC20 verification examples"""
    
    def __init__(self):
        # Base template for ERC20 contract
        self.template_path = os.path.join(
            "experiments", "solc_verify_generator", "ERC20", "imp", "ERC20_template.sol"
        )
        
        # Load the base template
        with open(self.template_path, 'r') as f:
            self.base_template = f.read()
        
        # Initialize the basic post-conditions for ERC20 functions
        self.basic_postconditions = {
            "transfer": [
                "/// @notice postcondition (_balances[msg.sender] == __verifier_old_uint(_balances[msg.sender]) - _value && _balances[_to] == __verifier_old_uint(_balances[_to]) + _value && success) || !success",
                "/// @notice postcondition msg.sender == _to || (_balances[msg.sender] == __verifier_old_uint(_balances[msg.sender]) - _value && success) || !success",
                "/// @notice postcondition msg.sender == _to || (_balances[_to] == __verifier_old_uint(_balances[_to]) + _value && success) || !success",
                "/// @notice postcondition msg.sender != _to || (_balances[msg.sender] == __verifier_old_uint(_balances[msg.sender]) && success) || !success",
                "/// @notice postcondition _value <= __verifier_old_uint(_balances[msg.sender]) || !success"
            ],
            "transferFrom": [
                "/// @notice postcondition (_balances[_from] == __verifier_old_uint(_balances[_from]) - _value && _balances[_to] == __verifier_old_uint(_balances[_to]) + _value && success) || !success",
                "/// @notice postcondition (_from == _to) || (_balances[_from] == __verifier_old_uint(_balances[_from]) - _value && success) || !success",
                "/// @notice postcondition (_from == _to) || (_balances[_to] == __verifier_old_uint(_balances[_to]) + _value && success) || !success",
                "/// @notice postcondition (_from == _to) || (_balances[_from] == __verifier_old_uint(_balances[_from]) - _value && _balances[_to] == __verifier_old_uint(_balances[_to]) + _value && success) || !success",
                "/// @notice postcondition _value <= __verifier_old_uint(_allowed[_from][msg.sender]) || !success || _from == msg.sender",
                "/// @notice postcondition _value <= __verifier_old_uint(_balances[_from]) || !success",
                "/// @notice postcondition (_allowed[_from][msg.sender] == __verifier_old_uint(_allowed[_from][msg.sender]) - _value && success) || !success || _from == msg.sender"
            ],
            "approve": [
                "/// @notice postcondition _allowed[msg.sender][_spender] == _value",
                "/// @notice postcondition success"
            ],
            "balanceOf": [
                "/// @notice postcondition balance == _balances[_owner]"
            ],
            "allowance": [
                "/// @notice postcondition remaining == _allowed[_owner][_spender]"
            ],
            "totalSupply": [
                "/// @notice postcondition supply == _totalSupply"
            ]
        }
        
        # Edge case parameters for ERC20 functions
        self.edge_parameters = {
            "transfer": {
                "_to": ["address(0)", "msg.sender"],
                "_value": ["0", "1", "2**256-1", "_balances[msg.sender]"]
            },
            "transferFrom": {
                "_from": ["msg.sender", "address(0)"],
                "_to": ["address(0)", "_from"],
                "_value": ["0", "1", "2**256-1", "_balances[_from]", "_allowed[_from][msg.sender]"]
            },
            "approve": {
                "_spender": ["address(0)", "msg.sender"],
                "_value": ["0", "1", "2**256-1"]
            }
        }

    def generate_basic_example(self, index: int) -> Dict:
        """Generate a basic ERC20 example with standard postconditions"""
        # Choose a random ERC20 function to focus on
        function_name = random.choice(list(self.basic_postconditions.keys()))
        
        # Get the postconditions for this function
        postconditions = self.basic_postconditions[function_name]
        
        # Create the contract
        contract = self._create_contract_with_postconditions(
            function_name, 
            postconditions
        )
        
        # Create the example
        example = {
            "id": f"erc20_basic_{index}",
            "category": "basic",
            "erc_type": "erc20",
            "contract": contract,
            "function_name": function_name
        }
        
        return example

    def generate_edge_example(self, index: int) -> Dict:
        """Generate an edge case example for ERC20"""
        # Choose a function that has edge cases defined
        function_name = random.choice(list(self.edge_parameters.keys()))
        
        # Get basic postconditions for this function
        postconditions = self.basic_postconditions[function_name]
        
        # Choose edge case parameters
        edge_params = {}
        for param, values in self.edge_parameters[function_name].items():
            # 50% chance to use an edge value
            if random.random() < 0.5:
                edge_params[param] = random.choice(values)
        
        # Add edge-specific postconditions
        edge_postconditions = self._generate_edge_postconditions(function_name, edge_params)
        
        # Combine basic and edge postconditions
        all_postconditions = postconditions + edge_postconditions
        
        # Create the contract
        contract = self._create_contract_with_postconditions(
            function_name, 
            all_postconditions,
            edge_params
        )

        # Create the example
        example = {
            "id": f"erc20_edge_{index}",
            "category": "edge",
            "erc_type": "erc20",
            "contract": contract,
            "function_name": function_name,
            "edge_params": edge_params
        }
        
        return example

    def _generate_edge_postconditions(self, function_name: str, edge_params: Dict[str, str]) -> List[str]:
        """Generate additional postconditions for edge cases"""
        additional_postconditions = []
        
        # Handle different edge cases based on function
        if function_name == "transfer":
            # Zero value transfer
            if edge_params.get("_value") == "0":
                additional_postconditions.append(
                    "/// @notice postcondition _balances[msg.sender] == __verifier_old_uint(_balances[msg.sender]) && _balances[_to] == __verifier_old_uint(_balances[_to]) && success"
                )
            
            # Self transfer
            if edge_params.get("_to") == "msg.sender":
                additional_postconditions.append(
                    "/// @notice postcondition _balances[msg.sender] == __verifier_old_uint(_balances[msg.sender]) && success"
                )
            
            # Transfer to zero address
            if edge_params.get("_to") == "address(0)":
                additional_postconditions.append("/// @notice postcondition !success")
            
        elif function_name == "transferFrom":
            # Zero value transferFrom
            if edge_params.get("_value") == "0":
                additional_postconditions.append(
                    "/// @notice postcondition _balances[_from] == __verifier_old_uint(_balances[_from]) && _balances[_to] == __verifier_old_uint(_balances[_to]) && success"
                )
            
            # Self transferFrom (from == to)
            if edge_params.get("_to") == "_from":
                additional_postconditions.append(
                    "/// @notice postcondition _balances[_from] == __verifier_old_uint(_balances[_from]) && success"
                )
            
            # Transfer from zero address
            if edge_params.get("_from") == "address(0)":
                additional_postconditions.append("/// @notice postcondition !success")
                
            # Transfer to zero address
            if edge_params.get("_to") == "address(0)":
                additional_postconditions.append("/// @notice postcondition !success")
            
        elif function_name == "approve":
            # Zero value approval
            if edge_params.get("_value") == "0":
                additional_postconditions.append(
                    "/// @notice postcondition _allowed[msg.sender][_spender] == 0"
                )
            
            # Self approval
            if edge_params.get("_spender") == "msg.sender":
                additional_postconditions.append(
                    "/// @notice postcondition _allowed[msg.sender][msg.sender] == _value"
                )
                
        return additional_postconditions

    def _create_contract_with_postconditions(
        self, 
        target_function: str, 
        postconditions: List[str],
        edge_params: Dict[str, str] = None
    ) -> str:
        """Create a contract with the specified postconditions for a function"""
        # Start with the base template
        contract = self.base_template
        # Replace the placeholder for the target function with postconditions
        function_placeholder = f"${target_function}"
        postconditions_str = "\n".join(postconditions)
        contract = contract.replace(function_placeholder, postconditions_str)
        
        # Replace other function placeholders with empty strings
        for func in self.basic_postconditions.keys():
            if func != target_function:
                contract = contract.replace(f"${func}", "")
        
        # If we have edge parameters, we need to modify the implementation
        if edge_params and target_function in ["transfer", "transferFrom", "approve"]:
            # Find the function implementation
            func_pattern = rf'function {target_function}\(.*?\)\s+public\s+returns\s+\(bool\s+success\)\s+{{'
            func_match = re.search(func_pattern, contract, re.DOTALL)
            
            if func_match:
                # Extract the full function text
                func_start = func_match.start()
                open_braces = 1
                func_end = func_start + func_match.end() - func_match.start()
                
                # Find the end of the function by tracking braces
                while open_braces > 0 and func_end < len(contract):
                    if contract[func_end] == '{':
                        open_braces += 1
                    elif contract[func_end] == '}':
                        open_braces -= 1
                    func_end += 1
                
                # Get the full function text
                full_func = contract[func_start:func_end]
                
                # Modify the function based on edge parameters
                for param, value in edge_params.items():
                    # Add special handling for edge cases
                    if param == "_to" and value == "address(0)":
                        # Add check for zero address
                        modified_func = full_func.replace(
                            "{", 
                            "{\n        // Edge case: transfer to zero address\n        require(_to != address(0), \"ERC20: transfer to the zero address\");\n"
                        )
                        contract = contract.replace(full_func, modified_func)
                    
                    # Additional edge case handling can be added here
        
        
        return contract