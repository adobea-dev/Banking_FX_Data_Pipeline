# Pipeline Plan — Banking FX Data Pipeline

## Source

- **What:** Daily foreign-exchange reference rates for EUR against USD, GBP and JPY.
- **Where:** Frankfurter API — https://api.frankfurter.dev/v2/rates
- **Format:** JSON array containing individual records.
- **Authentication:** No API key required.
- **Terms:** Check the provider's usage and attribution terms before wider or commercial use.

## Record Key

- One record = one base currency, one target currency and one observation date.
- **Key:** `base + quote + date`
- Example: `EUR + GBP + 2026-11-18`

## Data Contract (What Valid Means)

- **Required fields:** `date`, `base`, `quote`, `rate`.
- **Types:** date, string, string, numeric.
- **Validation rules:**
  1. Date must be present and follow a valid date format.
  2. Base and quote currency codes must be present and valid three-letter currency codes.
  3. Exchange rate must be numeric, finite and greater than zero.
  4. No duplicate `base + quote + date` combinations.
  5. Returned currencies must match the currencies requested.

## Layers

- **Bronze:** Preserve the raw JSON response exactly as received, together with retrieval timestamp and API request details.
- **Silver:** Store validated, typed records with one row per base currency, target currency and observation date.
- **Gold:** Calculate daily exchange-rate changes and percentage movements for each target currency against the previous available observation.

## Cadence

- The source provides daily reference-rate observations.
- Run the pipeline once daily.
- Re-read the most recent three days to accommodate possible revisions to recent observations.
- Use the record key to identify existing records and prevent duplicates.

## What Could Go Wrong

1. API unavailable or slow → retry the request and retain the last successful data.
2. A field is renamed or removed → reject the batch and preserve the Bronze response for investigation.
3. A currency is missing → flag the incomplete batch rather than silently treating the missing rate as zero.
4. Duplicate records → detect using the record key.
5. Historical rates are revised → reprocess the affected recent dates.
6. Unexpected response structure → flag schema drift and investigate before loading.

## Business Purpose

The pipeline provides a consistent historical record of foreign-exchange reference rates that can support treasury monitoring, currency movement analysis and financial reporting.