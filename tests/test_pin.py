"""Tests for envault/pin.py"""

from __future__ import annotations

import pytest

from envault.pin import (
    PinError,
    assert_not_pinned,
    is_pinned,
    list_pins,
    pin_var,
    unpin_var,
)
from envault.vault import init_vault, save_vault


@pytest.fixture()
def vault_dir(tmp_path):
    password = "test-pass"
    init_vault(str(tmp_path), password)
    save_vault(str(tmp_path), password, {"API_KEY": "abc123", "DB_URL": "postgres://"})
    return str(tmp_path)


def test_pin_var_persists(vault_dir):
    from envault.vault import load_vault
    variables = load_vault(vault_dir, "test-pass")
    pins = pin_var(vault_dir, "API_KEY", variables)
    assert "API_KEY" in pins
    assert list_pins(vault_dir) == ["API_KEY"]


def test_pin_var_unknown_key_raises(vault_dir):
    with pytest.raises(PinError, match="does not exist"):
        pin_var(vault_dir, "MISSING_KEY", {"OTHER": "val"})


def test_pin_var_duplicate_is_idempotent(vault_dir):
    from envault.vault import load_vault
    variables = load_vault(vault_dir, "test-pass")
    pin_var(vault_dir, "API_KEY", variables)
    pins = pin_var(vault_dir, "API_KEY", variables)
    assert pins.count("API_KEY") == 1


def test_unpin_var_removes_key(vault_dir):
    from envault.vault import load_vault
    variables = load_vault(vault_dir, "test-pass")
    pin_var(vault_dir, "API_KEY", variables)
    pins = unpin_var(vault_dir, "API_KEY")
    assert "API_KEY" not in pins
    assert not is_pinned(vault_dir, "API_KEY")


def test_unpin_var_not_pinned_raises(vault_dir):
    with pytest.raises(PinError, match="is not pinned"):
        unpin_var(vault_dir, "API_KEY")


def test_list_pins_empty_when_none(vault_dir):
    assert list_pins(vault_dir) == []


def test_list_pins_multiple_keys(vault_dir):
    from envault.vault import load_vault
    variables = load_vault(vault_dir, "test-pass")
    pin_var(vault_dir, "API_KEY", variables)
    pin_var(vault_dir, "DB_URL", variables)
    pins = list_pins(vault_dir)
    assert set(pins) == {"API_KEY", "DB_URL"}


def test_is_pinned_true(vault_dir):
    from envault.vault import load_vault
    variables = load_vault(vault_dir, "test-pass")
    pin_var(vault_dir, "API_KEY", variables)
    assert is_pinned(vault_dir, "API_KEY") is True


def test_is_pinned_false(vault_dir):
    assert is_pinned(vault_dir, "API_KEY") is False


def test_assert_not_pinned_raises_when_pinned(vault_dir):
    from envault.vault import load_vault
    variables = load_vault(vault_dir, "test-pass")
    pin_var(vault_dir, "API_KEY", variables)
    with pytest.raises(PinError, match="is pinned"):
        assert_not_pinned(vault_dir, "API_KEY", action="delete")


def test_assert_not_pinned_passes_when_not_pinned(vault_dir):
    # Should not raise
    assert_not_pinned(vault_dir, "API_KEY", action="modify")
