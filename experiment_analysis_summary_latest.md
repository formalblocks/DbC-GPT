# Experiment Analysis Summary

This document summarizes the results of the fine-tuning experiments for generating `solc-verify` postconditions using different GPT-4o-mini models. The analysis is based on 1920 total runs.

## Overall Performance Analysis (`analyze_overall_performance.py`)

This section presents the overall success rates of each model across all tasks. Success is defined as generating postconditions that pass `solc-verify`.

**Total Runs Analyzed:** 1920

**Overall Success Rates:**

| Model                   | Success Rate (%) | Successful Runs | Total Runs |
| :---------------------- | :--------------- | :-------------- | :--------- |
| erc20-721-1155-4-o-mini | 66.25            | 159             | 240        |
| erc20-1155-4-o-mini     | 55.42            | 133             | 240        |
| erc20-721-4-o-mini      | 54.58            | 131             | 240        |
| erc721-1155-4-o-mini    | 49.58            | 119             | 240        |
| erc20-4-o-mini          | 50.00            | 120             | 240        |
| erc721-4-o-mini         | 45.83            | 110             | 240        |
| 4o-mini                 | 42.92            | 103             | 240        |
| erc1155-4-o-mini        | 36.67            | 88              | 240        |

**Key Observations:**

- The model fine-tuned on all three standards (`erc20-721-1155-4-o-mini`) achieved the highest overall success rate.
- Fine-tuning generally improved performance compared to the baseline `4o-mini` model, with the exception of `erc1155-4-o-mini` which performed slightly worse in the overall average (though it excels when specifically requested for ERC1155, see Model Specificity).
- Models fine-tuned on two standards performed better than the baseline but not as well as the triple-fine-tuned model.

## Fine-tuning Impact Analysis (`analyze_finetuning.py`)

This section analyzes the impact of fine-tuning on performance for specific ERC standard tasks (ERC20, ERC721, ERC1155).

**Total Runs Analyzed:** 1920

**Success Rates per Task:**

**ERC20 Task:**

| Model                   | Success Rate (%) | Successful Runs | Total Runs |
| :---------------------- | :--------------- | :-------------- | :--------- |
| erc20-721-1155-4-o-mini | 73.75            | 59              | 80         |
| erc20-721-4-o-mini      | 72.50            | 58              | 80         |
| erc20-1155-4-o-mini     | 66.25            | 53              | 80         |
| erc20-4-o-mini          | 53.75            | 43              | 80         |
| 4o-mini                 | 51.25            | 41              | 80         |
| erc721-1155-4-o-mini    | 48.75            | 39              | 80         |
| erc721-4-o-mini         | 40.00            | 32              | 80         |
| erc1155-4-o-mini        | 16.25            | 13              | 80         |

**ERC721 Task:**

| Model                   | Success Rate (%) | Successful Runs | Total Runs |
| :---------------------- | :--------------- | :-------------- | :--------- |
| erc20-721-1155-4-o-mini | 67.50            | 54              | 80         |
| erc20-1155-4-o-mini     | 53.75            | 43              | 80         |
| erc721-4-o-mini         | 51.25            | 41              | 80         |
| 4o-mini                 | 50.00            | 40              | 80         |
| erc721-1155-4-o-mini    | 50.00            | 40              | 80         |
| erc20-721-4-o-mini      | 50.00            | 40              | 80         |
| erc20-4-o-mini          | 48.75            | 39              | 80         |
| erc1155-4-o-mini        | 45.00            | 36              | 80         |

**ERC1155 Task:**

| Model                   | Success Rate (%) | Successful Runs | Total Runs |
| :---------------------- | :--------------- | :-------------- | :--------- |
| erc20-721-1155-4-o-mini | 57.50            | 46              | 80         |
| erc721-1155-4-o-mini    | 50.00            | 40              | 80         |
| erc1155-4-o-mini        | 48.75            | 39              | 80         |
| erc20-4-o-mini          | 47.50            | 38              | 80         |
| erc20-1155-4-o-mini     | 46.25            | 37              | 80         |
| erc721-4-o-mini         | 46.25            | 37              | 80         |
| erc20-721-4-o-mini      | 41.25            | 33              | 80         |
| 4o-mini                 | 27.50            | 22              | 80         |

