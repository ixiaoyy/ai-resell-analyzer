from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.schemas import Platform, RawProduct


def build_sample_raw_products() -> list[RawProduct]:
    now = datetime.now(timezone.utc)
    return [
        RawProduct(
            id="xy-1001",
            platform=Platform.XIANYU,
            title="奶油风桌面收纳小推车 三层带滑轮",
            price=49.9,
            want_count=328,
            sales_count=None,
            image_url="https://example.com/images/cart.jpg",
            category="家居收纳",
            fetched_at=now - timedelta(hours=6),
            raw_tags=["奶油风", "桌面", "收纳"],
        ),
        RawProduct(
            id="pdd-2001",
            platform=Platform.PINDUODUO,
            title="宿舍床边折叠小夜灯 USB 充电",
            price=29.9,
            want_count=None,
            sales_count=1824,
            image_url="https://example.com/images/lamp.jpg",
            category="宿舍用品",
            fetched_at=now - timedelta(hours=4),
            raw_tags=["夜灯", "宿舍", "折叠"],
        ),
        RawProduct(
            id="xy-1002",
            platform=Platform.XIANYU,
            title="北欧风脏衣篮 可折叠大容量",
            price=39.9,
            want_count=96,
            sales_count=None,
            image_url="https://example.com/images/basket.jpg",
            category="家居清洁",
            fetched_at=now - timedelta(hours=8),
            raw_tags=["北欧风", "脏衣篮", "折叠"],
        ),
    ]
