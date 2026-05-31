import os
import json
import yaml
from typing import Dict, List, Optional
from pathlib import Path
from prompt_architect.models import PromptTemplate


class TemplateRegistry:
    """
    A centralized registry for managing and retrieving PromptTemplates.
    Handles in-memory caching and loading templates from the filesystem.
    """

    def __init__(self):
        # Store templates as: { name: { version: PromptTemplate } }
        self._templates: Dict[str, Dict[str, PromptTemplate]] = {}

    def register(self, template: PromptTemplate) -> None:
        """
        Registers a template in the in-memory cache.
        """
        if template.name not in self._templates:
            self._templates[template.name] = {}

        self._templates[template.name][template.version] = template

    def get(self, name: str, version: Optional[str] = None) -> PromptTemplate:
        """
        Retrieves a template by name and optionally by version.
        If version is None, returns the latest version.
        """
        if name not in self._templates:
            raise KeyError(f"Template '{name}' not found in registry.")

        versions = self._templates[name]

        if version:
            if version not in versions:
                raise KeyError(f"Version '{version}' for template '{name}' not found.")
            return versions[version]

        # Return the "latest" version (simple string sort for semver)
        latest_version = sorted(versions.keys(), reverse=True)[0]
        return versions[latest_version]

    def load_from_directory(self, directory_path: str) -> int:
        """
        Scans a directory for .json and .yaml template files and registers them.
        Returns the count of templates loaded.
        """
        path = Path(directory_path)
        if not path.is_dir():
            raise ValueError(f"Path '{directory_path}' is not a valid directory.")

        count = 0
        # Supported extensions
        extensions = (".json", ".yaml", ".yml")

        for file in path.iterdir():
            if file.suffix in extensions:
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        if file.suffix == ".json":
                            data = json.load(f)
                        else:
                            # yaml.safe_load handles both JSON and YAML
                            data = yaml.safe_load(f)

                        template = PromptTemplate.model_validate(data)
                        self.register(template)
                        count += 1
                except Exception as e:
                    # In a real production system, we might log this instead of printing
                    print(f"Error loading template {file.name}: {e}")
                    continue

        return count

    def list_all_templates(self) -> Dict[str, List[str]]:
        """
        Returns a mapping of template names to their available versions.
        """
        return {
            name: list(versions.keys()) for name, versions in self._templates.items()
        }

    def __repr__(self) -> str:
        return f"<TemplateRegistry(templates={list(self._templates.keys())})>"
