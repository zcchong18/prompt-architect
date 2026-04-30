import pytest
from prompt_architect.core.template import PromptTemplate

def test_prompt_template_render_success():
    """Test that a valid template renders correctly."""
    template = PromptTemplate(
        name="test_success",
        template_string="Hello, {name}! You are in {place}.",
        description="Test success case"
    )
    rendered = template.render(name="Zhi", place="Prompt Architect")
    assert rendered == "Hello, Zhi! You are in Prompt Architect."

def test_prompt_template_render_missing_variable():
    """Test that missing a required variable raises a KeyError."""
    template = PromptTemplate(
        name="test_missing_key",
        template_string="Hello, {name}!",
        description="Test missing variable case"
    )
    with pytest.raises(KeyError) as excinfo:
        template.render()  # Missing 'name'
    assert "Missing required template variable: 'name'" in str(excinfo.value)

def test_prompt_template_render_malformed_template():
    """Test that malformed template syntax raises a ValueError."""
    # A single brace without a closing one causes a ValueError in .format()
    template = PromptTemplate(
        name="test_malformed",
        template_string="Hello, {name!s",
        description="Test malformed syntax case"
    )
    with pytest.raises(ValueError) as excinfo:
        template.render(name="Zhi")
    assert "Template formatting error" in str(excinfo.value)
