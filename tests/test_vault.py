"""Unit tests for envault.vault and envault.storage modules."""

import pytest
from pathlib import Path
from envault.vault import Vault


PASSWORD = "test-password-123"


@pytest.fixture
def vault(tmp_path):
    """Provide a fresh Vault instance backed by a temporary directory."""
    return Vault(PASSWORD, vault_dir=tmp_path)


def test_set_and_get_project(vault):
    vault.set_project("myapp", {"API_KEY": "abc", "DEBUG": "true"})
    result = vault.get_project("myapp")
    assert result == {"API_KEY": "abc", "DEBUG": "true"}


def test_list_projects(vault):
    vault.set_project("alpha", {"X": "1"})
    vault.set_project("beta", {"Y": "2"})
    assert vault.list_projects() == ["alpha", "beta"]


def test_delete_project(vault):
    vault.set_project("temp", {"K": "V"})
    vault.delete_project("temp")
    assert "temp" not in vault.list_projects()


def test_delete_nonexistent_project_raises(vault):
    with pytest.raises(KeyError):
        vault.delete_project("ghost")


def test_get_nonexistent_project_raises(vault):
    with pytest.raises(KeyError):
        vault.get_project("ghost")


def test_persistence_across_instances(tmp_path):
    """Data written by one Vault instance should be readable by another."""
    v1 = Vault(PASSWORD, vault_dir=tmp_path)
    v1.set_project("service", {"TOKEN": "xyz"})

    v2 = Vault(PASSWORD, vault_dir=tmp_path)
    assert v2.get_project("service") == {"TOKEN": "xyz"}


def test_set_and_delete_var(vault):
    vault.set_project("app", {"A": "1", "B": "2"})
    vault.set_var("app", "C", "3")
    assert vault.get_project("app")["C"] == "3"
    vault.delete_var("app", "C")
    assert "C" not in vault.get_project("app")


def test_wrong_password_on_load(tmp_path):
    v1 = Vault(PASSWORD, vault_dir=tmp_path)
    v1.set_project("proj", {"K": "V"})

    with pytest.raises(ValueError):
        Vault("wrong-password", vault_dir=tmp_path)
