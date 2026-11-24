"""Validate raw FX responses and produce trusted Silver data."""

import polars as pl

from banking_fx_data_pipeline import config

# data contract

FIELDS = {
    "date": "date",
    "base": "base",
    "quote": "quote",
    "rate": "rate",
}

KEY = ["date", "base", "quote"]  # unique key for each record


# validator
def validate_rates(payload: list[dict]) -> pl.DataFrame:
    """Validate raw FX records and return a Polars DataFrame."""

    # Check that the API response is a list
    if not isinstance(payload, list):
        raise ValueError("Expected the FX payload to be a list of records.")

    # Check that every record is a dictionary
    for row_number, record in enumerate(payload, start=1):
        if not isinstance(record, dict):
            raise ValueError(f"Row {row_number} must be a dictionary.")

        # Check that every record contains all required fields
        missing_fields = set(FIELDS) - set(record)

        if missing_fields:
            raise ValueError(
                f"Row {row_number} is missing required fields: {', '.join(sorted(missing_fields))}"
            )

    # Convert the records into a Polars DataFrame
    frame = pl.DataFrame(payload, strict=False).select(
        [pl.col(source).alias(target) for source, target in FIELDS.items()]
    )

    frame = frame.with_columns(
        [
            pl.col("date").cast(pl.String).str.to_date(format="%Y-%m-%d", strict=False),
            pl.col("base").cast(pl.String, strict=False),
            pl.col("quote").cast(pl.String, strict=False),
            pl.col("rate").cast(pl.Float64, strict=False),
        ]
    )

    # Find rows containing null values
    invalid_rows = frame.with_row_index("row_number", offset=1).filter(
        pl.any_horizontal(pl.exclude("row_number").is_null())
    )

    # Reject the batch if any invalid rows are found
    if invalid_rows.height > 0:
        row_numbers = invalid_rows["row_number"].to_list()

        raise ValueError(f"Null or invalid values found in rows: {row_numbers}")

    # Check that currencies match the project configuration
    invalid_currencies = frame.with_row_index("row_number", offset=1).filter(
        (pl.col("base") != config.BASE_CURRENCY)
        | (~pl.col("quote").is_in(config.TARGET_CURRENCIES))
    )

    if invalid_currencies.height > 0:
        row_numbers = invalid_currencies["row_number"].to_list()

        raise ValueError(f"Unexpected currency combination in rows: {row_numbers}")

    # Check that exchange rates are positive and finite
    invalid_rates = frame.with_row_index("row_number", offset=1).filter(
        (pl.col("rate") <= 0) | (~pl.col("rate").is_finite())
    )

    if invalid_rates.height > 0:
        row_numbers = invalid_rates["row_number"].to_list()

        raise ValueError(f"Invalid exchange rates in rows: {row_numbers}")

    # Check for duplicate exchange-rate records
    duplicate_rows = frame.with_row_index("row_number", offset=1).filter(
        pl.struct(KEY).is_duplicated()
    )

    if duplicate_rows.height > 0:
        row_numbers = duplicate_rows["row_number"].to_list()

        raise ValueError(f"Duplicate exchange-rate records found in rows: {row_numbers}")

    # Sort validated records by their unique key
    frame = frame.sort(KEY)
    return frame
