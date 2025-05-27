import subprocess
import time
import argparse

ASSISTANTS = [
    "4o-mini",
    "erc-1155-001-3-16",
    "erc-1155-005-3-16",
    "erc-1155-010-3-16",
    "erc-1155-001-5-16",
    "erc-1155-005-5-16",
    "erc-1155-010-5-16",
    "erc-1155-001-7-16",
    "erc-1155-005-7-16",
    "erc-1155-010-7-16"
]

# Set up argument parser
parser = argparse.ArgumentParser(description="Run contract verifier for multiple assistants.")
parser.add_argument("--requested", type=str, required=True, help="The requested ERC type (e.g., erc20, erc1155).")
args = parser.parse_args()

for assistant in ASSISTANTS:
    print(f"Running for assistant: {assistant}")
    cmd = [
        "python3", "func_by_func_verifier.py",
        "--requested", args.requested,
        "--context", "",
        "--runs", "10",
        "--assistant", assistant,
        "--max-iterations", "10"
    ]
    subprocess.run(cmd)
    time.sleep(5)