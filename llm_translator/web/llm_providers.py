import os
import requests

class AbstractLLMProvider:

    def __init__(self, config):
        self.config = config

    def call(self, prompt) -> str:
        raise NotImplementedError()


class TogetherAIProvider(AbstractLLMProvider):

    def __init__(self, url=None, headers=None, model=None):
        self.url = url or "https://api.together.xyz/v1/chat/completions"
        self.model = model or "meta-llama/Llama-3.3-70B-Instruct-Turbo"
        self.api_key = os.getenv("TOGETHER_API_KEY")
        self.headers = headers or {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def call(self, prompt) -> str:
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": prompt,
                }
            ],
        }
        response = requests.post(self.url, headers=self.headers, json=data)
        response.raise_for_status()
        json_response = response.json()
        return json_response["choices"][0]["message"]["content"]