from __future__ import annotations

import pytest

from matcher.__main__ import MatcherConfig, MatcherError, SupplierMatcher


_BASE = {
    "id": "xy-9001",
    "platform": "xianyu",
    "title": "测试商品",
    "price": 50.0,
    "product_score": 80.0,
    "trend": "rising",
    "keywords": ["测试"],
    "category_label": "home",
    "analyzed_at": "2026-01-01T00:00:00Z",
}


def test_missing_required_field_raises() -> None:
    matcher = SupplierMatcher()
    bad = {k: v for k, v in _BASE.items() if k != "analyzed_at"}
    with pytest.raises(MatcherError, match="analyzed_at"):
        matcher.match_product(bad)


def test_profit_formula_correct() -> None:
    matcher = SupplierMatcher(config=MatcherConfig(platform_fee_rate=0.08))
    result = matcher.match_product(_BASE)
    expected = round(
        _BASE["price"] - result["source_price"] - result["shipping_cost"] - round(_BASE["price"] * 0.08, 2),
        2,
    )
    assert result["profit_est"] == expected


def test_unknown_category_uses_other_defaults() -> None:
    matcher = SupplierMatcher()
    product = {**_BASE, "category_label": "unknown_cat"}
    result = matcher.match_product(product)
    assert result["moq"] == 2
    assert result["plain_package"] is True


def test_declining_trend_lowers_source_price() -> None:
    matcher = SupplierMatcher()
    rising = matcher.match_product({**_BASE, "trend": "rising"})
    declining = matcher.match_product({**_BASE, "trend": "declining"})
    assert declining["source_price"] < rising["source_price"]


def test_supplier_id_contains_product_id() -> None:
    matcher = SupplierMatcher()
    result = matcher.match_product(_BASE)
    assert _BASE["id"] in result["supplier_id"]


def test_match_products_batch() -> None:
    matcher = SupplierMatcher()
    products = [
        {**_BASE, "id": f"xy-{i}"}
        for i in range(3)
    ]
    results = matcher.match_products(products)
    assert len(results) == 3
    assert [r["product_id"] for r in results] == [f"xy-{i}" for i in range(3)]
