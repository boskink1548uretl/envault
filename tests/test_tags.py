"""Tests for envault/tags.py and cli_tags.py."""

import pytest
from click.testing import CliRunner
import click

from envault.tags import add_tag, remove_tag, list_tags, find_by_tag, get_all_tags, TagError
from envault.cli_tags import register_tag_commands


class FakeVault:
    def __init__(self):
        self._data = {}

    def set_project(self, project, env_vars):
        self._data[project] = dict(env_vars)

    def get_project(self, project):
        return dict(self._data.get(project, {}))

    def list_projects(self):
        return list(self._data.keys())


@pytest.fixture
def vault():
    v = FakeVault()
    v.set_project("alpha", {"KEY": "val"})
    v.set_project("beta", {"KEY": "val"})
    return v


def test_add_tag(vault):
    add_tag(vault, "alpha", "production")
    assert "production" in list_tags(vault, "alpha")


def test_add_duplicate_tag_raises(vault):
    add_tag(vault, "alpha", "production")
    with pytest.raises(TagError, match="already exists"):
        add_tag(vault, "alpha", "production")


def test_remove_tag(vault):
    add_tag(vault, "alpha", "staging")
    remove_tag(vault, "alpha", "staging")
    assert "staging" not in list_tags(vault, "alpha")


def test_remove_nonexistent_tag_raises(vault):
    with pytest.raises(TagError, match="not found"):
        remove_tag(vault, "alpha", "ghost")


def test_list_tags_empty(vault):
    assert list_tags(vault, "alpha") == []


def test_list_tags_multiple(vault):
    add_tag(vault, "alpha", "prod")
    add_tag(vault, "alpha", "critical")
    tags = list_tags(vault, "alpha")
    assert "prod" in tags
    assert "critical" in tags


def test_find_by_tag(vault):
    add_tag(vault, "alpha", "shared")
    add_tag(vault, "beta", "shared")
    results = find_by_tag(vault, "shared")
    assert "alpha" in results
    assert "beta" in results


def test_find_by_tag_no_match(vault):
    assert find_by_tag(vault, "nonexistent") == []


def test_get_all_tags(vault):
    add_tag(vault, "alpha", "prod")
    add_tag(vault, "beta", "dev")
    mapping = get_all_tags(vault)
    assert mapping["alpha"] == ["prod"]
    assert mapping["beta"] == ["dev"]


# CLI tests

@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli_with_tags(vault):
    @click.group()
    @click.pass_context
    def cli(ctx):
        ctx.ensure_object(dict)
        ctx.obj["vault"] = vault

    def get_vault_fn(ctx):
        return ctx.obj["vault"]

    register_tag_commands(cli, get_vault_fn)
    return cli


def test_cli_tag_add(runner, cli_with_tags):
    result = runner.invoke(cli_with_tags, ["tag-add", "alpha", "mytag"])
    assert result.exit_code == 0
    assert "mytag" in result.output


def test_cli_tag_list(runner, cli_with_tags, vault):
    add_tag(vault, "alpha", "listed")
    result = runner.invoke(cli_with_tags, ["tag-list", "alpha"])
    assert result.exit_code == 0
    assert "listed" in result.output


def test_cli_tag_find(runner, cli_with_tags, vault):
    add_tag(vault, "beta", "findme")
    result = runner.invoke(cli_with_tags, ["tag-find", "findme"])
    assert result.exit_code == 0
    assert "beta" in result.output


def test_cli_tag_all_empty(runner, cli_with_tags):
    result = runner.invoke(cli_with_tags, ["tag-all"])
    assert result.exit_code == 0
    assert "No tags" in result.output
