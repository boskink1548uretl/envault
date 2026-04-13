"""Tests for vault password rotation."""

import json
import pytest

from click.testing import CliRunner

from envault.crypto import encrypt, decrypt
from envault.storage import get_vault_path, save_vault
from envault.rotate import rotate_password, RotationError
from envault.cli_rotate import rotate_cmd


@pytest.fixture()
def vault_home(tmp_path):
    """Provide a temp home with a pre-populated vault."""
    old_pw = "old-secret"
    projects = {
        "alpha": encrypt(json.dumps({"KEY": "val1"}), old_pw),
        "beta": encrypt(json.dumps({"TOKEN": "abc"}), old_pw),
    }
    data = {"projects": projects}
    vault_path = get_vault_path(home_dir=str(tmp_path))
    save_vault(vault_path, data)
    return tmp_path


def test_rotate_password_reencrypts_all_projects(vault_home):
    count = rotate_password("old-secret", "new-secret", home_dir=str(vault_home))
    assert count == 2


def test_rotate_password_new_password_decrypts_correctly(vault_home):
    rotate_password("old-secret", "new-secret", home_dir=str(vault_home))

    from envault.storage import load_vault, get_vault_path
    data = load_vault(get_vault_path(home_dir=str(vault_home)))
    plaintext = decrypt(data["projects"]["alpha"], "new-secret")
    assert json.loads(plaintext) == {"KEY": "val1"}


def test_rotate_password_old_password_no_longer_works(vault_home):
    rotate_password("old-secret", "new-secret", home_dir=str(vault_home))

    from envault.storage import load_vault, get_vault_path
    data = load_vault(get_vault_path(home_dir=str(vault_home)))
    with pytest.raises(Exception):
        decrypt(data["projects"]["alpha"], "old-secret")


def test_rotate_password_wrong_old_password_raises(vault_home):
    with pytest.raises(RotationError):
        rotate_password("wrong-password", "new-secret", home_dir=str(vault_home))


def test_rotate_password_empty_vault(tmp_path):
    from envault.storage import get_vault_path, save_vault
    vault_path = get_vault_path(home_dir=str(tmp_path))
    save_vault(vault_path, {"projects": {}})
    count = rotate_password("any", "other", home_dir=str(tmp_path))
    assert count == 0


def test_rotate_cmd_success(vault_home, monkeypatch):
    monkeypatch.setenv("HOME", str(vault_home))
    runner = CliRunner()
    result = runner.invoke(
        rotate_cmd,
        input="old-secret\nnew-secret\nnew-secret\n",
    )
    assert result.exit_code == 0
    assert "rotated successfully" in result.output


def test_rotate_cmd_same_password_rejected(vault_home, monkeypatch):
    monkeypatch.setenv("HOME", str(vault_home))
    runner = CliRunner()
    result = runner.invoke(
        rotate_cmd,
        input="old-secret\nold-secret\nold-secret\n",
    )
    assert result.exit_code != 0
    assert "must differ" in result.output
