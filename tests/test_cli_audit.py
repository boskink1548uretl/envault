"""Tests for the audit CLI commands."""

import pytest
from click.testing import CliRunner
import click

from envault.cli_audit import register_audit_commands, audit_log_cmd, audit_clear_cmd
from envault.audit import log_event, clear_audit_log


@pytest.fixture(autouse=True)
def tmp_audit_home(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_HOME", str(tmp_path))
    yield tmp_path


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli_with_audit():
    @click.group()
    def cli():
        pass

    register_audit_commands(cli)
    return cli


def test_audit_log_no_events(runner, cli_with_audit):
    result = runner.invoke(cli_with_audit, ["audit-log"])
    assert result.exit_code == 0
    assert "No audit events found" in result.output


def test_audit_log_shows_events(runner, cli_with_audit, tmp_audit_home):
    log_event("set", project="webapp", detail="DB_URL")
    log_event("get", project="webapp")
    result = runner.invoke(cli_with_audit, ["audit-log"])
    assert result.exit_code == 0
    assert "set" in result.output
    assert "webapp" in result.output


def test_audit_log_filter_by_project(runner, cli_with_audit, tmp_audit_home):
    log_event("set", project="alpha")
    log_event("set", project="beta")
    result = runner.invoke(cli_with_audit, ["audit-log", "--project", "alpha"])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" not in result.output


def test_audit_log_limit(runner, cli_with_audit, tmp_audit_home):
    for i in range(10):
        log_event("set", project=f"proj{i}")
    result = runner.invoke(cli_with_audit, ["audit-log", "--limit", "3"])
    assert result.exit_code == 0
    assert result.output.count("set") == 3


def test_audit_clear_confirmed(runner, cli_with_audit, tmp_audit_home):
    log_event("set", project="myapp")
    result = runner.invoke(cli_with_audit, ["audit-clear"], input="y\n")
    assert result.exit_code == 0
    assert "cleared" in result.output
    from envault.audit import get_audit_log_path
    assert not get_audit_log_path().exists()


def test_audit_clear_aborted(runner, cli_with_audit, tmp_audit_home):
    log_event("set", project="myapp")
    result = runner.invoke(cli_with_audit, ["audit-clear"], input="n\n")
    assert result.exit_code != 0 or "Aborted" in result.output
    from envault.audit import get_audit_log_path
    assert get_audit_log_path().exists()
