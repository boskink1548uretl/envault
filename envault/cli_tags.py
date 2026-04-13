"""CLI commands for tag management."""

import click
from envault.tags import add_tag, remove_tag, list_tags, find_by_tag, get_all_tags, TagError


def register_tag_commands(cli, get_vault_fn):
    """Register tag subcommands onto the given CLI group."""

    @cli.command("tag-add")
    @click.argument("project")
    @click.argument("tag")
    @click.pass_context
    def tag_add_cmd(ctx, project, tag):
        """Add a TAG to a PROJECT."""
        vault = get_vault_fn(ctx)
        try:
            add_tag(vault, project, tag)
            click.echo(f"Tag '{tag}' added to project '{project}'.")
        except TagError as e:
            raise click.ClickException(str(e))

    @cli.command("tag-remove")
    @click.argument("project")
    @click.argument("tag")
    @click.pass_context
    def tag_remove_cmd(ctx, project, tag):
        """Remove a TAG from a PROJECT."""
        vault = get_vault_fn(ctx)
        try:
            remove_tag(vault, project, tag)
            click.echo(f"Tag '{tag}' removed from project '{project}'.")
        except TagError as e:
            raise click.ClickException(str(e))

    @cli.command("tag-list")
    @click.argument("project")
    @click.pass_context
    def tag_list_cmd(ctx, project):
        """List all tags for a PROJECT."""
        vault = get_vault_fn(ctx)
        tags = list_tags(vault, project)
        if not tags:
            click.echo(f"No tags for project '{project}'.")
        else:
            for tag in tags:
                click.echo(tag)

    @cli.command("tag-find")
    @click.argument("tag")
    @click.pass_context
    def tag_find_cmd(ctx, tag):
        """Find all projects with a given TAG."""
        vault = get_vault_fn(ctx)
        projects = find_by_tag(vault, tag)
        if not projects:
            click.echo(f"No projects found with tag '{tag}'.")
        else:
            for project in projects:
                click.echo(project)

    @cli.command("tag-all")
    @click.pass_context
    def tag_all_cmd(ctx):
        """Show all tags across all projects."""
        vault = get_vault_fn(ctx)
        mapping = get_all_tags(vault)
        if not mapping:
            click.echo("No tags found.")
        else:
            for project, tags in mapping.items():
                click.echo(f"{project}: {', '.join(tags)}")
