"""Tests for envault/export.py — export and import utilities."""

import json
import os
import tempfile

import pytest

from envault.export import export_project, export_vault_json, import_env_file


class FakeVault:
    """Minimal fake Vault for testing export utilities."""

    def __init__(self, data: dict):
        self._data = data

    def get_project(self, project: str) -> dict:
        return self._data.get(project, {})

    def list_projects(self):
        return list(self._data.keys())


@pytest.fixture
def vault():
    return FakeVault(
        {
            "myapp": {"DB_URL": "postgres://localhost/myapp", "SECRET": "abc123"},
            "other": {"API_KEY": "xyz"},
        }
    )


def test_export_project_returns_env_content(vault):
    content = export_project(vault, "myapp")
    assert "DB_URL=postgres://localhost/myapp" in content
    assert "SECRET=abc123" in content
    assert "# Exported from envault" in content


def test_export_project_writes_file(vault):
    with tempfile.NamedTemporaryFile(suffix=".env", delete=False) as tmp:
        path = tmp.name
    try:
        export_project(vault, "myapp", output_path=path)
        with open(path) as f:
            content = f.read()
        assert "DB_URL=postgres://localhost/myapp" in content
    finally:
        os.unlink(path)


def test_export_project_raises_for_empty_project(vault):
    with pytest.raises(ValueError, match="no variables"):
        export_project(vault, "nonexistent")


def test_import_env_file_parses_correctly():
    content = "# comment\nFOO=bar\nBAZ=qux\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as tmp:
        tmp.write(content)
        path = tmp.name
    try:
        result = import_env_file(path)
        assert result == {"FOO": "bar", "BAZ": "qux"}
    finally:
        os.unlink(path)


def test_import_env_file_raises_if_not_found():
    with pytest.raises(FileNotFoundError):
        import_env_file("/nonexistent/path/.env")


def test_import_env_file_raises_on_invalid_line():
    content = "VALID=ok\nINVALID_LINE\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as tmp:
        tmp.write(content)
        path = tmp.name
    try:
        with pytest.raises(ValueError, match="Invalid line"):
            import_env_file(path)
    finally:
        os.unlink(path)


def test_export_vault_json_contains_all_projects(vault):
    content = export_vault_json(vault)
    data = json.loads(content)
    assert "myapp" in data["projects"]
    assert "other" in data["projects"]
    assert data["projects"]["myapp"]["DB_URL"] == "postgres://localhost/myapp"


def test_export_vault_json_writes_file(vault):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        path = tmp.name
    try:
        export_vault_json(vault, output_path=path)
        with open(path) as f:
            data = json.load(f)
        assert "projects" in data
    finally:
        os.unlink(path)
