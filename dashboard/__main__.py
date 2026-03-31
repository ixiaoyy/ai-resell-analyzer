from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("data/dashboard")
DEFAULT_DECISION = "pending"
PRIORITY_SCORES = {
    "high": 85.0,
    "medium": 60.0,
}


class DashboardError(Exception):
    """Raised when dashboard input or output is invalid."""


class DashboardAggregator:
    def build_rows(
        self,
        analyzed_products: list[dict[str, Any]],
        matched_suppliers: list[dict[str, Any]],
        copydrafts: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        supplier_map = {str(item["product_id"]): item for item in matched_suppliers}
        copy_map = {str(item["product_id"]): item for item in copydrafts}

        rows: list[dict[str, Any]] = []
        for analyzed_product in analyzed_products:
            self._validate_analyzed_product(analyzed_product)
            product_id = str(analyzed_product["id"])
            supplier = supplier_map.get(product_id)
            copydraft = copy_map.get(product_id)

            if supplier is None:
                raise DashboardError(f"Missing matched supplier for product_id: {product_id}")
            if copydraft is None:
                raise DashboardError(f"Missing copy draft for product_id: {product_id}")

            self._validate_matched_supplier(supplier)
            self._validate_copydraft(copydraft)
            rows.append(self._build_row(analyzed_product, supplier, copydraft))

        return rows

    def _build_row(
        self,
        analyzed_product: dict[str, Any],
        supplier: dict[str, Any],
        copydraft: dict[str, Any],
    ) -> dict[str, Any]:
        score = float(analyzed_product["product_score"])
        profit = float(supplier["profit_est"])
        recommendation = self._build_recommendation(score, profit, bool(supplier["plain_package"]))

        return {
            "product_id": analyzed_product["id"],
            "title": analyzed_product["title"],
            "platform": analyzed_product["platform"],
            "price": float(analyzed_product["price"]),
            "product_score": score,
            "trend": analyzed_product["trend"],
            "category_label": analyzed_product["category_label"],
            "supplier": {
                "supplier_id": supplier["supplier_id"],
                "supplier_name": supplier["supplier_name"],
                "source_price": float(supplier["source_price"]),
                "shipping_cost": float(supplier["shipping_cost"]),
                "profit_est": profit,
                "plain_package": bool(supplier["plain_package"]),
                "supplier_rating": float(supplier["supplier_rating"]),
            },
            "copydraft": {
                "title": copydraft["title"],
                "body": copydraft["body"],
                "tags": copydraft["tags"],
                "template_id": copydraft["template_id"],
            },
            "review": {
                "priority": self._infer_priority(score, profit),
                "recommendation": recommendation,
                "decision": DEFAULT_DECISION,
                "decision_options": ["approved", "skipped", "blacklisted"],
                "reason": "",
                "decided_by": "",
                "decided_at": None,
            },
            "dashboard_generated_at": utc_now_iso(),
        }

    def _infer_priority(self, score: float, profit: float) -> str:
        if score >= PRIORITY_SCORES["high"] and profit >= 8:
            return "high"
        if score >= PRIORITY_SCORES["medium"] and profit >= 3:
            return "medium"
        return "low"

    def _build_recommendation(self, score: float, profit: float, plain_package: bool) -> str:
        if score >= PRIORITY_SCORES["high"] and profit >= 8 and plain_package:
            return "建议优先人工确认，可直接进入上架准备"
        if score >= PRIORITY_SCORES["medium"] and profit >= 3:
            return "建议人工复核标题、利润和货源稳定性"
        return "建议先观察或跳过，避免占用上架精力"

    def _validate_analyzed_product(self, analyzed_product: dict[str, Any]) -> None:
        required_fields = [
            "id",
            "platform",
            "title",
            "price",
            "product_score",
            "trend",
            "category_label",
        ]
        missing = [field for field in required_fields if field not in analyzed_product]
        if missing:
            raise DashboardError(f"Missing analyzed product fields: {', '.join(missing)}")

    def _validate_matched_supplier(self, supplier: dict[str, Any]) -> None:
        required_fields = [
            "product_id",
            "supplier_id",
            "supplier_name",
            "source_price",
            "shipping_cost",
            "profit_est",
            "plain_package",
            "supplier_rating",
        ]
        missing = [field for field in required_fields if field not in supplier]
        if missing:
            raise DashboardError(f"Missing matched supplier fields: {', '.join(missing)}")

    def _validate_copydraft(self, copydraft: dict[str, Any]) -> None:
        required_fields = ["product_id", "title", "body", "tags", "template_id"]
        missing = [field for field in required_fields if field not in copydraft]
        if missing:
            raise DashboardError(f"Missing copy draft fields: {', '.join(missing)}")


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json_list(path: Path, label: str) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise DashboardError(f"{label} JSON must be a list or an object with an 'items' list")


def build_output_path(analyzed_path: Path, output: Path | None) -> Path:
    if output is not None:
        return output
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_OUTPUT_DIR / f"{analyzed_path.stem}_dashboard.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate analyzed, matched, and copy draft data for dashboard review")
    parser.add_argument("--analyzed", required=True, help="Path to AnalyzedProduct JSON file")
    parser.add_argument("--matched", required=True, help="Path to MatchedSupplier JSON file")
    parser.add_argument("--copydrafts", required=True, help="Path to CopyDraft JSON file")
    parser.add_argument("--output", help="Optional output path for dashboard JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    analyzed_path = Path(args.analyzed)
    matched_path = Path(args.matched)
    copydrafts_path = Path(args.copydrafts)
    output_path = build_output_path(analyzed_path, Path(args.output) if args.output else None)

    aggregator = DashboardAggregator()
    rows = aggregator.build_rows(
        load_json_list(analyzed_path, "AnalyzedProduct"),
        load_json_list(matched_path, "MatchedSupplier"),
        load_json_list(copydrafts_path, "CopyDraft"),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {len(rows)} dashboard rows -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
