import os
import requests
import logging
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
    

class LLMCaller:

    logger = logging.getLogger(f"{__name__}")

    @staticmethod
    def call(prompt: str) -> str:
        llm_providers = {
            # "ollama": OllamaLocalAPIProvider(),
            "together": TogetherAIProvider()
        }
        for p, implementation in llm_providers.items():
            try:
                LLMCaller.logger.info(f"Calling `{p}` LLM")
                return { "content": implementation.call(prompt), "provider": p }
            except Exception as e:
                LLMCaller.logger.error(f"Error calling `{p}` LLM: {e}")
                continue