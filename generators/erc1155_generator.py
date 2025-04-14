#!/usr/bin/env python3

import os
import json
import random
from typing import Dict, List, Any, Tuple
import re
from jinja2 import Template

class ERC1155Generator:
    """Generator for ERC1155 verification examples"""
    
    def __init__(self):
        # Base template for ERC1155 contract
        self.template_path = os.path.join(
            "experiments", "solc_verify_generator", "ERC1155", "imp", "ERC1155_template.sol"
        )
        
        # Load the base template
        with open(self.template_path, 'r') as f:
            self.base_template = f.read()
        
        # Initialize the basic post-conditions for ERC1155 functions
        self.basic_postconditions = {
            "balanceOf": [
                "/// @notice postcondition balance == _balances[account][id]"
            ],
            "balanceOfBatch": [
                "/// @notice postcondition forall (uint i) 0 <= i && i < accounts.length ==> batchBalances[i] == _balances[accounts[i]][ids[i]]"
            ],
            "setApprovalForAll": [
                "/// @notice postcondition _operatorApprovals[msg.sender][operator] == approved"
            ],
            "isApprovedForAll": [
                "/// @notice postcondition approved == _operatorApprovals[account][operator]"
            ],
            "safeTransferFrom": [
                "/// @notice postcondition _balances[from][id] == __verifier_old_uint(_balances[from][id]) - amount",
                "/// @notice postcondition _balances[to][id] == __verifier_old_uint(_balances[to][id]) + amount"
            ],
            "safeBatchTransferFrom": [
                "/// @notice postcondition forall (uint i) 0 <= i && i < ids.length ==> _balances[from][ids[i]] == __verifier_old_uint(_balances[from][ids[i]]) - amounts[i]",
                "/// @notice postcondition forall (uint i) 0 <= i && i < ids.length ==> _balances[to][ids[i]] == __verifier_old_uint(_balances[to][ids[i]]) + amounts[i]"
            ]
        }
        
        # Edge case parameters for ERC1155 functions
        self.edge_parameters = {
            "safeTransferFrom": {
                "from": ["address(0)", "msg.sender"],
                "to": ["address(0)", "msg.sender", "from"],
                "id": ["0", "1", "2**256-1"],
                "amount": ["0", "1", "2**256-1", "_balances[from][id]"]
            },
            "safeBatchTransferFrom": {
                "from": ["address(0)", "msg.sender"],
                "to": ["address(0)", "msg.sender", "from"],
                "ids_special": ["empty", "single", "duplicate"],
                "amounts_special": ["zeros", "mixed", "overflow"]
            }
        }

    def generate_basic_example(self, index: int) -> Dict:
        """Generate a basic ERC1155 example with standard postconditions"""
        # Choose a random ERC1155 function to focus on
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
            "id": f"erc1155_basic_{index}",
            "category": "basic",
            "erc_type": "erc1155",
            "contract": contract,
            "function_name": function_name
        }
        
        return example

    def generate_edge_example(self, index: int) -> Dict:
        """Generate an edge case example for ERC1155"""
        # Choose a function that has edge cases defined
        function_name = random.choice(list(self.edge_parameters.keys()))
        
        # Get basic postconditions for this function
        postconditions = self.basic_postconditions[function_name]
        
        # Choose edge case parameters
        edge_params = {}
        for param, values in self.edge_parameters[function_name].items():
            if param not in ["ids_special", "amounts_special"]:
                # 50% chance to use an edge value
                if random.random() < 0.5:
                    edge_params[param] = random.choice(values)
        
        # Handle special batch parameters
        if function_name == "safeBatchTransferFrom":
            # 50% chance to use special ids
            if random.random() < 0.5:
                edge_params["ids_special"] = random.choice(self.edge_parameters[function_name]["ids_special"])
            
            # 50% chance to use special amounts
            if random.random() < 0.5:
                edge_params["amounts_special"] = random.choice(self.edge_parameters[function_name]["amounts_special"])
        
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
            "id": f"erc1155_edge_{index}",
            "category": "edge",
            "erc_type": "erc1155",
            "contract": contract,
            "function_name": function_name,
            "edge_params": edge_params
        }
        
        return example

    def _generate_edge_postconditions(self, function_name: str, edge_params: Dict[str, str]) -> List[str]:
        """Generate additional postconditions for edge cases"""
        additional_postconditions = []
        
        # Handle different edge cases based on function
        if function_name == "safeTransferFrom":
            # Zero amount transfer
            if edge_params.get("amount") == "0":
                additional_postconditions.append(
                    "/// @notice postcondition _balances[from][id] == __verifier_old_uint(_balances[from][id]) && _balances[to][id] == __verifier_old_uint(_balances[to][id])"
                )
            
            # Self transfer
            if edge_params.get("to") == "from":
                additional_postconditions.append(
                    "/// @notice postcondition _balances[from][id] == __verifier_old_uint(_balances[from][id])"
                )
            
            # Transfer to zero address
            if edge_params.get("to") == "address(0)":
                additional_postconditions.append("/// @notice postcondition revert")
            
            # Transfer exact balance
            if edge_params.get("amount") == "_balances[from][id]":
                additional_postconditions.append(
                    "/// @notice postcondition _balances[from][id] == 0"
                )
                
        elif function_name == "safeBatchTransferFrom":
            # Empty arrays
            if edge_params.get("ids_special") == "empty":
                additional_postconditions.append(
                    "/// @notice postcondition true"
                )
            
            # Single item batch (length 1)
            if edge_params.get("ids_special") == "single":
                additional_postconditions.append(
                    "/// @notice postcondition _balances[from][ids[0]] == __verifier_old_uint(_balances[from][ids[0]]) - amounts[0]"
                )
                additional_postconditions.append(
                    "/// @notice postcondition _balances[to][ids[0]] == __verifier_old_uint(_balances[to][ids[0]]) + amounts[0]"
                )
            
            # All zero amounts
            if edge_params.get("amounts_special") == "zeros":
                additional_postconditions.append(
                    "/// @notice postcondition forall (uint i) 0 <= i && i < ids.length ==> _balances[from][ids[i]] == __verifier_old_uint(_balances[from][ids[i]])"
                )
                additional_postconditions.append(
                    "/// @notice postcondition forall (uint i) 0 <= i && i < ids.length ==> _balances[to][ids[i]] == __verifier_old_uint(_balances[to][ids[i]])"
                )
            
            # Self transfer for batch
            if edge_params.get("to") == "from":
                additional_postconditions.append(
                    "/// @notice postcondition forall (uint i) 0 <= i && i < ids.length ==> _balances[from][ids[i]] == __verifier_old_uint(_balances[from][ids[i]])"
                )
            
            # Transfer to zero address for batch
            if edge_params.get("to") == "address(0)":
                additional_postconditions.append("/// @notice postcondition revert")
                
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
        if edge_params and target_function in self.edge_parameters:
            # For simplicity, we'll just add a comment to show this is an edge case
            # In a real implementation, this would modify the code appropriately
            contract = contract.replace(
                f"contract ERC1155", 
                f"// Edge case contract for {target_function} with params: {edge_params}\ncontract ERC1155"
            )
            
            # Add special handling for batch operations
            if target_function == "safeBatchTransferFrom":
                if "ids_special" in edge_params:
                    if edge_params["ids_special"] == "empty":
                        # Add check for empty arrays
                        contract = contract.replace(
                            "function safeBatchTransferFrom(",
                            "// Modified to handle empty arrays\nfunction safeBatchTransferFrom("
                        )
                    elif edge_params["ids_special"] == "duplicate":
                        # Add handling for duplicate IDs
                        contract = contract.replace(
                            "function safeBatchTransferFrom(",
                            "// Modified to handle duplicate IDs in batch\nfunction safeBatchTransferFrom("
                        )
            
            # Add special checks for common edge cases
            if target_function in ["safeTransferFrom", "safeBatchTransferFrom"] and edge_params.get("to") == "address(0)":
                contract = contract.replace(
                    "function _safeTransferFrom(",
                    "function _safeTransferFrom(address from, address to, uint256 id, uint256 amount, bytes memory data) internal {\n        require(to != address(0), \"ERC1155: transfer to the zero address\");\n        // Rest of the function"
                )
        
        return contract 