from __future__ import annotations

import pytest

from copywriter.__main__ import CopywriterError, ProductCopywriter


_BASE = {
    "id": "xy-9001",
    "platform": "xianyu",
    "title": "测试商品",
    "price": 30.0,
    "trend": "rising",
    "keywords": ["测试", "商品"],
    "category_label": "home",
    "features": {"color": None, "material": None, "style": None},
    "analyzed_at": "2026-01-01T00:00:00Z",
}


def test_missing_required_field_raises() -> None:
    copywriter = ProductCopywriter()
    bad = {k: v for k, v in _BASE.items() if k != "trend"}
    with pytest.raises(CopywriterError, match="trend"):
        copywriter.generate_draft(bad)


def test_title_within_char_limit() -> None:
    copywriter = ProductCopywriter()
    result = copywriter.generate_draft(_BASE)
    assert len(result["title"]) <= 30


def test_stable_trend_uses_steady_template() -> None:
    copywriter = ProductCopywriter()
    product = {**_BASE, "trend": "stable"}
    result = copywriter.generate_draft(product)
    assert result["template_id"] == "steady-value"


def test_tags_respect_max_limit() -> None:
    copywriter = ProductCopywriter()
    product = {
        **_BASE,
        "keywords": ["a", "b", "c", "d", "e", "f", "g"],
    }
    result = copywriter.generate_draft(product)
    assert len(result["tags"]) <= 5


def test_price_appears_in_body() -> None:
    copywriter = ProductCopywriter()
    result = copywriter.generate_draft({**_BASE, "price": 99.0})
    assert "99.00" in result["body"]


def test_generate_drafts_batch() -> None:
    copywriter = ProductCopywriter()
    products = [
        {**_BASE, "id": f"xy-{i}"}
        for i in range(3)
    ]
    results = copywriter.generate_drafts(products)
    assert len(results) == 3
    assert [r["product_id"] for r in results] == [f"xy-{i}" for i in range(3)]
