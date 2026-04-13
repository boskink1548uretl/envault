"""Search functionality for envault: find keys across projects."""

from typing import Optional


def search_key(vault, key: str, project: Optional[str] = None) -> dict:
    """
    Search for a key across one or all projects in the vault.

    Args:
        vault: A Vault instance.
        key: The environment variable key to search for.
        project: If provided, limit search to this project.

    Returns:
        A dict mapping project names to the value found for the key,
        or an empty dict if no matches.
    """
    results = {}
    projects = [project] if project else vault.list_projects()

    for proj in projects:
        try:
            env_vars = vault.get_project(proj)
        except Exception:
            continue
        if key in env_vars:
            results[proj] = env_vars[key]

    return results


def search_value(vault, value: str, project: Optional[str] = None) -> dict:
    """
    Search for a value substring across one or all projects in the vault.

    Args:
        vault: A Vault instance.
        value: The substring to search for in env variable values.
        project: If provided, limit search to this project.

    Returns:
        A dict mapping project names to a dict of matching key-value pairs.
    """
    results = {}
    projects = [project] if project else vault.list_projects()

    for proj in projects:
        try:
            env_vars = vault.get_project(proj)
        except Exception:
            continue
        matches = {k: v for k, v in env_vars.items() if value in v}
        if matches:
            results[proj] = matches

    return results
