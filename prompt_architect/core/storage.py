import os
import json
from typing import List
from prompt_architect.core.template import PromptTemplate

class Storage:
    """
    Handles persistent storage of PromptTemplates using JSON files.
    """
    def __init__(self, storage_dir: str):
        self.storage_dir = os.path.abspath(storage_dir)
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def _get_file_path(self, name: str) -> str:
        return os.path.join(self.storage_dir, f"{name}.json")

    def save(self, template: PromptTemplate) -> None:
        """Saves a PromptTemplate to a JSON file named after the template's name."""
        file_path = self._get_file_path(template.name)
        data = template.model_dump()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def load(self, name: str) -> PromptTemplate:
        """Loads a PromptTemplate by name from its JSON file."""
        file_path = self._get_file_path(name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No template found with name: {name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return PromptTemplate(**data)

    def list_all(self) -> List[str]:
        """Returns a list of all template names available in the repository."""
        return [f.replace('.json', '') for f in os.listdir(self.storage_dir) if f.endswith('.json')]
