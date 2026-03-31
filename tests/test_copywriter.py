from copywriter.__main__ import ProductCopywriter


def test_generate_draft_generates_required_fields() -> None:
    copywriter = ProductCopywriter()
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

    draft = copywriter.generate_draft(analyzed_product)

    assert draft["product_id"] == analyzed_product["id"]
    assert draft["title"]
    assert len(draft["title"]) <= 30
    assert "29.90" in draft["body"]
    assert draft["template_id"] == "hot-trend"
    assert 1 <= len(draft["tags"]) <= 5
    assert draft["generated_at"].endswith("Z")


def test_generate_draft_uses_budget_template_for_declining_items() -> None:
    copywriter = ProductCopywriter()
    analyzed_product = {
        "id": "xy-1002",
        "platform": "xianyu",
        "title": "普通杂物袋",
        "price": 19.0,
        "want_count": 2,
        "category": "其他",
        "fetched_at": "2026-03-19T16:10:00Z",
        "raw_tags": [],
        "product_score": 21.0,
        "trend": "declining",
        "keywords": ["杂物袋", "收纳袋"],
        "category_label": "other",
        "features": {
            "color": None,
            "material": None,
            "style": None,
        },
        "analyzed_at": "2026-03-19T17:25:32Z",
    }

    draft = copywriter.generate_draft(analyzed_product)

    assert draft["template_id"] == "budget-pick"
    assert "19.00" in draft["body"]
    assert draft["tags"] == ["杂物袋", "收纳袋"]
