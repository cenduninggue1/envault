"""Tests for envault/audit.py"""

import json
import os
import pytest
from pathlib import Path

from envault.audit import (
    record_event,
    read_events,
    clear_log,
    format_event,
    AUDIT_LOG_FILENAME,
)


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


def test_record_event_creates_log_file(tmp_dir):
    record_event(tmp_dir, action="init")
    log_path = Path(tmp_dir) / AUDIT_LOG_FILENAME
    assert log_path.exists()


def test_record_event_writes_valid_json(tmp_dir):
    record_event(tmp_dir, action="set", key="API_KEY")
    log_path = Path(tmp_dir) / AUDIT_LOG_FILENAME
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["action"] == "set"
    assert event["key"] == "API_KEY"


def test_record_multiple_events(tmp_dir):
    record_event(tmp_dir, action="set", key="FOO")
    record_event(tmp_dir, action="get", key="FOO")
    record_event(tmp_dir, action="delete", key="FOO")
    events = read_events(tmp_dir)
    assert len(events) == 3
    assert [e["action"] for e in events] == ["set", "get", "delete"]


def test_read_events_empty_when_no_log(tmp_dir):
    events = read_events(tmp_dir)
    assert events == []


def test_event_contains_timestamp(tmp_dir):
    record_event(tmp_dir, action="init")
    events = read_events(tmp_dir)
    assert "timestamp" in events[0]
    assert events[0]["timestamp"].endswith("+00:00")


def test_event_user_override(tmp_dir):
    record_event(tmp_dir, action="set", key="X", user="alice")
    events = read_events(tmp_dir)
    assert events[0]["user"] == "alice"


def test_clear_log_removes_file(tmp_dir):
    record_event(tmp_dir, action="init")
    clear_log(tmp_dir)
    log_path = Path(tmp_dir) / AUDIT_LOG_FILENAME
    assert not log_path.exists()


def test_clear_log_no_error_if_missing(tmp_dir):
    clear_log(tmp_dir)  # should not raise


def test_format_event_basic():
    event = {
        "timestamp": "2024-01-01T00:00:00+00:00",
        "action": "set",
        "user": "bob",
        "key": "SECRET",
        "details": None,
    }
    result = format_event(event)
    assert "set" in result
    assert "bob" in result
    assert "SECRET" in result


def test_format_event_with_details():
    event = {
        "timestamp": "2024-01-01T00:00:00+00:00",
        "action": "export",
        "user": "ci",
        "key": None,
        "details": "format=dotenv",
    }
    result = format_event(event)
    assert "format=dotenv" in result
