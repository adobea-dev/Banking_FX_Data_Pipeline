"""Central configuration for the Banking FX Data Pipeline."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Where the Bronze data will be stored.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

BRONZE_DIR = PROJECT_ROOT / (os.getenv("BRONZE_DIR") or "data/bronze")

# Currency configuration.
BASE_CURRENCY = "EUR"
TARGET_CURRENCIES = ["USD", "GBP", "JPY"]

# Historical extraction settings.
FIRST_LOAD_DAYS = 30
OVERLAP_DAYS = 3
