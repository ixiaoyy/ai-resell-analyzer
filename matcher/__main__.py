from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("data/matched")
DEFAULT_PLATFORM_FEE_RATE = 0.08
CATEGORY_PRICE_FACTOR = {
    "home": 0.52,
    "fashion": 0.45,
    "digital": 0.68,
    "pet": 0.5,
    "beauty": 0.42,
    "other": 0.58,
}
CATEGORY_SHIPPING_COST = {
    "home": 3.5,
    "fashion": 2.8,
    "digital": 4.2,
    "pet": 3.2,
    "beauty": 2.5,
    "other": 3.8,
}
CATEGORY_MOQ = {
    "home": 2,
    "fashion": 2,
    "digital": 1,
    "pet": 2,
    "beauty": 3,
    "other": 2,
}
CATEGORY_RATING = {
    "home": 4.6,
    "fashion": 4.5,
    "digital": 4.4,
    "pet": 4.6,
    "beauty": 4.7,
    "other": 4.3,
}


@dataclass(slots=True)
class MatcherConfig:
    platform_fee_rate: float = DEFAULT_PLATFORM_FEE_RATE


class MatcherError(Exception):
    """Raised when matcher input or output is invalid."""


class SupplierMatcher:
    def __init__(self, config: MatcherConfig | None = None) -> None:
        self.config = config or MatcherConfig()

    def match_products(self, analyzed_products: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.match_product(product) for product in analyzed_products]

    def match_product(self, analyzed_product: dict[str, Any]) -> dict[str, Any]:
        self._validate_analyzed_product(analyzed_product)

        category_label = str(analyzed_product["category_label"])
        keywords = analyzed_product["keywords"]
        price = float(analyzed_product["price"])
        shipping_cost = CATEGORY_SHIPPING_COST.get(category_label, CATEGORY_SHIPPING_COST["other"])
        source_price = self._estimate_source_price(price, category_label, analyzed_product.get("trend"))
        moq = CATEGORY_MOQ.get(category_label, CATEGORY_MOQ["other"])
        supplier_rating = CATEGORY_RATING.get(category_label, CATEGORY_RATING["other"])
        fee = round(price * self.config.platform_fee_rate, 2)
        profit_est = round(price - source_price - shipping_cost - fee, 2)

        supplier_name = self._build_supplier_name(category_label, keywords)
        plain_package = category_label not in {"digital"}

        return {
            "product_id": analyzed_product["id"],
            "supplier_id": f"1688-{analyzed_product['id']}",
            "supplier_name": supplier_name,
            "source_price": source_price,
            "moq": moq,
            "shipping_cost": shipping_cost,
            "profit_est": profit_est,
            "plain_package": plain_package,
            "supplier_rating": supplier_rating,
            "matched_at": utc_now_iso(),
        }

    def _validate_analyzed_product(self, analyzed_product: dict[str, Any]) -> None:
        required_fields = [
            "id",
            "title",
            "price",
            "product_score",
            "trend",
            "keywords",
            "category_label",
            "analyzed_at",
        ]
        missing = [field for field in required_fields if field not in analyzed_product]
        if missing:
            raise MatcherError(f"Missing required fields: {', '.join(missing)}")

        if analyzed_product["trend"] not in {"rising", "stable", "declining"}:
            raise MatcherError("trend must be 'rising', 'stable', or 'declining'")

        if not isinstance(analyzed_product["keywords"], list):
            raise MatcherError("keywords must be a list")

        try:
            float(analyzed_product["price"])
            float(analyzed_product["product_score"])
        except (TypeError, ValueError) as exc:
            raise MatcherError("price and product_score must be numeric") from exc

    def _estimate_source_price(self, retail_price: float, category_label: str, trend: str | None) -> float:
        factor = CATEGORY_PRICE_FACTOR.get(category_label, CATEGORY_PRICE_FACTOR["other"])
        if trend == "rising":
            factor += 0.03
        elif trend == "declining":
            factor -= 0.02

        estimated = retail_price * factor
        return round(max(1.0, estimated), 2)

    def _build_supplier_name(self, category_label: str, keywords: list[Any]) -> str:
        lead_keyword = "通用"
        for keyword in keywords:
            value = str(keyword).strip()
            if value:
                lead_keyword = value
                break
        return f"1688{category_label}货源-{lead_keyword}"


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_analyzed_products(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise MatcherError("Input JSON must be a list or an object with an 'items' list")


def build_output_path(input_path: Path, output: Path | None) -> Path:
    if output is not None:
        return output
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_OUTPUT_DIR / f"{input_path.stem}_matched.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Match analyzed products to supplier candidates")
    parser.add_argument("--input", required=True, help="Path to AnalyzedProduct JSON file")
    parser.add_argument("--output", help="Optional output path for matched supplier JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = build_output_path(input_path, Path(args.output) if args.output else None)

    matcher = SupplierMatcher()
    analyzed_products = load_analyzed_products(input_path)
    matched_suppliers = matcher.match_products(analyzed_products)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(matched_suppliers, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Matched {len(matched_suppliers)} suppliers -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
