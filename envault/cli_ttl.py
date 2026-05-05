"""CLI commands for TTL management."""

from __future__ import annotations

import click

from envault.ttl import TTLError, list_ttls, purge_expired, remove_ttl, set_ttl


def _resolve_vault_dir(ctx: click.Context) -> str:
    return ctx.obj.get("vault_dir", ".")


@click.group("ttl")
def ttl_group() -> None:
    """Manage variable expiry (time-to-live)."""


@ttl_group.command("set")
@click.argument("key")
@click.argument("seconds", type=float)
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.pass_context
def set_ttl_cmd(ctx: click.Context, key: str, seconds: float, password: str) -> None:
    """Set a TTL of SECONDS on KEY."""
    vault_dir = _resolve_vault_dir(ctx)
    try:
        entry = set_ttl(vault_dir, password, key, seconds)
        click.echo(
            f"TTL set: '{key}' expires in {entry.seconds_remaining:.1f}s "
            f"(at {entry.expires_at:.0f})."
        )
    except TTLError as exc:
        raise click.ClickException(str(exc)) from exc


@ttl_group.command("remove")
@click.argument("key")
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.pass_context
def remove_ttl_cmd(ctx: click.Context, key: str, password: str) -> None:
    """Remove the TTL from KEY."""
    vault_dir = _resolve_vault_dir(ctx)
    try:
        removed = remove_ttl(vault_dir, password, key)
        if removed:
            click.echo(f"TTL removed from '{key}'.")
        else:
            click.echo(f"No TTL was set on '{key}'.")
    except TTLError as exc:
        raise click.ClickException(str(exc)) from exc


@ttl_group.command("list")
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.pass_context
def list_ttls_cmd(ctx: click.Context, password: str) -> None:
    """List all variables that have a TTL."""
    vault_dir = _resolve_vault_dir(ctx)
    entries = list_ttls(vault_dir, password)
    if not entries:
        click.echo("No TTLs configured.")
        return
    for entry in entries:
        status = "EXPIRED" if entry.is_expired else f"{entry.seconds_remaining:.1f}s remaining"
        click.echo(f"  {entry.key:<30} {status}")


@ttl_group.command("purge")
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.pass_context
def purge_cmd(ctx: click.Context, password: str) -> None:
    """Delete all variables whose TTL has elapsed."""
    vault_dir = _resolve_vault_dir(ctx)
    purged = purge_expired(vault_dir, password)
    if purged:
        click.echo(f"Purged {len(purged)} expired variable(s): {', '.join(purged)}")
    else:
        click.echo("Nothing to purge.")
