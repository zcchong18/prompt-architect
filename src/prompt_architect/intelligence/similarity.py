import numpy as np
from typing import List
from prompt_architect.embeddings.base import BaseEmbeddingProvider

class SimilarityEngine:
    """
    The mathematical core of the intelligence layer.
    Handles semantic similarity calculations using vector embeddings.
    """

    def __init__(self, provider: BaseEmbeddingProvider):
        """
        Initializes the engine with a specific embedding provider.

        Args:
            provider: An instance of a BaseEmbeddingProvider.
        """
        self.provider = provider

    def calculate_similarity(self, text_a: str, text_b: str) -> float:
        """
        Calculates the cosine similarity between two pieces of text.

        Args:
            text_a: The first text string.
            text_b: The second text string.

        Returns:
            float: The cosine similarity score, between 0.0 and 1.0.
        """
        vec_a = np.array(self.provider.embed_text(text_a))
        vec_b = np.array(self.provider.embed_text(text_b))

        # Compute cosine similarity: (A . B) / (||A|| * ||B||)
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))

    def is_regression(self, text_old: str, text_new: str, threshold: float = 0.9) -> bool:
        """
        Determates if the change in text represents a semantic regression.

        Args:
            text_old: The original text/template.
            text_new: The new version of the text/template.
            threshold: The minimum similarity required to avoid a regression flag.

        Returns:
            bool: True if the similarity is below the threshold, indicating a regression.
        """
        similarity = self.calculate_similarity(text_old, text_new)
        return similarity < threshold

