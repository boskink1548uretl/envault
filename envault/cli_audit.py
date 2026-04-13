"""CLI commands for the audit log feature."""

import click
from envault.audit import read_events, clear_audit_log


def register_audit_commands(cli: click.Group) -> None:
    """Attach audit sub-commands to the main CLI group."""
    cli.add_command(audit_log_cmd)
    cli.add_command(audit_clear_cmd)


@click.command("audit-log")
@click.option("--limit", default=20, show_default=True, help="Number of recent events to show.")
@click.option("--project", default=None, help="Filter events by project name.")
def audit_log_cmd(limit: int, project: str) -> None:
    """Display recent vault audit events."""
    events = read_events(limit=limit)
    if project:
        events = [e for e in events if e.get("project") == project]
    if not events:
        click.echo("No audit events found.")
        return
    for event in events:
        parts = [event.get("timestamp", ""), event.get("action", "")]
        if "project" in event:
            parts.append(f"project={event['project']}")
        if "detail" in event:
            parts.append(event["detail"])
        click.echo("  ".join(parts))


@click.command("audit-clear")
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
def audit_clear_cmd() -> None:
    """Clear all audit log entries."""
    clear_audit_log()
    click.echo("Audit log cleared.")
