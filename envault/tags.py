"""Tag management for envault projects."""

from typing import List, Dict


class TagError(Exception):
    pass


def add_tag(vault, project: str, tag: str) -> None:
    """Add a tag to a project."""
    env_vars = vault.get_project(project)
    tags = _get_tags(env_vars)
    if tag in tags:
        raise TagError(f"Tag '{tag}' already exists on project '{project}'")
    tags.append(tag)
    env_vars["__tags__"] = ",".join(tags)
    vault.set_project(project, env_vars)


def remove_tag(vault, project: str, tag: str) -> None:
    """Remove a tag from a project."""
    env_vars = vault.get_project(project)
    tags = _get_tags(env_vars)
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found on project '{project}'")
    tags.remove(tag)
    env_vars["__tags__"] = ",".join(tags)
    vault.set_project(project, env_vars)


def list_tags(vault, project: str) -> List[str]:
    """List all tags for a project."""
    env_vars = vault.get_project(project)
    return _get_tags(env_vars)


def find_by_tag(vault, tag: str) -> List[str]:
    """Return all project names that have the given tag."""
    results = []
    for project in vault.list_projects():
        env_vars = vault.get_project(project)
        if tag in _get_tags(env_vars):
            results.append(project)
    return results


def get_all_tags(vault) -> Dict[str, List[str]]:
    """Return a mapping of project -> tags for all projects."""
    result = {}
    for project in vault.list_projects():
        env_vars = vault.get_project(project)
        tags = _get_tags(env_vars)
        if tags:
            result[project] = tags
    return result


def _get_tags(env_vars: dict) -> List[str]:
    """Extract tags list from env vars dict."""
    raw = env_vars.get("__tags__", "")
    if not raw:
        return []
    return [t for t in raw.split(",") if t]
