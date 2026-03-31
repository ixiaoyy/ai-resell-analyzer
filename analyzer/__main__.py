from __future__ import annotations

import argparse
import json
<<<<<<< HEAD
from pathlib import Path

from analyzer import analyze_products
from app.schemas import RawProduct


def main() -> None:
    parser = argparse.ArgumentParser(description="分析 RawProduct 数据并输出候选结果")
    parser.add_argument("--input", type=Path, required=True, help="RawProduct JSON 文件路径")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data") / "analyzed" / "analyzed_latest.json",
        help="AnalyzedProduct 输出文件路径",
    )
    args = parser.parse_args()

    raw_data = json.loads(args.input.read_text(encoding="utf-8"))
    products = [RawProduct.model_validate(item) for item in raw_data]
    analyzed_products = analyze_products(products)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps([product.model_dump(mode="json") for product in analyzed_products], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"analyzed {len(analyzed_products)} products to {args.output}")


if __name__ == "__main__":
    main()
=======
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("data/analyzed")
STOPWORDS = {
    "2024",
    "2025",
    "2026",
    "包邮",
    "全新",
    "可刀",
    "出",
    "闲置",
    "同款",
    "自用",
    "二手",
    "现货",
    "转",
    "九成新",
}
CATEGORY_RULES = {
    "home": ["收纳", "桌面", "置物", "厨房", "浴室", "家居", "抱枕", "地毯"],
    "fashion": ["女包", "裙", "衬衫", "外套", "耳环", "项链", "帽子", "穿搭"],
    "digital": ["手机", "蓝牙", "耳机", "支架", "键盘", "鼠标", "充电", "数码"],
    "pet": ["宠物", "猫", "狗", "猫抓板", "猫窝", "牵引", "逗猫"],
    "beauty": ["美妆", "口红", "护肤", "香水", "化妆", "面膜"],
}
COLOR_WORDS = [
    "黑色",
    "白色",
    "灰色",
    "银色",
    "粉色",
    "蓝色",
    "绿色",
    "紫色",
    "黄色",
    "红色",
    "棕色",
    "米白",
    "奶油",
]
MATERIAL_WORDS = ["实木", "棉麻", "不锈钢", "陶瓷", "玻璃", "硅胶", "皮质", "亚克力", "金属", "绒面"]
STYLE_WORDS = ["极简", "ins", "复古", "奶油风", "原木风", "轻奢", "可爱", "通勤", "露营"]


@dataclass(slots=True)
class AnalyzerConfig:
    score_threshold_rising: float = 70.0
    score_threshold_stable: float = 45.0
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

        title = str(raw_product["title"])
        keywords = self._extract_keywords(title, raw_product.get("raw_tags") or [])
        category_label = self._infer_category_label(title, raw_product.get("category"))
        features = self._extract_features(title, raw_product.get("raw_tags") or [])
        score = self._calculate_score(raw_product, keywords, category_label, features)
        trend = self._infer_trend(score)

        analyzed_product = dict(raw_product)
        analyzed_product.update(
            {
                "product_score": round(score, 2),
                "trend": trend,
                "keywords": keywords,
                "category_label": category_label,
                "features": features,
                "analyzed_at": utc_now_iso(),
            }
        )
        return analyzed_product

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

    def _calculate_score(
        self,
        raw_product: dict[str, Any],
        keywords: list[str],
        category_label: str,
        features: dict[str, str | None],
    ) -> float:
        score = 20.0
        price = float(raw_product["price"])
        want_count = int(raw_product.get("want_count") or 0)
        sales_count = int(raw_product.get("sales_count") or 0)

        if want_count > 0:
            score += min(want_count / 8, 30)
        if sales_count > 0:
            score += min(sales_count / 15, 30)

        if 8 <= price <= 80:
            score += 15
        elif 80 < price <= 150:
            score += 8
        else:
            score -= 5

        score += min(len(keywords) * 4, 16)

        if category_label != "other":
            score += 8

        recognized_features = sum(1 for value in features.values() if value)
        score += recognized_features * 3

        if raw_product["platform"] == "xianyu" and want_count >= 80:
            score += 10
        if raw_product["platform"] == "pinduoduo" and sales_count >= 200:
            score += 10

        return max(0.0, min(score, 100.0))

    def _infer_trend(self, score: float) -> str:
        if score >= self.config.score_threshold_rising:
            return "rising"
        if score >= self.config.score_threshold_stable:
            return "stable"
        return "declining"

    def _extract_keywords(self, title: str, raw_tags: list[str]) -> list[str]:
        tokens = []
        tokens.extend(raw_tags)
        tokens.extend(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]+", title))

        cleaned: list[str] = []
        for token in tokens:
            word = str(token).strip().lower()
            if not word or word in STOPWORDS or len(word) <= 1:
                continue
            if word not in cleaned:
                cleaned.append(word)

        return cleaned[: self.config.max_keywords]

    def _infer_category_label(self, title: str, category: Any) -> str:
        haystack = f"{title} {category or ''}"
        for category_label, keywords in CATEGORY_RULES.items():
            if any(keyword in haystack for keyword in keywords):
                return category_label
        return "other"

    def _extract_features(self, title: str, raw_tags: list[str]) -> dict[str, str | None]:
        haystack = f"{title} {' '.join(map(str, raw_tags))}"
        return {
            "color": find_first(haystack, COLOR_WORDS),
            "material": find_first(haystack, MATERIAL_WORDS),
            "style": find_first(haystack, STYLE_WORDS),
        }


def find_first(text: str, candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in text:
            return candidate
    return None


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
    parser = argparse.ArgumentParser(description="Analyze raw product data into AnalyzedProduct records")
    parser.add_argument("--input", required=True, help="Path to RawProduct JSON file")
    parser.add_argument("--output", help="Optional output path for analyzed JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = build_output_path(input_path, Path(args.output) if args.output else None)

    analyzer = ProductAnalyzer()
    raw_products = load_raw_products(input_path)
    analyzed_products = analyzer.analyze_products(raw_products)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(analyzed_products, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Analyzed {len(analyzed_products)} products -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
>>>>>>> 3311d2de910204e56242a82af8a79f0e33c51ef4
