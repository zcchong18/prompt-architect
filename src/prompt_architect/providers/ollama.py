import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """
    LLM provider that executes prompts via a local Ollama instance.
    Uses the Ollama /api/generate endpoint.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.base_url = self._config.get("base_url", "http://localhost:11434")
        self.model = self._config.get("model", "llama3")

    def execute(self, template: PromptTemplate, context: Dict[str, Any]) -> str:
        prompt = template.render(**context)
        return self._generate(prompt)

    def _generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        body = json.dumps(
            {"model": self.model, "prompt": prompt, "stream": False}
        ).encode()

        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Ollama API returned status {resp.status}")
                result = json.loads(resp.read())
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Failed to connect to Ollama at {self.base_url}: {e.reason}"
            ) from e

        response = result.get("response", "")
        if not response:
            raise RuntimeError(
                f"Ollama returned empty response for model '{self.model}'"
            )
        return response

    @property
    def provider_name(self) -> str:
        return "ollama"
