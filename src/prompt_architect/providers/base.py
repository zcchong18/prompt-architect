from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from prompt_architect.models import PromptTemplate


class BaseLLMProvider(ABC):
    """
    Abstract Base Class for all LLM providers.
    Ensures a unified interface for executing prompt templates across different backends.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = config or {}

    @abstractmethod
    def execute(self, template: PromptTemplate, context: Dict[str, Any]) -> str:
        """
        Execute the given PromptTemplate with the provided context.

        Args:
            template: The PromptTemplate object containing the template string.
            context: A dictionary of variables to inject into the template.

        Returns:
            str: The LLM-generated response.

        Raises:
            ValueError: If the execution fails due to provider-specific errors or invalid parameters.
            RuntimeError: If there is a connection or infrastructure failure.
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the unique identifier for this provider (e.g., 'openai', 'ollama')."""
        pass
