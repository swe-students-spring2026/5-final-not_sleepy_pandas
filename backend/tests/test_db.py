"""Tests for db.py helper functions using mongomock."""

import pytest
import mongomock

from backend.db import (
    get_collection,
    get_budgets_collection,
    get_users_collection,
    save_transaction,
)
from backend.config import MONGO_COLLECTION_NAME, BUDGETS_COLLECTION_NAME, USERS_COLLECTION_NAME


@pytest.fixture
def mongo_client(monkeypatch):
    """Single mongomock client shared across all db calls within a test."""
    client = mongomock.MongoClient()
    monkeypatch.setattr("backend.db.MongoClient", lambda *a, **kw: client)
    return client


def test_get_collection_name(mongo_client):
    assert get_collection().name == MONGO_COLLECTION_NAME


def test_get_budgets_collection_name(mongo_client):
    assert get_budgets_collection().name == BUDGETS_COLLECTION_NAME


def test_get_users_collection_name(mongo_client):
    assert get_users_collection().name == USERS_COLLECTION_NAME


def test_save_transaction_returns_inserted_id(mongo_client):
    doc = {"type": "expense", "amount": 10.0, "category": "food", "date": "2026-04-01"}
    oid = save_transaction(doc)
    assert oid is not None
    # Both calls go through the same client instance so state is shared
    result = get_collection().find_one({"_id": oid})
    assert result["category"] == "food"
    assert result["amount"] == 10.0


def test_save_transaction_rejects_non_dict(mongo_client):
    with pytest.raises(ValueError, match="must be a dictionary"):
        save_transaction([1, 2, 3])


def test_save_transaction_rejects_string(mongo_client):
    with pytest.raises(ValueError, match="must be a dictionary"):
        save_transaction("not a dict")
