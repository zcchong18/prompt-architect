from typing import List
from collections import Counter
from prompt_architect.embeddings.base import BaseEmbeddingProvider


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """
    A simple, deterministic provider for testing purposes.
    It returns a vector based on character frequencies in the text.
    """

    def __init__(self, vector_dim: int = 384):
        self.vector_dim = vector_dim

    def embed_text(self, text: str) -> List[float]:
        """Generates a deterministic all-1.0 vector of fixed dimension."""
        return [1.0] * self.vector_dim

    @property
    def provider_name(self) -> str:
        return "mock"
