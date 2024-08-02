import logging
import openai
import time
import sys
import re
import pandas as pd
from dataclasses import dataclass
from typing import List

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

openai.api_key = "your_open_ai_key"
# 3.5
#assistant_id = "asst_l6McDS1eeFqRSRucPUerwD3x"
# 4o
assistant_id = "asst_8AOYbeZmLBx8Uic6tFUGBjhF"

# Initialize the global counter
interaction_counter = 0

#Initialize the global verification status
verification_status = []

class Assistant:
    
    def __init__(self, id) -> None:
        self.id = id

class Thread:
    
    def __init__(self, assistant: Assistant) -> None:
        self.assistant = assistant
        self._thread = openai.beta.threads.create()
    
    @property
    def id(self):
        return self._thread.id
    
    def send_message(self, content: str) -> 'Interaction':
        interaction = Interaction(self, content)
        return interaction
    
    @property
    def last_message(self) -> str:
        response = openai.beta.threads.messages.list(
            thread_id= self.id
        )
        # Returns last response from thread
        return response.data[0].content[0].text.value

class Interaction:
    
    def __init__(self, thread: Thread, prompt: str) -> None:
        self.thread = thread
        self.prompt = prompt
        self._create_message()
        self._create_run()

    def _create_message(self):
        openai.beta.threads.messages.create(
            thread_id = self.thread.id,
            role = "user",
            content = self.prompt
        )
    
    def _create_run(self):
        self._run = openai.beta.threads.runs.create(
            thread_id = self.thread.id,
            assistant_id = self.thread.assistant.id,
        )
    
    @property
    def id(self):
        return self._run.id
    
    def remote_sync(self):
        self._run = openai.beta.threads.runs.retrieve(
            thread_id = self.thread.id,
            run_id = self._run.id
        )
    
    @property
    def status(self):
        return self._run.status

    
    def await_for_response(self) -> str:
        status = self.status
        while (status != "completed"):
            self.remote_sync()
            status = self.status
            logging.info("awaiting for a response. status: " + str(status))
            time.sleep(2)
        return self.thread.last_message

@dataclass
class VerificationResult:
    status: int
    output: str

class SolcVerifyWrapper:

    SOLC_VERIFY_CMD = "solc-verify.py"
    SPEC_FILE_PATH = './temp/spec.sol'
    ERC20_TEMPLATE_PATH = './solc_verify_generator/ERC20/templates/imp_spec_merge.template'
    #ERC20_TEMPLATE_PATH = './solc_verify_generator/ERC20/templates/spec_refinement.template'
    ERC20_MERGE_PATH = './solc_verify_generator/ERC20/imp/ERC20_merge.sol'

    @classmethod
    def call_solc(cls, file_path) -> VerificationResult:
        from subprocess import PIPE, run
        command = [cls.SOLC_VERIFY_CMD, file_path]
        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        return VerificationResult(result.returncode, result.stdout + result.stderr)
    

    @classmethod
    def verify(cls, soldity_spec_str: str) -> VerificationResult:
        """
        Parameters
            spec_str: Solidity code with only the function signatures
            annotated with solc-verify conditions
        """
        Utils.save_string_to_file(cls.SPEC_FILE_PATH, soldity_spec_str)
        from solc_verify_generator.main import generate_merge
        try:
            generate_merge(cls.SPEC_FILE_PATH, cls.ERC20_TEMPLATE_PATH, cls.ERC20_MERGE_PATH)
        except RuntimeError as e:
            return VerificationResult(*e.args)
        return cls.call_solc(cls.ERC20_MERGE_PATH)


class Utils:

    @staticmethod
    def extract_solidity_code(markdown_text):
        # Regex pattern to match code blocks with "solidity" as the language identifier
        pattern = r'```solidity\n(.*?)```'
        
        # Use re.DOTALL to match newline characters in the code block
        matches = re.findall(pattern, markdown_text, re.DOTALL)
        
        # Try to return first match
        try:
            return matches[0]
        except IndexError:
            return None
        

    @staticmethod
    def save_string_to_file(file_name, content):
        try:
            with open(file_name, 'w') as file:
                file.write(content)
            print(f"Content successfully saved to {file_name}")
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")

    @staticmethod
    def save_results_to_csv(file_name: str, results: List[dict]):
        # Convert list of dictionaries to pandas DataFrame
        df = pd.DataFrame(results)
        
        try:
            # Save DataFrame to CSV
            df.to_csv(file_name, index=False)
            print(f"Results successfully saved to {file_name}")
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")

def loop(thread: Thread, message: str) -> bool:
    global interaction_counter
    interaction_counter += 1
    # Break the loop if the counter is greater than 10
    if (interaction_counter > 10):
        print("Counter exceeded 10, breaking the loop")
        return False
    print('COUNTER', interaction_counter)
    interaction: Interaction = thread.send_message(message)
    response: str = interaction.await_for_response()
    solidity_code = Utils.extract_solidity_code(response)

    if not solidity_code:
        print("ERROR - No Solidity code found in the response.")
        return False
    try:
        # Add error handling
        verification_result: VerificationResult = SolcVerifyWrapper.verify(solidity_code)
    except Exception as e:
        print(f"An error occurred during verification: {e}")
        return False

    if verification_result.status:
        global verification_status
        if "OK" in verification_result.output and "ERROR" in verification_result.output:
            verification_status.append(f'Iteraction: {interaction_counter}\n{verification_result.output}\n')

        instructions = """
        Instructions:
        - Function Bodies: The specification must not contain function implementations.
        - Postconditions Limit: Each function must have at most 4 postcondition (/// @notice postcondition) annotations above the function signature. Do not exceed this limit under any circumstances.
        - Position: add the solc-verify annotation above the related function, example:
            /// @notice postcondition supply == _totalSupply
            function totalSupply() public view returns (uint256 supply);
        - Output format: return the annotated interface inside code fence (```) to show the code block. RETURN JUST THE CONTRACT ANNOTATED, NOTHING MORE.\n\n
        """
        verification_result.output = instructions + verification_result.output
        logging.info("trying again with solc-verify output: " + str(verification_result.output))
        return loop(thread, verification_result.output)
    else:
        print("Verified!")
        return solidity_code

def run_verification_process():
    results = []
    for i in range(10):
        global interaction_counter
        global verification_status
        
        interaction_counter = 0 
        start_time = time.time()
        assistant = Assistant(assistant_id)
        thread = Thread(assistant)
        result = loop(thread, """
            
            """
        )
        end_time = time.time()
        duration = end_time - start_time
        annotated_contract = ""
        
        if result:
            annotated_contract = result

        results.append({
            "run": i + 1,
            "time_taken": duration,
            "iterations": interaction_counter - 1,
            "verified": result != False,
            "annotated_contract": annotated_contract,
            "status": verification_status
        })
        verification_status = []
    
    return results

verification_results = run_verification_process()
Utils.save_results_to_csv("erc20_[].csv", verification_results)