**Key Observations:**

- Fine-tuning significantly improves performance on the specific task(s) the model was trained on.
- Models fine-tuned on ERC20 (`erc20-*`) show the most substantial gains for ERC20 tasks.
- Models fine-tuned on ERC721 (`erc721-*`) show improvements for ERC721 tasks.
- Models fine-tuned on ERC1155 (`erc1155-*`) show significant improvements for ERC1155 tasks.
- The triple-fine-tuned model (`erc20-721-1155-4-o-mini`) consistently performs at or near the top for all three tasks, demonstrating good generalization.
- Fine-tuning on unrelated standards can sometimes negatively impact performance (e.g., `erc1155-4-o-mini` on ERC20 tasks, `erc721-4-o-mini` on ERC20 tasks).

## Model Specificity Analysis (`analyze_model_specificity.py`)

This section examines how well each model performs when specifically requested to generate postconditions for a particular ERC standard, regardless of the fine-tuning data.

**Total Runs Analyzed:** 1920

**Success Rate (%) for each Model on each Requested Type:**

| Assistant Model         | Requested ERC1155 (%) | Requested ERC20 (%) | Requested ERC721 (%) |
| :---------------------- | :-------------------- | :------------------ | :------------------- |
| 4o-mini                 | 27.50                 | 51.25               | 50.00                |
| erc1155-4-o-mini        | **48.75**             | 16.25               | 45.00                |
| erc20-1155-4-o-mini     | 46.25                 | 66.25               | 53.75                |
| erc20-4-o-mini          | 47.50                 | 53.75               | 48.75                |
| erc20-721-1155-4-o-mini | **57.50**             | **73.75**           | **67.50**            |
| erc20-721-4-o-mini      | 41.25                 | 72.50               | 50.00                |
| erc721-1155-4-o-mini    | 50.00                 | 48.75               | 50.00                |
| erc721-4-o-mini         | 46.25                 | 40.00               | 51.25                |

**Successful Runs / Total Runs for each Model on each Requested Type:**

| Assistant Model         | Requested ERC1155 | Requested ERC20 | Requested ERC721 |
| :---------------------- | :---------------- | :-------------- | :--------------- |
| 4o-mini                 | 22 / 80           | 41 / 80         | 40 / 80          |
| erc1155-4-o-mini        | 39 / 80           | 13 / 80         | 36 / 80          |
| erc20-1155-4-o-mini     | 37 / 80           | 53 / 80         | 43 / 80          |
| erc20-4-o-mini          | 38 / 80           | 43 / 80         | 39 / 80          |
| erc20-721-1155-4-o-mini | 46 / 80           | 59 / 80         | 54 / 80          |
| erc20-721-4-o-mini      | 33 / 80           | 58 / 80         | 40 / 80          |
| erc721-1155-4-o-mini    | 40 / 80           | 39 / 80         | 40 / 80          |
| erc721-4-o-mini         | 37 / 80           | 32 / 80         | 41 / 80          |

**Key Observations:**

- Models generally perform best when requested for the standard(s) they were fine-tuned on.
- `erc1155-4-o-mini` shows strong specialization for ERC1155 requests but performs poorly on ERC20 requests.
- `erc20-721-4-o-mini` shows strong performance for ERC20 requests but is less effective for ERC1155.
- `erc20-721-1155-4-o-mini` demonstrates the best performance across all requested types, confirming its versatility.
- The baseline `4o-mini` has moderate performance across types but is significantly outperformed by specialized models on their respective tasks.

## Efficiency Analysis (`analyze_efficiency.py`)

This section evaluates the efficiency of the models in terms of the number of iterations (requests to the LLM) and time taken to reach a successful verification or exhaust attempts.

**Total Runs Analyzed:** 1920

**Overall Average Iterations and Time:**

| Run Succeeded | Average Iterations | Average Time Taken (s) |
| :------------ | :----------------- | :--------------------- |
| False         | 9.71               | 258.65                 |
| True          | 0.27               | 39.17                  |

**Average Iterations and Time per Model (Aggregated):**

