#!/usr/bin/env python3
import os
import sys
import random
import argparse
from typing import Dict, List, Tuple
import json
from datetime import datetime
import logging
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, as_completed

# Import our components
from generators.erc20_generator import ERC20Generator
from generators.erc721_generator import ERC721Generator
from generators.erc1155_generator import ERC1155Generator
from generators.cross_erc_generator import CrossERCGenerator
from validators.solc_verify_validator import SolcVerifyValidator
from utils.template_utils import TemplateManager
from utils.error_injector import ErrorInjector

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dataset_generation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("dataset_generator")

@dataclass
class DatasetConfig:
    """Configuration for dataset generation"""
    erc_types: List[str]
    basic_percent: int = 40
    edge_percent: int = 30
    error_percent: int = 20
    cross_percent: int = 10
    total_examples: int = 1000
    output_dir: str = "datasets"
    random_seed: int = 42
    validate_examples: bool = True
    max_workers: int = 4

def create_output_dirs(config: DatasetConfig) -> Dict[str, str]:
    """Create output directories for each ERC type"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = os.path.join(config.output_dir, f"dataset_{timestamp}")
    
    dirs = {}
    for erc_type in config.erc_types:
        erc_dir = os.path.join(base_dir, erc_type)
        os.makedirs(erc_dir, exist_ok=True)
        
        # Create category subdirectories
        for category in ["basic", "edge", "error", "cross"]:
            category_dir = os.path.join(erc_dir, category)
            os.makedirs(category_dir, exist_ok=True)
        
        dirs[erc_type] = erc_dir
    
    return dirs

def generate_dataset(config: DatasetConfig) -> Dict[str, List[Dict]]:
    """Generate the complete dataset based on configuration"""
    # Set random seed for reproducibility
    random.seed(config.random_seed)
    
    # Create output directories
    output_dirs = create_output_dirs(config)
    
    # Initialize generators
    generators = {
        "erc20": ERC20Generator(),
        "erc721": ERC721Generator(),
        "erc1155": ERC1155Generator()
    }
    
    # Initialize cross-ERC generator
    cross_generator = CrossERCGenerator()
    
    # Initialize error injector
    error_injector = ErrorInjector()
    
    # Initialize validator
    validator = SolcVerifyValidator()
    
    dataset = {}
    
    # Process each ERC type
    for erc_type in config.erc_types:
        logger.info(f"Generating dataset for {erc_type}")
        
        # Calculate examples per category
        examples_count = config.total_examples
        basic_count = int(examples_count * config.basic_percent / 100)
        edge_count = int(examples_count * config.edge_percent / 100)
        error_count = int(examples_count * config.error_percent / 100)
        cross_count = int(examples_count * config.cross_percent / 100)
        
        # Adjust to ensure we get exactly the requested number
        remainder = examples_count - (basic_count + edge_count + error_count + cross_count)
        basic_count += remainder
        
        dataset[erc_type] = []
        
        # Generate basic examples
        logger.info(f"Generating {basic_count} basic examples for {erc_type}")
        basic_examples = generate_examples(
            generators[erc_type], 
            basic_count, 
            "basic", 
            erc_type,
            output_dirs[erc_type],
            validator if config.validate_examples else None,
            config.max_workers
        )
        dataset[erc_type].extend(basic_examples)
        
        # Generate edge cases
        logger.info(f"Generating {edge_count} edge case examples for {erc_type}")
        edge_examples = generate_examples(
            generators[erc_type], 
            edge_count, 
            "edge", 
            erc_type,
            output_dirs[erc_type],
            validator if config.validate_examples else None,
            config.max_workers
        )
        dataset[erc_type].extend(edge_examples)
        
        # Generate error examples from basic and edge examples
        valid_examples = basic_examples + edge_examples
        logger.info(f"Generating {error_count} error examples for {erc_type}")
        error_examples = generate_error_examples(
            error_injector,
            valid_examples,
            error_count,
            erc_type,
            output_dirs[erc_type],
            config.max_workers
        )
        dataset[erc_type].extend(error_examples)
        
        # Generate cross-ERC examples if there are multiple ERC types
        if len(config.erc_types) > 1 and cross_count > 0:
            logger.info(f"Generating {cross_count} cross-ERC examples for {erc_type}")
            cross_examples = generate_cross_examples(
                cross_generator,
                erc_type,
                [t for t in config.erc_types if t != erc_type],
                cross_count,
                output_dirs[erc_type],
                validator if config.validate_examples else None,
                config.max_workers
            )
            dataset[erc_type].extend(cross_examples)
    
    # Save dataset metadata
    save_dataset_metadata(dataset, config, output_dirs)
    
    return dataset

def generate_examples(
    generator, 
    count: int, 
    category: str,
    erc_type: str,
    output_dir: str,
    validator=None,
    max_workers: int = 4
) -> List[Dict]:
    """Generate a specific category of examples"""
    examples = []
    
    # Use process pool for parallel generation
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        
        for i in range(count):
            if category == "basic":
                futures.append(executor.submit(generator.generate_basic_example, i))
            else:  # edge case
                futures.append(executor.submit(generator.generate_edge_example, i))
        
        for future in as_completed(futures):
            try:
                example = future.result()
                # Validate if requested
                if validator:
                    validation_result = validator.validate(example["contract"])
                    example["validation"] = validation_result
                    
                    # Skip invalid examples
                    if not validation_result["success"]:
                        logger.warning(f"Skipping invalid example: {validation_result.get('output', 'Validation failed')}")
                        continue
                
                # Save example
                save_example(example, category, erc_type, output_dir)
                examples.append(example)
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                logger.error(f"Error generating example: {str(e)}\n{error_details}")
    
    return examples

def generate_error_examples(
    error_injector,
    valid_examples: List[Dict],
    count: int,
    erc_type: str,
    output_dir: str,
    max_workers: int = 4
) -> List[Dict]:
    """Generate error examples by corrupting valid examples"""
    error_examples = []
    
    # Ensure we have enough valid examples to work with
    if len(valid_examples) < count:
        logger.warning(f"Not enough valid examples ({len(valid_examples)}) to generate {count} error examples")
        count = len(valid_examples)
    
    # Sample from valid examples
    selected_examples = random.sample(valid_examples, count) if valid_examples else []
    
    # Use process pool for parallel generation
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        
        for i, valid_example in enumerate(selected_examples):
            futures.append(executor.submit(
                error_injector.inject_error, 
                valid_example["contract"],
                erc_type,
                valid_example.get("function_name", "unknown")
            ))
        
        for i, future in enumerate(as_completed(futures)):
            try:
                corrupt_contract = future.result()
                example = {
                    "id": f"error_{i}",
                    "category": "error",
                    "erc_type": erc_type,
                    "contract": corrupt_contract,
                    "original_id": selected_examples[i].get("id", "unknown"),
                    "function_name": selected_examples[i].get("function_name", "unknown"),
                    "error_type": error_injector.last_error_type
                }
                
                # Save example
                save_example(example, "error", erc_type, output_dir)
                error_examples.append(example)
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                logger.error(f"Error generating error example: {str(e)}\n{error_details}")
    
    return error_examples

def generate_cross_examples(
    cross_generator,
    primary_erc: str,
    other_ercs: List[str],
    count: int,
    output_dir: str,
    validator=None,
    max_workers: int = 4
) -> List[Dict]:
    """Generate cross-ERC examples"""
    cross_examples = []
    
    # Use process pool for parallel generation
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        
        for i in range(count):
            # Randomly choose a secondary ERC type
            secondary_erc = random.choice(other_ercs)
            futures.append(executor.submit(
                cross_generator.generate_cross_example, 
                primary_erc, 
                secondary_erc,
                i
            ))
        
        for future in as_completed(futures):
            try:
                example = future.result()
                
                # Validate if requested
                if validator:
                    validation_result = validator.validate(example["contract"])
                    example["validation"] = validation_result
                    
                    # Skip invalid examples
                    if not validation_result["success"]:
                        logger.warning(f"Skipping invalid cross-ERC example: {validation_result.get('output', 'Validation failed')}")
                        continue
                
                # Save example
                save_example(example, "cross", example["erc_type"], output_dir)
                cross_examples.append(example)
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                logger.error(f"Error generating cross-ERC example: {str(e)}\n{error_details}")
    
    return cross_examples

def save_example(example: Dict, category: str, erc_type: str, output_dir: str):
    """Save an example to a file"""
    category_dir = os.path.join(output_dir, category)
    filename = f"{example['id']}.json"
    filepath = os.path.join(category_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(example, f, indent=2)

def save_dataset_metadata(dataset: Dict, config: DatasetConfig, output_dirs: Dict[str, str]):
    """Save dataset metadata"""
    for erc_type, examples in dataset.items():
        metadata = {
            "erc_type": erc_type,
            "generated_at": datetime.now().isoformat(),
            "config": {
                "basic_percent": config.basic_percent,
                "edge_percent": config.edge_percent,
                "error_percent": config.error_percent,
                "cross_percent": config.cross_percent,
                "total_examples": config.total_examples,
                "random_seed": config.random_seed,
                "validate_examples": config.validate_examples
            },
            "stats": {
                "total": len(examples),
                "categories": {
                    "basic": len([e for e in examples if e["category"] == "basic"]),
                    "edge": len([e for e in examples if e["category"] == "edge"]),
                    "error": len([e for e in examples if e["category"] == "error"]),
                    "cross": len([e for e in examples if e["category"] == "cross"])
                }
            }
        }
        
        metadata_path = os.path.join(output_dirs[erc_type], "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Generate datasets for ERC verification")
    parser.add_argument("--erc-types", nargs="+", choices=["erc20", "erc721", "erc1155"], 
                        default=["erc20", "erc721", "erc1155"], 
                        help="ERC standards to generate datasets for")
    parser.add_argument("--basic-percent", type=int, default=40,
                        help="Percentage of basic examples (default: 40)")
    parser.add_argument("--edge-percent", type=int, default=30,
                        help="Percentage of edge case examples (default: 30)")
    parser.add_argument("--error-percent", type=int, default=20,
                        help="Percentage of error examples (default: 20)")
    parser.add_argument("--cross-percent", type=int, default=10,
                        help="Percentage of cross-ERC examples (default: 10)")
    parser.add_argument("--total", type=int, default=1000,
                        help="Total number of examples per ERC type (default: 1000)")
    parser.add_argument("--output-dir", default="datasets",
                        help="Output directory for datasets (default: datasets)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--no-validate", action="store_true",
                        help="Skip validation of generated examples")
    parser.add_argument("--workers", type=int, default=4,
                        help="Number of worker processes (default: 4)")
    
    args = parser.parse_args()
    
    # Check that percentages add up to 100
    total_percent = args.basic_percent + args.edge_percent + args.error_percent + args.cross_percent
    if total_percent != 100:
        parser.error(f"Percentages must add up to 100% (got {total_percent}%)")
    
    # Create config
    config = DatasetConfig(
        erc_types=args.erc_types,
        basic_percent=args.basic_percent,
        edge_percent=args.edge_percent,
        error_percent=args.error_percent,
        cross_percent=args.cross_percent,
        total_examples=args.total,
        output_dir=args.output_dir,
        random_seed=args.seed,
        validate_examples=not args.no_validate,
        max_workers=args.workers
    )
    
    # Generate dataset
    generate_dataset(config)
    
    logger.info(f"Dataset generation complete. Output in {args.output_dir}")

if __name__ == "__main__":
    main() 