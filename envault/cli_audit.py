"""CLI commands for viewing and managing the audit log."""

import os
import click

from envault.audit import read_events, clear_log, format_event


def _resolve_vault_dir(vault_path: str) -> str:
    """Return the directory containing the vault file."""
    return os.path.dirname(os.path.abspath(vault_path))


@click.group("audit")
def audit_group():
    """View and manage the audit log for a vault."""


@audit_group.command("log")
@click.option(
    "--vault",
    default=".envault",
    show_default=True,
    help="Path to the vault file.",
)
@click.option(
    "--tail",
    default=0,
    type=int,
    help="Show only the last N entries (0 = all).",
)
@click.option(
    "--action",
    default=None,
    help="Filter events by action type (e.g. set, get, delete).",
)
def show_log(vault: str, tail: int, action: str):
    """Display audit log entries."""
    vault_dir = _resolve_vault_dir(vault)
    events = read_events(vault_dir)

    if action:
        events = [e for e in events if e.get("action") == action]

    if tail > 0:
        events = events[-tail:]

    if not events:
        click.echo("No audit log entries found.")
        return

    for event in events:
        click.echo(format_event(event))


@audit_group.command("clear")
@click.option(
    "--vault",
    default=".envault",
    show_default=True,
    help="Path to the vault file.",
)
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
def clear_audit_log(vault: str):
    """Delete all audit log entries."""
    vault_dir = _resolve_vault_dir(vault)
    clear_log(vault_dir)
    click.echo("Audit log cleared.")
