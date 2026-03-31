from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel

from app.pipeline import build_candidate_bundles
from app.schemas import CandidateBundle, Decision, DecisionRecord
from app.storage import load_blacklist_summary, load_profit_summary, save_decision

app = FastAPI(title="AI 选品助手", version="0.1.0")


class DecisionPayload(BaseModel):
    decision: Decision
    reason: str | None = None
    decided_by: str = "api-user"


def get_candidate_bundles() -> list[CandidateBundle]:
    return build_candidate_bundles()


def get_dashboard_summary() -> dict[str, int | float]:
    candidates = get_candidate_bundles()
    decision_counts = {decision.value: 0 for decision in Decision}
    for candidate in candidates:
        if candidate.decision is not None:
            decision_counts[candidate.decision.decision.value] += 1

    profit_summary = load_profit_summary()
    blacklist_summary = load_blacklist_summary()
    return {
        "candidate_count": len(candidates),
        **decision_counts,
        "total_profit_records": int(profit_summary["total_count"]),
        "total_profit_est": profit_summary["total_profit"],
        "supplier_blacklist_count": blacklist_summary["supplier_count"],
        "category_blacklist_count": blacklist_summary["category_count"],
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/candidates")
def list_candidates() -> list[dict]:
    return [candidate.model_dump(mode="json") for candidate in get_candidate_bundles()]


@app.get("/api/summary")
def get_summary() -> dict[str, int | float]:
    return get_dashboard_summary()


@app.post("/api/candidates/{product_id}/decision")
def save_candidate_decision(product_id: str, payload: DecisionPayload) -> dict:
    candidates = {candidate.product.id: candidate for candidate in get_candidate_bundles()}
    candidate = candidates.get(product_id)
    if candidate is None:
        return {"status": "not_found", "product_id": product_id}

    record = DecisionRecord(
        product_id=product_id,
        decision=payload.decision,
        reason=payload.reason,
        decided_by=payload.decided_by,
        decided_at=datetime.now(timezone.utc),
    )
    save_decision(
        record,
        supplier_name=candidate.supplier.supplier_name if candidate.supplier else None,
        category_label=candidate.product.category_label,
        profit_est=candidate.supplier.profit_est if candidate.supplier else None,
        supplier_id=candidate.supplier.supplier_id if candidate.supplier else None,
    )

    return {
        "status": "ok",
        "record": record.model_dump(mode="json"),
    }
