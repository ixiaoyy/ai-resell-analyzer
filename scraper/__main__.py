from __future__ import annotations

import argparse
import json
from pathlib import Path

from scraper import build_sample_raw_products


def main() -> None:
    parser = argparse.ArgumentParser(description="导出示例抓取数据")
    parser.add_argument(
        "--platform",
        choices=["xianyu", "pinduoduo", "all"],
        default="all",
        help="按平台过滤输出结果",
    )
    parser.add_argument("--limit", type=int, default=100, help="限制输出条数")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="输出 JSON 文件路径，默认写入 data/raw/<platform>_latest.json",
    )
    args = parser.parse_args()

    products = build_sample_raw_products()
    if args.platform != "all":
        products = [product for product in products if product.platform.value == args.platform]
    products = products[: max(args.limit, 0)]

    output_path = args.output or Path("data") / "raw" / f"{args.platform}_latest.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([product.model_dump(mode="json") for product in products], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"exported {len(products)} products to {output_path}")


if __name__ == "__main__":
    main()
