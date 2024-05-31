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
                    # EIP 20
                    "file_id": "file-UJqP1JMzl0YRk1kVf8pjyUC9",
                    "tools": [{"type": "file_search"}]
                },
                {
                    # ERC 20 interface
                    "file_id": "file-y6f05hiBCqm6h8596aPJxc7e",
                    "tools": [{"type": "file_search"}]
                },
                {
                    # ERC 721 ref spec
                    "file_id": "file-g9etf6hVTpRxveujQkVvdysA",
                    "tools": [{"type": "file_search"}]
                },
                {
                    # EIP 721
                    "file_id": "file-qxLGK6Pnjq1oPzNYkQmk07r5",
                    "tools": [{"type": "file_search"}]
                },
                {
                    # ERC 721 interface
                    "file_id": "file-fM3pZzInzDIUcHCbn2kznwm7",
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
    - for ERC721 interface erc721_interface.md (file-fM3pZzInzDIUcHCbn2kznwm7) and EIP markdown erc-721.md (file-qxLGK6Pnjq1oPzNYkQmk07r5), the expected specification should be this one: erc721_ref_spec.md (file-g9etf6hVTpRxveujQkVvdysA)
    - for ERC20 interface erc20_interface.md (file-y6f05hiBCqm6h8596aPJxc7e) and EIP markdown erc-20.md (file-UJqP1JMzl0YRk1kVf8pjyUC9),  you should generate the specification.

    ### Guidance for Generating Postconditions:

    1. **State Changes**: Consider how the state variables change. For example, ownership transfer should reflect changes in token ownership and balances.
    2. **Invariants**: Ensure that invariants hold before and after the function execution, such as the total number of tokens.
    3. **Conditions on Input**: Reflect on how inputs affect the state variables. 
    4. **Reset Conditions**: Ensure that certain variables are reset after the function execution, if applicable.

    Can you please generate a specification given the following ERC interface (delimited by token <interface>) and EIP markdown (delimited by token <eip>)?
        
    ERC interface:

    <interface>
        pragma solidity >=0.5.0;

        contract ERC20 {

            mapping (address => uint) _balances;
            mapping (address => mapping (address => uint)) _allowed;
            uint public _totalSupply;

            event Transfer(address indexed _from, address indexed _to, uint _value);
            event Approval(address indexed _owner, address indexed _spender, uint _value);

            function totalSupply() public view returns (uint256 supply);
            
            function transfer(address to, uint value) public returns (bool success);

            function transferFrom(address from, address to, uint value) public returns (bool success);

            function approve(address spender, uint value) public returns (bool success);

            function balanceOf(address owner) public view returns (uint balance);

            function allowance(address owner, address spender) public view returns (uint remaining);
        }
    </interface>

    EIP markdown below:

    <eip>
        ## Simple Summary

        A standard interface for tokens.


        ## Abstract

        The following standard allows for the implementation of a standard API for tokens within smart contracts.
        This standard provides basic functionality to transfer tokens, as well as allow tokens to be approved so they can be spent by another on-chain third party.


        ## Motivation

        A standard interface allows any tokens on Ethereum to be re-used by other applications: from wallets to decentralized exchanges.


        ## Specification

        ## Token
        ### Methods

        **NOTES**:
        - The following specifications use syntax from Solidity `0.4.17` (or above)
        - Callers MUST handle `false` from `returns (bool success)`.  Callers MUST NOT assume that `false` is never returned!


        #### name

        Returns the name of the token - e.g. `"MyToken"`.

        OPTIONAL - This method can be used to improve usability,
        but interfaces and other contracts MUST NOT expect these values to be present.


        ``` js
        function name() public view returns (string)
        ```


        #### symbol

        Returns the symbol of the token. E.g. "HIX".

        OPTIONAL - This method can be used to improve usability,
        but interfaces and other contracts MUST NOT expect these values to be present.

        ``` js
        function symbol() public view returns (string)
        ```



        #### decimals

        Returns the number of decimals the token uses - e.g. `8`, means to divide the token amount by `100000000` to get its user representation.

        OPTIONAL - This method can be used to improve usability,
        but interfaces and other contracts MUST NOT expect these values to be present.

        ``` js
        function decimals() public view returns (uint8)
        ```


        #### totalSupply

        Returns the total token supply.

        ``` js
        function totalSupply() public view returns (uint256)
        ```



        #### balanceOf

        Returns the account balance of another account with address `_owner`.

        ``` js
        function balanceOf(address _owner) public view returns (uint256 balance)
        ```



        #### transfer

        Transfers `_value` amount of tokens to address `_to`, and MUST fire the `Transfer` event.
        The function SHOULD `throw` if the message caller's account balance does not have enough tokens to spend.

        *Note* Transfers of 0 values MUST be treated as normal transfers and fire the `Transfer` event.

        ``` js
        function transfer(address _to, uint256 _value) public returns (bool success)
        ```



        #### transferFrom

        Transfers `_value` amount of tokens from address `_from` to address `_to`, and MUST fire the `Transfer` event.

        The `transferFrom` method is used for a withdraw workflow, allowing contracts to transfer tokens on your behalf.
        This can be used for example to allow a contract to transfer tokens on your behalf and/or to charge fees in sub-currencies.
        The function SHOULD `throw` unless the `_from` account has deliberately authorized the sender of the message via some mechanism.

        *Note* Transfers of 0 values MUST be treated as normal transfers and fire the `Transfer` event.

        ``` js
        function transferFrom(address _from, address _to, uint256 _value) public returns (bool success)
        ```



        #### approve

        Allows `_spender` to withdraw from your account multiple times, up to the `_value` amount. If this function is called again it overwrites the current allowance with `_value`.

        **NOTE**: To prevent attack vectors like the one [described here](https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/) and discussed [here](https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729),
        clients SHOULD make sure to create user interfaces in such a way that they set the allowance first to `0` before setting it to another value for the same spender.
        THOUGH The contract itself shouldn't enforce it, to allow backwards compatibility with contracts deployed before

        ``` js
        function approve(address _spender, uint256 _value) public returns (bool success)
        ```


        #### allowance

        Returns the amount which `_spender` is still allowed to withdraw from `_owner`.

        ``` js
        function allowance(address _owner, address _spender) public view returns (uint256 remaining)
        ```



        ### Events


        #### Transfer

        MUST trigger when tokens are transferred, including zero value transfers.

        A token contract which creates new tokens SHOULD trigger a Transfer event with the `_from` address set to `0x0` when tokens are created.

        ``` js
        event Transfer(address indexed _from, address indexed _to, uint256 _value)
        ```



        #### Approval

        MUST trigger on any successful call to `approve(address _spender, uint256 _value)`.

        ``` js
        event Approval(address indexed _owner, address indexed _spender, uint256 _value)
        ```
    """
)
