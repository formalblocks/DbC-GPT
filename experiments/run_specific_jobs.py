import subprocess
import time
import argparse
import os
import itertools # Added for combinations

SPECIFIC_JOBS_TO_RUN = [
    # ("4o-mini", "erc1155", ""),
    # ("erc-20-001-5-16", "erc1155", ""),
    # ("erc-721-001-5-16", "erc1155", ""),
    # ("erc-1155-001-5-16", "erc1155", ""),
    # ("erc-20-721-001-5-16", "erc1155", ""),
    # ("erc-20-1155-001-5-16", "erc1155", ""),
    # ("erc-721-1155-001-5-16", "erc1155", ""),
    # ("erc-20-721-1155-001-5-16", "erc1155", ""),
    ("erc-1155-001-3-16", "erc1155", ""),
    ("erc-1155-005-3-16", "erc1155", ""),
    ("erc-721-001-3-16", "erc1155", ""),
]

# This is the one to use for --mode all.
# The verifier scripts themselves are responsible for mapping these keys to actual OpenAI Assistant IDs.
ASSISTANT_KEYS_FOR_ALL_MODE = {
    "4o-mini": "asst_uMJ30gjHtG1VIBnqJFKpR6gm",
    "erc-1155-001-5-16": "asst_Mkq2y7mUxjusd47rPSGXrrCM",
    "erc-20-001-5-16": "asst_M6Q7TjZTC5wLDXdA88kCre7o",
    "erc-721-001-5-16": "asst_kjoZHBonf5tXKpuiJ6Z4T3Gv",
    "erc-20-721-001-5-16": "asst_waYnC3Fcp2JVmsShGUkz9o5y",
    "erc-20-1155-001-5-16": "asst_xiVobEjKhGFhIFIPw3EySfsf",
    "erc-721-1155-001-5-16": "asst_YsmuTcAJW179xCxAufROe2k1",
    "erc-20-721-1155-001-5-16": "asst_0JMCtwBpCeOHZ1lWmy4nErjB",
    # Add any other assistants here that you want to include in "all" mode
    # These keys must be present in the ASSISTANT_IDS of the verifier scripts.
}

ALL_REQUESTED_ERCS = ['erc20', 'erc721', 'erc1155', 'erc123']
ALL_CONTEXT_ERCS = ['erc20', 'erc721', 'erc1155', 'erc123']


def generate_all_combinations():
    """Generates all combinations for --mode all."""
    jobs = []
    assistant_keys = list(ASSISTANT_KEYS_FOR_ALL_MODE.keys())
    
    # Generate context combinations (none, single, pairs, triples, all four)
    context_combos_list = []
    for i in range(len(ALL_CONTEXT_ERCS) + 1):
        for combo in itertools.combinations(ALL_CONTEXT_ERCS, i):
            context_combos_list.append(",".join(combo))
            
    for assistant_key in assistant_keys:
        for requested_erc in ALL_REQUESTED_ERCS:
            for context_str in context_combos_list:
                jobs.append((assistant_key, requested_erc, context_str))
    return jobs

def main():
    parser = argparse.ArgumentParser(description="Run specific or all contract verification combinations.")
    parser.add_argument(
        "--verifier",
        type=str,
        required=True,
        choices=["func_by_func", "loop_contract"],
        help="The verifier script to use: func_by_func_verifier.py or loop_contract_verifier.py"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="specific", # Default to specific to maintain current behavior if not specified
        choices=["specific", "all"],
        help="Mode of operation: 'specific' to run SPECIFIC_JOBS_TO_RUN, 'all' to run all combinations."
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
        default=15, # Kept user's preference from selection
        help="Delay in seconds between running jobs (default: 15)"
    )
    args = parser.parse_args()

    verifier_script = ""
    if args.verifier == "func_by_func":
        verifier_script = "func_by_func_verifier.py"
    elif args.verifier == "loop_contract":
        verifier_script = "loop_contract_verifier.py"
    else: # Should not happen due to choices in argparse
        print(f"Error: Invalid verifier choice '{args.verifier}'.")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    verifier_script_path = os.path.join(script_dir, verifier_script)

    if not os.path.exists(verifier_script_path):
        print(f"Error: Verifier script '{verifier_script_path}' not found.")
        print("Please ensure this script is in the 'experiments' directory alongside the verifier scripts.")
        return
        
    print(f"Using verifier: {verifier_script}")
    print(f"Mode: {args.mode}")

    jobs_to_run = []
    if args.mode == "specific":
        jobs_to_run = SPECIFIC_JOBS_TO_RUN
        if not jobs_to_run:
            print("Warning: SPECIFIC_JOBS_TO_RUN is empty and mode is 'specific'. No jobs to run.")
            return
    elif args.mode == "all":
        print("Generating all combinations...")
        jobs_to_run = generate_all_combinations()
        num_assistants = len(ASSISTANT_KEYS_FOR_ALL_MODE)
        num_requested = len(ALL_REQUESTED_ERCS)
        num_context_variations = 0
        for i in range(len(ALL_CONTEXT_ERCS) + 1):
            num_context_variations += len(list(itertools.combinations(ALL_CONTEXT_ERCS, i)))
        
        print(f"Total combinations generated for 'all' mode: {len(jobs_to_run)}")
        print(f"  Assistants: {num_assistants} (from ASSISTANT_KEYS_FOR_ALL_MODE)")
        print(f"  Requested ERCs: {num_requested} ({', '.join(ALL_REQUESTED_ERCS)})")
        print(f"  Context Variations: {num_context_variations}")
        if not jobs_to_run:
            print("Warning: No combinations generated for 'all' mode. Check configurations.")
            return
    
    if not jobs_to_run: # Should be caught earlier, but as a safeguard
        print("No jobs to run.")
        return

    for i, (assistant_key, requested_erc, context_erc) in enumerate(jobs_to_run):
        # Ensure assistant_key is valid for the chosen verifier by checking its internal ASSISTANT_IDS
        # This script will pass the key; the verifier script must be able to find it.
        # No explicit check here as the verifier scripts handle this lookup.

        print(f"\\n--- Running Job {i+1}/{len(jobs_to_run)} ---")
        print(f"  Verifier: {args.verifier}")
        print(f"  Assistant: {assistant_key}")
        print(f"  Requested: {requested_erc}")
        print(f"  Context: {context_erc if context_erc else 'None'}")
        print(f"  Runs: {args.runs}, Max Iterations: {args.max_iterations}")

        cmd = [
            "python3",
            verifier_script_path,
            "--assistant", assistant_key,
            "--requested", requested_erc,
            "--context", context_erc if context_erc else "", 
            "--runs", str(args.runs),
            "--max-iterations", str(args.max_iterations)
        ]

        print(f"Executing command: {' '.join(cmd)}")
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, cwd=script_dir)
            for line in process.stdout:
                print(line, end='')
            process.wait()
            if process.returncode != 0:
                print(f"WARNING: Command for job {i+1} (Assistant: {assistant_key}, Requested: {requested_erc}, Context: {context_erc if context_erc else 'None'}) exited with code {process.returncode}")
        except Exception as e:
            print(f"ERROR: Command execution failed for job {i+1} (Assistant: {assistant_key}, Requested: {requested_erc}, Context: {context_erc if context_erc else 'None'}): {str(e)}")

        if i < len(jobs_to_run) - 1:
            print(f"Waiting {args.delay} seconds before the next job...")
            time.sleep(args.delay)

    print("\\nAll scheduled jobs completed.")

if __name__ == "__main__":
    main() 