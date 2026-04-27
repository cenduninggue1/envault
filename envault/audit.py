"""Audit log for tracking vault access and modifications."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_LOG_FILENAME = ".envault_audit.log"


def _get_log_path(vault_dir: str) -> Path:
    return Path(vault_dir) / AUDIT_LOG_FILENAME


def record_event(
    vault_dir: str,
    action: str,
    key: Optional[str] = None,
    user: Optional[str] = None,
    details: Optional[str] = None,
) -> None:
    """Append a structured audit event to the log file."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "user": user or os.environ.get("USER", "unknown"),
        "key": key,
        "details": details,
    }
    log_path = _get_log_path(vault_dir)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def read_events(vault_dir: str) -> list[dict]:
    """Read all audit events from the log file."""
    log_path = _get_log_path(vault_dir)
    if not log_path.exists():
        return []
    events = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


def clear_log(vault_dir: str) -> None:
    """Remove the audit log file."""
    log_path = _get_log_path(vault_dir)
    if log_path.exists():
        log_path.unlink()


def format_event(event: dict) -> str:
    """Return a human-readable string for a single audit event."""
    ts = event.get("timestamp", "unknown")
    action = event.get("action", "unknown")
    user = event.get("user", "unknown")
    key = event.get("key")
    details = event.get("details")
    parts = [f"[{ts}] {action} by {user}"]
    if key:
        parts.append(f"key={key}")
    if details:
        parts.append(details)
    return " | ".join(parts)
