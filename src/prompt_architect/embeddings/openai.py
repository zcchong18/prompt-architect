import json
import urllib.error
import urllib.request
from typing import List, Optional

from prompt_architect.embeddings.base import BaseEmbeddingProvider


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-3-small",
        vector_dim: int = 1536,
    ):
        self.api_key = api_key or ""
        self.model = model
        self.vector_dim = vector_dim

    def embed_text(self, text: str) -> List[float]:
        url = "https://api.openai.com/v1/embeddings"
        body = json.dumps({"input": text, "model": self.model}).encode()

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
                    raise RuntimeError(
                        f"OpenAI Embedding API returned status {resp.status}"
                    )
                result = json.loads(resp.read())
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Failed to connect to OpenAI Embedding API: {e.reason}"
            ) from e

        data_entries = result.get("data", [])
        if not data_entries:
            raise RuntimeError(
                f"OpenAI Embedding API returned no data for model '{self.model}'"
            )

        embedding = data_entries[0].get("embedding", [])
        if not embedding:
            raise RuntimeError(
                f"OpenAI Embedding API returned empty embedding for model '{self.model}'"
            )
        return embedding

    @property
    def provider_name(self) -> str:
        return "openai"
