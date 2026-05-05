"""Main CLI entry-point for envault.

This file re-registers all sub-groups so that `envault --help` surfaces
every feature.  Only the group registration block at the bottom changes
when new sub-groups are added.
"""

from __future__ import annotations

import click

from envault.vault import init_vault, load_vault, save_vault
from envault.cli_audit import audit_group
from envault.cli_rotate import rotate_group
from envault.cli_snapshot import snapshot_group
from envault.cli_share import share_group
from envault.cli_search import search_group
from envault.cli_tag import tag_group
from envault.cli_template import template_group
from envault.cli_ttl import ttl_group


@click.group()
@click.option(
    "--vault-dir",
    default=".",
    show_default=True,
    help="Directory that contains the vault file.",
)
@click.pass_context
def cli(ctx: click.Context, vault_dir: str) -> None:
    """envault — secure environment variable manager."""
    ctx.ensure_object(dict)
    ctx.obj["vault_dir"] = vault_dir


# ---------------------------------------------------------------------------
# Inline commands
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--password", "-p", prompt=True, hide_input=True, confirmation_prompt=True)
@click.pass_context
def init(ctx: click.Context, password: str) -> None:
    """Initialise a new vault in VAULT_DIR."""
    vault_dir = ctx.obj["vault_dir"]
    try:
        init_vault(vault_dir, password)
        click.echo(f"Vault initialised in '{vault_dir}'.")
    except FileExistsError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.pass_context
def set_var(ctx: click.Context, key: str, value: str, password: str) -> None:
    """Store KEY=VALUE in the vault."""
    vault_dir = ctx.obj["vault_dir"]
    data = load_vault(vault_dir, password)
    data.setdefault("vars", {})[key] = value
    save_vault(vault_dir, password, data)
    click.echo(f"Set '{key}'.")


@cli.command("get")
@click.argument("key")
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.pass_context
def get_var(ctx: click.Context, key: str, password: str) -> None:
    """Print the value of KEY."""
    vault_dir = ctx.obj["vault_dir"]
    data = load_vault(vault_dir, password)
    value = data.get("vars", {}).get(key)
    if value is None:
        raise click.ClickException(f"Key '{key}' not found.")
    click.echo(value)


@cli.command("list")
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.pass_context
def list_vars(ctx: click.Context, password: str) -> None:
    """List all variable keys stored in the vault."""
    vault_dir = ctx.obj["vault_dir"]
    data = load_vault(vault_dir, password)
    variables = data.get("vars", {})
    if not variables:
        click.echo("No variables stored.")
        return
    for key in sorted(variables):
        click.echo(f"  {key}")


@cli.command("delete")
@click.argument("key")
@click.option("--password", "-p", prompt=True, hide_input=True)
@click.pass_context
def delete_var(ctx: click.Context, key: str, password: str) -> None:
    """Remove KEY from the vault."""
    vault_dir = ctx.obj["vault_dir"]
    data = load_vault(vault_dir, password)
    if key not in data.get("vars", {}):
        raise click.ClickException(f"Key '{key}' not found.")
    del data["vars"][key]
    save_vault(vault_dir, password, data)
    click.echo(f"Deleted '{key}'.")


# ---------------------------------------------------------------------------
# Sub-group registration
# ---------------------------------------------------------------------------

cli.add_command(audit_group)
cli.add_command(rotate_group)
cli.add_command(snapshot_group)
cli.add_command(share_group)
cli.add_command(search_group)
cli.add_command(tag_group)
cli.add_command(template_group)
cli.add_command(ttl_group)
