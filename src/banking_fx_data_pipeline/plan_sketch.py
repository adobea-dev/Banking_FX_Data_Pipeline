"""A sketch of the Banking FX Data Pipeline."""

from prefect import flow, task


@task
def fetch_rates() -> list[dict]:
    """Fetch daily exchange rates from the Frankfurter API."""
    print("Fetching EUR exchange rates against USD, GBP and JPY...")
    return []


@task
def check_rates(rates: list[dict]) -> list[dict]:
    """Validate exchange-rate records."""
    print("Checking required fields, data types and positive exchange rates...")
    return rates


@task
def save_rates(rates: list[dict]) -> None:
    """Save raw and validated exchange-rate records."""
    print(f"Saving {len(rates)} exchange-rate records...")


@flow(log_prints=True)
def fx_pipeline() -> None:
    """Coordinate the FX data pipeline."""
    rates = fetch_rates()
    checked_rates = check_rates(rates)
    save_rates(checked_rates)


if __name__ == "__main__":
    fx_pipeline()
