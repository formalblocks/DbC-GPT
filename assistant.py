import openai, time, logging
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI()

model='gpt-4-turbo'

'''
# Create an assistant
assistant = client.beta.assistants.create(
  name="Solc-verify specifications generator specialist",
  instructions="You help generate formal specifications for smart contracts on the Ethereum network, written in Solidity and which will be verified in the solc-verify verifier.",
  tools=[{"type": "file_search"}],
  model=model,
)

print(assistant.id)
'''

'''
# Create a thread
thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "What is ERC20?"
        }
    ]
)

print(thread.id)
'''

# Hardcoded assistant and thread IDs
assistant_id = 'asst_NVICrZqU05MSQrMrNc2oZCML'
thread_id = 'thread_oASLT9ploRgxq91RQIyd9RH6'

# Create a Message
message = '{"name": "uri", "visibility": "public", "mutability": "view", "inputs": [["", "uint256"]], "outputs": [["", "string"]]}'
message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=message
)

# Run the assistant
run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id,
    instructions="Given a function as input, return exactly the function annotation in the format accepted by the solc-verify smart contract verifier, just this, nothing more.",
)

def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    """

    Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                print(f"Assistant Response: {response}")
                break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)



wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)

#run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id)
#print(f"Steps---> {run_steps.data[0]}")