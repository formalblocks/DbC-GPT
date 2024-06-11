# Extracting Formal Smart-Contract Specifications from Natural Language with LLMs

This repository contains the implementation and experiments for the paper "Extracting formal smart-contract specifications from natural language with LLMs". The project leverages Large Language Models (LLMs), particularly ChatGPT, to automatically infer formal postcondition specifications for smart contract functions implemented in Solidity.

## Introduction

Developers often hesitate to provide formal specifications for software components, even well-established design-by-contract (DbC) properties like invariants, pre- and postconditions are neglected. This project employs state-of-the-art Natural Language (NL) processing technologies using LLMs to automatically infer formal specifications from component textual behavioral descriptions.

We implemented a framework, DbC-GPT, which generates postcondition specifications for smart contract functions implemented in Solidity. The framework uses the solc-verify tool to check the syntax and verify the reference implementation's conformance to the generated specifications.

## Project Structure

```
.
├── .devcontainer
├── .vscode
├── assets
│   ├── file_search
│   ├── fine-tuning
│   └── solc_verify_examples
├── experiments
│   ├── data_analysis
│   ├── loop_files
│   └── outputs
├── solc_verify_generator
│   ├── ERC1155
│   │   ├── imp
│   │   └── templates
│   ├── ERC20
│   │   ├── imp
│   │   │   └── math
│   │   └── templates]
│   ├── ERC721
│   │   ├── imp
│   │   └── templates
│   └── __pycache__
└── temp
```

- `experiments/loop_files`: Folder with scritps to run the iterative specification generation and verification process.
- `experiments/data_analysis`: Folder with scripts for analyzing the results of the verification process.
- `experiments/outputs`: Folder with the results of the experiments in csv format.
- `.env`: Environment variables (to be created by the user).
- `requirements.txt`: List of dependencies.

## Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/formalblocks/DbC-GPT.git
    cd DbC-GPT
    ```

2. **Create and activate a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate 
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**
Create a .env file in the root directory and add your OpenAI API key.

    ```bash
    OPENAI_API_KEY=your_openai_api_key
    ```