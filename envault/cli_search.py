"""CLI commands for searching keys and values across envault projects."""

import click
from envault.search import search_key, search_value


def register_search_commands(cli, get_vault):
    """Register search-related CLI commands onto the given Click group."""

    @cli.command("search-key")
    @click.argument("key")
    @click.option("--project", "-p", default=None, help="Limit search to a specific project.")
    @click.pass_context
    def search_key_cmd(ctx, key, project):
        """Search for a KEY across all projects (or a specific project)."""
        vault = get_vault(ctx)
        results = search_key(vault, key, project)

        if not results:
            click.echo(f"Key '{key}' not found in any project.")
            return

        for proj, val in results.items():
            click.echo(f"[{proj}] {key}={val}")

    @cli.command("search-value")
    @click.argument("value")
    @click.option("--project", "-p", default=None, help="Limit search to a specific project.")
    @click.pass_context
    def search_value_cmd(ctx, value, project):
        """Search for a VALUE substring across all projects (or a specific project)."""
        vault = get_vault(ctx)
        results = search_value(vault, value, project)

        if not results:
            click.echo(f"Value substring '{value}' not found in any project.")
            return

        for proj, matches in results.items():
            for k, v in matches.items():
                click.echo(f"[{proj}] {k}={v}")
