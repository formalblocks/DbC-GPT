# DbC-GPT

This project implements a framework for generating design-by-contract specifications for Solidity smart contracts using GPT models. It integrates natural language processing, AI, and formal verification.

## Project Structure

- `assistant.py`: Script to interact with OpenAI GPT for generating formal specifications.
- `functions_scrapper.py`: Script to extract function details from Solidity smart contracts.
- `requirements.txt`: List of dependencies.
- `.env`: Environment variables (to be created by the user).

## Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/DbC-GPT.git
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

5. **Run the scripts**
    ```bash
    python functions_scrapper.py
    python assistant.py
    ``` 