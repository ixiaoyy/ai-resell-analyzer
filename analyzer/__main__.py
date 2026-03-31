from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from analyzer import analyze_products as analyze_products_models
from app.schemas import RawProduct


DEFAULT_OUTPUT_DIR = Path("data/analyzed")

CATEGORY_LABELS = {
    "家居": "home",
    "收纳": "home",
    "家居收纳": "home",
    "家居清洁": "home",
    "穿搭": "fashion",
    "服饰": "fashion",
    "数码": "digital",
    "数码配件": "digital",
    "宠物": "pet",
    "美妆": "beauty",
}

COLOR_KEYWORDS = ["白色", "黑色", "灰色", "蓝色", "粉色", "米白"]
MATERIAL_KEYWORDS = ["塑料", "ABS", "棉麻", "金属", "木质", "硅胶"]
STYLE_KEYWORDS = ["ins", "奶油风", "北欧风", "通勤", "极简"]


@dataclass(slots=True)
class AnalyzerConfig:
    max_keywords: int = 5


class AnalyzerError(Exception):
    """Raised when analyzer input or output is invalid."""


class ProductAnalyzer:
    def __init__(self, config: AnalyzerConfig | None = None) -> None:
        self.config = config or AnalyzerConfig()

    def analyze_products(self, raw_products: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.analyze_product(product) for product in raw_products]

    def analyze_product(self, raw_product: dict[str, Any]) -> dict[str, Any]:
        self._validate_raw_product(raw_product)

        score = self._score_product(raw_product)
        trend = self._detect_trend(raw_product, score)
        return {
            **raw_product,
            "product_score": score,
            "trend": trend,
            "keywords": self._extract_keywords(raw_product),
            "category_label": self._category_label(raw_product),
            "features": self._extract_features(raw_product),
            "analyzed_at": utc_now_iso(),
        }

    def _validate_raw_product(self, raw_product: dict[str, Any]) -> None:
        required_fields = ["id", "platform", "title", "price", "fetched_at"]
        missing = [field for field in required_fields if field not in raw_product]
        if missing:
            raise AnalyzerError(f"Missing required fields: {', '.join(missing)}")

        if raw_product["platform"] not in {"xianyu", "pinduoduo"}:
            raise AnalyzerError("platform must be 'xianyu' or 'pinduoduo'")

        try:
            float(raw_product["price"])
        except (TypeError, ValueError) as exc:
            raise AnalyzerError("price must be numeric") from exc

    def _score_product(self, raw_product: dict[str, Any]) -> float:
        price = float(raw_product["price"])
        want_count = int(raw_product.get("want_count") or 0)
        sales_count = int(raw_product.get("sales_count") or 0)
        raw_tags = raw_product.get("raw_tags") or []
        category = str(raw_product.get("category") or "")
        title = str(raw_product.get("title") or "")

        score = 20.0
        score += min(want_count * 0.35, 45.0)
        score += min(sales_count * 0.03, 35.0)
        score += max(0.0, 10.0 - min(price, 200.0) / 20.0)
        score += min(len(raw_tags) * 2.0, 8.0)
        if any(token in title for token in ["奶油风", "ins", "蓝牙", "收纳", "耳机"]):
            score += 8.0
        if any(token in category for token in ["家居", "收纳", "数码", "服饰", "美妆", "宠物"]):
            score += 6.0
        return round(min(score, 100.0), 2)

    def _detect_trend(self, raw_product: dict[str, Any], score: float) -> str:
        want_count = int(raw_product.get("want_count") or 0)
        sales_count = int(raw_product.get("sales_count") or 0)
        signal = want_count + sales_count * 0.15
        if signal >= 80 or score >= 85:
            return "rising"
        if signal >= 20 or score >= 45:
            return "stable"
        return "declining"

    def _extract_keywords(self, raw_product: dict[str, Any]) -> list[str]:
        title_tokens = [token for token in str(raw_product.get("title") or "").replace("/", " ").split() if token.strip()]
        raw_tags = [str(tag).strip() for tag in (raw_product.get("raw_tags") or []) if str(tag).strip()]
        category = str(raw_product.get("category") or "").strip()
        keywords: list[str] = []
        for token in [*title_tokens, *raw_tags, category]:
            if token and token not in keywords:
                keywords.append(token)
            if len(keywords) >= self.config.max_keywords:
                break
        return keywords

    def _category_label(self, raw_product: dict[str, Any]) -> str:
        category = str(raw_product.get("category") or "")
        title = str(raw_product.get("title") or "")
        for keyword, label in CATEGORY_LABELS.items():
            if keyword in category or keyword in title:
                return label
        return "other"

    def _extract_features(self, raw_product: dict[str, Any]) -> dict[str, str | None]:
        haystack = " ".join(
            [
                str(raw_product.get("title") or ""),
                *[str(tag) for tag in (raw_product.get("raw_tags") or [])],
            ]
        )
        return {
            "color": next((item for item in COLOR_KEYWORDS if item in haystack), None),
            "material": next((item for item in MATERIAL_KEYWORDS if item in haystack), None),
            "style": next((item for item in STYLE_KEYWORDS if item in haystack), None),
        }


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_raw_products(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise AnalyzerError("Input JSON must be a list or an object with an 'items' list")


def build_output_path(input_path: Path, output: Path | None) -> Path:
    if output is not None:
        return output
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_OUTPUT_DIR / f"{input_path.stem}_analyzed.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="分析 RawProduct 数据并输出候选结果")
    parser.add_argument("--input", type=Path, required=True, help="RawProduct JSON 文件路径")
    parser.add_argument("--output", type=Path, default=None, help="AnalyzedProduct 输出文件路径")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    products = [RawProduct.model_validate(item) for item in load_raw_products(args.input)]
    analyzed_products = analyze_products_models(products)

    output_path = build_output_path(args.input, args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([product.model_dump(mode="json") for product in analyzed_products], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"analyzed {len(analyzed_products)} products to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
