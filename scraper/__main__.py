from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path


DEFAULT_OUTPUT_DIR = Path("data/raw")


class ScraperError(Exception):
    """Raised when scraper input or output is invalid."""


class ProductScraper:
    def scrape(self, platform: str = "all", count: int = 5) -> list[dict]:
        if platform not in {"xianyu", "pinduoduo", "all"}:
            raise ScraperError("Invalid platform")
        if count < 1:
            raise ScraperError("count must be greater than 0")

        products = self._sample_products()
        if platform != "all":
            products = [item for item in products if item["platform"] == platform]
        return products[:count]

    def _sample_products(self) -> list[dict]:
        now = utc_now_iso()
        earlier = (datetime.now(UTC) - timedelta(hours=2)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        return [
            {
                "id": "xy-1001",
                "platform": "xianyu",
                "title": "奶油风桌面收纳盒 ins 白色化妆品整理盒",
                "price": 29.9,
                "want_count": 168,
                "image_url": "https://example.com/images/xy-1001.jpg",
                "category": "家居收纳",
                "fetched_at": now,
                "raw_tags": ["桌面", "收纳", "奶油风", "ins"],
            },
            {
                "id": "pdd-2001",
                "platform": "pinduoduo",
                "title": "蓝牙耳机 迷你降噪通勤款 黑色",
                "price": 59.0,
                "sales_count": 356,
                "image_url": "https://example.com/images/pdd-2001.jpg",
                "category": "数码配件",
                "fetched_at": earlier,
                "raw_tags": ["蓝牙", "耳机", "通勤", "黑色"],
            },
            {
                "id": "xy-1002",
                "platform": "xianyu",
                "title": "普通杂物袋",
                "price": 19.0,
                "want_count": 2,
                "category": "其他",
                "fetched_at": now,
                "raw_tags": ["杂物袋", "收纳袋"],
            },
            {
                "id": "xy-1003",
                "platform": "xianyu",
                "title": "北欧风脏衣篮 可折叠大容量",
                "price": 39.9,
                "want_count": 96,
                "category": "家居清洁",
                "fetched_at": now,
                "raw_tags": ["北欧风", "脏衣篮", "折叠"],
            },
            {
                "id": "pdd-2002",
                "platform": "pinduoduo",
                "title": "宿舍床边折叠小夜灯 USB 充电",
                "price": 29.9,
                "sales_count": 1824,
                "category": "宿舍用品",
                "fetched_at": earlier,
                "raw_tags": ["夜灯", "宿舍", "折叠"],
            },
        ]


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_output_path(platform: str, output: Path | None) -> Path:
    if output is not None:
        return output
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_OUTPUT_DIR / f"{platform}_latest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导出示例抓取数据")
    parser.add_argument("--platform", choices=["xianyu", "pinduoduo", "all"], default="all", help="按平台过滤输出结果")
    parser.add_argument("--limit", type=int, default=100, help="限制输出条数")
    parser.add_argument("--output", type=Path, default=None, help="输出 JSON 文件路径")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scraper = ProductScraper()
    products = scraper.scrape(platform=args.platform, count=args.limit)
    output_path = build_output_path(args.platform, args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(products, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"exported {len(products)} products to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
