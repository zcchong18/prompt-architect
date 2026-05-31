import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self._config.get("api_key", "")
        self.model = self._config.get("model", "gpt-4o")
        self.base_url = self._config.get("base_url", "https://api.openai.com/v1")

    def execute(self, template: PromptTemplate, context: Dict[str, Any]) -> str:
        prompt = template.render(**context)
        return self._generate(prompt)

    def _generate(self, prompt: str) -> str:
        url = f"{self.base_url}/chat/completions"
        body = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode()

        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"OpenAI API returned status {resp.status}")
                result = json.loads(resp.read())
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to connect to OpenAI API: {e.reason}") from e

        choices = result.get("choices", [])
        if not choices:
            raise RuntimeError(
                f"OpenAI returned empty choices for model '{self.model}'"
            )

        content = choices[0].get("message", {}).get("content", "")
        if not content:
            raise RuntimeError(
                f"OpenAI returned empty content for model '{self.model}'"
            )
        return content

    @property
    def provider_name(self) -> str:
        return "openai"
