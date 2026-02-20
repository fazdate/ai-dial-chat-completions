import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):
    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json",
        }
        request_data = {
            "messages": [msg.to_dict() for msg in messages],
        }
        response = requests.post(self._endpoint, headers=headers, json=request_data)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        content = response.json()["choices"][0]["message"]["content"]
        print(content)
        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json",
        }
        request_data = {
            "stream": True,
            "messages": [msg.to_dict() for msg in messages],
        }
        contents: list[str] = []
        async with aiohttp.ClientSession() as session:
            async with session.post(self._endpoint, json=request_data, headers=headers) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"HTTP {response.status}: {text}")
                async for raw in response.content:
                    for line in raw.decode("utf-8").splitlines():
                        if not line.startswith("data: "):
                            continue
                        payload = line[6:].strip()
                        if payload == "[DONE]":
                            print()
                            return Message(role=Role.AI, content="".join(contents))
                        data = json.loads(payload)
                        delta = data["choices"][0]["delta"]
                        content = delta.get("content")
                        if not content:
                            continue
                        print(content, end="")
                        contents.append(content)
        return Message(role=Role.AI, content="".join(contents))
