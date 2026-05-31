import pytest
from prompt_architect.embeddings.mock import MockEmbeddingProvider

def test_mock_embedding_dimensions():
    """Verifies that the MockEmbeddingProvider returns the correct vector dimension."""
    dim = 128
    provider = MockEmbeddingProvider(vector_dim=dim)
    embedding = provider.embed_text("Hello World")
    
    assert len(embedding) == dim
    assert all(v == 1.0 for v in embedding)

def test_mock_embedding_deterministic():
    """Verifies that the MockEmbeddingProvider returns the same vector for any input."""
    provider = MockEmbeddingProvider()
    embedding1 = provider.embed_text("Prompt A")
    embedding2 = provider.embed_text("Prompt B")
    
    assert embedding1 == embedding2
