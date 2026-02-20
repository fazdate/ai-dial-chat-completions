from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._client = Dial(base_url=DIAL_ENDPOINT, api_key=self._api_key)
        self._async_client = AsyncDial(base_url=DIAL_ENDPOINT, api_key=self._api_key)

    def get_completion(self, messages: list[Message]) -> Message:
        response = self._client.chat.completions.create(
            deployment_name=self._deployment_name,
            messages=[msg.to_dict() for msg in messages],
        )
        if not getattr(response, "choices", None):
            raise Exception("No choices in response found")
        content = response.choices[0].message.content
        print(content)
        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        chunks = await self._async_client.chat.completions.create(
            deployment_name=self._deployment_name,
            messages=[msg.to_dict() for msg in messages],
            stream=True,
        )
        contents: list[str] = []
        async for chunk in chunks:
            delta = chunk.choices[0].delta if chunk.choices else None
            content = getattr(delta, "content", None) if delta else None
            if not content:
                continue
            print(content, end="")
            contents.append(content)
        print()
        return Message(role=Role.AI, content="".join(contents))
