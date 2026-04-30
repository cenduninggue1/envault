"""Tests for envault.template."""

from __future__ import annotations

import pytest

from envault.template import RenderResult, TemplateError, list_placeholders, render_template

VARS = {"HOST": "localhost", "PORT": "5432", "DB": "mydb"}


def test_render_basic_substitution():
    result = render_template("Connect to {{ HOST }}:{{ PORT }}/{{ DB }}", VARS)
    assert result.output == "Connect to localhost:5432/mydb"
    assert set(result.resolved) == {"HOST", "PORT", "DB"}
    assert result.missing == []


def test_render_missing_placeholder_left_unchanged_by_default():
    result = render_template("Hello {{ NAME }}", VARS)
    assert result.output == "Hello {{ NAME }}"
    assert result.missing == ["NAME"]
    assert result.resolved == []


def test_render_strict_raises_on_missing():
    with pytest.raises(TemplateError, match="NAME"):
        render_template("Hello {{ NAME }}", VARS, strict=True)


def test_render_extra_whitespace_in_placeholder():
    result = render_template("{{  HOST  }}", VARS)
    assert result.output == "localhost"


def test_render_empty_template():
    result = render_template("", VARS)
    assert result.output == ""
    assert result.resolved == []
    assert result.missing == []


def test_render_no_placeholders():
    result = render_template("no placeholders here", VARS)
    assert result.output == "no placeholders here"
    assert result.resolved == []
    assert result.missing == []


def test_render_duplicate_placeholder_resolved_once_each_occurrence():
    result = render_template("{{ HOST }} and {{ HOST }}", VARS)
    assert result.output == "localhost and localhost"
    # resolved list records each occurrence
    assert result.resolved == ["HOST", "HOST"]


def test_render_returns_render_result_instance():
    result = render_template("{{ HOST }}", VARS)
    assert isinstance(result, RenderResult)


def test_list_placeholders_basic():
    names = list_placeholders("{{ HOST }}:{{ PORT }}/{{ DB }}")
    assert names == ["HOST", "PORT", "DB"]


def test_list_placeholders_deduplicates():
    names = list_placeholders("{{ A }} {{ B }} {{ A }}")
    assert names == ["A", "B"]


def test_list_placeholders_empty_string():
    assert list_placeholders("") == []


def test_list_placeholders_no_placeholders():
    assert list_placeholders("plain text") == []
