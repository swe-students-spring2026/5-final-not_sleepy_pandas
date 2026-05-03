"""Database helpers for accessing MongoDB collections."""

from pymongo import MongoClient
from backend.config import (
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_COLLECTION_NAME,
    BUDGETS_COLLECTION_NAME,
    USERS_COLLECTION_NAME,
)

def get_collection():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    return db[MONGO_COLLECTION_NAME]


def get_users_collection():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    return db["users"]


def get_budgets_collection():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    return db["budgets"]

def get_budgets_collection():
    """Get the MongoDB collection for budgets."""
    client = MongoClient(MONGO_URI)
    return client[MONGO_DB_NAME][BUDGETS_COLLECTION_NAME]


def get_users_collection():
    """Get the MongoDB collection for users."""
    client = MongoClient(MONGO_URI)
    return client[MONGO_DB_NAME][USERS_COLLECTION_NAME]


def save_transaction(transaction: dict):
    """
    Save a transaction document to MongoDB.

    Args:
        transaction: A dictionary containing transaction data.

    Returns:
        The inserted MongoDB document ID.
    """
    if not isinstance(transaction, dict):
        raise ValueError("transaction must be a dictionary")

    collection = get_collection()
    result = collection.insert_one(transaction)
    return result.inserted_id
