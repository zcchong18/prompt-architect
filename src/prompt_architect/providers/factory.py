from typing import Any, Dict, Optional

from prompt_architect.providers.anthropic import AnthropicProvider
from prompt_architect.providers.base import BaseLLMProvider
from prompt_architect.providers.config import Settings
from prompt_architect.providers.gemini import GeminiProvider
from prompt_architect.providers.llamacpp import LlamaCppProvider
from prompt_architect.providers.mock import MockProvider
from prompt_architect.providers.ollama import OllamaProvider
from prompt_architect.providers.openai import OpenAIProvider


class ProviderFactory:
    """
    A factory class to instantiate LLM providers based on a configuration string.
    """

    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings or Settings()
        self._provider_map = {
            "mock": MockProvider,
            "ollama": OllamaProvider,
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "gemini": GeminiProvider,
            "llamacpp": LlamaCppProvider,
        }

    def get_provider(
        self, name: str, config: Optional[Dict[str, Any]] = None
    ) -> BaseLLMProvider:
        """
        Returns an instance of the requested provider.

        Args:
            name: The identifier for the provider (e.g., 'mock').
            config: Optional override configuration dictionary.

        Returns:
            An instance of a subclass of BaseLLMProvider.

        Raises:
            ValueError: If the provider name is not recognized.
        """
        provider_class = self._provider_map.get(name.lower())

        if not provider_class:
            raise ValueError(
                f"Unknown provider: '{name}'. Supported providers: {list(self._provider_map.keys())}"
            )

        merged_config = {**self._settings.for_provider(name), **(config or {})}
        return provider_class(config=merged_config)

    def list_supported_providers(self) -> list[str]:
        """Returns a list of all supported provider names."""
        return list(self._provider_map.keys())
