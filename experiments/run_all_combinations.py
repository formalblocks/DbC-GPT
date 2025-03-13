#!/usr/bin/env python3
import subprocess
import itertools
import time
import os
from datetime import datetime
import argparse

def run_command(cmd, log_file):
    """Run a command and log its output"""
    print(f"Running: {' '.join(cmd)}")
    
    # Open log file in append mode
    with open(log_file, 'a') as log:
        log.write(f"\n{'='*80}\n")
        log.write(f"Command: {' '.join(cmd)}\n")
        log.write(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"{'='*80}\n\n")
    
    # Run the command and capture output
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Stream and log output
    with open(log_file, 'a') as log:
        for line in process.stdout:
            print(line, end='')
            log.write(line)
    
    # Wait for the command to complete
    process.wait()
    
    # Record completion time
    with open(log_file, 'a') as log:
        log.write(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"Exit code: {process.returncode}\n\n")
    
    return process.returncode

def generate_all_combinations():
    """Generate all possible combinations of requested and context contracts"""
    contract_types = ['erc20', 'erc721', 'erc1155', '']
    all_combinations = []
    
    # For each contract type as the requested type
    for requested in contract_types:
        # Empty context - represented as empty string
        all_combinations.append((requested, requested))
        
        # Generate all possible non-empty context combinations
        context_options = [t for t in contract_types if t != requested]
        
        # Single contexts
        for ctx in context_options:
            all_combinations.append((requested, ctx))
        
        # Add self to context options for combinations including self
        all_context_options = contract_types.copy()
        
        # Pairs of contexts
        for pair in itertools.combinations(all_context_options, 2):
            # Only include if at least one context type is different from requested
            if pair[0] != requested or pair[1] != requested:
                all_combinations.append((requested, ','.join(pair)))
        
        # Triples (all three contract types)
        if len(all_context_options) == 3:
            all_combinations.append((requested, ','.join(all_context_options)))
    
    return all_combinations

def print_combinations():
    """Print all combinations that will be generated"""
    combinations = generate_all_combinations()
    print(f"Total combinations: {len(combinations)}")
    print("Combinations to be run:")
    for i, (requested, context) in enumerate(combinations, 1):
        print(f"{i}. Requested: {requested}, Context: {context}")

def main():
    parser = argparse.ArgumentParser(description='Run all contract verification combinations')
    parser.add_argument('--dry-run', action='store_true', 
                      help='Print combinations without running them')
    parser.add_argument('--delay', type=int, default=30,
                      help='Delay in seconds between combination runs (default: 30)')
    parser.add_argument('--start-from', type=int, default=1,
                      help='Start from this combination index (1-based, default: 1)')
    parser.add_argument('--end-at', type=int, default=None,
                      help='End at this combination index (inclusive, default: run all)')
    args = parser.parse_args()
    
    if args.dry_run:
        print_combinations()
        return
        
    # Ensure the logs directory exists
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"combination_run_{timestamp}.log")
    
    # Get all combinations
    combinations = generate_all_combinations()
    
    # Write run plan to log
    with open(log_file, 'w') as log:
        log.write(f"Run plan created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"Total combinations to run: {len(combinations)}\n\n")
        log.write("Planned combinations:\n")
        for i, (req, ctx) in enumerate(combinations, 1):
            log.write(f"{i}. Requested: {req}, Context: {ctx}\n")
        log.write("\n")
    
    # Slice combinations if start-from or end-at is specified
    start_idx = max(0, args.start_from - 1)  # Convert to 0-based index
    end_idx = args.end_at if args.end_at is None else args.end_at
    combinations_to_run = combinations[start_idx:end_idx]
    
    # Run each combination
    for i, (requested, context) in enumerate(combinations_to_run, start_idx + 1):
        print(f"\n[{i}/{len(combinations)}] Running combination: Requested={requested}, Context={context}")
        
        # Skip empty requested type (not valid)
        if not requested:
            print(f"Skipping combination with empty requested type")
            continue
        
        # Build the command
        cmd = [
            "python", 
            "loop_contract_verifier.py",
            "--requested", requested,
            "--context", context,
            "--assistant", "4o_mini_single",  # Use default assistant (change if needed)
            "--runs", "10",       # Default number of runs
            "--max-iterations", "10"  # Default max iterations
        ]
        
        # Run the command and capture exit code
        try:
            exit_code = run_command(cmd, log_file)
            
            if exit_code != 0:
                print(f"WARNING: Command exited with code {exit_code}")
                # Add extra delay after an error
                print(f"Adding extra delay (60s) after error...")
                time.sleep(60)
        except Exception as e:
            print(f"ERROR: Command execution failed: {str(e)}")
            # Log the error
            with open(log_file, 'a') as log:
                log.write(f"\nERROR: Command execution failed: {str(e)}\n")
            # Add extra delay after an error
            print(f"Adding extra delay (60s) after error...")
            time.sleep(60)
        
        # Small delay between runs to let system resources settle
        if i < len(combinations):
            delay = args.delay
            print(f"Waiting {delay} seconds before next combination...")
            time.sleep(delay)
    
    print(f"\nAll combinations completed! Log file: {log_file}")

if __name__ == "__main__":
    # Uncomment to print all combinations without running them
    # print_combinations()
    main() 