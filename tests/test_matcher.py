from matcher.__main__ import SupplierMatcher


def test_match_product_generates_required_fields() -> None:
    matcher = SupplierMatcher()
    analyzed_product = {
        "id": "xy-1001",
        "platform": "xianyu",
        "title": "奶油风桌面收纳盒 ins 白色化妆品整理盒",
        "price": 29.9,
        "want_count": 168,
        "category": "家居收纳",
        "fetched_at": "2026-03-19T16:00:00Z",
        "raw_tags": ["桌面", "收纳", "奶油风", "ins"],
        "product_score": 96.0,
        "trend": "rising",
        "keywords": ["桌面", "收纳", "奶油风", "ins"],
        "category_label": "home",
        "features": {
            "color": "白色",
            "material": None,
            "style": "ins",
        },
        "analyzed_at": "2026-03-19T17:25:32Z",
    }

    matched = matcher.match_product(analyzed_product)

    assert matched["product_id"] == analyzed_product["id"]
    assert matched["supplier_id"] == "1688-xy-1001"
    assert matched["source_price"] > 0
    assert matched["shipping_cost"] > 0
    assert matched["profit_est"] > 0
    assert matched["moq"] >= 1
    assert matched["plain_package"] is True
    assert matched["supplier_rating"] >= 4.0
    assert matched["matched_at"].endswith("Z")


def test_match_product_handles_digital_category() -> None:
    matcher = SupplierMatcher()
    analyzed_product = {
        "id": "pdd-2001",
        "platform": "pinduoduo",
        "title": "蓝牙耳机 迷你降噪通勤款 黑色",
        "price": 59.0,
        "sales_count": 356,
        "category": "数码配件",
        "fetched_at": "2026-03-19T16:05:00Z",
        "raw_tags": ["蓝牙", "耳机", "通勤", "黑色"],
        "product_score": 98.73,
        "trend": "rising",
        "keywords": ["蓝牙", "耳机", "通勤", "黑色", "蓝牙耳机"],
        "category_label": "digital",
        "features": {
            "color": "黑色",
            "material": None,
            "style": "通勤",
        },
        "analyzed_at": "2026-03-19T17:25:32Z",
    }

    matched = matcher.match_product(analyzed_product)

    assert matched["plain_package"] is False
    assert matched["moq"] == 1
    assert matched["supplier_name"].startswith("1688digital货源-")
    assert matched["profit_est"] > 0
