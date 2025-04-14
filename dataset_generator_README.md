# ERC Standards Verification Dataset Generator

This tool automatically generates large datasets of formal verification conditions for different ERC standards (ERC20, ERC721, ERC1155) to train models for smart contract verification.

## Overview

The dataset generator creates examples across four categories:

1. **Basic Examples (40%)**: Standard compliant contracts with correct verification conditions
2. **Edge Cases (30%)**: Contracts that handle boundary conditions and edge cases
3. **Error Examples (20%)**: Intentionally incorrect verification conditions for error correction training
4. **Cross-ERC Examples (10%)**: Contracts that combine multiple ERC standards

## Requirements

- Python 3.7+
- solc-verify (for validation)
- Dependencies listed in requirements.txt

## Installation

```bash
# Clone the repository
git clone https://github.com/formalblocks/DbC-GPT.git
cd DbC-GPT

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Make sure solc-verify is installed and accessible in your PATH
```

## Usage

Generate datasets with default parameters:

```bash
python dataset_generator.py
```

### Command Line Options

```
usage: dataset_generator.py [-h] [--erc-types ERC_TYPES [ERC_TYPES ...]]
                           [--basic-percent BASIC_PERCENT]
                           [--edge-percent EDGE_PERCENT]
                           [--error-percent ERROR_PERCENT]
                           [--cross-percent CROSS_PERCENT]
                           [--total TOTAL] [--output-dir OUTPUT_DIR]
                           [--seed SEED] [--no-validate] [--workers WORKERS]

optional arguments:
  -h, --help            show this help message and exit
  --erc-types ERC_TYPES [ERC_TYPES ...]
                        ERC standards to generate datasets for
                        (choices: erc20, erc721, erc1155)
  --basic-percent BASIC_PERCENT
                        Percentage of basic examples (default: 40)
  --edge-percent EDGE_PERCENT
                        Percentage of edge case examples (default: 30)
  --error-percent ERROR_PERCENT
                        Percentage of error examples (default: 20)
  --cross-percent CROSS_PERCENT
                        Percentage of cross-ERC examples (default: 10)
  --total TOTAL         Total number of examples per ERC type (default: 1000)
  --output-dir OUTPUT_DIR
                        Output directory for datasets (default: datasets)
  --seed SEED           Random seed for reproducibility (default: 42)
  --no-validate         Skip validation of generated examples
  --workers WORKERS     Number of worker processes (default: 4)
```

### Examples

Generate 500 examples each for ERC20 and ERC721:

```bash
python dataset_generator.py --erc-types erc20 erc721 --total 500
```

Generate dataset with custom category distribution:

```bash
python dataset_generator.py --basic-percent 50 --edge-percent 30 --error-percent 15 --cross-percent 5
```

Skip validation to generate dataset faster:

```bash
python dataset_generator.py --no-validate
```

Generate large dataset with 10 worker processes:

```bash
python dataset_generator.py --total 5000 --workers 10
```

## Dataset Structure

The generated dataset will be organized as follows:

```
datasets/
└── dataset_YYYYMMDD_HHMMSS/
    ├── erc20/
    │   ├── basic/
    │   ├── edge/
    │   ├── error/
    │   ├── cross/
    │   └── metadata.json
    ├── erc721/
    │   ├── basic/
    │   ├── edge/
    │   ├── error/
    │   ├── cross/
    │   └── metadata.json
    └── erc1155/
        ├── basic/
        ├── edge/
        ├── error/
        ├── cross/
        └── metadata.json
```

Each example is stored as a JSON file containing:

- Contract code with formal verification conditions
- Metadata about the example (category, function focus, etc.)
- Validation results (if validation was performed)

## JSON Example Format

```json
{
  "id": "erc20_basic_123",
  "category": "basic",
  "erc_type": "erc20",
  "contract": "pragma solidity >=0.5.0;\n\ncontract ERC20 {\n...",
  "function_name": "transfer",
  "validation": {
    "success": true,
    "verified_conditions": 5,
    "failed_conditions": 0
  }
}
```

## Extending the Generator

### Adding New Edge Cases

Modify the appropriate generator class (e.g., `ERC20Generator`) and update its `edge_parameters` dictionary with new values.

### Adding New Error Types

Add new error injection methods to the `ErrorInjector` class in `utils/error_injector.py`.

### Adding New Cross-ERC Patterns

Add new interaction patterns in the `CrossERCGenerator` class in `generators/cross_erc_generator.py`.

## License

[MIT License](LICENSE)
