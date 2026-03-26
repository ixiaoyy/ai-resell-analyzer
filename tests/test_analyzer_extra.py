from __future__ import annotations

import pytest

from analyzer.__main__ import AnalyzerConfig, AnalyzerError, ProductAnalyzer


_BASE = {
    "id": "xy-9001",
    "platform": "xianyu",
    "title": "测试商品",
    "price": 20.0,
    "fetched_at": "2026-01-01T00:00:00Z",
}


def test_missing_required_field_raises() -> None:
    analyzer = ProductAnalyzer()
    bad = {k: v for k, v in _BASE.items() if k != "fetched_at"}
    with pytest.raises(AnalyzerError, match="fetched_at"):
        analyzer.analyze_product(bad)


def test_invalid_platform_raises() -> None:
    analyzer = ProductAnalyzer()
    bad = {**_BASE, "platform": "taobao"}
    with pytest.raises(AnalyzerError, match="platform"):
        analyzer.analyze_product(bad)


def test_non_numeric_price_raises() -> None:
    analyzer = ProductAnalyzer()
    bad = {**_BASE, "price": "free"}
    with pytest.raises(AnalyzerError, match="price"):
        analyzer.analyze_product(bad)


def test_category_label_falls_back_to_other() -> None:
    analyzer = ProductAnalyzer()
    product = {**_BASE, "title": "神秘物品无关键词", "category": "未知分类", "raw_tags": []}
    result = analyzer.analyze_product(product)
    assert result["category_label"] == "other"


def test_features_none_when_no_match() -> None:
    analyzer = ProductAnalyzer()
    product = {**_BASE, "title": "无颜色无材质无风格", "raw_tags": []}
    result = analyzer.analyze_product(product)
    assert result["features"]["color"] is None
    assert result["features"]["material"] is None
    assert result["features"]["style"] is None


def test_score_boundary_stable() -> None:
    """want_count near the stable/rising threshold should yield stable trend."""
    analyzer = ProductAnalyzer()
    # want_count=30 → low engagement, expect stable or declining, not rising
    product = {**_BASE, "want_count": 30, "raw_tags": []}
    result = analyzer.analyze_product(product)
    assert result["trend"] in ("stable", "declining")


def test_keywords_max_count() -> None:
    analyzer = ProductAnalyzer(config=AnalyzerConfig(max_keywords=3))
    product = {
        **_BASE,
        "title": "蓝牙耳机 收纳盒 猫抓板 口红 置物架",
        "raw_tags": ["桌面", "支架", "化妆", "实木", "宠物"],
    }
    result = analyzer.analyze_product(product)
    assert len(result["keywords"]) <= 3


def test_analyze_products_batch() -> None:
    analyzer = ProductAnalyzer()
    products = [
        {**_BASE, "id": f"xy-{i}", "title": f"商品{i}"}
        for i in range(4)
    ]
    results = analyzer.analyze_products(products)
    assert len(results) == 4
    assert [r["id"] for r in results] == [f"xy-{i}" for i in range(4)]
