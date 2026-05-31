import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self._config.get("api_key", "")
        self.model = self._config.get("model", "gemini-2.0-flash")

    def execute(self, template: PromptTemplate, context: Dict[str, Any]) -> str:
        prompt = template.render(**context)
        return self._generate(prompt)

    def _generate(self, prompt: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()

        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Gemini API returned status {resp.status}")
                result = json.loads(resp.read())
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to connect to Gemini API: {e.reason}") from e

        candidates = result.get("candidates", [])
        if not candidates:
            raise RuntimeError(
                f"Gemini returned no candidates for model '{self.model}'"
            )

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise RuntimeError(f"Gemini returned empty parts for model '{self.model}'")

        text = parts[0].get("text", "")
        if not text:
            raise RuntimeError(f"Gemini returned empty text for model '{self.model}'")
        return text

    @property
    def provider_name(self) -> str:
        return "gemini"
