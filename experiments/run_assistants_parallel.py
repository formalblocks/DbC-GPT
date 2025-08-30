import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import logging
import os
import psutil
import time
import sys
from loop_contract_verifier import run_verification_process as run_loop_verification
from func_by_func_verifier import run_verification_process as run_func_by_func_verification
from itertools import combinations

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


ALL_ASSISTANTS = {
    "4o-mini",
    "erc-1155-001-5-16",
    "erc-20-001-5-16",
    "erc-721-001-5-16",
    "erc-20-721-001-5-16",
    "erc-20-1155-001-5-16",
    "erc-721-1155-001-5-16",
    "erc-20-721-1155-001-5-16"
}

ALL_CONTEXT_TYPES = ["erc20", "erc721", "erc1155"]

def auto_tune_workers_and_batch(mode='func_by_func'):
    """
    Auto-tune max_workers and batch_size based on system resources and workload type.
    
    Args:
        mode: 'func_by_func' or 'entire_contract'
    
    Returns:
        tuple: (max_workers, batch_size)
    """
    try:
        cpu_count = os.cpu_count() or 4
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Estimate memory usage per worker based on mode
        if mode == 'func_by_func':
            # func_by_func is more memory intensive (solc-verify + temp files)
            per_worker_gb = 2.0  # Conservative for process-based func_by_func
        else:
            # entire_contract mode is typically lighter
            per_worker_gb = 1.5
        
        # Calculate max workers based on RAM constraint
        max_by_ram = max(1, int((memory_gb * 0.8) // per_worker_gb))  # Use 80% of available RAM
        
        # Calculate max workers based on CPU constraint
        # For CPU-intensive process work, use 60-70% of cores
        max_by_cpu = max(1, int(cpu_count * 0.65))
        
        # Take the minimum to avoid bottlenecks
        max_workers = min(max_by_ram, max_by_cpu)
        
        # Ensure reasonable bounds
        max_workers = max(1, min(max_workers, 16))  # Cap at 16 for sanity
        
        # Calculate batch size
        # Rule: batch_size should be 2-3x max_workers to keep workers busy
        # but not so large as to overwhelm memory
        batch_multiplier = 2.5
        batch_size = max(max_workers, int(max_workers * batch_multiplier))
        
        # Cap batch size based on available memory
        max_batch_by_memory = max(1, int((memory_gb * 0.9) // per_worker_gb))
        batch_size = min(batch_size, max_batch_by_memory)
        
        logging.info(f"Auto-tuned for process executor, {mode} mode:")
        logging.info(f"  System: {cpu_count} cores, {memory_gb:.1f} GB RAM")
        logging.info(f"  Estimated {per_worker_gb:.1f} GB per worker")
        logging.info(f"  Max workers: {max_workers} (RAM limit: {max_by_ram}, CPU limit: {max_by_cpu})")
        logging.info(f"  Batch size: {batch_size}")
        
        return max_workers, batch_size
        
    except Exception as e:
        logging.warning(f"Could not auto-tune resources: {e}, using conservative defaults")
        return 2, 4  # Very conservative fallback

def get_optimal_worker_count():
    """Legacy function - kept for backward compatibility but now calls auto_tune_workers_and_batch"""
    max_workers, _ = auto_tune_workers_and_batch()
    return max_workers

def check_system_health():
    """Check if system is under stress - renamed from check_container_health for clarity"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        if memory_percent > 85:
            logging.warning(f"High memory usage: {memory_percent}% - pausing")
            time.sleep(30)  # Longer pause
            return False
        if cpu_percent > 95:
            logging.warning(f"High CPU usage: {cpu_percent}% - pausing")
            time.sleep(10)
            return False
        return True
    except:
        return True

def get_all_context_combinations():
    """Generate all possible combinations of context types"""
    all_combinations: list = [None]  # Start with no context
    # Generate all possible combinations of 1 to len(ALL_CONTEXT_TYPES) contexts
    for r in range(1, len(ALL_CONTEXT_TYPES) + 1):
        for combo in combinations(ALL_CONTEXT_TYPES, r):
            all_combinations.append(list(combo))
    return all_combinations

def run_single_assistant(assistant_key, requested_type, context_types, num_runs, max_iterations, mode):
    """Run verification process for a single assistant and context type"""
    try:
        # Enhanced resource monitoring before starting
        if not check_system_health():
            logging.warning(f"System under stress before starting assistant: {assistant_key}")
            time.sleep(30)
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        logging.info(f"Starting verification for assistant: {assistant_key} with contexts: {context_types} (CPU: {cpu_percent}%, Memory: {memory_percent}%)")
        
        if mode == "entire_contract":
            results = run_loop_verification(
                requested_type=requested_type,
                context_types=context_types if context_types else [],
                assistant_key=assistant_key,
                num_runs=num_runs,
                max_iterations=max_iterations
            )
        else:  # func_by_func mode
            results = run_func_by_func_verification(
                requested_type=requested_type,
                context_types=context_types if context_types else [],
                assistant_key=assistant_key,
                num_runs=num_runs,
                max_iterations=max_iterations
            )
            
        # Force cleanup after completion
        import gc
        gc.collect()
            
        logging.info(f"Completed verification for assistant: {assistant_key} with contexts: {context_types}")
        return results
    except Exception as e:
        logging.error(f"Error running assistant {assistant_key} with contexts {context_types}: {str(e)}")
        # Force cleanup on error
        import gc
        gc.collect()
        return None

def main():
    parser = argparse.ArgumentParser(description='Run all assistants in parallel with auto-tuned resource management')
    parser.add_argument('--mode', type=str, required=True,
                        choices=['entire_contract', 'func_by_func'],
                        help='Verification mode: entire_contract or func_by_func')
    parser.add_argument('--requested', type=str, required=True, 
                         choices=['erc20', 'erc721', 'erc1155', 'ercx'],
                         help='The contract type to verify')
    parser.add_argument('--runs', type=int, default=10,
                        help='Number of verification runs per assistant')
    parser.add_argument('--max-iterations', type=int, default=10,
                        help='Maximum iterations per run')
    parser.add_argument('--max-workers', type=int, default=None,
                        help='Maximum number of parallel workers (auto-detect if not specified)')
    parser.add_argument('--assistants', type=str, default='all',
                        help='Comma-separated list of assistants to run, or "all" for all available assistants')
    parser.add_argument('--contexts', type=str, default='all',
                        help='Comma-separated list of context types to use, or "all" for all possible combinations, or empty for no context')
    parser.add_argument('--all-contexts-only', action='store_true',
                        help='Run only the combination with all specified context types together (ignores other combinations)')
    parser.add_argument('--batch-size', type=int, default=None,
                        help='Process tasks in batches to prevent resource exhaustion (auto-detect if not specified)')
    parser.add_argument('--restart-after', type=int, default=100,
                        help='Restart after this many completed tasks to prevent resource leaks (default: 100)')
    parser.add_argument('--disable-auto-tune', action='store_true',
                        help='Disable auto-tuning and use manual/default values')
    
    args = parser.parse_args()

    # Constants for health management
    RESTART_AFTER_RUNS = args.restart_after

    # Auto-tune or use manual settings
    if not args.disable_auto_tune and (args.max_workers is None or args.batch_size is None):
        auto_max_workers, auto_batch_size = auto_tune_workers_and_batch(mode=args.mode)
        
        # Use auto-tuned values if not manually specified
        if args.max_workers is None:
            args.max_workers = auto_max_workers
        if args.batch_size is None:
            args.batch_size = auto_batch_size
    else:
        # Fallback to legacy method if auto-tuning is disabled
        if args.max_workers is None:
            args.max_workers = get_optimal_worker_count()
        if args.batch_size is None:
            args.batch_size = max(1, args.max_workers // 2)

    # Get list of assistants to run
    if args.assistants.lower() == 'all':
        assistants = ALL_ASSISTANTS
    else:
        assistants = [a.strip() for a in args.assistants.split(',') if a.strip()]
        # Validate that all requested assistants exist
        invalid_assistants = [a for a in assistants if a not in ALL_ASSISTANTS]
        if invalid_assistants:
            raise ValueError(f"Invalid assistant(s): {', '.join(invalid_assistants)}")

    # Get list of context combinations to run
    if args.contexts.lower() == 'all':
        context_combinations = get_all_context_combinations()
    elif args.contexts.strip() == '':
        context_combinations = [None]  # Use None to indicate empty context
    else:
        requested_contexts = [c.strip() for c in args.contexts.split(',') if c.strip()]
        # Validate that all requested context types exist
        invalid_contexts = [c for c in requested_contexts if c not in ALL_CONTEXT_TYPES]
        if invalid_contexts:
            raise ValueError(f"Invalid context type(s): {', '.join(invalid_contexts)}")
        # Generate all possible combinations of the requested contexts
        if args.all_contexts_only:
            # Only run the combination with all contexts together
            context_combinations = [requested_contexts]
        else:
            # Generate all possible combinations
            context_combinations = [None]  # Start with no context
            for r in range(1, len(requested_contexts) + 1):
                for combo in combinations(requested_contexts, r):
                    context_combinations.append(list(combo))  # type: ignore

    # Create all tasks
    all_tasks = [
        (assistant_key, args.requested, context_types, args.runs, args.max_iterations, args.mode)
        for assistant_key in assistants
        for context_types in context_combinations
    ]

    logging.info(f"=== EXECUTION CONFIGURATION ===")
    logging.info(f"Mode: {args.mode}")
    logging.info(f"Requested type: {args.requested}")
    logging.info(f"Max workers: {args.max_workers}")
    logging.info(f"Batch size: {args.batch_size}")
    logging.info(f"Runs per assistant: {args.runs}")
    logging.info(f"Max iterations per run: {args.max_iterations}")
    logging.info(f"Total tasks: {len(all_tasks)}")
    logging.info(f"Assistants: {list(assistants)}")
    logging.info(f"Context combinations: {context_combinations}")
    logging.info(f"Will restart after {RESTART_AFTER_RUNS} completed tasks")
    logging.info(f"Auto-tuning: {'disabled' if args.disable_auto_tune else 'enabled'}")

    completed_tasks = 0
    total_tasks = len(all_tasks)
    batch_size = args.batch_size

    # Process tasks in batches to prevent resource exhaustion
    for i in range(0, len(all_tasks), batch_size):
        # Check system health before starting each batch
        if not check_system_health():
            logging.info("System under stress, extending pause...")
            time.sleep(60)
        
        # Check for restart condition
        if completed_tasks > 0 and completed_tasks % RESTART_AFTER_RUNS == 0:
            logging.info(f"Scheduled restart after {completed_tasks} completed tasks")
            logging.info("Saving current state and exiting gracefully for restart")
            # Force cleanup before restart
            import gc
            gc.collect()
            sys.exit(0)  # Let process manager restart
        
        batch = all_tasks[i:i + batch_size]
        batch_num = i//batch_size + 1
        total_batches = (len(all_tasks) + batch_size - 1)//batch_size
        
        logging.info(f"=== BATCH {batch_num}/{total_batches} ===")
        logging.info(f"Processing {len(batch)} tasks with {args.max_workers} workers")
        
        # Create executor for this batch
        with ProcessPoolExecutor(max_workers=args.max_workers) as executor:
            # Submit batch tasks
            future_to_run = {
                executor.submit(run_single_assistant, *task): task
                for task in batch
            }

            # Process completed futures as they finish
            for future in as_completed(future_to_run):
                task = future_to_run[future]
                assistant_key, requested_type, context_types, num_runs, max_iterations, mode = task
                completed_tasks += 1
                
                try:
                    results = future.result()
                    if results:
                        logging.info(f"✅ [{completed_tasks}/{total_tasks}] SUCCESS: {assistant_key} with contexts: {context_types}")
                    else:
                        logging.error(f"❌ [{completed_tasks}/{total_tasks}] FAILED: {assistant_key} with contexts: {context_types}")
                except Exception as e:
                    logging.error(f"💥 [{completed_tasks}/{total_tasks}] ERROR: {assistant_key} with contexts {context_types}: {str(e)}")

        # Pause between batches with health check
        if i + batch_size < len(all_tasks):
            logging.info("Pausing between batches for system recovery...")
            time.sleep(5)
            
            # Force garbage collection between batches
            import gc
            gc.collect()
            
            # Additional health check
            if not check_system_health():
                logging.info("Additional recovery pause due to system stress...")
                time.sleep(30)

    logging.info("🎉 All parallel executions completed successfully!")
    
    # Final cleanup
    import gc
    gc.collect()

if __name__ == "__main__":
    main()