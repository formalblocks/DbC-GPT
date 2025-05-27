import subprocess
import time
import argparse
import os

SPECIFIC_JOBS_TO_RUN = [
    # ("4o-mini", "erc1155", ""),
    # ("erc-20-001-5-16", "erc1155", ""),
    ("erc-721-001-5-16", "erc1155", ""),
    # ("erc-1155-001-5-16", "erc1155", ""),
    ("erc-20-721-001-5-16", "erc1155", ""),
    ("erc-20-1155-001-5-16", "erc1155", ""),
    ("erc-721-1155-001-5-16", "erc1155", ""),
    ("erc-20-721-1155-001-5-16", "erc1155", ""),
    ("erc-1155-001-3-16", "erc1155", ""),
    ("erc-1155-005-3-16", "erc1155", ""),
    ("erc-721-001-3-16", "erc1155", ""),
]

# Assistant ID mappings - ensure these are up-to-date with your verifier scripts
# These are based on the provided file contents. You might need to update them
# if the verifier scripts change.
ASSISTANT_IDS_FUNC_BY_FUNC = {
    "4o-mini": "asst_WRF0J9P9EiZ70DcntBSlapWB",
    "erc-1155-001-3-16": "asst_uMYPmlxmT9ppnPKZQ8ZTyfYb",
    "erc-1155-005-3-16": "asst_tsqw3GcFG1kyPz9rNkqkIYAU",
    "erc-1155-010-3-16": "asst_BsZDuAHsmBfrlimXinHt96Cb",
    "erc-1155-001-5-16": "asst_Mkq2y7mUxjusd47rPSGXrrCM",
    "erc-1155-005-5-16": "asst_8ZL8R3zwXyurmmjkFX14kcuS",
    "erc-1155-010-5-16": "asst_wOnRMvawOAI1sO83lfRWWBLu",
    "erc-1155-001-7-16": "asst_sZLa64l2Xrb1zNhogDl7RXap",
    "erc-1155-005-7-16": "asst_m8y0QMRJVtvDRYcPZLVIcHW6",
    "erc-1155-010-7-16": "asst_MRg3E5ds4NRfFKPTPqLsx9rS",
    "erc-721-001-3-16": "asst_nPqcpEo7lJnH4nmX9sNSBmfX",
    "erc-721-005-3-16": "asst_wipOM1IWYzuK1jyqwqRJmDic",
    "erc-721-010-3-16": "asst_MnKQphy1oPqu7QUWah63JFJk",
    "erc-721-001-5-16": "asst_kjoZHBonf5tXKpuiJ6Z4T3Gv",
    "erc-721-005-5-16": "asst_u2r0eDkkqERqTmOY5soRPU7n",
    "erc-721-010-5-16": "asst_YNv1CBWWYuzTg4D7rRK7JVL6",
    "erc-721-001-7-16": "asst_odutVf248qCN3C9zlFKLNd9a",
    "erc-721-005-7-16": "asst_HdOeD4DYTJAHfluUAeu6cwNJ",
    "erc-20-001-3-16": "asst_wn9R7oQTUr60VpfvvaZ5asBa",
    "erc-20-005-3-16": "asst_3pHhhAMFwXi9JCVPOvftRQJU",
    "erc-20-010-3-16": "asst_OZk81q3HVr1mrGXCfOiVKaku",
    "erc-20-001-5-16": "asst_M6Q7TjZTC5wLDXdA88kCre7o",
    "erc-20-005-5-16": "asst_XFsmrlLmDMcbQ8uPeG4EVGA0",
    "erc-20-010-5-16": "asst_d1TPZLOP9HSmJq0va4vD2rcW",
    "erc-20-001-7-16": "asst_M8jjeryyXFYdnGSiQuyOB4ij",
    "erc-20-005-7-16": "asst_w98aowF6diNCOJxaM9li84Hi",
    "erc-20-010-7-16": "asst_FEGX60kN1RpiFGQP3CaQI6vO",
    "erc-20-721-001-5-16": "asst_waYnC3Fcp2JVmsShGUkz9o5y",
    "erc-20-1155-001-5-16": "asst_xiVobEjKhGFhIFIPw3EySfsf",
    "erc-721-1155-001-5-16": "asst_YsmuTcAJW179xCxAufROe2k1",
    "erc-20-721-1155-001-5-16": "asst_0JMCtwBpCeOHZ1lWmy4nErjB",

}

