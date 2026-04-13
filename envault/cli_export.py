"""CLI commands for exporting and importing env variables in envault."""

import click

from envault.export import export_project, export_vault_json, import_env_file


def register_export_commands(cli, get:
    """Register export/import commands onto the given Click group.

    Args:
        cli: The Click group to attach commands to.
        get_vault: Callable returning an authenticated Vault instance.
    """

    @cli.command("export")
    @click.argument("project")
    @click.option(
        "--output", "-o", default=None, help="Output .env file path. Prints to stdout if omitted."
    )
    @click.pass_context
    def export_cmd(ctx, project, output):
        """Export a project's variables to a .env file."""
        vault = get_vault(ctx)
        try:
            content = export_project(vault, project, output_path=output)
        except ValueError as e:
            raise click.ClickException(str(e))
        if output:
            click.echo(f"Exported '{project}' to {output}")
        else:
            click.echo(content, nl=False)

    @cli.command("export-all")
    @click.option(
        "--output", "-o", default=None, help="Output JSON file path. Prints to stdout if omitted."
    )
    @click.pass_context
    def export_all_cmd(ctx, output):
        """Export all projects in the vault to JSON."""
        vault = get_vault(ctx)
        content = export_vault_json(vault, output_path=output)
        if output:
            click.echo(f"Vault exported to {output}")
        else:
            click.echo(content)

    @cli.command("import")
    @click.argument("project")
    @click.argument("env_file", type=click.Path(exists=True))
    @click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing variables.")
    @click.pass_context
    def import_cmd(ctx, project, env_file, overwrite):
        """Import variables from a .env file into a project."""
        vault = get_vault(ctx)
        try:
            variables = import_env_file(env_file)
        except (FileNotFoundError, ValueError) as e:
            raise click.ClickException(str(e))

        existing = vault.get_project(project) or {}
        if existing and not overwrite:
            skipped = [k for k in variables if k in existing]
            variables = {k: v for k, v in variables.items() if k not in existing}
            if skipped:
                click.echo(
                    f"Skipped {len(skipped)} existing key(s): {', '.join(skipped)}. "
                    "Use --overwrite to replace them."
                )

        if variables:
            vault.set_project(project, {**existing, **variables})
            click.echo(f"Imported {len(variables)} variable(s) into '{project}'.")
        else:
            click.echo("No new variables to import.")
