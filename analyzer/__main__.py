from __future__ import annotations

import argparse
import json
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
