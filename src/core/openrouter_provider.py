import time
from typing import Dict, Any, Optional, Generator
from openai import OpenAI
from src.core.llm_provider import LLMProvider


class OpenRouterProvider(LLMProvider):
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        model_name: str = "qwen/qwen3-8b:free",
        api_key: Optional[str] = None,
        site_url: Optional[str] = None,
        site_name: Optional[str] = None,
    ):
        super().__init__(model_name, api_key)

        extra_headers: Dict[str, str] = {}
        if site_url:
            extra_headers["HTTP-Referer"] = site_url
        if site_name:
            extra_headers["X-Title"] = site_name

        self.client = OpenAI(
            base_url=self.OPENROUTER_BASE_URL,
            api_key=self.api_key,
            default_headers=extra_headers if extra_headers else None,
        )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        messages: Optional[list] = None,
    ) -> Dict[str, Any]:
        if messages is None:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

        start_time = time.time()
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )
        latency_ms = int((time.time() - start_time) * 1000)

        content = response.choices[0].message.content
        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return {
            "content": content,
            "usage": usage,
            "latency_ms": latency_ms,
            "provider": "openrouter",
            "model": self.model_name,
        }

    def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        messages: Optional[list] = None,
    ) -> Generator[str, None, None]:
        if messages is None:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

        stream_resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True,
        )
        for chunk in stream_resp:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
