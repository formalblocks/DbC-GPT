#!/usr/bin/env python3
import os
import json
import glob
from itertools import product

# Base directory for ERC1155 corpus
# Replace for other ERCs
BASE_DIR = "llm_spec/app/assets/corpus/erc721"

def read_file(file_path):
    """Read the contents of a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def main():
    # Dictionary to store md and sol files for each function
    functions = {}
    
    # Find all function directories
    function_dirs = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    
    # Collect all md and sol files for each function
    for function_dir in function_dirs:
        full_dir = os.path.join(BASE_DIR, function_dir)
        
        # Find all .md and .sol files
        md_files = glob.glob(os.path.join(full_dir, "*.md"))
        sol_files = glob.glob(os.path.join(full_dir, "*.sol"))
        
        if md_files and sol_files:
            functions[function_dir] = {
                "md_files": md_files,
                "sol_files": sol_files
            }
    
    # Prepare JSONL data
    jsonl_data = []
    
    # Create all possible combinations
    for function_name, files in functions.items():
        for md_file, sol_file in product(files["md_files"], files["sol_files"]):
            # Read file contents
            md_content = read_file(md_file)
            sol_content = read_file(sol_file)
            
            # Create the JSON entry
            entry = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a coding assistant specialized in generating formal postconditions for ERC interface with solc-verify postconditions annotations."
                    },
                    {
                        "role": "user",
                        "content": md_content
                    },
                    {
                        "role": "assistant",
                        "content": sol_content
                    }
                ]
            }
            
            jsonl_data.append(entry)
    
    # Write the JSONL file
    output_file = "erc1155_corpus.jsonl"
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in jsonl_data:
            f.write(json.dumps(entry) + '\n')
    
    # Print statistics
    print(f"Generated {len(jsonl_data)} combinations in {output_file}")
    for function_name, files in functions.items():
        print(f"Function {function_name}: {len(files['md_files'])} MD files × {len(files['sol_files'])} SOL files = {len(files['md_files']) * len(files['sol_files'])} combinations")
    
if __name__ == "__main__":
    main() 