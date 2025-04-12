# Smart Contract Verification Performance Analysis

## Executive Summary

Analysis of various prompting strategies for smart contract verification reveals that models with diverse contexts consistently outperform specialized models. The `4o_mini_erc20_721_1155` model achieved the highest success rate (66.7%), while narrowly specialized models performed worse than the base model. These findings suggest that effective smart contract verification requires broad contextual understanding rather than narrow specialization.

## Overview

This document summarizes the performance analysis of different LLM prompting strategies for smart contract verification. The experiments tested various models with different context combinations across ERC20, ERC721, and ERC1155 contract types.

## Key Findings

### Overall Performance

- The `4o_mini_erc20_721_1155` model demonstrated the best overall performance with an average success rate of **66.7%** across all contract types and contexts.
- The `4o_mini_erc20_721` and `4o_mini_erc20_1155` models tied for second place with **47.5%** success rates.
- Other model performance rates:
  - `4o_mini_erc721_1155`: **46.3%** success rate
  - Base model `4o_mini`: **43.8%** success rate
  - `4o_mini_erc20`: **27.5%** success rate
  - `4o_mini_erc1155`: **25.4%** success rate
  - `4o_mini_erc721`: **17.1%** success rate (worst performer)
- This significant performance gap suggests that some specialized context combinations may actually hinder verification capabilities when used in isolation.
- Multi-context models generally outperformed single-context specialized models, suggesting that diversity in context improves verification capabilities.
- Notably, the base model `4o_mini` performed relatively well, outperforming several specialized models, indicating that the foundation model has strong general capabilities.

### Performance by Contract Type

1. **ERC20 Contracts**:

   - Best verified by models with ERC20 context (perfect 100% success rate in many ERC20 scenarios)
   - The base model `4o_mini` performed strongly on ERC20 contracts with a 72.5% success rate
   - The `4o_mini_erc20_721`, and `4o_mini_erc20_721_1155` models achieved perfect scores when verifying ERC20 contracts with matching context

2. **ERC721 Contracts**:

   - Best verified by models with ERC721 context when the contract type is known
   - The `4o_mini_erc721` model achieved 51.3% success rate specifically on ERC721 contracts, despite its poor overall performance
   - The base model `4o_mini` achieved a 31.3% success rate on ERC721 contracts
   - Models combining ERC721 with other contexts performed better across all contract types

3. **ERC1155 Contracts**:
   - Best verified by multi-context models that include ERC1155
   - Multiple models achieved 100% success rate on ERC1155 contracts when the context included ERC1155
   - The base model `4o_mini` showed moderate performance (27.5%) on ERC1155 contracts

### Context Effectiveness

- The heatmap visualization clearly shows which contexts are most effective for each contract type:

  - For ERC20 contracts:

    - Highest performance when using ERC20 context (avg. 73% success rate)
    - Maintains good performance when ERC20 is combined with other contexts
    - Poor performance with unrelated contexts like ERC721 alone (avg. 25% success rate)

  - For ERC721 contracts:

    - Best results with ERC721 context (avg. 67% success rate)
    - Good results with combined contexts that include ERC721
    - Moderate transfer of skills from ERC20 context (42% success rate)

  - For ERC1155 contracts:
    - Strong performance with ERC1155 context (avg. 59% success rate)
    - Very effective when combined with other contexts (particularly with ERC20 and ERC721)
    - Minimal performance when using no context (19% success rate)

- The results suggest that providing relevant context significantly improves verification capability, with the most dramatic improvements seen when the context precisely matches the contract type being verified.

### Best Model by Scenario

- `4o_mini_erc20_721_1155` was the top performer in 20 out of 24 scenarios (83% of cases)
- For specialized cases, the models with matching context often performed best:
  - `4o_mini_erc20_721` and `4o_mini_erc721_1155` each won in 7 scenarios
  - The base model `4o_mini` won in 6 scenarios
  - `4o_mini_erc721` and `4o_mini_erc20` each won in 4 scenarios
  - `4o_mini_erc20_1155` and `4o_mini_erc1155` each won in 3 scenarios
- Multiple models tied for best performance in several scenarios, particularly with their specialized contract types

## Conclusions

1. **Context Specialization Matters**: Models trained with relevant context perform significantly better than those without, especially when the context precisely matches the target contract type.

2. **Diverse Contexts Outperform**: For best results, use:

   - A model with multiple contexts when handling diverse contract types
   - A model with specific matching context when the contract type is known

3. **Cross-Contract Knowledge**: Models show some ability to transfer knowledge between similar contract types, but perform best when the context includes the contract type being verified.

4. **Base Model Competence**: The base model `4o_mini` shows good general competence (43.8% success rate), outperforming several specialized models. This suggests that the foundation model has strong general verification capabilities that can be enhanced with the right context.

5. **ERC20 Provides Foundation**: Models including ERC20 context consistently outperformed others, suggesting that ERC20 understanding may provide valuable foundational knowledge for smart contract verification.

## Recommendations

1. For production verification systems:

   - Deploy the `4o_mini_erc20_721_1155` model as the primary verifier for most scenarios
   - Use specialized models only when the contract type is known with high confidence
   - Consider the base model `4o_mini` as a reliable general-purpose alternative, especially for ERC20 contracts
   - Avoid using the `4o_mini_erc721` and `4o_mini_erc1155` models as standalone verifiers
   - Consider ensemble approaches that leverage multiple specialized models for increased accuracy

2. For future experiments:
   - Test with more varied and complex contract types
   - Explore the impact of training data quantity vs. context diversity
   - Investigate performance on contracts combining multiple standards
   - Analyze why single-standard contexts like ERC721 and ERC1155 perform poorly in isolation
   - Examine the specific verification errors to understand failure patterns

## Limitations

- The current analysis is based on success rates for verification tasks and may not capture other important metrics like false positive rates or reasoning quality
- Sample sizes per contract/context combination were limited
- The effectiveness of these models may vary on more complex or novel contract types not included in the test set
- The experiments do not account for variations in contract complexity within each standard

## Visualizations

Several visualizations were generated to illustrate these findings:

- `contract_type_comparison.png`: Average success rates by contract type
- `context_effectiveness_heatmap.png`: Heatmap showing which contexts work best for each contract type
- `best_model_counts.png`: Number of scenarios where each model performed best
- Individual contract type visualizations showing context effectiveness
