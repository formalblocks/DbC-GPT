# Context Combination Verification Report (entire_contract - erc1155)

This table summarizes the performance of different context combinations for the assistant on the ERC1155 contract verification task, using the 'entire_contract' approach.

- **context**: The context combination used for the run.
- **verification_rate**: Fraction of runs that were successfully verified (higher is better).
- **min_success_iterations**: Minimum number of iterations needed to achieve a successful verification (lower is better).
- **max_iterations**: Maximum number of iterations used in any run.
- Other columns show averages and counts for each context.

| context | verification_rate | verified_count | total_runs | avg_time | avg_iterations | min_success_iterations | max_iterations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| erc20_erc721_erc1155 | 100.00 | 10 | 10 | 67.38982698917388 | 0.5 | 0.0 | 2 |
| erc721_erc1155 | 100.00 | 10 | 10 | 78.49783952236176 | 0.6 | 0.0 | 3 |
| erc20_erc1155 | 90.00 | 9 | 10 | 158.28276958465577 | 2.6 | 1.0 | 10 |
| erc1155 | 80.00 | 8 | 10 | 218.93863186836242 | 3.6 | 1.0 | 10 |
| erc20_erc721 | 40.00 | 4 | 10 | 300.93873727321625 | 7.2 | 1.0 | 10 |
| erc721 | 10.00 | 1 | 10 | 312.891521859169 | 9.2 | 2.0 | 10 |
| erc20 | 0.00 | 0 | 10 | 258.2753127336502 | 10.0 | - | 10 |
| none | 0.00 | 0 | 10 | 305.8131155014038 | 10.0 | - | 10 |
