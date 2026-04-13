"""Export and import utilities for envault vault data."""

import json
import os
from datetime import datetime
from typing import Optional


def export_project(vault, project: str, output_path: Optional[str] = None) -> str:
    """Export a project's env variables to a .env file or JSON.

    Args:
        vault: Vault instance to export from.
        project: Project name to export.
        output_path: Optional file path to write to. If None, returns content as string.

    Returns:
        The exported content as a string.
    """
    variables = vault.get_project(project)
    if not variables:
        raise ValueError(f"Project '{project}' has no variables to export.")

    lines = [
        f"# Exported from envault — project: {project}",
        f"# Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "",
    ]
    for key, value in sorted(variables.items()):
        lines.append(f"{key}={value}")

    content = "\n".join(lines) + "\n"

    if output_path:
        with open(output_path, "w") as f:
            f.write(content)

    return content


def import_env_file(path: str) -> dict:
    """Parse a .env file and return a dict of key-value pairs.

    Args:
        path: Path to the .env file.

    Returns:
        Dictionary of environment variable key-value pairs.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains invalid lines.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    variables = {}
    with open(path, "r") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"Invalid line {lineno} in '{path}': {line!r}")
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if not key:
                raise ValueError(f"Empty key on line {lineno} in '{path}'.")
            variables[key] = value

    return variables


def export_vault_json(vault, output_path: Optional[str] = None) -> str:
    """Export all projects in the vault to a JSON string.

    Args:
        vault: Vault instance.
        output_path: Optional path to write JSON to.

    Returns:
        JSON string of all projects and their variables.
    """
    projects = vault.list_projects()
    data = {
        "exported_at": datetime.utcnow().isoformat(),
        "projects": {p: vault.get_project(p) for p in projects},
    }
    content = json.dumps(data, indent=2)
    if output_path:
        with open(output_path, "w") as f:
            f.write(content)
    return content
