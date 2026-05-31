from abc import ABC, abstractmethod
from typing import List

class BaseEmbeddingProvider(ABC):
    """
    Abstract Base Class for all Embedding providers.
    Ensures a unified interface for generating text embeddings.
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Generates a vector embedding for the provided text.

        Args:
            text: The input string to embed.

        Returns:
            List[float]: A list of floats representing the embedding vector.

        Raises:
            ValueError: If the embedding process fails due to invalid input.
            RuntimeError: If there is a connection or infrastructure failure.
        """
        pass
