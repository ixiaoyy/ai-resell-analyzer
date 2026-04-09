from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.schemas import Decision, DecisionRecord
from app.storage import load_blacklist, load_blacklist_summary, load_decisions, load_profit_summary, save_decision



def _record(product_id: str, decision: Decision, *, reason: str | None = None) -> DecisionRecord:
    return DecisionRecord(
        product_id=product_id,
        decision=decision,
        reason=reason,
        decided_by="tester",
        decided_at=datetime(2026, 4, 9, 6, 0, tzinfo=timezone.utc),
    )



def test_save_decision_persists_approval_and_profit(monkeypatch: object, tmp_path: Path) -> None:
    from app import storage

    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "app.db")

    save_decision(
        _record("p-1", Decision.APPROVED, reason="looks good"),
        supplier_name="supplier-a",
        category_label="home",
        profit_est=12.5,
        supplier_id="s-1",
    )

    decisions = load_decisions()
    assert decisions["p-1"].decision is Decision.APPROVED
    assert decisions["p-1"].reason == "looks good"

    profit_summary = load_profit_summary()
    assert profit_summary["total_count"] == 1.0
    assert profit_summary["total_profit"] == 12.5

    blacklist_summary = load_blacklist_summary()
    assert blacklist_summary == {"supplier_count": 0, "category_count": 0}



def test_save_decision_blacklists_and_then_removes_entries(monkeypatch: object, tmp_path: Path) -> None:
    from app import storage

    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "app.db")

    save_decision(
        _record("p-2", Decision.BLACKLISTED, reason="bad supplier"),
        supplier_name="supplier-b",
        category_label="digital",
        supplier_id="s-2",
    )

    blacklist = load_blacklist()
    assert blacklist["supplier"] == {"supplier-b"}
    assert blacklist["category"] == {"digital"}

    save_decision(
        _record("p-2", Decision.SKIPPED, reason="re-evaluated"),
        supplier_name="supplier-b",
        category_label="digital",
        supplier_id="s-2",
    )

    blacklist = load_blacklist()
    assert blacklist["supplier"] == set()
    assert blacklist["category"] == set()



def test_save_decision_removes_profit_when_approval_is_reverted(monkeypatch: object, tmp_path: Path) -> None:
    from app import storage

    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "app.db")

    save_decision(
        _record("p-3", Decision.APPROVED),
        supplier_name="supplier-c",
        category_label="home",
        profit_est=8.0,
        supplier_id="s-3",
    )
    save_decision(
        _record("p-3", Decision.BLACKLISTED),
        supplier_name="supplier-c",
        category_label="home",
        supplier_id="s-3",
    )

    profit_summary = load_profit_summary()
    assert profit_summary["total_count"] == 0.0
    assert profit_summary["total_profit"] == 0.0

    blacklist = load_blacklist()
    assert blacklist["supplier"] == {"supplier-c"}
    assert blacklist["category"] == {"home"}
