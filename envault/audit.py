"""Audit log for tracking vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

AUDIT_LOG_FILENAME = "audit.log"


def get_audit_log_path() -> Path:
    """Return the path to the audit log file."""
    base = Path(os.environ.get("ENVAULT_HOME", Path.home() / ".envault"))
    base.mkdir(parents=True, exist_ok=True)
    return base / AUDIT_LOG_FILENAME


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(action: str, project: Optional[str] = None, detail: Optional[str] = None) -> None:
    """Append a structured audit event to the log file."""
    entry = {
        "timestamp": _now_iso(),
        "action": action,
    }
    if project is not None:
        entry["project"] = project
    if detail is not None:
        entry["detail"] = detail

    with open(get_audit_log_path(), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def read_events(limit: int = 50) -> List[dict]:
    """Read the most recent audit events from the log."""
    path = get_audit_log_path()
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as fh:
        lines = [line.strip() for line in fh if line.strip()]
    events = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events[-limit:]


def clear_audit_log() -> None:
    """Erase all audit log entries."""
    path = get_audit_log_path()
    if path.exists():
        path.unlink()
