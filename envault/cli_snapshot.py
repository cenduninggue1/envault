"""CLI commands for vault snapshot management."""

import click
from pathlib import Path

from envault.snapshot import (
    SnapshotError,
    create_snapshot,
    restore_snapshot,
    list_snapshots,
    delete_snapshot,
)


def _resolve_vault_dir(vault_dir: str) -> Path:
    return Path(vault_dir) if vault_dir else Path.cwd()


@click.group(name="snapshot")
def snapshot_group():
    """Manage vault snapshots."""


@snapshot_group.command("create")
@click.argument("name")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--vault-dir", default=None, help="Path to vault directory.")
def create_snapshot_cmd(name: str, password: str, vault_dir: str):
    """Create a named snapshot of the current vault."""
    path = _resolve_vault_dir(vault_dir)
    try:
        count = create_snapshot(path, password, name)
        click.echo(f"Snapshot '{name}' created with {count} variable(s).")
    except SnapshotError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot_group.command("restore")
@click.argument("name")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--vault-dir", default=None, help="Path to vault directory.")
def restore_snapshot_cmd(name: str, password: str, vault_dir: str):
    """Restore vault variables from a named snapshot."""
    path = _resolve_vault_dir(vault_dir)
    try:
        count = restore_snapshot(path, password, name)
        click.echo(f"Restored {count} variable(s) from snapshot '{name}'.")
    except SnapshotError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot_group.command("list")
@click.option("--vault-dir", default=None, help="Path to vault directory.")
def list_snapshots_cmd(vault_dir: str):
    """List all available snapshots."""
    path = _resolve_vault_dir(vault_dir)
    snapshots = list_snapshots(path)
    if not snapshots:
        click.echo("No snapshots found.")
        return
    for snap in snapshots:
        click.echo(f"  {snap['name']}  ({snap['count']} vars)  created: {snap['created_at']}")


@snapshot_group.command("delete")
@click.argument("name")
@click.option("--vault-dir", default=None, help="Path to vault directory.")
def delete_snapshot_cmd(name: str, vault_dir: str):
    """Delete a named snapshot."""
    path = _resolve_vault_dir(vault_dir)
    try:
        delete_snapshot(path, name)
        click.echo(f"Snapshot '{name}' deleted.")
    except SnapshotError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
