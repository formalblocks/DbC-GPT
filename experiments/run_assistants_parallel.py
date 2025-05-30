import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import logging
from loop_contract_verifier import run_verification_process as run_loop_verification
from func_by_func_verifier import run_verification_process as run_func_by_func_verification

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# List of all available assistants
ALL_ASSISTANTS = [
    # ERC1155 assistants
    "erc-1155-001-3-16",
    "erc-1155-005-3-16",
    "erc-1155-010-3-16",
    "erc-1155-001-5-16",
    "erc-1155-005-5-16",
    "erc-1155-010-5-16",
    "erc-1155-001-7-16",
    "erc-1155-005-7-16",
    "erc-1155-010-7-16",
    # ERC20 assistants
    "erc-20-001-3-16",
    "erc-20-005-3-16",
    "erc-20-010-3-16",
    "erc-20-001-5-16",
    "erc-20-005-5-16",
    "erc-20-010-5-16",
    "erc-20-001-7-16",
    "erc-20-005-7-16",
    "erc-20-010-7-16",
    # ERC721 assistants
    "erc-721-001-3-16",
    "erc-721-005-3-16",
    "erc-721-010-3-16",
    "erc-721-001-5-16",
    "erc-721-005-5-16",
    "erc-721-010-5-16",
    "erc-721-001-7-16",
    "erc-721-005-7-16",
    "erc-721-010-7-16"
]

ALL_CONTEXT_TYPES = ["erc20", "erc721", "erc1155"]

def run_single_assistant(assistant_key, requested_type, context_type, num_runs, max_iterations, mode):
    """Run verification process for a single assistant and context type"""
    try:
        logging.info(f"Starting verification for assistant: {assistant_key} with context: {context_type}")
        
        if mode == "entire_contract":
            results = run_loop_verification(
                requested_type=requested_type,
                context_types=[context_type] if context_type else [],
                assistant_key=assistant_key,
                num_runs=num_runs,
                max_iterations=max_iterations
            )
        else:  # func_by_func mode
            results = run_func_by_func_verification(
                requested_type=requested_type,
                context_types=[context_type] if context_type else [],
                assistant_key=assistant_key,
                num_runs=num_runs,
                max_iterations=max_iterations
            )
            
        logging.info(f"Completed verification for assistant: {assistant_key} with context: {context_type}")
        return results
    except Exception as e:
        logging.error(f"Error running assistant {assistant_key} with context {context_type}: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Run all assistants in parallel')
    parser.add_argument('--mode', type=str, required=True,
                        choices=['entire_contract', 'func_by_func'],
                        help='Verification mode: entire_contract or func_by_func')
    parser.add_argument('--requested', type=str, required=True,
                        choices=['erc20', 'erc721', 'erc1155'],
                        help='The contract type to verify')
    parser.add_argument('--runs', type=int, default=10,
                        help='Number of verification runs per assistant')
    parser.add_argument('--max-iterations', type=int, default=10,
                        help='Maximum iterations per run')
    parser.add_argument('--max-workers', type=int, default=8,
                        help='Maximum number of parallel workers')
    parser.add_argument('--assistants', type=str, default='all',
                        help='Comma-separated list of assistants to run, or "all" for all available assistants')
    parser.add_argument('--contexts', type=str, default='',
                        help='Comma-separated list of context types to use, or "all" for all context types, or empty for no context')
    
    args = parser.parse_args()

    # Get list of assistants to run
    if args.assistants.lower() == 'all':
        assistants = ALL_ASSISTANTS
    else:
        assistants = [a.strip() for a in args.assistants.split(',') if a.strip()]
        # Validate that all requested assistants exist
        invalid_assistants = [a for a in assistants if a not in ALL_ASSISTANTS]
        if invalid_assistants:
            raise ValueError(f"Invalid assistant(s): {', '.join(invalid_assistants)}")

    # Get list of context types to run
    if args.contexts.lower() == 'all':
        context_types = ALL_CONTEXT_TYPES
    elif args.contexts.strip() == '':
        context_types = [None]  # Use None to indicate empty context
    else:
        context_types = [c.strip() for c in args.contexts.split(',') if c.strip()]
        # Validate that all requested context types exist
        invalid_contexts = [c for c in context_types if c not in ALL_CONTEXT_TYPES]
        if invalid_contexts:
            raise ValueError(f"Invalid context type(s): {', '.join(invalid_contexts)}")

    logging.info(f"Starting parallel execution with {args.max_workers} workers")
    logging.info(f"Running {args.runs} runs per assistant with max {args.max_iterations} iterations")
    logging.info(f"Mode: {args.mode}")
    logging.info(f"Requested type: {args.requested}")
    logging.info(f"Assistants: {assistants}")
    logging.info(f"Context types: {context_types}")

    # Create a ProcessPoolExecutor with the specified number of workers
    with ProcessPoolExecutor(max_workers=args.max_workers) as executor:
        # Submit all assistant/context runs to the executor
        future_to_run = {
            executor.submit(
                run_single_assistant,
                assistant_key,
                args.requested,
                context_type,
                args.runs,
                args.max_iterations,
                args.mode
            ): (assistant_key, context_type)
            for assistant_key in assistants
            for context_type in context_types
        }

        # Process completed futures as they finish
        for future in as_completed(future_to_run):
            assistant_key, context_type = future_to_run[future]
            try:
                results = future.result()
                if results:
                    logging.info(f"Successfully completed all runs for assistant: {assistant_key} with context: {context_type}")
                else:
                    logging.error(f"Failed to complete runs for assistant: {assistant_key} with context: {context_type}")
            except Exception as e:
                logging.error(f"Error processing results for assistant {assistant_key} with context {context_type}: {str(e)}")

    logging.info("All parallel executions completed")

if __name__ == "__main__":
    main() 