from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.schemas import AnalyzedProduct
from matcher import match_suppliers as match_suppliers_models


DEFAULT_OUTPUT_DIR = Path("data/matched")
CATEGORY_BASE_PRICE = {
    "home": 0.58,
    "fashion": 0.52,
    "digital": 0.63,
    "pet": 0.55,
    "beauty": 0.5,
    "other": 0.57,
}
PLAIN_PACKAGE_CATEGORIES = {"home", "fashion", "pet", "beauty", "other"}


@dataclass(slots=True)
class MatcherConfig:
    platform_fee_rate: float = 0.06


class MatcherError(Exception):
    """Raised when matcher input or output is invalid."""


class SupplierMatcher:
    def __init__(self, config: MatcherConfig | None = None) -> None:
        self.config = config or MatcherConfig()

    def match_products(self, analyzed_products: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.match_product(product) for product in analyzed_products]

    def match_product(self, analyzed_product: dict[str, Any]) -> dict[str, Any]:
        self._validate_analyzed_product(analyzed_product)

        product_id = str(analyzed_product["id"])
        category_label = str(analyzed_product.get("category_label") or "other")
        normalized_category = category_label if category_label in CATEGORY_BASE_PRICE else "other"
        price = float(analyzed_product["price"])
        trend = str(analyzed_product["trend"])

        source_ratio = CATEGORY_BASE_PRICE[normalized_category]
        if trend == "rising":
            source_ratio += 0.02
        elif trend == "declining":
            source_ratio -= 0.06

        source_price = round(max(1.0, price * source_ratio), 2)
        shipping_cost = round(3.5 if normalized_category == "digital" else 2.8, 2)
        fee = round(price * self.config.platform_fee_rate, 2)
        profit_est = round(price - source_price - shipping_cost - fee, 2)
        plain_package = normalized_category in PLAIN_PACKAGE_CATEGORIES
        moq = 1 if normalized_category == "digital" else 2
        supplier_rating = 4.2 if normalized_category == "digital" else 4.6

        return {
            "product_id": product_id,
            "supplier_id": f"1688-{product_id}",
            "supplier_name": f"1688{category_label}货源-{self._supplier_suffix(analyzed_product)}",
            "source_price": source_price,
            "shipping_cost": shipping_cost,
            "profit_est": profit_est,
            "moq": moq,
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

    def _supplier_suffix(self, analyzed_product: dict[str, Any]) -> str:
        keywords = analyzed_product.get("keywords") or []
        for keyword in keywords:
            value = str(keyword).strip()
            if value:
                return value
        return str(analyzed_product.get("id") or "default")


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
    parser = argparse.ArgumentParser(description="为分析后的商品生成货源匹配结果")
    parser.add_argument("--input", type=Path, required=True, help="AnalyzedProduct JSON 文件路径")
    parser.add_argument("--output", type=Path, default=None, help="MatchedSupplier 输出文件路径")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    products = [AnalyzedProduct.model_validate(item) for item in load_analyzed_products(args.input)]
    matched = match_suppliers_models(products)

    output_path = build_output_path(args.input, args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([item.model_dump(mode="json") for item in matched], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"matched {len(matched)} suppliers to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