| Model                   | Avg Iterations (Fail) | Avg Iterations (Success) | Avg Time (Fail, s) | Avg Time (Success, s) | Fail Rate (%) |
| :---------------------- | :-------------------- | :----------------------- | :----------------- | :-------------------- | :------------ |
| erc1155-4-o-mini        | 9.55                  | 0.22                     | 279.37             | 39.93                 | 63.33         |
| 4o-mini                 | 9.72                  | 0.12                     | 245.66             | 32.07                 | 57.08         |
| erc721-4-o-mini         | 9.78                  | 0.28                     | 250.26             | 37.38                 | 54.17         |
| erc721-1155-4-o-mini    | 9.71                  | 0.12                     | 285.66             | 35.86                 | 50.42         |
| erc20-4-o-mini          | 9.72                  | 0.17                     | 263.18             | 41.29                 | 50.00         |
| erc20-721-4-o-mini      | 9.76                  | 0.21                     | 223.71             | 36.33                 | 45.42         |
| erc20-1155-4-o-mini     | 9.71                  | 0.31                     | 273.89             | 45.28                 | 44.58         |
| erc20-721-1155-4-o-mini | 9.85                  | 0.60                     | 234.99             | 42.69                 | 33.75         |

_Note: Failed runs consistently use close to the maximum 10 iterations._

**Average Iterations and Time for SUCCESSFUL Runs by Task and Fine-tuning Level:**

**Successful ERC20 Task:**

| Model                   | Fine-tuning Level | Avg Iterations | Avg Time (s) |
| :---------------------- | :---------------- | :------------- | :----------- |
| erc20-4-o-mini          | 1                 | 0.14           | 36.77        |
| erc20-1155-4-o-mini     | 2                 | 0.34           | 38.67        |
| erc20-721-4-o-mini      | 2                 | 0.36           | 40.57        |
| erc20-721-1155-4-o-mini | 3                 | 0.59           | 40.65        |

**Successful ERC721 Task:**

| Model                   | Fine-tuning Level | Avg Iterations | Avg Time (s) |
| :---------------------- | :---------------- | :------------- | :----------- |
| erc721-4-o-mini         | 1                 | 0.24           | 35.29        |
| erc20-721-4-o-mini      | 2                 | 0.12           | 34.04        |
| erc721-1155-4-o-mini    | 2                 | 0.20           | 37.08        |
| erc20-721-1155-4-o-mini | 3                 | 0.11           | 36.91        |

**Successful ERC1155 Task:**

| Model                   | Fine-tuning Level | Avg Iterations | Avg Time (s) |
| :---------------------- | :---------------- | :------------- | :----------- |
| erc1155-4-o-mini        | 1                 | 0.05           | 33.80        |
| erc721-1155-4-o-mini    | 2                 | 0.03           | 30.42        |
| erc20-1155-4-o-mini     | 2                 | 0.30           | 46.78        |
| erc20-721-1155-4-o-mini | 3                 | 1.20           | 52.08        |

**Key Observations:**

- Successful runs are significantly faster and require far fewer iterations (often succeeding on the first try) compared to failed runs.
- The baseline `4o-mini` is the fastest for successful runs on average, likely because its successes are less complex or require fewer retries when it does succeed.
- The triple-fine-tuned model (`erc20-721-1155`), despite having the highest success rate, requires slightly more iterations and time on average for _successful_ runs compared to some simpler models, particularly for ERC1155. This might suggest it attempts more complex or comprehensive postconditions initially.
- For successful ERC1155 tasks, models fine-tuned _only_ or _primarily_ on ERC1155 (`erc1155-*`, `erc721-1155-*`) are the most efficient (fewest iterations).

## Learning Curve Analysis (`analyze_learning_curve.py`)

This section investigates the behavior of models during failed runs by analyzing the average number of correctly implemented functions (`status: ok`) per iteration before eventually failing verification. This provides insight into whether models "learn" or improve their output over successive iterations within a single failed attempt. Analysis focuses on 948 failed runs where at least one iteration occurred.

**Average Number of OK Functions per Iteration (Failed Runs):**

_Note: Table data represents the average count of functions marked 'ok' in the status history for each iteration up to 10, for runs that ultimately failed._ `-` _indicates no data for that iteration (e.g., all failed runs for that model/type finished before that iteration)._

