import pytest
from prompt_architect.providers.factory import ProviderFactory
from prompt_architect.providers.mock import MockProvider
from prompt_architect.providers.base import BaseLLMProvider


def test_factory_returns_mock_provider():
    """Verifies that the factory correctly returns the MockProvider."""
    factory = ProviderFactory()
    provider = factory.get_provider("mock")

    assert isinstance(provider, MockProvider)
    assert provider.provider_name == "mock"


def test_factory_returns_correct_type():
    """Verifies that all returned providers adhere to the BaseLLMProvider interface."""
    factory = ProviderFactory()
    provider = factory.get_provider("mock")

    assert isinstance(provider, BaseLLMProvider)


def test_factory_invalid_provider_raises_error():
    """Verifies that requesting an unknown provider raises a ValueError."""
    factory = ProviderFactory()
    with pytest.raises(ValueError, match="Unknown provider: 'unknown_llm'"):
        factory.get_provider("unknown_llm")


def test_factory_list_providers():
    """Verifies that the factory correctly lists supported providers."""
    factory = ProviderFactory()
    providers = factory.list_supported_providers()

    assert "mock" in providers
    assert "ollama" in providers
    assert "openai" in providers
    assert "anthropic" in providers
    assert "gemini" in providers
    assert "llamacpp" in providers
    assert isinstance(providers, list)
