import asyncio

from task.clients.client import DialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    deployment_name = "gpt-4o"
    client = DialClient(deployment_name)

    conversation = Conversation()
    print("Provide System prompt or press 'enter' to continue.")
    system_prompt = input("> ").strip() or DEFAULT_SYSTEM_PROMPT
    conversation.add_message(Message(role=Role.SYSTEM, content=system_prompt))

    print("Type your question or 'exit' to quit.")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "exit":
            print("Exiting the chat. Goodbye!")
            break
        conversation.add_message(Message(role=Role.USER, content=user_input))
        print("AI: ", end="")
        if stream:
            assistant_message = await client.stream_completion(conversation.get_messages())
        else:
            assistant_message = client.get_completion(conversation.get_messages())
        conversation.add_message(assistant_message)
        print()


asyncio.run(
    start(True)
)
