"""Tests for envault/search.py and cli_search.py."""

import pytest
from click.testing import CliRunner
import click

from envault.search import search_key, search_value
from envault.cli_search import register_search_commands


class FakeVault:
    def __init__(self):
        self._data = {
            "alpha": {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc123"},
            "beta": {"DB_HOST": "remotehost", "API_KEY": "xyz789"},
            "gamma": {"REDIS_URL": "redis://localhost:6379"},
        }

    def list_projects(self):
        return list(self._data.keys())

    def get_project(self, name):
        if name not in self._data:
            raise KeyError(f"Project '{name}' not found")
        return self._data[name]


@pytest.fixture
def vault():
    return FakeVault()


# --- search_key tests ---

def test_search_key_found_in_multiple_projects(vault):
    results = search_key(vault, "DB_HOST")
    assert "alpha" in results
    assert "beta" in results
    assert results["alpha"] == "localhost"
    assert results["beta"] == "remotehost"


def test_search_key_not_found(vault):
    results = search_key(vault, "NONEXISTENT_KEY")
    assert results == {}


def test_search_key_limited_to_project(vault):
    results = search_key(vault, "DB_HOST", project="alpha")
    assert list(results.keys()) == ["alpha"]


def test_search_key_project_missing_key(vault):
    results = search_key(vault, "API_KEY", project="alpha")
    assert results == {}


# --- search_value tests ---

def test_search_value_found(vault):
    results = search_value(vault, "localhost")
    assert "alpha" in results
    assert "gamma" in results
    assert "DB_HOST" in results["alpha"]


def test_search_value_not_found(vault):
    results = search_value(vault, "doesnotexist")
    assert results == {}


def test_search_value_limited_to_project(vault):
    results = search_value(vault, "localhost", project="gamma")
    assert list(results.keys()) == ["gamma"]


# --- CLI tests ---

@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli_with_search(vault):
    @click.group()
    @click.pass_context
    def cli(ctx):
        ctx.ensure_object(dict)
        ctx.obj["vault"] = vault

    def get_vault(ctx):
        return ctx.obj["vault"]

    register_search_commands(cli, get_vault)
    return cli


def test_cli_search_key_found(runner, cli_with_search):
    result = runner.invoke(cli_with_search, ["search-key", "DB_HOST"])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_cli_search_key_not_found(runner, cli_with_search):
    result = runner.invoke(cli_with_search, ["search-key", "MISSING"])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_cli_search_value_found(runner, cli_with_search):
    result = runner.invoke(cli_with_search, ["search-value", "localhost"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_cli_search_value_not_found(runner, cli_with_search):
    result = runner.invoke(cli_with_search, ["search-value", "nope"])
    assert result.exit_code == 0
    assert "not found" in result.output
