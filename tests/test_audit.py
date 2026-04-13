"""Tests for envault.audit module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envault.audit import log_event, read_events, clear_audit_log, get_audit_log_path


@pytest.fixture(autouse=True)
def tmp_audit_home(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_HOME", str(tmp_path))
    yield tmp_path


def test_log_event_creates_file(tmp_audit_home):
    log_event("set", project="myapp")
    assert get_audit_log_path().exists()


def test_log_event_writes_valid_json(tmp_audit_home):
    log_event("set", project="myapp", detail="KEY=value")
    path = get_audit_log_path()
    line = path.read_text().strip()
    data = json.loads(line)
    assert data["action"] == "set"
    assert data["project"] == "myapp"
    assert data["detail"] == "KEY=value"
    assert "timestamp" in data


def test_log_event_without_optional_fields(tmp_audit_home):
    log_event("unlock")
    data = json.loads(get_audit_log_path().read_text().strip())
    assert "project" not in data
    assert "detail" not in data


def test_read_events_returns_list(tmp_audit_home):
    for i in range(5):
        log_event("set", project=f"proj{i}")
    events = read_events(limit=10)
    assert len(events) == 5
    assert all(isinstance(e, dict) for e in events)


def test_read_events_respects_limit(tmp_audit_home):
    for i in range(10):
        log_event("set", project=f"proj{i}")
    events = read_events(limit=3)
    assert len(events) == 3


def test_read_events_empty_when_no_log(tmp_audit_home):
    assert read_events() == []


def test_clear_audit_log_removes_file(tmp_audit_home):
    log_event("set", project="alpha")
    assert get_audit_log_path().exists()
    clear_audit_log()
    assert not get_audit_log_path().exists()


def test_clear_audit_log_noop_when_missing(tmp_audit_home):
    # Should not raise
    clear_audit_log()
