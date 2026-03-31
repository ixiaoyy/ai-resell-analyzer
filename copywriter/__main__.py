from __future__ import annotations

import argparse
import json
<<<<<<< HEAD
from pathlib import Path

from app.schemas import AnalyzedProduct, MatchedSupplier
from copywriter import build_copy_drafts


def main() -> None:
    parser = argparse.ArgumentParser(description="为商品候选生成文案草稿")
    parser.add_argument("--products", type=Path, required=True, help="AnalyzedProduct JSON 文件路径")
    parser.add_argument("--suppliers", type=Path, required=True, help="MatchedSupplier JSON 文件路径")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data") / "copy" / "copy_latest.json",
        help="CopyDraft 输出文件路径",
    )
    args = parser.parse_args()

    product_data = json.loads(args.products.read_text(encoding="utf-8"))
    supplier_data = json.loads(args.suppliers.read_text(encoding="utf-8"))
    products = [AnalyzedProduct.model_validate(item) for item in product_data]
    suppliers = {
        supplier.product_id: supplier
        for supplier in (MatchedSupplier.model_validate(item) for item in supplier_data)
    }
    drafts = build_copy_drafts(products, suppliers)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps([draft.model_dump(mode="json") for draft in drafts], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"generated {len(drafts)} copy drafts to {args.output}")


if __name__ == "__main__":
    main()
=======
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("data/copydrafts")
TITLE_LIMIT = 30
BODY_TAG_LIMIT = 5

CATEGORY_PREFIX = {
    "home": "家居好物",
    "fashion": "穿搭推荐",
    "digital": "数码实用",
    "pet": "养宠必备",
    "beauty": "颜值单品",
    "other": "闲置推荐",
}
TREND_OPENING = {
    "rising": "最近问的人很多，已经帮你挑过重点了。",
    "stable": "这类东西一直都很实用，属于不容易踩雷的选择。",
    "declining": "热度没那么夸张，但胜在价格友好、使用稳定。",
}


@dataclass(slots=True)
class CopywriterConfig:
    max_tags: int = BODY_TAG_LIMIT
    title_limit: int = TITLE_LIMIT


class CopywriterError(Exception):
    """Raised when copywriter input or output is invalid."""


class ProductCopywriter:
    def __init__(self, config: CopywriterConfig | None = None) -> None:
        self.config = config or CopywriterConfig()

    def generate_drafts(self, analyzed_products: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.generate_draft(product) for product in analyzed_products]

    def generate_draft(self, analyzed_product: dict[str, Any]) -> dict[str, Any]:
        self._validate_analyzed_product(analyzed_product)

        product_id = str(analyzed_product["id"])
        title = self._build_title(analyzed_product)
        body, template_id = self._build_body(analyzed_product)
        tags = self._build_tags(analyzed_product)

        return {
            "product_id": product_id,
            "title": title,
            "body": body,
            "tags": tags,
            "template_id": template_id,
            "generated_at": utc_now_iso(),
        }

    def _validate_analyzed_product(self, analyzed_product: dict[str, Any]) -> None:
        required_fields = [
            "id",
            "title",
            "price",
            "trend",
            "keywords",
            "category_label",
            "features",
            "analyzed_at",
        ]
        missing = [field for field in required_fields if field not in analyzed_product]
        if missing:
            raise CopywriterError(f"Missing required fields: {', '.join(missing)}")

        if analyzed_product["trend"] not in {"rising", "stable", "declining"}:
            raise CopywriterError("trend must be 'rising', 'stable', or 'declining'")

        if not isinstance(analyzed_product["keywords"], list):
            raise CopywriterError("keywords must be a list")

        if not isinstance(analyzed_product["features"], dict):
            raise CopywriterError("features must be an object")

        try:
            float(analyzed_product["price"])
        except (TypeError, ValueError) as exc:
            raise CopywriterError("price must be numeric") from exc

    def _build_title(self, analyzed_product: dict[str, Any]) -> str:
        category_label = str(analyzed_product.get("category_label") or "other")
        prefix = CATEGORY_PREFIX.get(category_label, CATEGORY_PREFIX["other"])
        features = analyzed_product.get("features") or {}
        title_parts = [prefix]

        for key in ("style", "color", "material"):
            value = str(features.get(key) or "").strip()
            if value and value not in title_parts:
                title_parts.append(value)

        for keyword in analyzed_product["keywords"]:
            value = str(keyword).strip()
            if value and value not in title_parts:
                title_parts.append(value)
            candidate = " ".join(title_parts)
            if len(candidate) >= self.config.title_limit:
                break

        title = " ".join(title_parts)
        if len(title) > self.config.title_limit:
            title = title[: self.config.title_limit].rstrip()
        return title

    def _build_body(self, analyzed_product: dict[str, Any]) -> tuple[str, str]:
        trend = str(analyzed_product["trend"])
        price = float(analyzed_product["price"])
        features = analyzed_product.get("features") or {}
        feature_summary = self._build_feature_summary(features, analyzed_product["keywords"])

        if trend == "rising":
            template_id = "hot-trend"
            body = (
                f"{TREND_OPENING[trend]} "
                f"这款我更看重的是 {feature_summary}，"
                f"现在到手参考价 {price:.2f} 元，适合想低预算先入手试试的人。"
            )
        elif trend == "stable":
            template_id = "steady-value"
            body = (
                f"{TREND_OPENING[trend]} "
                f"整体卖点比较清晰：{feature_summary}。"
                f"参考价 {price:.2f} 元，日常自用或者顺手转卖都比较顺。"
            )
        else:
            template_id = "budget-pick"
            body = (
                f"{TREND_OPENING[trend]} "
                f"如果你在意的是性价比，这款的亮点还是 {feature_summary}。"
                f"参考价 {price:.2f} 元，适合蹲实用型需求。"
            )

        return body, template_id

    def _build_feature_summary(self, features: dict[str, Any], keywords: list[Any]) -> str:
        parts: list[str] = []
        for key in ("style", "color", "material"):
            value = str(features.get(key) or "").strip()
            if value:
                parts.append(value)

        for keyword in keywords:
            value = str(keyword).strip()
            if value and value not in parts:
                parts.append(value)
            if len(parts) >= 3:
                break

        return " / ".join(parts) if parts else "基础需求覆盖比较完整"

    def _build_tags(self, analyzed_product: dict[str, Any]) -> list[str]:
        tags: list[str] = []
        features = analyzed_product.get("features") or {}

        for key in ("style", "color", "material"):
            value = str(features.get(key) or "").strip()
            if value and value not in tags:
                tags.append(value)

        for keyword in analyzed_product["keywords"]:
            value = str(keyword).strip()
            if value and value not in tags:
                tags.append(value)
            if len(tags) >= self.config.max_tags:
                break

        return tags[: self.config.max_tags]


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_analyzed_products(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise CopywriterError("Input JSON must be a list or an object with an 'items' list")


def build_output_path(input_path: Path, output: Path | None) -> Path:
    if output is not None:
        return output
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_OUTPUT_DIR / f"{input_path.stem}_copydrafts.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate copy drafts from analyzed product data")
    parser.add_argument("--input", required=True, help="Path to AnalyzedProduct JSON file")
    parser.add_argument("--output", help="Optional output path for copy draft JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = build_output_path(input_path, Path(args.output) if args.output else None)

    copywriter = ProductCopywriter()
    analyzed_products = load_analyzed_products(input_path)
    drafts = copywriter.generate_drafts(analyzed_products)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(drafts, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Generated {len(drafts)} copy drafts -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
>>>>>>> 3311d2de910204e56242a82af8a79f0e33c51ef4
