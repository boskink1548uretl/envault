"""Vault class for managing encrypted project environment variables."""

from typing import Dict, List, Optional

from envault.crypto import decrypt, encrypt
from envault.storage import load_vault, save_vault, vault_exists


class Vault:
    """Manages encrypted storage of per-project environment variables."""

    def __init__(self, password: str, vault_path: str):
        """
        Args:
            password: Master password used for encryption/decryption.
            vault_path: Path to the encrypted vault file.
        """
        self._password = password
        self._vault_path = vault_path
        if vault_exists(vault_path):
            encrypted = load_vault(vault_path)
            import json
            self._data: dict = json.loads(decrypt(encrypted, password))
        else:
            self._data = {}
            self._save()

    def _save(self):
        """Serialize and encrypt vault data to disk."""
        import json
        encrypted = encrypt(json.dumps(self._data), self._password)
        save_vault(self._vault_path, encrypted)

    def set_project(self, project: str, variables: Dict[str, str]) -> None:
        """Store or replace all variables for a project.

        Args:
            project: Project name.
            variables: Dict of environment variable key-value pairs.
        """
        self._data[project] = variables
        self._save()

    def get_project(self, project: str) -> Optional[Dict[str, str]]:
        """Retrieve variables for a project.

        Args:
            project: Project name.

        Returns:
            Dict of variables, or empty dict if project not found.
        """
        return self._data.get(project, {})

    def list_projects(self) -> List[str]:
        """Return a sorted list of all project names."""
        return sorted(self._data.keys())

    def delete_project(self, project: str) -> None:
        """Delete a project and all its variables.

        Args:
            project: Project name.

        Raises:
            KeyError: If the project does not exist.
        """
        if project not in self._data:
            raise KeyError(f"Project '{project}' not found.")
        del self._data[project]
        self._save()

    def set_variable(self, project: str, key: str, value: str) -> None:
        """Set a single variable in a project.

        Args:
            project: Project name.
            key: Variable name.
            value: Variable value.
        """
        project_data = self._data.get(project, {})
        project_data[key] = value
        self._data[project] = project_data
        self._save()

    def delete_variable(self, project: str, key: str) -> None:
        """Remove a single variable from a project.

        Args:
            project: Project name.
            key: Variable name.

        Raises:
            KeyError: If the project or variable does not exist.
        """
        if project not in self._data:
            raise KeyError(f"Project '{project}' not found.")
        if key not in self._data[project]:
            raise KeyError(f"Variable '{key}' not found in project '{project}'.")
        del self._data[project][key]
        self._save()
