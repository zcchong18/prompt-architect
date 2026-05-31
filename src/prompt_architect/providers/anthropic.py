import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self._config.get("api_key", "")
        self.model = self._config.get("model", "claude-sonnet-4-20250514")
        self.max_tokens = self._config.get("max_tokens", 1024)

    def execute(self, template: PromptTemplate, context: Dict[str, Any]) -> str:
        prompt = template.render(**context)
        return self._generate(prompt)

    def _generate(self, prompt: str) -> str:
        url = "https://api.anthropic.com/v1/messages"
        body = json.dumps(
            {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode()

        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Anthropic API returned status {resp.status}")
                result = json.loads(resp.read())
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to connect to Anthropic API: {e.reason}") from e

        content_blocks = result.get("content", [])
        if not content_blocks:
            raise RuntimeError(
                f"Anthropic returned empty content for model '{self.model}'"
            )

        text = content_blocks[0].get("text", "")
        if not text:
            raise RuntimeError(
                f"Anthropic returned empty text for model '{self.model}'"
            )
        return text

    @property
    def provider_name(self) -> str:
        return "anthropic"
