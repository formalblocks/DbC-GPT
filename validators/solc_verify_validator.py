#!/usr/bin/env python3

import os
import subprocess
import tempfile
import re
import shutil
from typing import Dict, Any, List, Tuple

class SolcVerifyValidator:
    """Validator for Solidity verification conditions using solc-verify"""
    
    def __init__(self, solc_verify_cmd: str = "solc-verify.py"):
        """
        Initialize the validator
        
        Args:
            solc_verify_cmd: Command to run solc-verify
        """
        self.solc_verify_cmd = solc_verify_cmd
        
        # Track validation results for analysis
        self.validation_results = []
        
    def validate(self, contract: str) -> Dict[str, Any]:
        """
        Validate a Solidity contract with solc-verify
        
        Args:
            contract: The Solidity contract code with formal verification conditions
            
        Returns:
            Dict with validation results
        """
        # Create a temporary directory to hold the contract and its dependencies
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, "Contract.sol")
        
        try:
            # Write contract to a temporary file
            with open(temp_file_path, 'w') as temp_file:
                temp_file.write(contract)
            
            # Check if this contract needs imports based on its content
            if "import \"./IERC20.sol\"" in contract or "import './IERC20.sol'" in contract:
                self._copy_erc20_dependencies(temp_dir)
            elif "import \"./IERC721.sol\"" in contract or "import './IERC721.sol'" in contract:
                self._copy_erc721_dependencies(temp_dir)
            elif "import \"./IERC1155.sol\"" in contract or "import './IERC1155.sol'" in contract:
                self._copy_erc1155_dependencies(temp_dir)
            
            # Run solc-verify on the temporary file
            result = self._run_solc_verify(temp_file_path)
            
            # Parse the result
            validation_result = self._parse_verification_result(result)
            
            # Check if we have import issues and handle them with a custom error
            if not validation_result["success"] and "Error: Source" in validation_result["output"] and "not found" in validation_result["output"]:
                validation_result["output"] = "Error while running compiler, details:\n" + validation_result["output"]
            
            # Add to validation history
            self.validation_results.append(validation_result)
            
            return validation_result
        finally:
            # Clean up the temporary directory and all its contents
            shutil.rmtree(temp_dir)
    
    def _copy_erc20_dependencies(self, temp_dir: str):
        """
        Copy ERC20 dependency files to the temporary directory
        
        Args:
            temp_dir: Path to the temporary directory
        """
        # Create math subdirectory
        math_dir = os.path.join(temp_dir, "math")
        os.makedirs(math_dir, exist_ok=True)
        
        # Source paths
        erc20_base_dir = os.path.join("experiments", "solc_verify_generator", "ERC20", "imp")
        ierc20_path = os.path.join(erc20_base_dir, "IERC20.sol")
        safemath_path = os.path.join(erc20_base_dir, "math", "SafeMath.sol")
        
        # Destination paths
        ierc20_dest = os.path.join(temp_dir, "IERC20.sol")
        safemath_dest = os.path.join(math_dir, "SafeMath.sol")
        
        # Copy the files if they exist
        if os.path.exists(ierc20_path):
            shutil.copy(ierc20_path, ierc20_dest)
        
        if os.path.exists(safemath_path):
            shutil.copy(safemath_path, safemath_dest)
    
    def _copy_erc721_dependencies(self, temp_dir: str):
        """
        Copy ERC721 dependency files to the temporary directory
        
        Args:
            temp_dir: Path to the temporary directory
        """
        # Create subdirectories
        math_dir = os.path.join(temp_dir, "math")
        introspection_dir = os.path.join(temp_dir, "introspection")
        utils_dir = os.path.join(temp_dir, "utils")
        os.makedirs(math_dir, exist_ok=True)
        os.makedirs(introspection_dir, exist_ok=True)
        os.makedirs(utils_dir, exist_ok=True)
        
        # Source paths
        erc721_base_dir = os.path.join("experiments", "solc_verify_generator", "ERC721", "imp")
        
        # Map of source files to destination files
        file_map = {
            "IERC721.sol": "IERC721.sol",
            "IERC721Receiver.sol": "IERC721Receiver.sol",
            "SafeMath.sol": os.path.join("math", "SafeMath.sol"),
            "Address.sol": os.path.join("utils", "Address.sol"),
            "IERC165.sol": os.path.join("introspection", "IERC165.sol"),
            "ERC165.sol": os.path.join("introspection", "ERC165.sol")
        }
        
        # Copy files that exist
        for src_file, dest_path in file_map.items():
            src_path = os.path.join(erc721_base_dir, src_file)
            dest_full_path = os.path.join(temp_dir, dest_path)
            
            # Make sure parent directory exists
            os.makedirs(os.path.dirname(dest_full_path), exist_ok=True)
            
            if os.path.exists(src_path):
                shutil.copy(src_path, dest_full_path)
    
    def _copy_erc1155_dependencies(self, temp_dir: str):
        """
        Copy ERC1155 dependency files to the temporary directory
        
        Args:
            temp_dir: Path to the temporary directory
        """
        # Create subdirectories
        introspection_dir = os.path.join(temp_dir, "introspection")
        utils_dir = os.path.join(temp_dir, "utils")
        os.makedirs(introspection_dir, exist_ok=True)
        os.makedirs(utils_dir, exist_ok=True)
        
        # Source paths
        erc1155_base_dir = os.path.join("experiments", "solc_verify_generator", "ERC1155", "imp")
        
        # Map of source files to destination files
        file_map = {
            "IERC1155.sol": "IERC1155.sol",
            "IERC1155Receiver.sol": "IERC1155Receiver.sol",
            "IERC1155MetadataURI.sol": "IERC1155MetadataURI.sol",
            "Address.sol": os.path.join("utils", "Address.sol"),
            "Context.sol": os.path.join("utils", "Context.sol"),
            "IERC165.sol": os.path.join("introspection", "IERC165.sol"),
            "ERC165.sol": os.path.join("introspection", "ERC165.sol")
        }
        
        # Copy files that exist
        for src_file, dest_path in file_map.items():
            src_path = os.path.join(erc1155_base_dir, src_file)
            dest_full_path = os.path.join(temp_dir, dest_path)
            
            # Make sure parent directory exists
            os.makedirs(os.path.dirname(dest_full_path), exist_ok=True)
            
            if os.path.exists(src_path):
                shutil.copy(src_path, dest_full_path)
    
    def _run_solc_verify(self, file_path: str) -> Tuple[int, str]:
        """
        Run solc-verify on a Solidity file
        
        Args:
            file_path: Path to the Solidity file
            
        Returns:
            Tuple of (return_code, output)
        """
        try:
            result = subprocess.run(
                [self.solc_verify_cmd, file_path],
                capture_output=True,
                text=True,
                timeout=60  # Limit execution time to 1 minute
            )
            return result.returncode, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return 124, "Verification timed out after 60 seconds"
        except Exception as e:
            return 1, f"Error running solc-verify: {str(e)}"
    
    def _parse_verification_result(self, result: Tuple[int, str]) -> Dict[str, Any]:
        """
        Parse the output of solc-verify
        
        Args:
            result: Tuple of (return_code, output) from solc-verify
            
        Returns:
            Dict with parsed results
        """
        return_code, output = result
        
        # Initialize result dictionary
        validation_result = {
            "success": return_code == 0,
            "return_code": return_code,
            "output": output,
            "errors": [],
            "warnings": [],
            "verified_conditions": 0,
            "failed_conditions": 0
        }
        
        # Count verified and failed conditions
        verified_matches = re.findall(r'Verified [0-9]+ assertions', output)
        if verified_matches:
            for match in verified_matches:
                count = int(re.search(r'Verified ([0-9]+) assertions', match).group(1))
                validation_result["verified_conditions"] += count
        
        # Parse errors
        error_matches = re.findall(r'Error: .+', output)
        for error in error_matches:
            validation_result["errors"].append(error)
        
        # Parse warnings
        warning_matches = re.findall(r'Warning: .+', output)
        for warning in warning_matches:
            validation_result["warnings"].append(warning)
        
        # Parse failed assertions
        assertion_failures = re.findall(r'Assertion might not hold', output)
        validation_result["failed_conditions"] = len(assertion_failures)
        
        return validation_result
    
    def generate_dataset_stats(self) -> Dict[str, Any]:
        """
        Generate statistics for all validations performed
        
        Returns:
            Dict with validation statistics
        """
        if not self.validation_results:
            return {"total": 0, "success_rate": 0, "error_types": {}}
        
        total = len(self.validation_results)
        successful = sum(1 for result in self.validation_results if result["success"])
        
        # Count error types
        error_types = {}
        for result in self.validation_results:
            if not result["success"]:
                for error in result["errors"]:
                    error_type = self._categorize_error(error)
                    error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total": total,
            "successful": successful,
            "success_rate": successful / total if total > 0 else 0,
            "error_types": error_types,
            "verified_conditions": sum(r["verified_conditions"] for r in self.validation_results),
            "failed_conditions": sum(r["failed_conditions"] for r in self.validation_results)
        }
    
    def _categorize_error(self, error_message: str) -> str:
        """
        Categorize an error message into a common error type
        
        Args:
            error_message: Error message from solc-verify
            
        Returns:
            Categorized error type as a string
        """
        if "Assertion might not hold" in error_message:
            return "assertion_failure"
        elif "undeclared identifier" in error_message:
            return "undeclared_identifier"
        elif "overflow" in error_message:
            return "arithmetic_overflow"
        elif "syntax error" in error_message:
            return "syntax_error"
        elif "type error" in error_message:
            return "type_error"
        elif "function has no implementation" in error_message:
            return "missing_implementation"
        else:
            return "other_error"
            
    def reset_validation_history(self):
        """Clear the validation history"""
        self.validation_results = []
        
    def get_failed_validations(self) -> List[Dict[str, Any]]:
        """
        Get a list of all failed validations
        
        Returns:
            List of validation results that failed
        """
        return [result for result in self.validation_results if not result["success"]]
    
    def get_successful_validations(self) -> List[Dict[str, Any]]:
        """
        Get a list of all successful validations
        
        Returns:
            List of validation results that succeeded
        """
        return [result for result in self.validation_results if result["success"]] 