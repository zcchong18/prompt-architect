import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.base import BaseLLMProvider


class LlamaCppProvider(BaseLLMProvider):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.base_url = self._config.get("base_url", "http://localhost:8080")
        self.model = self._config.get("model", "default")

    def execute(self, template: PromptTemplate, context: Dict[str, Any]) -> str:
        prompt = template.render(**context)
        return self._generate(prompt)

    def _generate(self, prompt: str) -> str:
        url = f"{self.base_url}/v1/chat/completions"
        body = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode()

        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"llama.cpp API returned status {resp.status}")
                result = json.loads(resp.read())
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Failed to connect to llama.cpp at {self.base_url}: {e.reason}"
            ) from e

        choices = result.get("choices", [])
        if not choices:
            raise RuntimeError(
                f"llama.cpp returned empty choices for model '{self.model}'"
            )

        content = choices[0].get("message", {}).get("content", "")
        if not content:
            raise RuntimeError(
                f"llama.cpp returned empty content for model '{self.model}'"
            )
        return content

    @property
    def provider_name(self) -> str:
        return "llamacpp"
