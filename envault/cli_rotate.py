"""CLI commands for vault key rotation."""

from pathlib import Path

import click

from envault.rotate import rotate_key, RotationError


def _resolve_vault_dir(ctx: click.Context) -> Path:
    """Return vault directory from context or default."""
    return Path(ctx.obj.get("vault_dir", ".")) if ctx.obj else Path(".")


@click.group("rotate")
def rotate_group() -> None:
    """Key rotation commands."""


@rotate_group.command("key")
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
@click.pass_context
def rotate_key_cmd(ctx: click.Context, old_password: str, new_password: str) -> None:
    """Re-encrypt the vault with a new password."""
    vault_dir = _resolve_vault_dir(ctx)

    try:
        count = rotate_key(vault_dir, old_password, new_password)
    except RotationError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(
        click.style("✔", fg="green")
        + f" Key rotated successfully. {count} variable(s) re-encrypted."
    )
