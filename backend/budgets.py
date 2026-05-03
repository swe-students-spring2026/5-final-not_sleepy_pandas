"""Budget endpoints — CRUD and spending-vs-limit status."""

import datetime
import re

from bson import ObjectId
from flask import Blueprint, jsonify, request

_MONTH_RE = re.compile(r"^\d{4}-\d{2}$")

from backend.db import get_budgets_collection, get_collection

budgets_bp = Blueprint("budgets", __name__)

_REQUIRED = ["category", "limit", "month"]


def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


@budgets_bp.route("", methods=["POST"])
def create_budget():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be JSON"}), 400

    for field in _REQUIRED:
        if field not in data or data[field] in [None, ""]:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    if not isinstance(data["limit"], (int, float)) or data["limit"] <= 0:
        return jsonify({"error": "limit must be a positive number"}), 400

    budgets = get_budgets_collection()
    result = budgets.insert_one(
        {
            "category": data["category"],
            "limit": float(data["limit"]),
            "month": data["month"],
            "created_at": datetime.datetime.utcnow().isoformat(),
        }
    )
    return jsonify({"message": "Budget created successfully", "budget_id": str(result.inserted_id)}), 201


@budgets_bp.route("", methods=["GET"])
def get_budgets():
    budgets = get_budgets_collection()
    result = [_serialize(b) for b in budgets.find()]
    return jsonify({"budgets": result}), 200


@budgets_bp.route("/<budget_id>", methods=["GET"])
def get_budget(budget_id):
    if not ObjectId.is_valid(budget_id):
        return jsonify({"error": "Invalid budget id"}), 400

    budgets = get_budgets_collection()
    doc = budgets.find_one({"_id": ObjectId(budget_id)})
    if not doc:
        return jsonify({"error": "Budget not found"}), 404

    return jsonify({"budget": _serialize(doc)}), 200


@budgets_bp.route("/<budget_id>", methods=["PUT"])
def update_budget(budget_id):
    if not ObjectId.is_valid(budget_id):
        return jsonify({"error": "Invalid budget id"}), 400

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be JSON"}), 400

    for field in _REQUIRED:
        if field not in data or data[field] in [None, ""]:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    if not isinstance(data["limit"], (int, float)) or data["limit"] <= 0:
        return jsonify({"error": "limit must be a positive number"}), 400

    budgets = get_budgets_collection()
    result = budgets.update_one(
        {"_id": ObjectId(budget_id)},
        {"$set": {"category": data["category"], "limit": float(data["limit"]), "month": data["month"]}},
    )
    if result.matched_count == 0:
        return jsonify({"error": "Budget not found"}), 404

    return jsonify({"message": "Budget updated successfully"}), 200


@budgets_bp.route("/<budget_id>", methods=["DELETE"])
def delete_budget(budget_id):
    if not ObjectId.is_valid(budget_id):
        return jsonify({"error": "Invalid budget id"}), 400

    budgets = get_budgets_collection()
    result = budgets.delete_one({"_id": ObjectId(budget_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Budget not found"}), 404

    return jsonify({"message": "Budget deleted successfully"}), 200


@budgets_bp.route("/status", methods=["GET"])
def budget_status():
    """Compare actual spending against each budget limit for its month.

    Optional query parameter ?month=YYYY-MM narrows both the budget lookup and
    the aggregation pipeline to a single month, avoiding a full-collection scan.
    """
    month = request.args.get("month")
    if month and not _MONTH_RE.match(month):
        return jsonify({"error": "month must be in YYYY-MM format"}), 400

    budgets_col = get_budgets_collection()
    transactions_col = get_collection()

    budget_query = {"month": month} if month else {}
    all_budgets = list(budgets_col.find(budget_query))
    if not all_budgets:
        return jsonify({"status": []}), 200

    if month:
        # Targeted pipeline: restrict to the requested month before grouping so
        # MongoDB can use a date-prefix index and skip unrelated documents.
        pipeline = [
            {"$match": {"type": "expense", "date": {"$regex": f"^{month}"}}},
            {"$group": {"_id": "$category", "total_spent": {"$sum": "$amount"}}},
        ]
        spent_map = {row["_id"]: row["total_spent"] for row in transactions_col.aggregate(pipeline)}
    else:
        pipeline = [
            {"$match": {"type": "expense"}},
            {
                "$project": {
                    "category": 1,
                    "amount": 1,
                    "month": {"$substr": ["$date", 0, 7]},
                }
            },
            {
                "$group": {
                    "_id": {"month": "$month", "category": "$category"},
                    "total_spent": {"$sum": "$amount"},
                }
            },
        ]
        spent_map = {}
        for row in transactions_col.aggregate(pipeline):
            key = (row["_id"]["month"], row["_id"]["category"])
            spent_map[key] = row["total_spent"]

    result = []
    for b in all_budgets:
        spent = spent_map.get(b["category"] if month else (b["month"], b["category"]), 0.0)
        limit = b["limit"]
        result.append(
            {
                "budget_id": str(b["_id"]),
                "category": b["category"],
                "month": b["month"],
                "limit": limit,
                "spent": spent,
                "remaining": round(limit - spent, 2),
                "over_budget": spent > limit,
            }
        )

    return jsonify({"status": result}), 200
