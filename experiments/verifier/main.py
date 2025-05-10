#!/usr/bin/env python3
import argparse
import logging
import sys
import os
import json
from dotenv import load_dotenv

from .config.config_manager import ConfigManager
from .core.verifier import Verifier


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_default_config():
    """Create and load a default configuration."""
    config_dir = os.path.join(os.path.dirname(__file__), '../config')
    os.makedirs(config_dir, exist_ok=True)
    
    # Get the absolute path to the assets directory
    assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../assets/file_search'))
    
    default_config = {
        "assistant_ids": {
            "4o-mini": "asst_WRF0J9P9EiZ70DcntBSlapWB",
            "erc-1155-001-3-16": "asst_uMYPmlxmT9ppnPKZQ8ZTyfYb",
            "erc-1155-005-3-16": "asst_tsqw3GcFG1kyPz9rNkqkIYAU",
            "erc-1155-010-3-16": "asst_BsZDuAHsmBfrlimXinHt96Cb",
            "erc-1155-001-5-16": "asst_Mkq2y7mUxjusd47rPSGXrrCM",
            "erc-1155-005-5-16": "asst_8ZL8R3zwXyurmmjkFX14kcuS",
            "erc-1155-010-5-16": "asst_wOnRMvawOAI1sO83lfRWWBLu",
            "erc-1155-001-7-16": "asst_sZLa64l2Xrb1zNhogDl7RXap",
            "erc-1155-005-7-16": "asst_m8y0QMRJVtvDRYcPZLVIcHW6",
            "erc-1155-001-7-16": "asst_MRg3E5ds4NRfFKPTPqLsx9rS"
        },
        "interface_paths": {
            "erc20": os.path.join(assets_path, "erc20_interface.md"),
            "erc721": os.path.join(assets_path, "erc721_interface.md"),
            "erc1155": os.path.join(assets_path, "erc1155_interface.md")
        },
        "eip_paths": {
            "erc20": os.path.join(assets_path, "erc-20.md"),
            "erc721": os.path.join(assets_path, "erc-721.md"),
            "erc1155": os.path.join(assets_path, "erc-1155.md")
        },
        "reference_spec_paths": {
            "erc20": os.path.join(assets_path, "erc20_ref_spec.md"),
            "erc721": os.path.join(assets_path, "erc721_ref_spec.md"),
            "erc1155": os.path.join(assets_path, "erc1155_ref_spec.md")
        },
        "verifier": {
            "max_iterations_per_function": 10,
            "max_retries": 5,
            "verification_timeout": 60
        }
    }
    
    config_path = os.path.join(config_dir, 'default_config.json')
    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    return config_path


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Run contract verification with different contexts')
    parser.add_argument('--requested', type=str, required=True, 
                        choices=['erc20', 'erc721', 'erc1155'],
                        help='The contract type to verify')
    parser.add_argument('--context', type=str, required=True,
                        help='Comma-separated list of context contract types (e.g., "erc20,erc721,erc1155")')
    parser.add_argument('--assistant', type=str, default='4o-mini',
                        help='The assistant to use')
    parser.add_argument('--runs', type=int, default=1,
                        help='Number of verification runs')
    parser.add_argument('--config', type=str, default=None,
                        help='Path to configuration file')
    
    return parser.parse_args()


def main():
    """Run the verification process."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Set up logging
    setup_logging()
    
    # Parse command-line arguments
    args = parse_args()
    
    # Load configuration
    config_path = args.config
    if not config_path:
        # Create and load default configuration
        config_path = load_default_config()
    
    config = ConfigManager(config_path)
    
    # Parse context types
    if not args.context.strip():
        context_types = [""]
    else:
        context_types = [ctx.strip().lower() for ctx in args.context.split(',')]
    
    # Create and run verifier
    verifier = Verifier(config)
    results = verifier.verify_contract(
        requested_type=args.requested.lower(),
        context_types=context_types,
        assistant_key=args.assistant,
        num_runs=args.runs
    )
    
    logging.info(f"Verification complete. {len(results)} runs completed.")
    
    successful_runs = sum(1 for result in results if result["verified"])
    logging.info(f"Successful runs: {successful_runs}/{len(results)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 