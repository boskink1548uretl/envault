"""High-level vault operations: store, retrieve, list, and delete env entries."""

from pathlib import Path

from envault.storage import load_vault, save_vault, vault_exists, DEFAULT_VAULT_DIR


class Vault:
    """Manages named .env project entries inside the encrypted vault."""

    def __init__(self, password: str, vault_dir: Path = DEFAULT_VAULT_DIR):
        self.password = password
        self.vault_dir = vault_dir
        self._data: dict = load_vault(password, vault_dir)

    def _save(self) -> None:
        save_vault(self._data, self.password, self.vault_dir)

    def set_project(self, project: str, env_vars: dict) -> None:
        """Store or overwrite env vars for a project."""
        self._data[project] = env_vars
        self._save()

    def get_project(self, project: str) -> dict:
        """Retrieve env vars for a project. Raises KeyError if not found."""
        if project not in self._data:
            raise KeyError(f"Project '{project}' not found in vault.")
        return dict(self._data[project])

    def delete_project(self, project: str) -> None:
        """Delete a project entry from the vault."""
        if project not in self._data:
            raise KeyError(f"Project '{project}' not found in vault.")
        del self._data[project]
        self._save()

    def list_projects(self) -> list[str]:
        """Return a sorted list of stored project names."""
        return sorted(self._data.keys())

    def set_var(self, project: str, key: str, value: str) -> None:
        """Set a single env variable within a project."""
        project_data = self._data.get(project, {})
        project_data[key] = value
        self._data[project] = project_data
        self._save()

    def delete_var(self, project: str, key: str) -> None:
        """Remove a single env variable from a project."""
        if project not in self._data or key not in self._data[project]:
            raise KeyError(f"Variable '{key}' not found in project '{project}'.")
        del self._data[project][key]
        self._save()
