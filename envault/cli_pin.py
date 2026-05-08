"""CLI commands for pinning/unpinning vault variables."""

from __future__ import annotations

import os
from pathlib import Path

import click

from envault.pin import PinError, pin_var, unpin_var, list_pins
from envault.vault import load_vault


def _resolve_vault_dir(ctx: click.Context) -> str:
    return ctx.obj.get("vault_dir", os.getcwd()) if ctx.obj else os.getcwd()


@click.group("pin")
def pin_group() -> None:
    """Pin or unpin variables to protect them from changes."""


@pin_group.command("add")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.pass_context
def pin_cmd(ctx: click.Context, key: str, password: str) -> None:
    """Pin KEY so it cannot be modified or deleted."""
    vault_dir = _resolve_vault_dir(ctx)
    try:
        variables = load_vault(vault_dir, password)
        pins = pin_var(vault_dir, key, variables)
        click.echo(f"Pinned '{key}'. Total pinned: {len(pins)}.")
    except PinError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@pin_group.command("remove")
@click.argument("key")
@click.pass_context
def unpin_cmd(ctx: click.Context, key: str) -> None:
    """Unpin KEY, allowing it to be modified or deleted again."""
    vault_dir = _resolve_vault_dir(ctx)
    try:
        pins = unpin_var(vault_dir, key)
        click.echo(f"Unpinned '{key}'. Total pinned: {len(pins)}.")
    except PinError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@pin_group.command("list")
@click.pass_context
def list_pins_cmd(ctx: click.Context) -> None:
    """List all pinned variable keys."""
    vault_dir = _resolve_vault_dir(ctx)
    pins = list_pins(vault_dir)
    if not pins:
        click.echo("No variables are currently pinned.")
    else:
        click.echo(f"Pinned variables ({len(pins)}):")
        for key in pins:
            click.echo(f"  {key}")
