import os
from git import Repo
from typing import List, Dict

class GitManager:
    """
    Manplements Git operations specifically for the prompts directory.
    """
    def __init__(self, project_root: str, prompts_dir: str):
        self.project_root = os.path.abspath(project_root)
        self.prompts_dir = os.path.abspath(prompts_dir)
        try:
            self.repo = Repo(self.project_root)
        except Exception as e:
            raise Exception(f"Failed to initialize Git repository at {self.project_root}: {e}")

    def _get_file_path(self, name: str) -> str:
        return os.path.join(self.prompts_dir, f"{name}.json")

    def commit_prompt(self, prompt_name: str, message: str) -> str:
        """Adds and commits a specific prompt file."""
        file_path = self._get_file_path(prompt_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist. Cannot commit.")

        # Stage the file
        self.repo.index.add([file_path])
        
        # Commit
        commit = self.repo.index.commit(message)
        return commit.hexsha

    def checkout_prompt(self, prompt_name: str, commit_hash: str) -> None:
        """Restores a specific version of a prompt file from a commit hash."""
        file_path = self._get_file_path(prompt_name)
        self.repo.git.checkout(commit_hash, "--", file_path)

    def get_history(self, prompt_name: str) -> List[Dict[str, str]]:
        """Returns a list of recent commits for a specific prompt file."""
        file_path = self._get_file_path(prompt_name)
        commits = []
        
        # Iterate through commits that touched this file
        for commit in self.repo.iter_commits(paths=file_path, max_count=10):
            commits.append({
                "hash": commit.hexsha,
                "message": commit.message.strip(),
                "date": commit.authored_datetime.isoformat()
            })
        return commits