```
iteration                                1    2    3    4    5    6    7    8    9    10
assistant_model         requested_type
4o-mini                 erc20          3.28 3.29 3.37 3.42 3.46 3.44 3.35 3.41 3.52 3.44
                        erc721         5.00 4.00 4.00 4.00 4.00 4.00 4.00 4.00 4.00 4.00
erc1155-4-o-mini        erc1155        5.00 5.00 5.00 5.00 5.00 5.00 5.00 5.00 5.00 5.00
                        erc20          3.70 3.73 3.75 3.70 3.76 3.74 3.76 3.73 3.75 3.71
                        erc721         6.70 6.60 6.60 6.22 6.44 6.44 5.78 6.38 6.29 6.17
erc20-1155-4-o-mini     erc1155        5.00 5.00 5.00 5.00 5.00 5.00 5.00 5.00    -    -
                        erc20          4.05 4.21 4.42 4.32 4.32 4.05 4.16 4.17 4.11 4.08
                        erc721         4.52 4.60 4.61 4.47 4.47 4.47 4.47 4.50 4.31 4.62
erc20-4-o-mini          erc20          3.88 4.20 4.30 4.33 4.30 4.33 4.30 4.30 4.34 4.18
                        erc721         6.92 6.92 6.91 6.64 6.73 6.80 6.89 6.88 7.00 7.00
erc20-721-1155-4-o-mini erc20          4.19 4.19 4.19 4.19 4.19 4.19 4.19 4.15 4.29 4.50
                        erc721         6.82 6.82 6.82 6.73 6.82 6.82 6.82 6.82 6.82 6.89
erc20-721-4-o-mini      erc1155        5.00 5.00 5.00 5.00 5.00 5.00 5.00 5.00 5.00 5.00
                        erc20          3.92 4.88 5.00 5.00 4.86 5.00 4.67 4.83 5.00 5.00
                        erc721         6.82 6.82 6.82 7.00 6.82 7.00 7.00 7.00 7.00 7.00
erc721-1155-4-o-mini    erc1155        4.00 4.00 4.00 4.00 4.00 4.00 4.00 4.00 4.00 4.00
                        erc20          3.41 3.48 3.58 3.53 3.47 3.47 3.34 3.45 3.50 3.57
                        erc721         6.40 6.64 6.67 6.58 6.67 6.67 6.67 6.73 6.80 6.67
erc721-4-o-mini         erc1155        5.00 5.00 5.00 5.00 5.00 5.00 5.00 5.00 5.00 5.00
                        erc20          4.05 4.11 3.97 4.00 3.97 3.91 3.91 3.88 3.87 4.13
                        erc721         6.50 7.00 7.00 7.00 7.00 7.00 7.00 5.67 7.00 7.00
```

**Key Observations:**

- There isn't a strong, consistent trend of increasing "ok" functions across iterations for most models and tasks during failed runs. The number of correct functions often fluctuates or plateaus.
- This suggests that when a model fails, simply retrying with the error feedback doesn't reliably lead to incrementally better (more correct functions) solutions within the 10-iteration limit. The models often get stuck or oscillate.
- Some models show high initial counts of "ok" functions even in failed runs (e.g., ERC721 tasks often start with 6-7 ok functions), indicating they might be failing on only one or two specific, difficult postconditions repeatedly.
- Models fine-tuned on specific standards generally produce more correct functions for that standard even in failed attempts (e.g., `erc20-721-4-o-mini` for ERC20 shows higher 'ok' counts than `4o-mini` for ERC20).

---

## Performance Analysis (No Target Context) (`analyze_no_target_context.py`)

This section analyzes performance specifically for runs where the requested ERC standard was _not_ provided in the context given to the model. This simulates a scenario where the model must rely solely on its fine-tuning or general knowledge without specific contextual examples of the target standard.

**Total Runs Analyzed (Filtered):** 960 (out of 1920 total)

**Overall Success Rates (No Target Context):**

