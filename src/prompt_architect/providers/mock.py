from typing import Any, Dict, Optional

from prompt_architect.models import PromptTemplate
from prompt_architect.providers.base import BaseLLMProvider


class MockProvider(BaseLLMProvider):
    """
    A simple, deterministic provider for testing purposes.
    It does not call any external APIs; it simply returns the
    template string with variables replaced by their values.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    def execute(self, template: PromptTemplate, context: Dict[str, Any]) -> str:
        result = template.template_string
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result

    @property
    def provider_name(self) -> str:
        return "mock"
