"""Tests for CLI export/import commands in envault."""

import os
import tempfile

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock

import click
from envault.cli_export import register_export_commands


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_vault():
    vault = MagicMock()
    vault.get_project.return_value = {"DB_URL": "postgres://localhost/db", "KEY": "secret"}
    vault.list_projects.return_value = ["myapp"]
    vault.set_project = MagicMock()
    return vault


@pytest.fixture
def cli_with_export(mock_vault):
    @click.group()
    @click.pass_context
    def cli(ctx):
        ctx.ensure_object(dict)

    def get_vault(ctx):
        return mock_vault

    register_export_commands(cli, get_vault)
    return cli


def test_export_prints_to_stdout(runner, cli_with_export):
    result = runner.invoke(cli_with_export, ["export", "myapp"])
    assert result.exit_code == 0
    assert "DB_URL=postgres://localhost/db" in result.output
    assert "KEY=secret" in result.output


def test_export_writes_to_file(runner, cli_with_export):
    with tempfile.NamedTemporaryFile(suffix=".env", delete=False) as tmp:
        path = tmp.name
    try:
        result = runner.invoke(cli_with_export, ["export", "myapp", "--output", path])
        assert result.exit_code == 0
        assert f"Exported 'myapp' to {path}" in result.output
        with open(path) as f:
            content = f.read()
        assert "DB_URL" in content
    finally:
        os.unlink(path)


def test_export_nonexistent_project_shows_error(runner, cli_with_export, mock_vault):
    mock_vault.get_project.return_value = {}
    result = runner.invoke(cli_with_export, ["export", "ghost"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_export_all_prints_json(runner, cli_with_export):
    result = runner.invoke(cli_with_export, ["export-all"])
    assert result.exit_code == 0
    assert "myapp" in result.output
    assert "projects" in result.output


def test_import_adds_variables(runner, cli_with_export, mock_vault):
    mock_vault.get_project.return_value = {}
    content = "NEW_KEY=newvalue\nANOTHER=123\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as tmp:
        tmp.write(content)
        path = tmp.name
    try:
        result = runner.invoke(cli_with_export, ["import", "myapp", path])
        assert result.exit_code == 0
        assert "Imported 2 variable(s)" in result.output
        mock_vault.set_project.assert_called_once()
    finally:
        os.unlink(path)


def test_import_skips_existing_without_overwrite(runner, cli_with_export, mock_vault):
    mock_vault.get_project.return_value = {"DB_URL": "existing"}
    content = "DB_URL=newvalue\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as tmp:
        tmp.write(content)
        path = tmp.name
    try:
        result = runner.invoke(cli_with_export, ["import", "myapp", path])
        assert result.exit_code == 0
        assert "Skipped" in result.output
        assert "No new variables" in result.output
    finally:
        os.unlink(path)
