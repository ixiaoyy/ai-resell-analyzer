from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.schemas import AnalyzedProduct
from matcher import match_suppliers


def main() -> None:
    parser = argparse.ArgumentParser(description="为分析后的商品生成货源匹配结果")
    parser.add_argument("--input", type=Path, required=True, help="AnalyzedProduct JSON 文件路径")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data") / "matched" / "matched_latest.json",
        help="MatchedSupplier 输出文件路径",
    )
    args = parser.parse_args()

    analyzed_data = json.loads(args.input.read_text(encoding="utf-8"))
    products = [AnalyzedProduct.model_validate(item) for item in analyzed_data]
    matched = match_suppliers(products)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps([item.model_dump(mode="json") for item in matched], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"matched {len(matched)} suppliers to {args.output}")


if __name__ == "__main__":
    main()
