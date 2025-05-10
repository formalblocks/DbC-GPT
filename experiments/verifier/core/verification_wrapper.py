import os
import logging
import subprocess
from typing import Tuple, Optional
from dataclasses import dataclass
import re

from ..utils.file_utils import FileUtils


@dataclass
class VerificationResult:
    """
    Result of a verification operation.
    
    Attributes:
        status: The exit code of the verification process.
        output: The output of the verification process.
    """
    status: int
    output: str


class SolcVerifyWrapper:
    """
    Wrapper for the solc-verify tool.
    
    This class provides methods for verifying Solidity code using solc-verify.
    """
    
    SOLC_VERIFY_CMD = "solc-verify.py"
    SPEC_FILE_PATH = '../temp/spec.sol'
    
    # Template paths for different ERC standards
    TEMPLATE_PATHS = {
        "erc20": './experiments/solc_verify_generator/ERC20/templates/imp_spec_merge.template',
        "erc721": './experiments/solc_verify_generator/ERC721/templates/imp_spec_merge.template',
        "erc1155": './experiments/solc_verify_generator/ERC1155/templates/imp_spec_merge.template',
    }
    
    # Merge paths for different ERC standards
    MERGE_PATHS = {
        "erc20": './experiments/solc_verify_generator/ERC20/imp/ERC20_merge.sol',
        "erc721": './experiments/solc_verify_generator/ERC721/imp/ERC721_merge.sol',
        "erc1155": './experiments/solc_verify_generator/ERC1155/imp/ERC1155_merge.sol',
    }

    @classmethod
    def call_solc(cls, file_path: str) -> VerificationResult:
        """
        Call the solc-verify command on a file.
        
        Args:
            file_path: The path to the file to verify.
            
        Returns:
            A VerificationResult object with the status and output of the verification.
        """
        try:
            command = [cls.SOLC_VERIFY_CMD, file_path]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            return VerificationResult(result.returncode, result.stdout + result.stderr)
        except Exception as e:
            logging.error(f"Error calling solc-verify: {e}")
            return VerificationResult(1, f"Error calling solc-verify: {e}")
    
    @classmethod
    def verify(cls, solidity_spec_str: str, requested_type: str = "erc20") -> VerificationResult:
        """
        Verify a Solidity specification.
        
        Args:
            solidity_spec_str: Solidity code with only the function signatures
                annotated with solc-verify conditions.
            requested_type: The ERC standard to verify ("erc20", "erc721", "erc1155").
            
        Returns:
            A VerificationResult object with the status and output of the verification.
        """
        # Convert relative paths to absolute paths
        base_dir = os.path.abspath(os.path.dirname(__file__) + "/../../..")
        
        # Use appropriate template and merge paths based on requested_type
        template_path = os.path.join(
            base_dir, 
            "experiments/solc_verify_generator", 
            requested_type.upper(), 
            "templates/imp_spec_merge.template"
        )
        
        merge_path = os.path.join(
            base_dir, 
            "experiments/solc_verify_generator", 
            requested_type.upper(), 
            "imp",
            f"{requested_type.upper()}_merge.sol"
        )
        
        spec_file_path = os.path.join(base_dir, "experiments/temp/spec.sol")
        
        # Make sure directories exist
        os.makedirs(os.path.dirname(spec_file_path), exist_ok=True)
        os.makedirs(os.path.dirname(merge_path), exist_ok=True)
        
        # Save the specification to a file
        FileUtils.save_string_to_file(spec_file_path, solidity_spec_str)
        
        try:
            # Import here to avoid circular imports
            import sys
            sys.path.append(base_dir)
            from experiments.solc_verify_generator.main import generate_merge
            
            logging.info(f"Generating merge file: {spec_file_path} -> {template_path} -> {merge_path}")
            generate_merge(spec_file_path, template_path, merge_path)
        except RuntimeError as e:
            return VerificationResult(*e.args)
        except Exception as e:
            logging.error(f"Error generating merge file: {e}")
            return VerificationResult(1, f"Error generating merge file: {e}")
            
        return cls.call_solc(merge_path)
    
    @classmethod
    def analyze_verification_result(cls, verification_result: VerificationResult, func_name: str) -> Tuple[bool, str]:
        """
        Analyze the result of a verification operation.
        
        Args:
            verification_result: The result of the verification.
            func_name: The name of the function that was verified.
            
        Returns:
            A tuple of (verification_passed, error_message).
        """
        verification_passed = False
        error_output = verification_result.output
        error_message = ""

        if verification_result.status == 0:
            verification_passed = True
        else:
            # Status is non-zero, check if it's just benign warnings
            lines = error_output.strip().split('\n')
            
            # Filter out known benign warnings
            benign_warning_patterns = [
                r'Warning: Unused function parameter',
                r'Warning: Unused local variable',
                r'Warning: Function state mutability can be restricted',
                r'Warning: This is a pre-release compiler version'
            ]
            
            # Check for actual solc-verify errors or unknown warnings
            critical_errors = []
            for line in lines:
                is_benign = False
                for pattern in benign_warning_patterns:
                    if re.search(pattern, line):
                        is_benign = True
                        break
                        
                if not is_benign and line.strip():  # Ignore empty lines
                    # Check specifically for solc-verify errors mentioning the current function
                    if f"::{func_name}:" in line or f"Annotation for {func_name}" in line or "solc-verify error:" in line:
                        critical_errors.append(line)

            if not critical_errors:
                logging.warning(f"Verification status non-zero, but only benign warnings detected for {func_name}. Treating as success.")
                verification_passed = True
            else:
                logging.warning(f"Verification failed for {func_name} with critical errors/warnings:")
                for err_line in critical_errors:
                    logging.warning(f"  - {err_line}")
                    error_message += f"{err_line}\n"

        return verification_passed, error_message 