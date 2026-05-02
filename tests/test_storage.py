import os
import pytest
import shutil
from prompt_architect.core.template import PromptTemplate
from prompt_architect.core.storage import Storage

@pytest.fixture
def repo(tmp_path):
    """Provides a clean PromptRepository in a temporary directory for each test."""
    test_dir = tmp_path / "test_prompts"
    return Storage(str(test_dir))

def test_save_and_load_success(repo):
    """Test that a template can be saved and reloaded perfectly."""
    template = PromptTemplate(
        name="test_vault",
        template_string="Hello, {user}!",
        description="A test template"
    )
    repo.save(template)
    
    loaded = repo.load("test_vault")
    assert loaded.name == "test_vault"
    assert loaded.template_string == "Hello, {user}!"
    assert loaded.render(user="Zhi") == "Hello, Zhi!"

def test_load_nonexistent_raises_error(repo):
    """Test that loading a non-existent template raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        repo.load("ghost_template")

def test_list_all_functionality(repo):
    """Test that list_all correctly identifies all saved templates."""
    t1 = PromptTemplate(name="t1", template_string="t1", description="d1")
    t2 = PromptTemplate(name="t2", template_string="t2", description="d2")
    
    repo.save(t1)
    repo.save(t2)
    
    all_names = repo.list_all()
    assert "t1" in all_names
    assert "t2" in all_names
    assert len(all_names) == 2
