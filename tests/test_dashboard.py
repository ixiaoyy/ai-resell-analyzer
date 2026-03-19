from dashboard.__main__ import DashboardAggregator, DashboardError


def test_build_rows_generates_review_ready_records() -> None:
    aggregator = DashboardAggregator()
    analyzed_products = [
        {
            "id": "xy-1001",
            "platform": "xianyu",
            "title": "奶油风桌面收纳盒 ins 白色化妆品整理盒",
            "price": 29.9,
            "product_score": 96.0,
            "trend": "rising",
            "category_label": "home",
        }
    ]
    matched_suppliers = [
        {
            "product_id": "xy-1001",
            "supplier_id": "1688-xy-1001",
            "supplier_name": "1688home货源-桌面",
            "source_price": 16.45,
            "shipping_cost": 3.5,
            "profit_est": 8.56,
            "plain_package": True,
            "supplier_rating": 4.6,
        }
    ]
    copydrafts = [
        {
            "product_id": "xy-1001",
            "title": "家居好物 ins 白色 桌面 收纳",
            "body": "最近问的人很多，已经帮你挑过重点了。",
            "tags": ["ins", "白色", "桌面"],
            "template_id": "hot-trend",
        }
    ]

    rows = aggregator.build_rows(analyzed_products, matched_suppliers, copydrafts)

    assert len(rows) == 1
    row = rows[0]
    assert row["product_id"] == "xy-1001"
    assert row["supplier"]["supplier_id"] == "1688-xy-1001"
    assert row["copydraft"]["template_id"] == "hot-trend"
    assert row["review"]["priority"] == "high"
    assert row["review"]["decision"] == "pending"
    assert row["review"]["decision_options"] == ["approved", "skipped", "blacklisted"]
    assert row["dashboard_generated_at"].endswith("Z")


def test_build_rows_raises_when_copydraft_missing() -> None:
    aggregator = DashboardAggregator()
    analyzed_products = [
        {
            "id": "xy-1001",
            "platform": "xianyu",
            "title": "奶油风桌面收纳盒 ins 白色化妆品整理盒",
            "price": 29.9,
            "product_score": 96.0,
            "trend": "rising",
            "category_label": "home",
        }
    ]
    matched_suppliers = [
        {
            "product_id": "xy-1001",
            "supplier_id": "1688-xy-1001",
            "supplier_name": "1688home货源-桌面",
            "source_price": 16.45,
            "shipping_cost": 3.5,
            "profit_est": 8.56,
            "plain_package": True,
            "supplier_rating": 4.6,
        }
    ]

    try:
        aggregator.build_rows(analyzed_products, matched_suppliers, [])
    except DashboardError as exc:
        assert "Missing copy draft" in str(exc)
    else:
        raise AssertionError("Expected DashboardError when copy draft is missing")
