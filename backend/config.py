"""Application configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "money_tracker")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "transactions")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-prod")
