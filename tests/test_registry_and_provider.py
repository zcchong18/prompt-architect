import pytest
from pathlib import Path
import yaml
from prompt_architect.models import PromptTemplate
from prompt_architect.registry import TemplateRegistry
from prompt_architect.providers.mock import MockProvider

@pytest.fixture
def temp_template_dir(tmp_path):
    """Fixture to create a directory with a valid YAML template."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    
    template_content = {
        "name": "test_greeting",
        "template_string": "Hello, {{user}}! Welcome to {{location}}.",
        "variables": ["user", "location"],
        "version": "1.0.0",
        "description": "A simple greeting template.",
        "author": "Tester"
    }
    
    template_file = template_dir / "greeting.yaml"
    with open(template_file, "w", encoding="utf-8") as f:
        yaml.dump(template_content, f)
    
    return template_dir

def test_registry_loading(temp_template_dir):
    """Verifies that the registry can load templates from a directory."""
    registry = TemplateRegistry()
    loaded_count = registry.load_from_directory(str(temp_template_dir))
    
    assert loaded_count == 1
    
    template = registry.get("test_greeting")
    assert template.name == "test_greeting"
    assert template.version == "1.0.0"
    assert "user" in template.variables

def test_registry_versioning():
    """Verifies that the registry handles multiple versions of the same template."""
    registry = TemplateRegistry()
    
    v1 = PromptTemplate(
        name="multi_version",
        template_string="V1 content",
        variables=[],
        version="1.0.0"
    )

    v2 = PromptTemplate(
        name="multi_version",
        template_string="V2 content",
        variables=[],
        version="2.0.0"
    )
    
    registry.register(v1)
    registry.register(v2)
    
    # Test retrieval of specific version
    assert registry.get("multi_version", version="1.0.0").version == "1.0.0"
    # Test retrieval of latest version
    assert registry.get("multi_version").version == "2.0.0"

def test_end_to_end_mock_execution(temp_template_dir):
    """Verifies a full round-trip: Load -> Registry -> Provider -> Render."""
    # 1. Setup Registry and Load Template
    registry = TemplateRegistry()
    registry.load_from_directory(str(temp_template_dir))
    template = registry.get("test_greeting")
    
    # 2. Setup Provider
    provider = MockProvider()
    
    # 3. Execute with Context
    context = {"user": "Zhi", "location": "Berlin"}
    result = provider.execute(template, context)
    
    # 4. Verify Result
    # Note: MockProvider uses {{var}} replacement logic internally as per its implementation
    assert result == "Hello, Zhi! Welcome to Berlin."

def test_registry_error_on_missing_template():
    """Verifies that requesting a non-existent template raises a KeyError."""
    registry = TemplateRegistry()
    with pytest.raises(KeyError):
        registry.get("non_existent")
