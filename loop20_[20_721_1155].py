import logging
import openai
import time
import sys
import re
import pandas as pd
from dataclasses import dataclass
from typing import List

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

openai.api_key = "sk-proj-klVFxlWU41a2lERXRag4T3BlbkFJ58oP09nvtT4sJHQhO0VB"
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
            Given an examaple of ERC interface, the ERC interface to be annotated and an EIP markdown, generate a specification for the ERC interface with solc-verify postconditions annotations, just postconditions, no other annotations types, this is very important!

            Instructions:

            - Function Bodies: The specification must not contain function implementations.
            - Postconditions Limit: Each function must have at most 4 postcondition (/// @notice postcondition) annotations above the function signature. Do not exceed this limit under any circumstances.
            - Position: add the solc-verify annotation above the related function, example:
                /// @notice postcondition supply == _totalSupply
                function totalSupply() public view returns (uint256 supply);
            - Output format: return the annotated interface inside code fence (```) to show the code block. RETURN JUST THE CONTRACT ANNOTATED, NOTHING MORE.

            Guidance for Generating Postconditions:

            - State Changes: Reflect how state variables change. For example, ownership transfer should reflect changes in token ownership and balances.
            - Conditions on Input: Consider how inputs affect the state variables.
            - Reset Conditions: Ensure certain variables are reset after the function execution, if applicable.

            ERC interface example:
            ```solidity
                pragma solidity >=0.5.0;
                
                contract ERC721 {
                    
                    /// @notice postcondition _ownedTokensCount[_owner] == balance
                    function balanceOf(address _owner) public view returns (uint256 balance);
                    
                    /// @notice postcondition _tokenOwner[_tokenId] == _owner
                    /// @notice postcondition  _owner !=  address(0)
                    function ownerOf(uint256 _tokenId) public view returns (address owner);

                    /// @notice postcondition _tokenApprovals[_tokenId] == _approved 
                    function approve(address _approved, uint256 _tokenId) external;
                    
                    /// @notice postcondition _tokenOwner[tokenId] != address(0)
                    /// @notice postcondition _tokenApprovals[tokenId] == approved
                    function getApproved(uint256 _tokenId) external view returns (address approved);

                    /// @notice postcondition _operatorApprovals[msg.sender][_operator] == _approved
                    function setApprovalForAll(address _operator, bool _approved) external;
                    
                    /// @notice postcondition _operatorApprovals[_owner][_operator] == approved
                    function isApprovedForAll(address _owner, address _operator) external view returns (bool);

                    /// @notice  postcondition ( ( _ownedTokensCount[_from] ==  __verifier_old_uint (_ownedTokensCount[_from] ) - 1  &&  _from  != _to ) || ( _from == _to )  ) 
                    /// @notice  postcondition ( ( _ownedTokensCount[_to] ==  __verifier_old_uint ( _owned_kensCount[to] ) + 1  &&  _from  != _to ) || ( _from  == _to ) )
                    /// @notice  postcondition  _tokenOwner[_tokenId] == _to
                    function transferFrom(address _from, address _to, uint256 _tokenId) external;
                    
                    /// @notice  postcondition ( ( _ownedTokensCount[_from] ==  __verifier_old_uint (_ownedTokensCount[_from] ) - 1  &&  _from  != _to ) || ( _from == _to )  ) 
                    /// @notice  postcondition ( ( _ownedTokensCount[_to] ==  __verifier_old_uint ( _ownedTokensCount[_to] ) + 1  &&  _from  != _to ) || ( _from  == _to ) )
                    /// @notice  postcondition  _tokenOwner[_tokenId] == to
                    function safeTransferFrom(address _from, address _to, uint256 _tokenId) external;

                    /// @notice  postcondition ( ( _ownedTokensCount[_from] ==  __verifier_old_uint (_ownedTokensCount[_from] ) - 1  &&  _from  != _to ) || ( _from == _to )  ) 
                    /// @notice  postcondition ( ( _ownedTokensCount[_to] ==  __verifier_old_uint ( _ownedTokensCount[_to] ) + 1  &&  _from  != _to ) || ( _from  == _to ) )
                    /// @notice  postcondition  _tokenOwner[_tokenId] == _to
                    function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes calldata _data) external;
                }
            ```
            
            ERC interface example:
            ```solidity
                contract ERC1155  {
                    /// @notice postcondition _balances[_id][_owner] == balance  
                    function balanceOf(address _owner, uint256 _id) public view   returns (uint256 balance);
                    
                    /// @notice postcondition batchBalances.length == _owners.length 
                    /// @notice postcondition batchBalances.length == _ids.length
                    /// @notice postcondition forall (uint x) !( 0 <= x &&  x < batchBalances.length ) || batchBalances[x] == _balances[_ids[x]][_owners[x]]
                    function balanceOfBatch(address[] memory _owners, uint256[] memory _ids) public view returns (uint256[] memory batchBalances);

                    /// @notice  postcondition _operatorApprovals[msg.sender][_operator] ==  _approved 
                    function setApprovalForAll(address _operator, bool _approved) public;

                    /// @notice postcondition _operatorApprovals[_owner][_operator] == approved
                    function isApprovedForAll(address _owner, address _operator) public view returns (bool approved);

                    /// @notice postcondition _to != address(0) 
                    /// @notice postcondition _operatorApprovals[_from][msg.sender] || _from == msg.sender
                    /// @notice postcondition __verifier_old_uint ( _balances[_id][_from] ) >= _value    
                    /// @notice postcondition _balances[_id][_from] == __verifier_old_uint ( _balances[_id][_from] ) - _value
                    /// @notice postcondition _balances[_id][_to] == __verifier_old_uint ( _balances[_id][_to] ) + _value
                    function safeTransferFrom(address _from, address _to, uint256 _id, uint256 _value, bytes memory _data) public;

                    /// @notice postcondition _operatorApprovals[_from][msg.sender] || _from == msg.sender
                    /// @notice postcondition _to != address(0)
                    function safeBatchTransferFrom(address _from, address _to, uint256[] memory _ids, uint256[] memory _values, bytes memory _data) public;
                }
            ```
                    
            ERC interface example:
            ```solidity
                pragma solidity >=0.5.0;
                
                contract ERC20 {

                    mapping (address => uint) _balances;
                    mapping (address => mapping (address => uint)) _allowed;
                    uint public _totalSupply;

                    event Transfer(address indexed _from, address indexed _to, uint _value);
                    event Approval(address indexed _owner, address indexed _spender, uint _value);

                    /// @notice postcondition supply == _totalSupply
                    function totalSupply() public view returns (uint256 supply);

                    /// @notice  postcondition ( ( _balances[msg.sender] ==  __verifier_old_uint (_balances[msg.sender] ) - _value  && msg.sender  != _to ) ||   ( _balances[msg.sender] ==  __verifier_old_uint ( _balances[msg.sender]) && msg.sender  == _to ) &&  success )   || !success
                    /// @notice  postcondition ( ( _balances[_to] ==  __verifier_old_uint ( _balances[_to] ) + _value  && msg.sender  != _to ) ||   ( _balances[_to] ==  __verifier_old_uint ( _balances[_to] ) && msg.sender  == _to )  )   || !success
                    function transfer(address _to, uint256 _value) public returns (bool success);

                    /// @notice  postcondition ( ( _balances[_from] ==  __verifier_old_uint (_balances[_from] ) - _value  &&  _from  != _to ) || ( _balances[_from] ==  __verifier_old_uint ( _balances[_from] ) &&  _from == _to ) && success ) || !success 
                    /// @notice  postcondition ( ( _balances[_to] ==  __verifier_old_uint ( _balances[_to] ) + _value  &&  _from  != _to ) || ( _balances[_to] ==  __verifier_old_uint ( _balances[_to] ) &&  _from  == _to ) && success ) || !success 
                    /// @notice  postcondition ( _allowed[_from ][msg.sender] ==  __verifier_old_uint (_allowed[_from ][msg.sender] ) - _value && success) || ( _allowed[_from ][msg.sender] ==  __verifier_old_uint (_allowed[_from ][msg.sender]) && !success) ||  _from  == msg.sender
                    /// @notice  postcondition  _allowed[_from ][msg.sender]  <= __verifier_old_uint (_allowed[_from ][msg.sender] ) ||  _from  == msg.sender
                    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success);

                    /// @notice  postcondition (_allowed[msg.sender ][ _spender] ==  _value  &&  success) || ( _allowed[msg.sender ][ _spender] ==  __verifier_old_uint ( _allowed[msg.sender ][ _spender] ) && !success )    
                    function approve(address _spender, uint256 _value) public returns (bool success);

                    /// @notice postcondition _balances[_owner] == balance
                    function balanceOf(address _owner) public view returns (uint256 balance);

                    /// @notice postcondition _allowed[_owner][_spender] == remaining
                    function allowance(address _owner, address _spender) public view returns (uint256 remaining);
                }
            ```
            
            Can you please generate a specification given the following ERC interface (delimited by token ```solidity ```) and EIP markdown (delimited by token <eip>)?
                      
            HERE FOLLOWS THE CONTRACT TO ADD SOLC-VERIFY ANNOTATIONS, LIKE THE EXAMPLES ABOVE:

            ```solidity
                pragma solidity >=0.5.0;

                contract ERC20 {

                    mapping (address => uint) _balances;
                    mapping (address => mapping (address => uint)) _allowed;
                    uint public _totalSupply;

                    /**
                    * Returns the total token supply.
                    */
                    $ADD POSTCONDITION HERE
                    function totalSupply() public view returns (uint256 supply);
                    
                    /**
                    * Transfers `_value` amount of tokens to address `_to`, and MUST fire the `Transfer` event.
                    * The function SHOULD `throw` if the message caller's account balance does not have enough tokens to spend.

                    * *Note* Transfers of 0 values MUST be treated as normal transfers and fire the `Transfer` event.
                    */
                    $ADD POSTCONDITION HERE
                    function transfer(address _to, uint256 _value) public returns (bool success);

                    /**
                    * Transfers `_value` amount of tokens from address `_from` to address `_to`, and MUST fire the `Transfer` event.
                    * The `transferFrom` method is used for a withdraw workflow, allowing contracts to transfer tokens on your behalf.
                    * This can be used for example to allow a contract to transfer tokens on your behalf and/or to charge fees in sub-currencies.
                    * The function SHOULD `throw` unless the `_from` account has deliberately authorized the sender of the message via some mechanism.
                    * *Note* Transfers of 0 values MUST be treated as normal transfers and fire the `Transfer` event.
                    */
                    $ADD POSTCONDITION HERE
                    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success);

                    /**
                    * Allows `_spender` to withdraw from your account multiple times, up to the `_value` amount. If this function is called again it overwrites the current allowance with `_value`.
                    */
                    $ADD POSTCONDITION HERE
                    function approve(address _spender, uint256 _value) public returns (bool success);

                    /**
                    * Returns the account balance of another account with address `_owner`.
                    */
                    $ADD POSTCONDITION HERE
                    function balanceOf(address _owner) public view returns (uint256 balance);

                    /**
                    * Returns the amount which `_spender` is still allowed to withdraw from `_owner`.
                    */
                    $ADD POSTCONDITION HERE
                    function allowance(address _owner, address _spender) public view returns (uint256 remaining);
                }
            ```
            
            EIP ERC20 markdown below:

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
            </eip>
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
Utils.save_results_to_csv("erc20_[20_721_1155].csv", verification_results)
