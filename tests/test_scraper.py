from scraper.__main__ import ProductScraper, ScraperError

import pytest


REQUIRED_FIELDS = {"id", "platform", "title", "price", "fetched_at"}


def test_scrape_all_returns_raw_product_fields() -> None:
    scraper = ProductScraper()
    products = scraper.scrape(platform="all", count=3)

    assert len(products) == 3
    for p in products:
        missing = REQUIRED_FIELDS - p.keys()
        assert not missing, f"Missing fields: {missing}"
        assert isinstance(p["id"], str)
        assert p["platform"] in ("xianyu", "pinduoduo")
        assert isinstance(p["price"], (int, float))
        assert p["fetched_at"].endswith("Z")


def test_scrape_xianyu_only() -> None:
    scraper = ProductScraper()
    products = scraper.scrape(platform="xianyu", count=10)

    assert len(products) >= 1
    for p in products:
        assert p["platform"] == "xianyu"
        assert "want_count" in p


def test_scrape_pinduoduo_only() -> None:
    scraper = ProductScraper()
    products = scraper.scrape(platform="pinduoduo", count=10)

    assert len(products) >= 1
    for p in products:
        assert p["platform"] == "pinduoduo"
        assert "sales_count" in p


def test_scrape_count_limits_results() -> None:
    scraper = ProductScraper()
    products = scraper.scrape(platform="all", count=2)
    assert len(products) == 2


def test_scrape_default_count() -> None:
    scraper = ProductScraper()
    products = scraper.scrape()
    assert len(products) == 5


def test_scrape_invalid_platform_raises() -> None:
    scraper = ProductScraper()
    with pytest.raises(ScraperError, match="Invalid platform"):
        scraper.scrape(platform="taobao")


def test_scrape_invalid_count_raises() -> None:
    scraper = ProductScraper()
    with pytest.raises(ScraperError, match="count must be"):
        scraper.scrape(count=0)


def test_scrape_output_is_valid_raw_product_schema() -> None:
    scraper = ProductScraper()
    products = scraper.scrape(platform="all", count=5)

    for p in products:
        # required fields present and correct types
        assert isinstance(p["id"], str) and p["id"]
        assert p["platform"] in ("xianyu", "pinduoduo")
        assert isinstance(p["title"], str) and p["title"]
        assert isinstance(p["price"], (int, float)) and p["price"] > 0
        assert isinstance(p["fetched_at"], str) and p["fetched_at"].endswith("Z")
        # optional fields type-check when present
        if "want_count" in p:
            assert isinstance(p["want_count"], int)
        if "sales_count" in p:
            assert isinstance(p["sales_count"], int)
        if "raw_tags" in p:
            assert isinstance(p["raw_tags"], list)
