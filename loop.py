import logging
import openai
import time
import sys
import re
from dataclasses import dataclass


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

openai.api_key = "sk-proj-klVFxlWU41a2lERXRag4T3BlbkFJ58oP09nvtT4sJHQhO0VB"
assistant_id = "asst_b4escj1bEDE6vlyqJundnEn0"

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
                    "file_id": "file-UJqP1JMzl0YRk1kVf8pjyUC9",
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
    Given an ERC20 specification template and the ERC20 EIP attached on file search, return the exact same specification template with solc-verify postconditions annotations added.
     
    ERC20 function with solc-verify annotation example:
    /// @notice postcondition _allowed[_owner][_spender] == remaining
    function allowance(address _owner, address _spender) public view returns (uint256 remaining);
     
    Here follows the ERC20 specification file, return the exactly same specification file with solc-verify postconditions annotations added:

    pragma solidity >=0.5.0;

    contract ERC20 {

        mapping (address => uint) _balances;
        mapping (address => mapping (address => uint)) _allowed;
        uint public _totalSupply;

        event Transfer(address indexed _from, address indexed _to, uint _value);
        event Approval(address indexed _owner, address indexed _spender, uint _value);
     
        function transfer(address to, uint value) public returns (bool success);

        function transferFrom(address from, address to, uint value) public returns (bool success);

        function approve(address spender, uint value) public returns (bool success);

        function balanceOf(address owner) public view returns (uint balance);

        function allowance(address owner, address spender) public view returns (uint remaining);
    }
    """
)