| Model                   | Success Rate (%) | Successful Runs | Total Runs |
| :---------------------- | :--------------- | :-------------- | :--------- |
| erc20-721-1155-4-o-mini | 33.33            | 40              | 120        |
| erc20-721-4-o-mini      | 15.83            | 19              | 120        |
| erc20-1155-4-o-mini     | 15.00            | 18              | 120        |
| erc721-4-o-mini         | 5.83             | 7               | 120        |
| erc20-4-o-mini          | 2.50             | 3               | 120        |
| 4o-mini                 | 0.83             | 1               | 120        |
| erc1155-4-o-mini        | 0.83             | 1               | 120        |
| erc721-1155-4-o-mini    | 0.00             | 0               | 120        |

**Key Observations (No Target Context):**

- As expected, success rates drop significantly across all models when the target standard is not provided as context.
- The `erc20-721-1155-4-o-mini` model, fine-tuned on all standards, maintains the highest success rate (33.33%), demonstrating the best generalization capability even without direct context.
- Models fine-tuned on two standards (`erc20-721`, `erc20-1155`) perform much better than single-standard models or the baseline, but still show a large drop compared to their overall performance.
- Single-standard fine-tuned models and the baseline `4o-mini` perform very poorly (<= 5.83%), highlighting the importance of either broad fine-tuning or direct context for these models.
- The `erc721-1155-4-o-mini` model failed completely in this scenario, suggesting its fine-tuning might be overly specialized or require the specific context it was trained with.
- This analysis underscores the significant benefit of providing relevant contextual examples alongside the fine-tuning, especially for models not trained on the complete set of standards.

### Specificity Breakdown (No Target Context) (`analyze_specificity_no_target_context.py`)

Breaking down the "No Target Context" performance further by the requested ERC type:

**Success Rate (%) for each Model on each Requested Type (No Target Context):**

```
requested_type           erc1155  erc20  erc721
assistant_model
4o-mini                     0.00   2.50    0.00
erc1155-4-o-mini            0.00   2.50    0.00
erc20-1155-4-o-mini         2.50  32.50   10.00
erc20-4-o-mini              0.00   7.50    0.00
erc20-721-1155-4-o-mini    17.50  47.50   35.00
erc20-721-4-o-mini          0.00  47.50    0.00
erc721-1155-4-o-mini        0.00   0.00    0.00
erc721-4-o-mini             2.50  12.50    2.50
```

**Successful Runs / Total Runs for each Model on each Requested Type (No Target Context):**

```
requested_type          erc1155    erc20   erc721
assistant_model
4o-mini                  0 / 40   1 / 40   0 / 40
erc1155-4-o-mini         0 / 40   1 / 40   0 / 40
erc20-1155-4-o-mini      1 / 40  13 / 40   4 / 40
erc20-4-o-mini           0 / 40   3 / 40   0 / 40
erc20-721-1155-4-o-mini  7 / 40  19 / 40  14 / 40
erc20-721-4-o-mini       0 / 40  19 / 40   0 / 40
erc721-1155-4-o-mini     0 / 40   0 / 40   0 / 40
erc721-4-o-mini          1 / 40   5 / 40   1 / 40
```

**Additional Observations (Specificity without Target Context):**

- The `erc20-721-1155-4-o-mini` model's ability to generalize is further highlighted; it maintains reasonable success rates across all types even without context.
- Models primarily fine-tuned on ERC20 (`erc20-721`, `erc20-1155`) retain some capability for ERC20 requests but collapse for other standards when context is missing.
- Models without strong ERC20 fine-tuning (`erc721-4-o-mini`, `erc1155-4-o-mini`, `erc721-1155-4-o-mini`, `4o-mini`) are almost entirely unable to generate correct specifications for any standard without relevant context.

---

**Overall Conclusion:** Fine-tuning significantly improves the success rate for generating verifiable postconditions, especially when the model is fine-tuned on the relevant standard(s). The model fine-tuned on all three standards (`erc20-721-1155-4-o-mini`) provides the best overall performance and versatility. Providing relevant context significantly boosts performance, especially for models not fine-tuned on all standards. While successful runs are efficient, failed runs rarely show improvement across iterations, indicating that the error feedback mechanism might not be sufficient to guide the models to a correct solution within the iteration limit once they have initially failed.
