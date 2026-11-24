"""Tests for the FX data validation module."""

import polars as pl
import pytest

from banking_fx_data_pipeline.validate import validate_rates


def make_payload():
    """Create a sample of valid FX records."""
    return [
        {
            "date": "2026-11-20",
            "base": "EUR",
            "quote": "USD",
            "rate": 1.0988,
        },
        {
            "date": "2026-11-20",
            "base": "EUR",
            "quote": "GBP",
            "rate": 0.8335,
        },
        {
            "date": "2026-11-20",
            "base": "EUR",
            "quote": "JPY",
            "rate": 175.25,
        },
    ]


def test_valid_payload_returns_silver_dataframe():
    """Check that valid FX records become a correctly typed DataFrame."""

    payload = make_payload()

    result = validate_rates(payload)

    assert isinstance(result, pl.DataFrame)
    assert result.height == 3
    assert result.columns == ["date", "base", "quote", "rate"]

    assert result.schema == {
        "date": pl.Date,
        "base": pl.String,
        "quote": pl.String,
        "rate": pl.Float64,
    }


def test_zero_exchange_rate_is_rejected():
    """Check that an exchange rate of zero is rejected."""

    payload = make_payload()
    payload[0]["rate"] = 0

    with pytest.raises(ValueError, match="Invalid exchange rates"):
        validate_rates(payload)


def test_unexpected_currency_is_rejected():
    """Check that an unapproved quote currency is rejected."""

    payload = make_payload()
    payload[0]["quote"] = "CAD"

    with pytest.raises(ValueError, match="Unexpected currency combination"):
        validate_rates(payload)


def test_duplicate_exchange_rate_is_rejected():
    """Check that duplicate exchange-rate records are rejected."""

    payload = make_payload()

    # Add a copy of the first record
    payload.append(payload[0].copy())

    with pytest.raises(
        ValueError,
        match="Duplicate exchange-rate records found",
    ):
        validate_rates(payload)


def test_missing_required_field_is_rejected():
    """Check that records missing required fields are rejected."""

    payload = make_payload()

    del payload[0]["rate"]

    with pytest.raises(ValueError, match="missing required fields"):
        validate_rates(payload)


def test_invalid_date_is_rejected():
    """Check that an invalid date is rejected."""

    payload = make_payload()
    payload[0]["date"] = "not-a-date"

    with pytest.raises(ValueError, match="Null or invalid values"):
        validate_rates(payload)
