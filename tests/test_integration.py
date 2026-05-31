import pytest
from prompt_architect.models import PromptTemplate
from prompt_architect.registry import TemplateRegistry
from prompt_architect.providers.mock import MockProvider

def test_template_execution_flow():
    """
    Integration test: Ensures the Registry can load a template and 
    the MockProvider can execute it correctly with context.
    """
    # 1. Setup Registry and Template
    registry = TemplateRegistry()
    template_data = {
        "name": "greeting_template",
        "template_string": "Hello, {{name}}! Welcome to {{place}}.",
        "variables": ["name", "place"],
        "version": "1.0.0",
        "description": "A simple greeting template."
    }
    template = PromptTemplate.model_validate(template_data)
    registry.register(template)

    # 2. Setup Provider
    provider = MockProvider()

    # 3. Define Execution Context
    context = {"name": "Zhi", "place": "Prompt Architect"}

    # 4. Execute the Template via the Provider
    # The MockProvider replaces {{var}} with the value from context
    result = provider.execute(template, context)

    # 5. Assert the result is exactly what we expect
    # Note: MockProvider replaces '{{name}}' with 'Zhi'
    assert result == "Hello, Zhi! Welcome to Prompt Architect."

def test_registry_retrieval():
    """
    Test that the registry correctly retrieves the latest version of a template.
    """
    registry = TemplateRegistry()
    
    t1 = PromptTemplate(name="test", template_string="v1", variables=[], version="1.0.0")
    t2 = PromptTemplate(name="test", template_string="v2", variables=[], version="2.0.0")
    
    registry.register(t1)
    registry.register(t2)

    # Should get the latest (2.0.0)
    latest = registry.get("test")
    assert latest.version == "2.0.0"
    assert latest.template_string == "v2"

    # Should be able to get specific version
    old = registry.get("test", version="1.0.0")
    assert old.version == "1.0.0"
