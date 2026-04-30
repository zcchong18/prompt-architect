from pydantic import BaseModel, Field
from typing import Any, Dict
import string

class PromptTemplate(BaseModel):
    """
    Represents a versionable LLM prompt template.
    Uses Python string formatting syntax (e.g., {user_name}).
    """
    name: str = Field(..., description="Unique identifier for the prompt template.")
    template_string: str = Field(..., description="The raw template string containing placeholders.")
    description: str = Field("", description="A brief description of what this prompt does.")

    def render(self, **kwargs) -> str:
        """
        Injects variables into the template string.
        
        Args:
            **kwargs: The variables to inject into the template.
            
        Returns:
            str: The rendered prompt string.
            
        Raises:
            KeyError: If a required variable is missing from kwargs.
        """
        try:
            return self.template_string.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"Missing required template variable: {e}")
        except ValueError as e:
            raise ValueError(f"Template formatting error: {e}")

if __name__ == "__main__":
    # Quick integrity check
    test_prompt = PromptTemplate(
        name="greeting",
        template_string="Hello, {name}! Welcome to {place}.",
        description="A simple greeting template."
    )
    print(f"Test Render: {test_prompt.render(name='Zhi', place='Prompt Architect')}")
