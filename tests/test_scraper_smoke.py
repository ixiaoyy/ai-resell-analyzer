from __future__ import annotations

import os

import pytest

from scraper.__main__ import ProductScraper


RUN_REAL_SCRAPER_SMOKE = os.getenv("RUN_REAL_SCRAPER_SMOKE") == "1"


@pytest.mark.skipif(not RUN_REAL_SCRAPER_SMOKE, reason="set RUN_REAL_SCRAPER_SMOKE=1 to run real scraper smoke test")
def test_real_scraper_smoke() -> None:
    scraper = ProductScraper(use_real_source=True, use_sample_fallback=False, backend="auto")
    products = scraper.scrape(platform="all", count=1)

    assert products, "real scraper returned no products"
    first = products[0]
    assert first["data_source"] == "real"
    assert first["backend_used"] in {"auto", "browser", "proxy", "text"} or first["backend_used"]
    assert first["source_detail"]
    assert first["fetch_error_category"] is None
