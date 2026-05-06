"""CLI commands for variable change history."""

from __future__ import annotations

import time
from pathlib import Path

import click

from envault.history import HistoryError, clear_history, get_history


def _resolve_vault_dir(ctx: click.Context) -> Path:
    return Path(ctx.obj.get("vault_dir", "."))


@click.group("history")
def history_group() -> None:
    """Commands for inspecting and managing variable change history."""


@history_group.command("log")
@click.option("--key", "-k", default=None, help="Filter history to a specific key.")
@click.option("--limit", "-n", default=20, show_default=True, help="Max entries to show.")
@click.password_option("--password", "-p", prompt="Vault password", confirmation_prompt=False)
@click.pass_context
def history_log_cmd(ctx: click.Context, key: str, limit: int, password: str) -> None:
    """Show recent change history for vault variables."""
    vault_dir = _resolve_vault_dir(ctx)
    try:
        entries = get_history(vault_dir, password, key=key)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    if not entries:
        click.echo("No history entries found.")
        return

    for entry in entries[-limit:]:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry.timestamp))
        old = entry.old_value if entry.old_value is not None else "(none)"
        new = entry.new_value if entry.new_value is not None else "(none)"
        click.echo(f"[{ts}] {entry.action.upper():6s}  {entry.key}  {old!r} -> {new!r}")


@history_group.command("clear")
@click.option("--key", "-k", default=None, help="Clear history only for this key.")
@click.option("--yes", is_flag=True, default=False, help="Skip confirmation prompt.")
@click.password_option("--password", "-p", prompt="Vault password", confirmation_prompt=False)
@click.pass_context
def history_clear_cmd(ctx: click.Context, key: str, yes: bool, password: str) -> None:
    """Clear change history from the vault."""
    vault_dir = _resolve_vault_dir(ctx)
    scope = f"key '{key}'" if key else "all keys"
    if not yes:
        click.confirm(f"Clear history for {scope}?", abort=True)
    try:
        removed = clear_history(vault_dir, password, key=key)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Removed {removed} history entry/entries for {scope}.")
