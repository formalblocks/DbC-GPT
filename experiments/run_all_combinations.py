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
        if not requested:  # Skip empty requested type (not valid)
            continue
            
        # Empty context
        all_combinations.append((requested, ''))
        
        # Single contexts
        for ctx in contract_types:
            if ctx:  # Only add non-empty contexts
                all_combinations.append((requested, ctx))
        
        # Pairs of contexts
        for pair in itertools.combinations([c for c in contract_types if c], 2):
            # Use comma-separation instead of underscores
            all_combinations.append((requested, ','.join(pair)))
        
        # All three or more contract types as context
        for n in range(3, len([c for c in contract_types if c]) + 1):
            for combo in itertools.combinations([c for c in contract_types if c], n):
                # Use comma-separation
                all_combinations.append((requested, ','.join(combo)))
    
    return all_combinations

def is_combination_processed(requested, context, assistant_key="4o_mini"):
    """Check if a combination has already been processed"""
    # Convert context string to directory structure
    if not context:
        context_dir = "none"
    else:
        # Directory names use underscores, but our combinations now use commas
        context_dir = context.replace(',', '_')
    
    # Check only the new directory structure (by assistant key)
    results_path = f"results_{assistant_key}/{requested}/{context_dir}/{requested}_[{context}].csv"
    if os.path.exists(results_path):
        return True
    
    # Also check with underscores in the filename for compatibility
    if ',' in context:
        results_path = f"results_{assistant_key}/{requested}/{context_dir}/{requested}_[{context.replace(',', '_')}].csv"
        if os.path.exists(results_path):
            return True
    
    return False

def get_processed_combinations(assistant_key="4o_mini"):
    """Find all combinations that have already been processed"""
    processed = []
    
    # Check only the new directory structure (by assistant key)
    results_dir = f"results_{assistant_key}"
    if os.path.exists(results_dir):
        print(f"Checking results directory: {results_dir}")
        
        # Check each requested type directory
        for requested in os.listdir(results_dir):
            requested_dir = f"{results_dir}/{requested}"
            if not os.path.isdir(requested_dir):
                continue
                
            # Check each context directory
            for context_dir in os.listdir(requested_dir):
                result_dir = f"{requested_dir}/{context_dir}"
                if not os.path.isdir(result_dir):
                    continue
                    
                print(f'Checking context_dir: {context_dir} in {requested}')
                    
                # Check each CSV file
                for file in os.listdir(result_dir):
                    if file.endswith('.csv'):
                        try:
                            # Extract context from filename pattern: {requested}_[{context}].csv
                            parts = file.split('[')
                            if len(parts) > 1:
                                context = parts[1].split(']')[0]
                                
                                # Handle the empty context case
                                if context_dir == "none" and context == "none":
                                    processed.append((requested, ""))
                                else:
                                    # Convert underscores to commas for multi-context types
                                    if '_' in context and context != 'none':
                                        context = context.replace('_', ',')
                                    processed.append((requested, context))
                        except Exception as e:
                            print(f"Warning: Couldn't parse combination from {result_dir}/{file}: {e}")
    
    return processed

def print_combinations(combinations=None, processed=None):
    """Print all combinations that will be generated"""
    if combinations is None:
        combinations = generate_all_combinations()
        
    if processed is None:
        processed = get_processed_combinations()
    
    processed_set = set(processed)
    
    print(f"Total combinations: {len(combinations)}")
    print(f"Already processed: {len(processed_set)}")
    print(f"Remaining to process: {len(combinations) - len(processed_set)}")
    
    print("\nCombinations to be run:")
    for i, (requested, context) in enumerate(combinations, 1):
        status = "DONE" if (requested, context) in processed_set else "TODO"
        print(f"{i}. Requested: {requested}, Context: {context} - {status}")

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
    parser.add_argument('--skip-processed', action='store_true', default=True,
                      help='Skip combinations that have already been processed (default: True)')
    parser.add_argument('--force-all', action='store_true',
                      help='Force running all combinations, even if already processed')
    parser.add_argument('--assistant', type=str, default='4o_mini',
                      choices=['4o_mini', '4.1-mini', '4o-mini-erc-1155-new', '4o_mini_single', '4o_mini_erc20', '4o_mini_erc721', '4o_mini_erc1155', '4o_mini_erc721_1155', '4o_mini_erc20_1155', '4o_mini_erc20_721', '4o_mini_erc20_721_1155'],
                      help='The assistant to use (default: 4o_mini)')
    args = parser.parse_args()
    
    # Get all combinations
    combinations = generate_all_combinations()
    
    # Get already processed combinations
    processed_combinations = get_processed_combinations(args.assistant)
    processed_set = set(processed_combinations)
    
    if args.dry_run:
        print_combinations(combinations, processed_combinations)
        return
        
    # Ensure the logs directory exists
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"combination_run_{timestamp}.log")
    
    # Filter out already processed combinations if requested
    if args.skip_processed and not args.force_all:
        combinations_to_run = [(req, ctx) for req, ctx in combinations 
                              if (req, ctx) not in processed_set]
        print(f"Filtered out {len(combinations) - len(combinations_to_run)} already processed combinations.")
    else:
        combinations_to_run = combinations
    
    # Slice combinations if start-from or end-at is specified
    start_idx = max(0, args.start_from - 1)  # Convert to 0-based index
    end_idx = args.end_at
    combinations_to_run = combinations_to_run[start_idx:end_idx]
    
    # Write run plan to log
    with open(log_file, 'w') as log:
        log.write(f"Run plan created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"Total combinations: {len(combinations)}\n")
        log.write(f"Already processed: {len(processed_set)}\n")
        log.write(f"Combinations to run in this session: {len(combinations_to_run)}\n\n")
        log.write("Planned combinations:\n")
        for i, (req, ctx) in enumerate(combinations_to_run, 1):
            log.write(f"{i}. Requested: {req}, Context: {ctx}\n")
        log.write("\n")
    
    total_to_run = len(combinations_to_run)
    
    # Run each combination
    for i, (requested, context) in enumerate(combinations_to_run, 1):
        print(f"\n[{i}/{total_to_run}] Running combination: Requested={requested}, Context={context}")
        
        # Skip if already processed and we're not forcing re-runs
        if (requested, context) in processed_set and args.skip_processed and not args.force_all:
            print(f"Skipping combination - already processed")
            continue
        
        # Build the command
        cmd = [
            "python3", 
            "loop_contract_verifier.py",
            "--requested", requested,
            "--context", context,
            "--assistant", args.assistant,
            "--runs", "10",
            "--max-iterations", "10"
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
        if i < total_to_run:
            delay = args.delay
            print(f"Waiting {delay} seconds before next combination...")
            time.sleep(delay)
    
    print(f"\nAll combinations completed! Log file: {log_file}")

if __name__ == "__main__":
    main() 