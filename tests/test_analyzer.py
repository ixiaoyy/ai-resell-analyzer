from analyzer.__main__ import ProductAnalyzer


def test_analyze_product_generates_required_fields() -> None:
    analyzer = ProductAnalyzer()
    raw_product = {
        "id": "xy-1001",
        "platform": "xianyu",
        "title": "奶油风桌面收纳盒 ins 白色化妆品整理盒",
        "price": 29.9,
        "want_count": 168,
        "image_url": "https://example.com/images/xy-1001.jpg",
        "category": "家居收纳",
        "fetched_at": "2026-03-19T16:00:00Z",
        "raw_tags": ["桌面", "收纳", "奶油风", "ins"],
    }

    analyzed = analyzer.analyze_product(raw_product)

    assert analyzed["id"] == raw_product["id"]
    assert analyzed["product_score"] >= 70
    assert analyzed["trend"] == "rising"
    assert analyzed["category_label"] == "home"
    assert analyzed["keywords"]
    assert analyzed["features"]["color"] == "白色"
    assert analyzed["features"]["style"] == "ins"
    assert analyzed["analyzed_at"].endswith("Z")


def test_analyze_product_handles_low_signal_item() -> None:
    analyzer = ProductAnalyzer()
    raw_product = {
        "id": "xy-1002",
        "platform": "xianyu",
        "title": "普通杂物袋",
        "price": 199.0,
        "want_count": 2,
        "category": "其他",
        "fetched_at": "2026-03-19T16:10:00Z",
        "raw_tags": [],
    }

    analyzed = analyzer.analyze_product(raw_product)

    assert analyzed["trend"] == "declining"
    assert analyzed["category_label"] == "other"
    assert analyzed["product_score"] < 45
