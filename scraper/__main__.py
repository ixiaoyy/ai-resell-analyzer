from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("data/raw")
VALID_PLATFORMS = ("xianyu", "pinduoduo")

# Static mock catalogue — representative samples per platform/category
_MOCK_ITEMS: list[dict[str, Any]] = [
    {
        "id": "xy-3001",
        "platform": "xianyu",
        "title": "奶油风桌面收纳盒 ins 白色化妆品整理盒",
        "price": 29.9,
        "want_count": 168,
        "image_url": "https://example.com/images/xy-3001.jpg",
        "category": "家居收纳",
        "raw_tags": ["桌面", "收纳", "奶油风", "ins"],
    },
    {
        "id": "xy-3002",
        "platform": "xianyu",
        "title": "宠物猫抓板 可爱耐磨瓦楞纸 猫窝两用",
        "price": 15.9,
        "want_count": 87,
        "image_url": "https://example.com/images/xy-3002.jpg",
        "category": "宠物用品",
        "raw_tags": ["宠物", "猫", "猫抓板", "耐磨"],
    },
    {
        "id": "xy-3003",
        "platform": "xianyu",
        "title": "极简风实木置物架桌面书架 原木色",
        "price": 89.0,
        "want_count": 204,
        "image_url": "https://example.com/images/xy-3003.jpg",
        "category": "家居收纳",
        "raw_tags": ["实木", "置物架", "极简", "原木风"],
    },
    {
        "id": "xy-3004",
        "platform": "xianyu",
        "title": "Y2K辣妹风格耳环 银色金属感",
        "price": 18.0,
        "want_count": 312,
        "image_url": "https://example.com/images/xy-3004.jpg",
        "category": "饰品配件",
        "raw_tags": ["耳环", "银色", "y2k", "辣妹"],
    },
    {
        "id": "xy-3005",
        "platform": "xianyu",
        "title": "口红 哑光丝绒显白色号 美妆",
        "price": 39.9,
        "want_count": 130,
        "image_url": "https://example.com/images/xy-3005.jpg",
        "category": "美妆护肤",
        "raw_tags": ["口红", "美妆", "哑光", "显白"],
    },
    {
        "id": "pdd-4001",
        "platform": "pinduoduo",
        "title": "蓝牙耳机 迷你降噪通勤款 黑色",
        "price": 59.0,
        "sales_count": 356,
        "image_url": "https://example.com/images/pdd-4001.jpg",
        "category": "数码配件",
        "raw_tags": ["蓝牙", "耳机", "通勤", "黑色"],
    },
    {
        "id": "pdd-4002",
        "platform": "pinduoduo",
        "title": "硅胶手机支架 折叠懒人桌面款 粉色",
        "price": 12.9,
        "sales_count": 892,
        "image_url": "https://example.com/images/pdd-4002.jpg",
        "category": "数码配件",
        "raw_tags": ["支架", "硅胶", "手机", "粉色"],
    },
    {
        "id": "pdd-4003",
        "platform": "pinduoduo",
        "title": "露营折叠椅轻便户外便携 绿色",
        "price": 49.9,
        "sales_count": 215,
        "image_url": "https://example.com/images/pdd-4003.jpg",
        "category": "户外运动",
        "raw_tags": ["露营", "折叠椅", "户外", "绿色"],
    },
    {
        "id": "pdd-4004",
        "platform": "pinduoduo",
        "title": "棉麻通勤衬衫 宽松显瘦 白色",
        "price": 45.0,
        "sales_count": 438,
        "image_url": "https://example.com/images/pdd-4004.jpg",
        "category": "女装",
        "raw_tags": ["衬衫", "棉麻", "通勤", "白色"],
    },
    {
        "id": "pdd-4005",
        "platform": "pinduoduo",
        "title": "狗狗牵引绳 反光夜跑款 可调节",
        "price": 22.9,
        "sales_count": 167,
        "image_url": "https://example.com/images/pdd-4005.jpg",
        "category": "宠物用品",
        "raw_tags": ["宠物", "狗", "牵引", "反光"],
    },
]


@dataclass(slots=True)
class ScraperConfig:
    default_count: int = 5


class ScraperError(Exception):
    """Raised when scraper input or output is invalid."""


class ProductScraper:
    def __init__(self, config: ScraperConfig | None = None) -> None:
        self.config = config or ScraperConfig()

    def scrape(self, platform: str = "all", count: int | None = None) -> list[dict[str, Any]]:
        """Return RawProduct records for the given platform and count."""
        if platform not in (*VALID_PLATFORMS, "all"):
            raise ScraperError(f"Invalid platform '{platform}'. Must be one of: xianyu, pinduoduo, all")

        effective_count = count if count is not None else self.config.default_count
        if effective_count < 1:
            raise ScraperError(f"count must be >= 1, got {effective_count}")

        if platform == "all":
            pool = _MOCK_ITEMS
        else:
            pool = [item for item in _MOCK_ITEMS if item["platform"] == platform]

        selected = pool[:effective_count]
        fetched_at = utc_now_iso()
        return [self._stamp(item, fetched_at) for item in selected]

    def _stamp(self, item: dict[str, Any], fetched_at: str) -> dict[str, Any]:
        result = dict(item)
        result["fetched_at"] = fetched_at
        return result


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_output_path(platform: str, output: Path | None) -> Path:
    if output is not None:
        return output
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_OUTPUT_DIR / f"{platform}_latest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape hot product data into RawProduct records")
    parser.add_argument(
        "--platform",
        default="all",
        choices=["xianyu", "pinduoduo", "all"],
        help="Platform to scrape (default: all)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Max number of products to return (default: 5)",
    )
    parser.add_argument("--output", help="Optional output path for raw product JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = build_output_path(args.platform, Path(args.output) if args.output else None)

    scraper = ProductScraper()
    products = scraper.scrape(platform=args.platform, count=args.count)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(products, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Scraped {len(products)} products -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
