import logging
import openai
import time
import sys
import re
from dataclasses import dataclass


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

openai.api_key = "sk-proj-klVFxlWU41a2lERXRag4T3BlbkFJ58oP09nvtT4sJHQhO0VB"
assistant_id = "asst_b4escj1bEDE6vlyqJundnEn0"

# Initialize the global counter
interaction_counter = 0

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
            content = self.prompt,
            attachments = [
                {
                    # ERC 20 interface
                    "file_id": "file-y6f05hiBCqm6h8596aPJxc7e",
                    "tools": [{"type": "file_search"}]
                },
                {
                    # ERC 20 ref spec
                    "file_id": "file-8KXyHtZx5wdBLwLUFerN8xdP",
                    "tools": [{"type": "file_search"}]
                },
                {
                    # EIP 1155
                    "file_id": "file-nzCmYOTTTv0dX5JISGtHJiGF",
                    "tools": [{"type": "file_search"}]
                },
                {
                    # ERC 1155 interface
                    "file_id": "file-qAHkhdXcxNUTlgszVabGfIDW",
                    "tools": [{"type": "file_search"}]
                }               
            ]
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
    ERC20_TEMPLATE_PATH = './solc_verify_generator/ERC1155/templates/imp_spec_merge.template'
    #ERC20_TEMPLATE_PATH = './solc_verify_generator/ERC20/templates/spec_refinement.template'
    ERC20_MERGE_PATH = './solc_verify_generator/ERC1155/imp/ERC1155_merge.sol'

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
        
        # Return first match
        return matches[0]

    @staticmethod
    def save_string_to_file(file_name, content):
        try:
            with open(file_name, 'w') as file:
                file.write(content)
            print(f"Content successfully saved to {file_name}")
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")



def loop(thread: Thread, message: str):
    global interaction_counter
    interaction_counter += 1
    # Break the loop if the counter is greater than 10
    if interaction_counter > 10:
        print("Counter exceeded 10, breaking the loop")
        return
    print('COUNTER', interaction_counter)
    interaction: Interaction = thread.send_message(message)
    response: str = interaction.await_for_response()
    solidity_code = Utils.extract_solidity_code(response)

    verification_result: VerificationResult = SolcVerifyWrapper.verify(solidity_code)

    if verification_result.status:
        logging.info("trying again with solc-verify output: " + str(verification_result.output))
        loop(thread, verification_result.output)
    else:
        print("Verified!")


assistant = Assistant(assistant_id)
thread = Thread(assistant)
loop(thread, """
    Given an ERC interface and an EIP markdown, I would like you to generate a specification for the ERC interface with solc-verify postconditions annotations, just postconditions, no other annotations types, this is very important!

    The specification must not contain function bodies (i.e. implementations). Please each function must have at most 4 postcondition (/// @notice postcondition) annotations, do not exceed this amount under any circumstances!

    For instance: 
    - for ERC20 interface erc20_interface.md (file-y6f05hiBCqm6h8596aPJxc7e), the expected specification should be this one: erc20_ref_spec.md (file-8KXyHtZx5wdBLwLUFerN8xdP)
    - for ERC1155 interface erc1155_interface.md (file-qAHkhdXcxNUTlgszVabGfIDW) and EIP markdown erc-1155.md (file-nzCmYOTTTv0dX5JISGtHJiGF), please generate the specification.

    *Note:* For the transfer function, when `msg.sender` is the same as `_to` the balance must not change

    Can you please generate a specification given the following ERC interface (delimited by token <interface>)?

    Remember to follow the same syntax of: erc20_ref_spec.md (file-8KXyHtZx5wdBLwLUFerN8xdP)
        
    ERC interface:

    <interface>
        // SPDX-License-Identifier: MIT

        pragma solidity >= 0.5.0;

        contract IERC1155  {

            function balanceOf(address account, uint256 id) public view   returns (uint256 balance);
            
            function balanceOfBatch(address[] memory accounts, uint256[] memory ids) public view returns (uint256[] memory batchBalances);

            function setApprovalForAll(address operator, bool approved) public;

            function isApprovedForAll(address account, address operator) public view returns (bool approved);

            function safeTransferFrom(address from, address to, uint256 id, uint256 amount, bytes memory data) public;

            function safeBatchTransferFrom(address from, address to, uint256[] memory ids, uint256[] memory amounts, bytes memory data) public;
        }
    </interface>
    """
)
