import re
from pydantic import BaseModel, Field, model_validator, field_validator
from typing import List, Self

_IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
_PLACEHOLDER_RE = re.compile(r"\{\{(.*?)\}\}")


class PromptTemplate(BaseModel):
    """
    Represents a validated prompt template within the Prompt Architect system.
    """

    name: str = Field(
        ..., min_length=1, description="The unique identifier for the template."
    )
    template_string: str = Field(
        ...,
        min_length=1,
        description="The actual prompt string, containing placeholders like {{user}}.",
    )
    variables: List[str] = Field(
        default_factory=list,
        description="A list of allowed variable names (e.g., ['user', 'context']).",
    )
    version: str = Field(
        default="1.0.0", description="The semantic version of this template."
    )
    description: str | None = Field(
        default=None, description="A brief description of what the template does."
    )
    author: str | None = Field(default=None, description="The author of the template.")

    @field_validator("version")
    @classmethod
    def validate_semver(cls, v: str) -> str:
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError("must follow semver format")
        return v

    @model_validator(mode="after")
    def validate_variable_names(self) -> Self:
        for var in self.variables:
            if not _IDENTIFIER_RE.match(var):
                raise ValueError(f"Invalid variable name: '{var}'")
        return self

    @model_validator(mode="after")
    def validate_no_duplicate_variables(self) -> Self:
        seen = set()
        for var in self.variables:
            if var in seen:
                raise ValueError(f"Duplicate variable: '{var}'")
            seen.add(var)
        return self

    @model_validator(mode="after")
    def validate_variables(self) -> Self:
        placeholders = _PLACEHOLDER_RE.findall(self.template_string)

        for placeholder in placeholders:
            if placeholder not in self.variables:
                raise ValueError(f"Unauthorized variable found: '{placeholder}'")
        return self

    @model_validator(mode="after")
    def validate_balanced_braces(self) -> Self:
        depth = 0
        for ch in self.template_string:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            if depth < 0:
                raise ValueError("Unmatched closing brace '}' in template_string")
        if depth > 0:
            raise ValueError("Unmatched opening brace '{' in template_string")
        return self

    def render(self, **kwargs) -> str:
        try:
            return self.template_string.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"Missing required template variable: {e}")
        except ValueError as e:
            raise ValueError(f"Template formatting error: {e}")
