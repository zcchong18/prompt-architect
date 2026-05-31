import pytest
from prompt_architect.models import PromptTemplate
from pydantic import ValidationError


def test_prompt_template_valid_instantiation():
    """Test that a valid PromptTemplate can be created."""
    template = PromptTemplate(
        name="test_template",
        template_string="Hello {{user}}!",
        variables=["user"],
        version="1.0.0",
    )
    assert template.name == "test_template"
    assert template.template_string == "Hello {{user}}!"
    assert template.version == "1.0.0"
    assert "user" in template.variables


def test_prompt_template_missing_name():
    """Test that missing name raises ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        PromptTemplate(template_string="Hello!")
    assert "Field required" in str(excinfo.value)


def test_prompt_template_empty_name():
    """Test that an empty name raises ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        PromptTemplate(name="", template_string="Hello!")
    assert "String should have at least 1 character" in str(excinfo.value)


def test_prompt_template_default_version():
    """Test that the default version is correctly applied."""
    template = PromptTemplate(name="test", template_string="Hello!")
    assert template.version == "1.0.0"


def test_prompt_template_invalid_version():
    """Test that an invalid semver version raises ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        PromptTemplate(
            name="test_invalid_ver",
            template_string="Hello {{user}}!",
            variables=["user"],
            version="1.0",
        )
    assert "must follow semver format" in str(excinfo.value).lower()


def test_metadata_fields():
    """Test that description and author fields can be set."""
    template = PromptTemplate(
        name="Test Template",
        template_string="Hello {{user}}!",
        version="1.0.0",
        variables=["user"],
        description="A test description",
        author="Zhi",
    )
    assert template.description == "A test description"
    assert template.author == "Zhi"


def test_metadata_fields_optional():
    """Test that description and author are optional."""
    template = PromptTemplate(
        name="Minimal Template", template_string="Hello!", version="1.0.0"
    )
    assert template.description is None
    assert template.author is None


def test_empty_template_string():
    """Test that empty template_string raises ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        PromptTemplate(name="empty", template_string="")
    assert "String should have at least 1 character" in str(excinfo.value)


def test_invalid_variable_name():
    """Test that invalid variable names are rejected."""
    with pytest.raises(ValidationError) as excinfo:
        PromptTemplate(
            name="test",
            template_string="Hello {{123invalid}}!",
            variables=["123invalid"],
        )
    assert "Invalid variable name" in str(excinfo.value)


def test_variable_name_with_special_chars():
    """Test that variable names with special chars are rejected."""
    with pytest.raises(ValidationError) as excinfo:
        PromptTemplate(
            name="test", template_string="Hello {{foo-bar}}!", variables=["foo-bar"]
        )
    assert "Invalid variable name" in str(excinfo.value)


def test_duplicate_variables():
    """Test that duplicate variable names are rejected."""
    with pytest.raises(ValidationError) as excinfo:
        PromptTemplate(
            name="test", template_string="Hello {{user}}!", variables=["user", "user"]
        )
    assert "Duplicate variable" in str(excinfo.value)


def test_unauthorized_placeholder():
    """Test that {{var}} not in variables list raises ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        PromptTemplate(name="test", template_string="Hello {{user}}!", variables=[])
    assert "Unauthorized variable found" in str(excinfo.value)


def test_unmatched_opening_brace():
    """Test that template with unmatched { is rejected."""
    with pytest.raises(ValidationError) as excinfo:
        PromptTemplate(name="test", template_string="Hello {name")
    assert "Unmatched opening brace" in str(excinfo.value)


def test_unmatched_closing_brace():
    """Test that template with unmatched } is rejected."""
    with pytest.raises(ValidationError) as excinfo:
        PromptTemplate(name="test", template_string="Hello name}")
    assert "Unmatched closing brace" in str(excinfo.value)


def test_double_braces_are_allowed():
    """Test that {{escaped}} double braces pass balanced brace check."""
    template = PromptTemplate(
        name="test", template_string="Hello {{user}}!", variables=["user"]
    )
    assert template.template_string == "Hello {{user}}!"


def test_mixed_brace_syntaxes():
    """Test that templates can mix {var} and {{var}} syntax."""
    template = PromptTemplate(
        name="test", template_string="{greeting} {{name}}!", variables=["name"]
    )
    assert template.template_string == "{greeting} {{name}}!"
