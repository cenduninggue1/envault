"""CLI entry point for envault using Click."""

import pathlib
import click

from envault.vault import init_vault, load_vault, save_vault

VAULT_OPTION = click.option(
    "--vault",
    default=".envault",
    show_default=True,
    help="Path to the vault file.",
)


@click.group()
def cli():
    """envault — Securely manage environment variables in encrypted local vaults."""


@cli.command()
@VAULT_OPTION
@click.password_option(prompt="Master password")
def init(vault: str, password: str):
    """Initialize a new empty vault."""
    path = pathlib.Path(vault)
    try:
        init_vault(password, path)
        click.echo(f"Vault initialized at {path}")
    except FileExistsError as exc:
        raise click.ClickException(str(exc))


@cli.command(name="set")
@VAULT_OPTION
@click.argument("key")
@click.argument("value")
@click.password_option(prompt="Master password")
def set_var(vault: str, key: str, value: str, password: str):
    """Set an environment variable in the vault."""
    path = pathlib.Path(vault)
    try:
        env_vars = load_vault(password, path)
        env_vars[key] = value
        save_vault(env_vars, password, path)
        click.echo(f"Set {key}")
    except (FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc))


@cli.command(name="get")
@VAULT_OPTION
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
def get_var(vault: str, key: str, password: str):
    """Get an environment variable from the vault."""
    path = pathlib.Path(vault)
    try:
        env_vars = load_vault(password, path)
        if key not in env_vars:
            raise click.ClickException(f"Key '{key}' not found in vault.")
        click.echo(env_vars[key])
    except (FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc))


@cli.command(name="list")
@VAULT_OPTION
@click.option("--password", prompt=True, hide_input=True)
def list_vars(vault: str, password: str):
    """List all keys stored in the vault."""
    path = pathlib.Path(vault)
    try:
        env_vars = load_vault(password, path)
        if not env_vars:
            click.echo("Vault is empty.")
        for key in sorted(env_vars):
            click.echo(key)
    except (FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc))
