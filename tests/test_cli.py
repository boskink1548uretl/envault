import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from envault.cli import cli

PASSWORD = "test-password"
PROJECT = "myapp"
ENV_CONTENT = "DB_HOST=localhost\nDB_PORT=5432\n# comment\nSECRET=abc123\n"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(ENV_CONTENT)
    return str(p)


@pytest.fixture
def mock_vault():
    with patch("envault.cli.get_vault") as mock_get:
        vault_instance = MagicMock()
        mock_get.return_value = vault_instance
        yield vault_instance


def test_set_project_stores_variables(runner, env_file, mock_vault):
    result = runner.invoke(cli, ["set", PROJECT, env_file, "--password", PASSWORD])
    assert result.exit_code == 0
    assert "Stored 3 variable(s)" in result.output
    mock_vault.set_project.assert_called_once_with(
        PROJECT, {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"}
    )


def test_get_project_prints_to_stdout(runner, mock_vault):
    mock_vault.get_project.return_value = {"KEY": "value", "FOO": "bar"}
    result = runner.invoke(cli, ["get", PROJECT, "--password", PASSWORD])
    assert result.exit_code == 0
    assert "KEY=value" in result.output
    assert "FOO=bar" in result.output


def test_get_project_writes_to_file(runner, tmp_path, mock_vault):
    mock_vault.get_project.return_value = {"KEY": "value"}
    out_file = str(tmp_path / "out.env")
    result = runner.invoke(cli, ["get", PROJECT, "--password", PASSWORD, "--output", out_file])
    assert result.exit_code == 0
    assert os.path.exists(out_file)
    assert open(out_file).read() == "KEY=value\n"


def test_get_project_not_found_exits_nonzero(runner, mock_vault):
    mock_vault.get_project.side_effect = KeyError(PROJECT)
    result = runner.invoke(cli, ["get", PROJECT, "--password", PASSWORD])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_list_projects_shows_names(runner, mock_vault):
    mock_vault.list_projects.return_value = ["app1", "app2"]
    result = runner.invoke(cli, ["list", "--password", PASSWORD])
    assert result.exit_code == 0
    assert "app1" in result.output
    assert "app2" in result.output


def test_list_projects_empty(runner, mock_vault):
    mock_vault.list_projects.return_value = []
    result = runner.invoke(cli, ["list", "--password", PASSWORD])
    assert result.exit_code == 0
    assert "No projects" in result.output


def test_delete_project_success(runner, mock_vault):
    result = runner.invoke(cli, ["delete", PROJECT, "--password", PASSWORD, "--yes"])
    assert result.exit_code == 0
    assert "deleted" in result.output
    mock_vault.delete_project.assert_called_once_with(PROJECT)


def test_delete_project_not_found(runner, mock_vault):
    mock_vault.delete_project.side_effect = KeyError(PROJECT)
    result = runner.invoke(cli, ["delete", PROJECT, "--password", PASSWORD, "--yes"])
    assert result.exit_code == 1
    assert "not found" in result.output
