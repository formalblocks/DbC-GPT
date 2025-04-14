#!/usr/bin/env python3

import os
import json
import random
from typing import Dict, List, Any, Tuple
import re
from jinja2 import Template

class ERC721Generator:
    """Generator for ERC721 verification examples"""
    
    def __init__(self):
        # Base template for ERC721 contract
        self.template_path = os.path.join(
            "experiments", "solc_verify_generator", "ERC721", "imp", "ERC721_template.sol"
        )
        
        # Load the base template
        with open(self.template_path, 'r') as f:
            self.base_template = f.read()
        
        # Initialize the basic post-conditions for ERC721 functions
        self.basic_postconditions = {
            "balanceOf": [
                "/// @notice postcondition balance == _ownedTokensCount[owner]"
            ],
            "ownerOf": [
                "/// @notice postcondition owner == _tokenOwner[tokenId]",
                "/// @notice postcondition owner != address(0)"
            ],
            "safeTransferFrom": [
                "/// @notice postcondition _tokenOwner[tokenId] == to",
                "/// @notice postcondition _ownedTokensCount[from] == __verifier_old_uint(_ownedTokensCount[from]) - 1",
                "/// @notice postcondition _ownedTokensCount[to] == __verifier_old_uint(_ownedTokensCount[to]) + 1",
                "/// @notice postcondition _tokenApprovals[tokenId] == address(0)"
            ],
            "transferFrom": [
                "/// @notice postcondition _tokenOwner[tokenId] == to",
                "/// @notice postcondition _ownedTokensCount[from] == __verifier_old_uint(_ownedTokensCount[from]) - 1",
                "/// @notice postcondition _ownedTokensCount[to] == __verifier_old_uint(_ownedTokensCount[to]) + 1",
                "/// @notice postcondition _tokenApprovals[tokenId] == address(0)"
            ],
            "approve": [
                "/// @notice postcondition _tokenApprovals[tokenId] == to"
            ],
            "getApproved": [
                "/// @notice postcondition operator == _tokenApprovals[tokenId]"
            ],
            "setApprovalForAll": [
                "/// @notice postcondition _operatorApprovals[msg.sender][to] == approved"
            ],
            "isApprovedForAll": [
                "/// @notice postcondition ret == _operatorApprovals[owner][operator]"
            ]
        }
        
        # Edge case parameters for ERC721 functions
        self.edge_parameters = {
            "safeTransferFrom": {
                "from": ["address(0)", "msg.sender"],
                "to": ["address(0)", "msg.sender", "from"],
                "tokenId": ["0", "1", "2**256-1", "nonExistentTokenId"]
            },
            "transferFrom": {
                "from": ["address(0)", "msg.sender"],
                "to": ["address(0)", "msg.sender", "from"],
                "tokenId": ["0", "1", "2**256-1", "nonExistentTokenId"]
            },
            "approve": {
                "to": ["address(0)", "msg.sender", "_tokenOwner[tokenId]"],
                "tokenId": ["0", "1", "2**256-1", "nonExistentTokenId"]
            },
            "setApprovalForAll": {
                "to": ["address(0)", "msg.sender"],
                "approved": ["true", "false"]
            }
        }

    def generate_basic_example(self, index: int) -> Dict:
        """Generate a basic ERC721 example with standard postconditions"""
        # Choose a random ERC721 function to focus on
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
            "id": f"erc721_basic_{index}",
            "category": "basic",
            "erc_type": "erc721",
            "contract": contract,
            "function_name": function_name
        }
        
        return example

    def generate_edge_example(self, index: int) -> Dict:
        """Generate an edge case example for ERC721"""
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
            "id": f"erc721_edge_{index}",
            "category": "edge",
            "erc_type": "erc721",
            "contract": contract,
            "function_name": function_name,
            "edge_params": edge_params
        }
        
        return example

    def _generate_edge_postconditions(self, function_name: str, edge_params: Dict[str, str]) -> List[str]:
        """Generate additional postconditions for edge cases"""
        additional_postconditions = []
        
        # Handle different edge cases based on function
        if function_name in ["safeTransferFrom", "transferFrom"]:
            # Non-existent token
            if edge_params.get("tokenId") == "nonExistentTokenId":
                additional_postconditions.append("/// @notice postcondition _tokenOwner[tokenId] == address(0)")
                additional_postconditions.append("/// @notice postcondition revert")
            
            # Self transfer
            if edge_params.get("to") == "from":
                additional_postconditions.append("/// @notice postcondition _ownedTokensCount[from] == __verifier_old_uint(_ownedTokensCount[from])")
                additional_postconditions.append("/// @notice postcondition _tokenOwner[tokenId] == from")
            
            # Transfer to zero address
            if edge_params.get("to") == "address(0)":
                additional_postconditions.append("/// @notice postcondition revert")
            
        elif function_name == "approve":
            # Approve zero address
            if edge_params.get("to") == "address(0)":
                additional_postconditions.append("/// @notice postcondition _tokenApprovals[tokenId] == address(0)")
            
            # Approve self as owner
            if edge_params.get("to") == "_tokenOwner[tokenId]":
                additional_postconditions.append("/// @notice postcondition revert")
                
            # Approve for non-existent token
            if edge_params.get("tokenId") == "nonExistentTokenId":
                additional_postconditions.append("/// @notice postcondition revert")
            
        elif function_name == "setApprovalForAll":
            # Self approval
            if edge_params.get("to") == "msg.sender":
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
        
        # Handle overloaded functions
        if target_function == "safeTransferFrom":
            # Replace both overloaded versions
            contract = contract.replace("$safeTransferFrom3", postconditions_str)
            contract = contract.replace("$safeTransferFrom4", postconditions_str)
        else:
            contract = contract.replace(function_placeholder, postconditions_str)
        
        # Replace other function placeholders with empty strings
        for func in self.basic_postconditions.keys():
            if func != target_function:
                if func == "safeTransferFrom":
                    contract = contract.replace("$safeTransferFrom3", "")
                    contract = contract.replace("$safeTransferFrom4", "")
                else:
                    contract = contract.replace(f"${func}", "")
        
        # If we have edge parameters, we need to modify the implementation
        if edge_params and target_function in self.edge_parameters:
            # For simplicity, we'll just add a comment to show this is an edge case
            # In a real implementation, this would modify the code appropriately
            contract = contract.replace(
                f"contract ERC721", 
                f"// Edge case contract for {target_function} with params: {edge_params}\ncontract ERC721"
            )
            
            # Add special checks for edge cases where needed
            if target_function in ["safeTransferFrom", "transferFrom"] and edge_params.get("to") == "address(0)":
                contract = contract.replace(
                    "function _transferFrom(address from, address to, uint256 tokenId) internal {",
                    "function _transferFrom(address from, address to, uint256 tokenId) internal {\n        require(to != address(0), \"ERC721: transfer to the zero address\");"
                )
            
            # Handle non-existent tokens
            if edge_params.get("tokenId") == "nonExistentTokenId":
                contract = contract.replace(
                    "function _exists(uint256 tokenId) internal view returns (bool) {",
                    "function _exists(uint256 tokenId) internal view returns (bool) {\n        if (tokenId == nonExistentTokenId) return false;"
                )
                
                # Add the nonExistentTokenId to contract state
                contract = contract.replace(
                    "contract ERC721", 
                    "contract ERC721 {\n    uint256 constant nonExistentTokenId = 999999999;"
                )
        
        return contract 