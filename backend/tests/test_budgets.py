"""Tests for budget endpoints — @kelaier."""

from bson import ObjectId

from backend.app import create_app


class FakeInsertResult:
    def __init__(self, oid=None):
        self.inserted_id = oid or ObjectId()


class FakeUpdateResult:
    def __init__(self, matched):
        self.matched_count = matched


class FakeDeleteResult:
    def __init__(self, deleted):
        self.deleted_count = deleted


class FakeBudgetsCollection:
    def __init__(self):
        self._oid = ObjectId()
        self._doc = {
            "_id": self._oid,
            "category": "food",
            "limit": 300.0,
            "month": "2026-04",
            "created_at": "2026-04-01T00:00:00",
        }

    def find(self, query=None):
        if query and query.get("month") and query["month"] != self._doc["month"]:
            return []
        return [dict(self._doc)]

    def find_one(self, query):
        if query.get("_id") == self._oid:
            return dict(self._doc)
        return None

    def insert_one(self, doc):
        return FakeInsertResult(self._oid)

    def update_one(self, query, update):
        if query.get("_id") == self._oid:
            self._doc.update(update["$set"])
            return FakeUpdateResult(1)
        return FakeUpdateResult(0)

    def delete_one(self, query):
        if query.get("_id") == self._oid:
            return FakeDeleteResult(1)
        return FakeDeleteResult(0)


class FakeTransactionsCollection:
    def aggregate(self, pipeline):
        return [
            {"_id": {"month": "2026-04", "category": "food"}, "total_spent": 120.0}
        ]


def _patch(monkeypatch, budgets=None, transactions=None):
    b = budgets or FakeBudgetsCollection()
    t = transactions or FakeTransactionsCollection()
    monkeypatch.setattr("backend.budgets.get_budgets_collection", lambda: b)
    monkeypatch.setattr("backend.budgets.get_collection", lambda: t)
    return b


def _app():
    return create_app()


