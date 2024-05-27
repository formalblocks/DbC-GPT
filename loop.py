import openai
import time
import re

openai.api_key = "sk-proj-klVFxlWU41a2lERXRag4T3BlbkFJ58oP09nvtT4sJHQhO0VB"
assistant_id = "asst_oD5x8GieyWtIjNZPtkcXKFG4"

def save_string_to_file(file_name, content):
    try:
        with open(file_name, 'w') as file:
            file.write(content)
        print(f"Content successfully saved to {file_name}")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
        
def extract_solidity_code(markdown_text):
    # Regex pattern to match code blocks with "solidity" as the language identifier
    pattern = r'```solidity\n(.*?)```'
    
    # Use re.DOTALL to match newline characters in the code block
    matches = re.findall(pattern, markdown_text, re.DOTALL)
    
    # Return first match
    return matches[0]

def create_thread():
    #create a thread
    thread = openai.beta.threads.create()
    return thread.id

def send_message(assistant_id, thread_id, prompt):
    #create a message
    message = openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )
    #run
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    ) 
    return run.id, thread_id

def check_status(run_id, thread_id):
    run = openai.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id,
    )
    return run.status

def await_for_response(run_id, thread_id) -> str:
    status = check_status(run_id, thread_id)
    while (status != "completed"):
        status = check_status(run_id, thread_id)
        print("awaiting for a response")
        time.sleep(2)
    response = openai.beta.threads.messages.list(
        thread_id=thread_id
    )

    # Returns last response from thread
    return response.data[0].content[0].text.value

SOLC_VERIFY_CMD = "solc-verify.py"
def call_solc(file_path):
    from subprocess import PIPE, run
    command = [SOLC_VERIFY_CMD, file_path]
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return result.returncode, result.stdout, result.stderr

def loop(assistant_id, thread_id, message):
    my_run_id, my_thread_id = send_message(assistant_id, thread_id, message)
    
    response_str = await_for_response(my_run_id, my_thread_id)
    solidity_code = extract_solidity_code(response_str)

    from solc_verify_generator.main import generate_merge
    spec_file_path = './temp/spec.sol'
    # erc20_template_path = './solc_verify_generator/ERC20/templates/imp_spec_merge.template'
    erc20_template_path = './solc_verify_generator/ERC20/templates/spec_refinement.template'
    erc20_merge_path = './solc_verify_generator/ERC20/imp/ERC20_merge.sol'
    save_string_to_file(spec_file_path, solidity_code)
    generate_merge(spec_file_path, erc20_template_path, erc20_merge_path)
    status, stdout, stderr = call_solc(erc20_merge_path)

    if status:
        print("trying again with solc-verify output: ", stdout, stderr)
        loop(assistant_id, thread_id, stdout+stderr)
    else:
        print("verified!")


thread_id = create_thread()
loop(assistant_id,  thread_id, """
    pragma solidity >=0.5.0;

    contract ERC20 {

        mapping (address => uint) _balances;
        mapping (address => mapping (address => uint)) _allowed;
        uint public _totalSupply;

        event Transfer(address indexed from, address indexed to, uint value);
        event Approval(address indexed owner, address indexed spender, uint value);


        
        function transfer(address to, uint value) public returns (bool success);

        
        function transferFrom(address from, address to, uint value) public returns (bool success);

        function approve(address spender, uint value) public returns (bool success);

        function balanceOf(address owner) public view returns (uint balance);

        function allowance(address owner, address spender) public view returns (uint remaining);
    }
    """)