ASSISTANT_IDS_LOOP_CONTRACT = {
    "4o-mini": "asst_uMJ30gjHtG1VIBnqJFKpR6gm",
    "erc-20-001-3-16": "asst_wn9R7oQTUr60VpfvvaZ5asBa",
    "erc-20-005-3-16": "asst_3pHhhAMFwXi9JCVPOvftRQJU",
    "erc-20-010-3-16": "asst_OZk81q3HVr1mrGXCfOiVKaku",
    "erc-20-001-5-16": "asst_M6Q7TjZTC5wLDXdA88kCre7o",
    "erc-20-005-5-16": "asst_XFsmrlLmDMcbQ8uPeG4EVGA0",
    "erc-20-010-5-16": "asst_d1TPZLOP9HSmJq0va4vD2rcW",
    "erc-20-001-7-16": "asst_M8jjeryyXFYdnGSiQuyOB4ij",
    "erc-20-005-7-16": "asst_w98aowF6diNCOJxaM9li84Hi",
    "erc-20-010-7-16": "asst_FEGX60kN1RpiFGQP3CaQI6vO",
    "erc-721-001-3-16": "asst_nPqcpEo7lJnH4nmX9sNSBmfX",
    "erc-721-005-3-16": "asst_wipOM1IWYzuK1jyqwqRJmDic",
    "erc-721-010-3-16": "asst_MnKQphy1oPqu7QUWah63JFJk",
    "erc-721-001-5-16": "asst_kjoZHBonf5tXKpuiJ6Z4T3Gv",
    "erc-721-005-5-16": "asst_u2r0eDkkqERqTmOY5soRPU7n",
    "erc-721-010-5-16": "asst_YNv1CBWWYuzTg4D7rRK7JVL6",
    "erc-721-001-7-16": "asst_odutVf248qCN3C9zlFKLNd9a",
    "erc-721-005-7-16": "asst_HdOeD4DYTJAHfluUAeu6cwNJ",
    "erc-721-010-7-16": "asst_JNnQFWooGybyzS3juCJT5GQg",
    "erc-20-001-3-16": "asst_wn9R7oQTUr60VpfvvaZ5asBa",
    "erc-20-005-3-16": "asst_3pHhhAMFwXi9JCVPOvftRQJU",
    "erc-20-010-3-16": "asst_OZk81q3HVr1mrGXCfOiVKaku",
    "erc-20-001-5-16": "asst_M6Q7TjZTC5wLDXdA88kCre7o",
    "erc-20-005-5-16": "asst_XFsmrlLmDMcbQ8uPeG4EVGA0",
    "erc-20-010-5-16": "asst_d1TPZLOP9HSmJq0va4vD2rcW",
    "erc-20-001-7-16": "asst_M8jjeryyXFYdnGSiQuyOB4ij",
    "erc-20-005-7-16": "asst_w98aowF6diNCOJxaM9li84Hi",
    "erc-20-010-7-16": "asst_FEGX60kN1RpiFGQP3CaQI6vO",
}

# Add combined assistant IDs for those specified in SPECIFIC_JOBS_TO_RUN
# This is a simple way to handle them; you might want a more robust lookup.
ASSISTANT_IDS_COMBINED = {**ASSISTANT_IDS_FUNC_BY_FUNC, **ASSISTANT_IDS_LOOP_CONTRACT}

def main():
    parser = argparse.ArgumentParser(description="Run specific contract verification combinations.")
    parser.add_argument(
        "--verifier",
        type=str,
        required=True,
        choices=["func_by_func", "loop_contract"],
        help="The verifier script to use: func_by_func_verifier.py or loop_contract_verifier.py"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=10,
        help="Number of verification runs for each combination (default: 10)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="Maximum iterations per run for each combination (default: 10)"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=15,
        help="Delay in seconds between running jobs (default: 5)"
    )
    args = parser.parse_args()

    verifier_script = ""
    if args.verifier == "func_by_func":
        verifier_script = "func_by_func_verifier.py"
    elif args.verifier == "loop_contract":
        verifier_script = "loop_contract_verifier.py"
    else:
        print(f"Error: Invalid verifier choice '{args.verifier}'.")
        return

    # Ensure the script is run from the 'experiments' directory or adjust path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    verifier_script_path = os.path.join(script_dir, verifier_script)

    if not os.path.exists(verifier_script_path):
        print(f"Error: Verifier script '{verifier_script_path}' not found.")
        print("Please ensure this script is in the 'experiments' directory alongside the verifier scripts.")
        return
        
    print(f"Using verifier: {verifier_script}")

    for i, (assistant_key, requested_erc, context_erc) in enumerate(SPECIFIC_JOBS_TO_RUN):
        print(f"\\n--- Running Job {i+1}/{len(SPECIFIC_JOBS_TO_RUN)} ---")
        print(f"Assistant: {assistant_key}, Requested: {requested_erc}, Context: {context_erc if context_erc else 'None'}")

        # Check if the assistant_key is directly usable or needs mapping (optional, based on verifier script logic)
        # The verifier scripts seem to lookup assistant_key in their own ASSISTANT_IDS
        # So, we pass the key directly.

        cmd = [
            "python3",
            verifier_script_path,
            "--assistant", assistant_key,
            "--requested", requested_erc,
            "--context", context_erc if context_erc else "", # Pass empty string for no context
            "--runs", str(args.runs),
            "--max-iterations", str(args.max_iterations)
        ]

        print(f"Executing command: {' '.join(cmd)}")
        try:
            # Run the command and stream output
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, cwd=script_dir)
            for line in process.stdout:
                print(line, end='')
            process.wait()
            if process.returncode != 0:
                print(f"WARNING: Command for job {i+1} exited with code {process.returncode}")
        except Exception as e:
            print(f"ERROR: Command execution failed for job {i+1}: {str(e)}")

        if i < len(SPECIFIC_JOBS_TO_RUN) - 1:
            print(f"Waiting {args.delay} seconds before the next job...")
            time.sleep(args.delay)

    print("\\nAll specific jobs completed.")

if __name__ == "__main__":
    main() 