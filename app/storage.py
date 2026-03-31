from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from app.schemas import Decision, DecisionRecord

DB_PATH = Path("data") / "app.db"


def ensure_storage() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS decision_records (
                product_id TEXT PRIMARY KEY,
                decision TEXT NOT NULL,
                reason TEXT,
                decided_by TEXT NOT NULL,
                decided_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS blacklist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_type TEXT NOT NULL,
                target_value TEXT NOT NULL,
                source_product_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(target_type, target_value)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS profit_records (
                product_id TEXT PRIMARY KEY,
                supplier_id TEXT NOT NULL,
                profit_est REAL NOT NULL,
                recorded_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    ensure_storage()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def save_decision(record: DecisionRecord, supplier_name: str | None = None, category_label: str | None = None, profit_est: float | None = None, supplier_id: str | None = None) -> None:
    with _connect() as connection:
        previous_row = connection.execute(
            "SELECT decision FROM decision_records WHERE product_id = ?",
            (record.product_id,),
        ).fetchone()
        previous_decision = Decision(previous_row["decision"]) if previous_row is not None else None

        connection.execute(
            """
            INSERT INTO decision_records (product_id, decision, reason, decided_by, decided_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(product_id) DO UPDATE SET
                decision = excluded.decision,
                reason = excluded.reason,
                decided_by = excluded.decided_by,
                decided_at = excluded.decided_at
            """,
            (
                record.product_id,
                record.decision.value,
                record.reason,
                record.decided_by,
                record.decided_at.isoformat(),
            ),
        )

        if previous_decision == Decision.BLACKLISTED and record.decision != Decision.BLACKLISTED:
            if supplier_name:
                _remove_blacklist(connection, "supplier", supplier_name)
            if category_label:
                _remove_blacklist(connection, "category", category_label)

        if previous_decision == Decision.APPROVED and record.decision != Decision.APPROVED:
            connection.execute("DELETE FROM profit_records WHERE product_id = ?", (record.product_id,))

        if record.decision == Decision.BLACKLISTED:
            if supplier_name:
                _upsert_blacklist(connection, "supplier", supplier_name, record.product_id)
            if category_label:
                _upsert_blacklist(connection, "category", category_label, record.product_id)

        if record.decision == Decision.APPROVED and supplier_id and profit_est is not None:
            connection.execute(
                """
                INSERT INTO profit_records (product_id, supplier_id, profit_est, recorded_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(product_id) DO UPDATE SET
                    supplier_id = excluded.supplier_id,
                    profit_est = excluded.profit_est,
                    recorded_at = excluded.recorded_at
                """,
                (
                    record.product_id,
                    supplier_id,
                    profit_est,
                    record.decided_at.isoformat(),
                ),
            )


def _upsert_blacklist(connection: sqlite3.Connection, target_type: str, target_value: str, product_id: str) -> None:
    connection.execute(
        """
        INSERT INTO blacklist_items (target_type, target_value, source_product_id, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(target_type, target_value) DO UPDATE SET
            source_product_id = excluded.source_product_id,
            created_at = excluded.created_at
        """,
        (target_type, target_value, product_id, datetime.now(timezone.utc).isoformat()),
    )


def _remove_blacklist(connection: sqlite3.Connection, target_type: str, target_value: str) -> None:
    connection.execute(
        "DELETE FROM blacklist_items WHERE target_type = ? AND target_value = ?",
        (target_type, target_value),
    )


def load_decisions() -> dict[str, DecisionRecord]:
    with _connect() as connection:
        rows = connection.execute(
            "SELECT product_id, decision, reason, decided_by, decided_at FROM decision_records"
        ).fetchall()

    return {
        row["product_id"]: DecisionRecord(
            product_id=row["product_id"],
            decision=Decision(row["decision"]),
            reason=row["reason"],
            decided_by=row["decided_by"],
            decided_at=datetime.fromisoformat(row["decided_at"]),
        )
        for row in rows
    }


def load_blacklist() -> dict[str, set[str]]:
    with _connect() as connection:
        rows = connection.execute("SELECT target_type, target_value FROM blacklist_items").fetchall()

    blacklist: dict[str, set[str]] = {"supplier": set(), "category": set()}
    for row in rows:
        blacklist.setdefault(row["target_type"], set()).add(row["target_value"])
    return blacklist


def load_profit_summary() -> dict[str, float]:
    with _connect() as connection:
        row = connection.execute(
            "SELECT COUNT(*) AS total_count, COALESCE(SUM(profit_est), 0) AS total_profit FROM profit_records"
        ).fetchone()

    return {
        "total_count": float(row["total_count"]),
        "total_profit": float(row["total_profit"]),
    }


def load_blacklist_summary() -> dict[str, int]:
    blacklist = load_blacklist()
    return {
        "supplier_count": len(blacklist.get("supplier", set())),
        "category_count": len(blacklist.get("category", set())),
    }
