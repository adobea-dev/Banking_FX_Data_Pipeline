
"""Tests for the Banking FX extraction module."""

import json
from datetime import date

import httpx
import pytest

from banking_fx_data_pipeline import extract


def test_bronze_keeps_the_original_payload(tmp_path):
    """Check that Bronze preserves the original API records."""
    payload = [
        {
            "date": "2026-11-20",
            "base": "EUR",
            "quote": "USD",
            "rate": 1.0988,
        }
    ]

    path = extract.save_bronze(payload, str(tmp_path))
    record = json.loads(path.read_text())

    assert record["payload"] == payload
    assert record["_source"] == extract.API_URL
    assert "_ingested_at" in record


def fake_answer(status_code):
    """Create a fake HTTP response for testing."""

    def fake_get(url, params, timeout):
        return httpx.Response(
            status_code,
            json={},
            request=httpx.Request("GET", url),
        )

    return fake_get


def test_a_server_error_is_temporary(monkeypatch):
    """Check that HTTP 503 raises a temporary source error."""
    monkeypatch.setattr(httpx, "get", fake_answer(503))

    with pytest.raises(extract.TemporarySourceError):
        extract.fetch_rates(date(2026, 1, 1), date(2026, 1, 3))


def test_a_bad_request_is_permanent(monkeypatch):
    """Check that HTTP 400 raises an HTTP status error."""
    monkeypatch.setattr(httpx, "get", fake_answer(400))

    with pytest.raises(httpx.HTTPStatusError):
        extract.fetch_rates(date(2026, 1, 1), date(2026, 1, 3))
