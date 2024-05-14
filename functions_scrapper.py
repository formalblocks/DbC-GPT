from solcx import compile_standard, install_solc
import json
import os

# Ensure the correct version of solc is installed
install_solc('v0.8.20')

# Path to the Solidity contract
contract_file_path = './safeevolution/experiment/ERC3156/ERC3156/512268_26-12-2020/FlashBorrower.sol'

# Check if the contract file exists
if not os.path.exists(contract_file_path):
    raise FileNotFoundError("The contract file does not exist.")

# Read Solidity source code from file
with open(contract_file_path, 'r') as file:
    solc_source = file.read()

# Compile Solidity with detailed output selection for AST
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {contract_file_path: {"content": solc_source}},
    "settings": {
        "outputSelection": {
            "*": {  # Applies to all contracts
                "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap", "storageLayout"],  # Detailed outputs
                "": ["ast"]  # Request AST at file level
            }
        }
    }
}, solc_version='v0.8.20')

# Save the compilation output to a file to review the structure
with open('compiled_output.json', 'w') as f:
    json.dump(compiled_sol, f, indent=4)

# Attempt to access the AST and handle possible KeyError
try:
    # Accessing AST from the first source file mentioned as this script assumes a single source
    ast = next(iter(compiled_sol['sources'].values()))['ast']
except KeyError as e:
    print(f"Error accessing AST: {str(e)}")
    print("Check compiled_output.json for structure.")
    exit(1)

# Extract contract name
contract_name = os.path.splitext(os.path.basename(contract_file_path))[0]

# Process ABI for function details
contract_data = compiled_sol['contracts'][contract_file_path][contract_name]

function_details = []
for item in contract_data['abi']:
    if item['type'] == 'function':
        function_info = {
            'name': item['name'],
            'visibility': item.get('visibility', 'public'),  # default to public if not specified
            'mutability': item.get('stateMutability', 'nonpayable'),  # default to nonpayable if not specified
            'inputs': [(input['name'], input['type']) for input in item.get('inputs', [])],
            'outputs': [(output.get('name', "(Unnamed)"), output['type']) for output in item.get('outputs', [])]
        }
        function_details.append(function_info)

# Optionally, save function details to a file
with open('function_signatures.txt', 'w') as f:
    for function in function_details:
        f.write(json.dumps(function) + '\n')

print("Function signatures extracted and saved to function_signatures.txt")
