"""CLI commands for vault password rotation."""

import click

from envault.rotate import rotate_password, RotationError


def register_rotate_commands(cli_group):
    """Attach rotation commands to the given Click group."""
    cli_group.add_command(rotate_cmd)


@click.command("rotate")
@click.option(
    "--old-password",
    prompt=True,
    hide_input=True,
    help="Current vault password.",
)
@click.option(
    "--new-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="New vault password.",
)
def rotate_cmd(old_password: str, new_password: str):
    """Re-encrypt the vault with a new master password."""
    if old_password == new_password:
        click.echo("New password must differ from the current password.", err=True)
        raise SystemExit(1)

    try:
        count = rotate_password(old_password, new_password)
    except RotationError as exc:
        click.echo(f"Rotation failed: {exc}", err=True)
        raise SystemExit(1)

    click.echo(
        f"Password rotated successfully. {count} project(s) re-encrypted."
    )
