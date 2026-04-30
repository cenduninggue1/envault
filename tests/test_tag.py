"""Tests for envault.tag module."""

from __future__ import annotations

import pytest

from envault.tag import (
    TagError,
    add_tag,
    filter_by_tag,
    list_tags,
    remove_tag,
)
from envault.vault import init_vault, save_vault


PASSWORD = "test-secret"


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path), PASSWORD)
    save_vault(str(tmp_path), PASSWORD, {"DB_URL": "postgres://localhost", "API_KEY": "abc123"})
    return str(tmp_path)


def test_add_tag_persists(vault_dir):
    add_tag(vault_dir, PASSWORD, "DB_URL", "database")
    tags = list_tags(vault_dir, PASSWORD, "DB_URL")
    assert "database" in tags["DB_URL"]


def test_add_tag_duplicate_is_idempotent(vault_dir):
    add_tag(vault_dir, PASSWORD, "DB_URL", "database")
    add_tag(vault_dir, PASSWORD, "DB_URL", "database")
    tags = list_tags(vault_dir, PASSWORD, "DB_URL")
    assert tags["DB_URL"].count("database") == 1


def test_add_tag_unknown_variable_raises(vault_dir):
    with pytest.raises(TagError, match="not found"):
        add_tag(vault_dir, PASSWORD, "MISSING_VAR", "mytag")


def test_remove_tag(vault_dir):
    add_tag(vault_dir, PASSWORD, "API_KEY", "secret")
    remove_tag(vault_dir, PASSWORD, "API_KEY", "secret")
    tags = list_tags(vault_dir, PASSWORD, "API_KEY")
    assert tags["API_KEY"] == []


def test_remove_tag_not_present_raises(vault_dir):
    with pytest.raises(TagError, match="not found"):
        remove_tag(vault_dir, PASSWORD, "API_KEY", "nonexistent")


def test_list_tags_all(vault_dir):
    add_tag(vault_dir, PASSWORD, "DB_URL", "database")
    add_tag(vault_dir, PASSWORD, "API_KEY", "secret")
    tags = list_tags(vault_dir, PASSWORD)
    assert "DB_URL" in tags
    assert "API_KEY" in tags


def test_list_tags_excludes_deleted_variables(vault_dir):
    add_tag(vault_dir, PASSWORD, "API_KEY", "secret")
    # Remove API_KEY from vault data but keep tag entry
    from envault.vault import load_vault
    data = load_vault(vault_dir, PASSWORD)
    del data["API_KEY"]
    save_vault(vault_dir, PASSWORD, data)
    tags = list_tags(vault_dir, PASSWORD)
    assert "API_KEY" not in tags


def test_filter_by_tag_returns_matching_vars(vault_dir):
    add_tag(vault_dir, PASSWORD, "DB_URL", "infra")
    add_tag(vault_dir, PASSWORD, "API_KEY", "infra")
    results = filter_by_tag(vault_dir, PASSWORD, "infra")
    assert set(results.keys()) == {"DB_URL", "API_KEY"}


def test_filter_by_tag_no_matches_returns_empty(vault_dir):
    results = filter_by_tag(vault_dir, PASSWORD, "nonexistent")
    assert results == {}


def test_multiple_tags_on_same_variable(vault_dir):
    add_tag(vault_dir, PASSWORD, "DB_URL", "database")
    add_tag(vault_dir, PASSWORD, "DB_URL", "infra")
    tags = list_tags(vault_dir, PASSWORD, "DB_URL")
    assert "database" in tags["DB_URL"]
    assert "infra" in tags["DB_URL"]
