#!/usr/bin/env python3
import os
import sys

def check_path(path):
    exists = os.path.exists(path)
    print(f"Path: {path}")
    print(f"Exists: {exists}")
    if exists:
        print(f"Is file: {os.path.isfile(path)}")
        print(f"Is directory: {os.path.isdir(path)}")
    print()

# Get the base directory
base_dir = os.path.abspath(".")
print(f"Base directory: {base_dir}")
print()

# Check the template paths
for erc_type in ["erc20", "erc721", "erc1155"]:
    # Check the absolute path
    template_path = os.path.join(
        base_dir, 
        "experiments/solc_verify_generator", 
        erc_type.upper(), 
        "templates/imp_spec_merge.template"
    )
    check_path(template_path)
    
    # Check the relative path
    relative_path = f"./experiments/solc_verify_generator/{erc_type.upper()}/templates/imp_spec_merge.template"
    check_path(relative_path)

print("Check if solc_verify_generator module can be imported:")
try:
    sys.path.append(base_dir)
    from experiments.solc_verify_generator.main import generate_merge
    print("Import successful!")
except Exception as e:
    print(f"Import failed: {e}") 