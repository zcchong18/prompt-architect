import os
import pytest
from prompt_architect.core.template import PromptTemplate
from prompt_architect.core.storage import PromptRepository
from prompt_architect.core.git_manager import GitManager

@pytest.fixture
def project_env(tmp_path):
    """
    Sets up a temporary project environment with Git initialized.
    """
    # Create a real directory structure for the test
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    
    prompts_dir = project_dir / ".prompts"
    prompts_dir.mkdir()
    
    # Initialize Git in the temp directory
    # Note: We use the actual repo path, so we must do this via terminal to ensure git init works correctly
    import subprocess
    subprocess.run(["git", "init"], cwd=str(project_dir), check=True, capture_output=True)
    
    repo = PromptRepository(str(prompts_dir))
    git_mgr = GitManager(str(project_dir), str(prompts_dir))
    
    return {
        "project_dir": str(project_dir),
        "prompts_dir": str(prompts_dir),
        "repo": repo,
        "git_mgr": git_mgr
    }

def test_git_workflow_cycle(project_env):
    """
    Verifies the full lifecycle: 
    Create -> Save -> Commit -> Modify -> Commit -> Checkout
    """
    repo = project_env["repo"]
    git_mgr = project_env["git_mgr"]
    
    prompt_name = "v1_prompt"
    template = PromptTemplate(
        name=prompt_name,
        template_string="Initial version: {text}",
        description="The original template"
    )

    # 1. Save and Commit Version 1
    repo.save(template)
    commit_v1 = git_mgr.commit_prompt(prompt_name, "Initial commit of prompt")
    
    # 2. Modify the template (Version 2)
    template_v2 = PromptTemplate(
        name=prompt_name,
        template_string="Updated version: {text} (and some extra flair!)",
        description="The updated template"
    )
    repo.save(template_v2)
    
    # 3. Commit Version 2
    commit_v2 = git_mgr.commit_prompt(prompt_name, "Updated prompt with flair")
    
    # Verify we are currently on V2 in the filesystem
    current_loaded = repo.load(prompt_name)
    assert "extra flair" in current_loaded.template_string
    
    # 4. Checkout Version 1
    git_mgr.checkout_prompt(prompt_name, commit_v1)
    
    # Verify we are back to V1
    reverted_loaded = repo.load(prompt_name)
    assert "Initial version" in reverted_loaded.template_string
    assert "extra flair" not in reverted_loaded.template_string

def test_get_history(project_env):
    """Tests that we can retrieve the commit history for a prompt."""
    repo = project_env["repo"]
    git_mgr = project_env["git_mgr"]
    prompt_name = "history_test"
    
    template = PromptTemplate(name=prompt_name, template_string="v1", description="d")
    repo.save(template)
    git_mgr.commit_prompt(prompt_name, "First commit")
    
    template_v2 = PromptTemplate(name=prompt_name, template_string="v2", description="d")
    repo.save(template_v2)
    git_mgr.commit_prompt(prompt_name, "Second commit")
    
    history = git_mgr.get_history(prompt_name)
    
    assert len(history) >= 2
    assert "Second commit" in history[0]["message"]
    assert "First commit" in history[1]["message"]
