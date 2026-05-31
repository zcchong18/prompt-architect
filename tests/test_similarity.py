import pytest
from prompt_architect.embeddings.mock import MockEmbeddingProvider
from prompt_architect.intelligence.similarity import SimilarityEngine

@pytest.fixture
def engine():
    """Fixture to provide a SimilarityEngine using the MockProvider."""
    provider = MockEmbeddingProvider(vector_dim=384)
    return SimilarityEngine(provider)

def test_similarity_is_perfect_for_identical_strings(engine):
    """Identical strings should have a similarity of 1.0."""
    text = "This is a test prompt."
    similarity = engine.calculate_similarity(text, text)
    assert similarity == pytest.approx(1.0)

def test_similarity_is_low_for_different_strings_with_real_provider():
    """
    Test similarity with a provider that returns different vectors.
    Since our MockProvider always returns 1.0s, we need a custom provider 
    to test 'different' vectors.
    """
    class CustomProvider:
        def embed_text(self, text: str):
            if "A" in text:
                return [1.0, 0.0]
            else:
                return [0.0, 1.0]
    
    engine = SimilarityEngine(CustomProvider())
    similarity = engine.calculate_similarity("Text A", "Text B")
    assert similarity == 0.0

def test_is_regression_detection(engine):
    """Verifies that is_regression flags low similarity."""
    # Using our mock provider, all vectors are identical, so similarity is always 1.0.
    # To test regression, we need different vectors.
    
    class RegressionProvider:
        def embed_text(self, text: str):
            if "old" in text:
                return [1.0, 0.0]
            return [0.0, 1.0]
    
    engine = SimilarityEngine(RegressionProvider())
    
    # Similarity will be 0.0, which is < 0.9 threshold
    assert engine.is_regression("old text", "new text", threshold=0.9) is True
    # Similarity will be 1.0, which is >= 0.9 threshold
    assert engine.is_regression("old text", "old text", threshold=0.9) is False

def test_similarity_engine_handles_zero_vectors():
    """Verifies that the engine handles zero vectors without crashing."""
    class ZeroProvider:
        def embed_text(self, text: str):
            return [0.0, 0.0]
            
    engine = SimilarityEngine(ZeroProvider())
    similarity = engine.calculate_similarity("A", "B")
    assert similarity == 0.0