def test_create_budget_success(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().post(
        "/api/budgets",
        json={"category": "food", "limit": 300, "month": "2026-04"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["message"] == "Budget created successfully"


def test_create_budget_missing_field(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().post("/api/budgets", json={"category": "food", "limit": 300})
    assert resp.status_code == 400
    assert "Missing required field" in resp.get_json()["error"]


def test_create_budget_invalid_limit(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().post(
        "/api/budgets",
        json={"category": "food", "limit": -10, "month": "2026-04"},
    )
    assert resp.status_code == 400
    assert "positive" in resp.get_json()["error"]


def test_create_budget_bad_json(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().post("/api/budgets", data="not-json", content_type="application/json")
    assert resp.status_code == 400


def test_get_budgets(monkeypatch):
    fake = _patch(monkeypatch)
    resp = _app().test_client().get("/api/budgets")
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data["budgets"]) == 1
    assert data["budgets"][0]["category"] == "food"


def test_get_budget_success(monkeypatch):
    fake = _patch(monkeypatch)
    resp = _app().test_client().get(f"/api/budgets/{fake._oid}")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["budget"]["month"] == "2026-04"


def test_get_budget_not_found(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().get(f"/api/budgets/{ObjectId()}")
    assert resp.status_code == 404


def test_get_budget_invalid_id(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().get("/api/budgets/bad-id")
    assert resp.status_code == 400


def test_update_budget_success(monkeypatch):
    fake = _patch(monkeypatch)
    resp = _app().test_client().put(
        f"/api/budgets/{fake._oid}",
        json={"category": "food", "limit": 400, "month": "2026-04"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "Budget updated successfully"


def test_update_budget_not_found(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().put(
        f"/api/budgets/{ObjectId()}",
        json={"category": "food", "limit": 400, "month": "2026-04"},
    )
    assert resp.status_code == 404


def test_update_budget_invalid_limit(monkeypatch):
    fake = _patch(monkeypatch)
    resp = _app().test_client().put(
        f"/api/budgets/{fake._oid}",
        json={"category": "food", "limit": 0, "month": "2026-04"},
    )
    assert resp.status_code == 400


def test_update_budget_bad_json(monkeypatch):
    fake = _patch(monkeypatch)
    resp = _app().test_client().put(
        f"/api/budgets/{fake._oid}", data="not-json", content_type="application/json"
    )
    assert resp.status_code == 400


def test_delete_budget_success(monkeypatch):
    fake = _patch(monkeypatch)
    resp = _app().test_client().delete(f"/api/budgets/{fake._oid}")
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "Budget deleted successfully"


def test_delete_budget_not_found(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().delete(f"/api/budgets/{ObjectId()}")
    assert resp.status_code == 404


def test_delete_budget_invalid_id(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().delete("/api/budgets/bad-id")
    assert resp.status_code == 400


def test_budget_status(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().get("/api/budgets/status")
    data = resp.get_json()
    assert resp.status_code == 200
    row = data["status"][0]
    assert row["category"] == "food"
    assert row["spent"] == 120.0
    assert row["remaining"] == 180.0
    assert row["over_budget"] is False


def test_budget_status_empty(monkeypatch):
    class EmptyBudgets:
        def find(self, query=None):
            return []

    monkeypatch.setattr("backend.budgets.get_budgets_collection", lambda: EmptyBudgets())
    monkeypatch.setattr("backend.budgets.get_collection", lambda: FakeTransactionsCollection())
    resp = _app().test_client().get("/api/budgets/status")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == []


def test_budget_status_over_budget(monkeypatch):
    class OverSpentTransactions:
        def aggregate(self, pipeline):
            return [{"_id": {"month": "2026-04", "category": "food"}, "total_spent": 500.0}]

    _patch(monkeypatch, transactions=OverSpentTransactions())
    resp = _app().test_client().get("/api/budgets/status")
    row = resp.get_json()["status"][0]
    assert row["over_budget"] is True
    assert row["remaining"] == -200.0


def test_budget_status_with_month_filter(monkeypatch):
    # Targeted pipeline returns category as the _id (not a nested month+category dict)
    class MonthScopedTransactions:
        def aggregate(self, pipeline):
            return [{"_id": "food", "total_spent": 120.0}]

    _patch(monkeypatch, transactions=MonthScopedTransactions())
    resp = _app().test_client().get("/api/budgets/status?month=2026-04")
    data = resp.get_json()
    assert resp.status_code == 200
    row = data["status"][0]
    assert row["category"] == "food"
    assert row["spent"] == 120.0
    assert row["remaining"] == 180.0
    assert row["over_budget"] is False


def test_budget_status_month_no_matching_budgets(monkeypatch):
    _patch(monkeypatch)
    # Requesting a month that has no budgets stored
    resp = _app().test_client().get("/api/budgets/status?month=2025-01")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == []


def test_budget_status_invalid_month_format(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().get("/api/budgets/status?month=April-2026")
    assert resp.status_code == 400
    assert "YYYY-MM" in resp.get_json()["error"]


# --- coverage gap: non-dict JSON bodies ---

def test_create_budget_json_array(monkeypatch):
    # Valid JSON but not a dict — hits the isinstance check on line 27
    _patch(monkeypatch)
    resp = _app().test_client().post("/api/budgets", json=[1, 2, 3])
    assert resp.status_code == 400
    assert "JSON" in resp.get_json()["error"]


def test_update_budget_json_array(monkeypatch):
    # Valid JSON but not a dict — hits the isinstance check in update_budget
    fake = _patch(monkeypatch)
    resp = _app().test_client().put(f"/api/budgets/{fake._oid}", json=[1, 2, 3])
    assert resp.status_code == 400
    assert "JSON" in resp.get_json()["error"]


# --- coverage gap: update_budget missing id / missing fields ---

def test_update_budget_invalid_id(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().put(
        "/api/budgets/not-an-objectid",
        json={"category": "food", "limit": 100, "month": "2026-04"},
    )
    assert resp.status_code == 400
    assert "Invalid budget id" in resp.get_json()["error"]


def test_update_budget_missing_field(monkeypatch):
    fake = _patch(monkeypatch)
    resp = _app().test_client().put(
        f"/api/budgets/{fake._oid}",
        json={"category": "food", "limit": 100},  # missing "month"
    )
    assert resp.status_code == 400
    assert "Missing required field" in resp.get_json()["error"]


# --- additional edge-case tests ---

def test_create_budget_null_field(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().post(
        "/api/budgets",
        json={"category": None, "limit": 100, "month": "2026-04"},
    )
    assert resp.status_code == 400
    assert "Missing required field" in resp.get_json()["error"]


def test_create_budget_empty_string_field(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().post(
        "/api/budgets",
        json={"category": "", "limit": 100, "month": "2026-04"},
    )
    assert resp.status_code == 400
    assert "Missing required field" in resp.get_json()["error"]


def test_create_budget_limit_is_string(monkeypatch):
    _patch(monkeypatch)
    resp = _app().test_client().post(
        "/api/budgets",
        json={"category": "food", "limit": "lots", "month": "2026-04"},
    )
    assert resp.status_code == 400
    assert "positive" in resp.get_json()["error"]


def test_get_budgets_empty(monkeypatch):
    class EmptyBudgets:
        def find(self, query=None):
            return []

    monkeypatch.setattr("backend.budgets.get_budgets_collection", lambda: EmptyBudgets())
    resp = _app().test_client().get("/api/budgets")
    assert resp.status_code == 200
    assert resp.get_json()["budgets"] == []


def test_budget_status_no_spending(monkeypatch):
    # Budget exists but no transactions match — spent should default to 0
    class NoTransactions:
        def aggregate(self, pipeline):
            return []

    _patch(monkeypatch, transactions=NoTransactions())
    resp = _app().test_client().get("/api/budgets/status")
    row = resp.get_json()["status"][0]
    assert row["spent"] == 0.0
    assert row["remaining"] == 300.0
    assert row["over_budget"] is False


def test_budget_status_month_filter_no_spending(monkeypatch):
    # Month-scoped query with no matching transactions — spent defaults to 0
    class NoTransactions:
        def aggregate(self, pipeline):
            return []

    _patch(monkeypatch, transactions=NoTransactions())
    resp = _app().test_client().get("/api/budgets/status?month=2026-04")
    row = resp.get_json()["status"][0]
    assert row["spent"] == 0.0
    assert row["remaining"] == 300.0


def test_budget_status_month_filter_over_budget(monkeypatch):
    class OverSpentMonth:
        def aggregate(self, pipeline):
            return [{"_id": "food", "total_spent": 450.0}]

    _patch(monkeypatch, transactions=OverSpentMonth())
    resp = _app().test_client().get("/api/budgets/status?month=2026-04")
    row = resp.get_json()["status"][0]
    assert row["over_budget"] is True
    assert row["remaining"] == -150.0
