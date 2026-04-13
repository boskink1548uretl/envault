import sys
import click
from envault.vault import Vault


def get_vault(password: str) -> Vault:
    """Helper to load or initialize the vault with the given password."""
    return Vault(password=password)


@click.group()
def cli():
    """envault — Securely manage and sync .env files across projects."""
    pass


@cli.command("set")
@click.argument("project")
@click.argument("env_file", type=click.Path(exists=True))
@click.password_option("--password", "-p", prompt="Vault password", help="Master password for the vault.")
def set_project(project: str, env_file: str, password: str):
    """Store .env variables for PROJECT from ENV_FILE."""
    with open(env_file, "r") as f:
        content = f.read()

    env_vars = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env_vars[key.strip()] = value.strip()

    vault = get_vault(password)
    vault.set_project(project, env_vars)
    click.echo(f"✓ Stored {len(env_vars)} variable(s) for project '{project}'.")


@cli.command("get")
@click.argument("project")
@click.option("--password", "-p", prompt="Vault password", hide_input=True, help="Master password for the vault.")
@click.option("--output", "-o", type=click.Path(), default=None, help="Write variables to a file instead of stdout.")
def get_project(project: str, password: str, output: str):
    """Retrieve .env variables for PROJECT."""
    vault = get_vault(password)
    try:
        env_vars = vault.get_project(project)
    except KeyError:
        click.echo(f"Error: project '{project}' not found in vault.", err=True)
        sys.exit(1)

    lines = [f"{k}={v}" for k, v in env_vars.items()]
    content = "\n".join(lines) + "\n"

    if output:
        with open(output, "w") as f:
            f.write(content)
        click.echo(f"✓ Written {len(env_vars)} variable(s) to '{output}'.")
    else:
        click.echo(content, nl=False)


@cli.command("list")
@click.option("--password", "-p", prompt="Vault password", hide_input=True, help="Master password for the vault.")
def list_projects(password: str):
    """List all projects stored in the vault."""
    vault = get_vault(password)
    projects = vault.list_projects()
    if not projects:
        click.echo("No projects stored in vault.")
    else:
        click.echo("Projects in vault:")
        for name in projects:
            click.echo(f"  - {name}")


@cli.command("delete")
@click.argument("project")
@click.option("--password", "-p", prompt="Vault password", hide_input=True, help="Master password for the vault.")
@click.confirmation_option(prompt="Are you sure you want to delete this project?")
def delete_project(project: str, password: str):
    """Delete a PROJECT from the vault."""
    vault = get_vault(password)
    try:
        vault.delete_project(project)
        click.echo(f"✓ Project '{project}' deleted from vault.")
    except KeyError:
        click.echo(f"Error: project '{project}' not found in vault.", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
