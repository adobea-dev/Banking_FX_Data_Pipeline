
"""Extract exchange rates and preserve the original response in Bronze."""

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx

from banking_fx_data_pipeline import config

API_URL = "https://api.frankfurter.dev/v2/rates"
class TemporarySourceError(RuntimeError):
    """The data source failed in a way that might succeed if we try again."""


def fetch_rates(start_date, end_date) -> list[dict]:
    """Fetch exchange rates from Frankfurter without transforming the response."""

    params = {
        "base": config.BASE_CURRENCY,
        "quotes": ",".join(config.TARGET_CURRENCIES),
        "from": start_date.isoformat(),
        "to": end_date.isoformat(),
    }

    try:
        response = httpx.get(API_URL, params=params, timeout=30)

    except httpx.TransportError as error:
        raise TemporarySourceError(
            f"Could not reach Frankfurter: {error}"
        ) from error

    if response.status_code == 429 or response.status_code >= 500:
        raise TemporarySourceError(
            f"Frankfurter answered {response.status_code}. Try later."
        )

    response.raise_for_status()

    return response.json()


def save_bronze(payload: list[dict], bronze_dir: str) -> Path:
    """Save the original API response with its source and ingestion time."""

    now = datetime.now(UTC)

    folder = (
        Path(bronze_dir)
        / f"ingest_date={now.date()}" #create a folder for the current date
    )

    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}.json" #create a unique filename for the JSON file for every extraction
    path = folder / filename

    record = {
        "_source": API_URL,
        "_ingested_at": now.isoformat(),
        "payload": payload,
    }

    path.write_text(json.dumps(record, indent=2))

    return path
