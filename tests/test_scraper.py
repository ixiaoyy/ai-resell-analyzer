from scraper.__main__ import ProductScraper, ScraperError, summarize_products
from scraper.fetchers import (
    BasePageFetcher,
    _extract_pinduoduo_records,
    _extract_signal_from_context,
    _extract_xianyu_records,
    fetch_real_products,
)

import pytest


REQUIRED_FIELDS = {
    "id",
    "platform",
    "title",
    "price",
    "fetched_at",
    "data_source",
    "backend_used",
    "source_detail",
    "fetch_error_category",
}


def test_scrape_all_returns_raw_product_fields() -> None:
    scraper = ProductScraper(use_real_source=False, use_sample_fallback=True, backend="text")
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
    scraper = ProductScraper(use_real_source=False, use_sample_fallback=True, backend="text")
    products = scraper.scrape(platform="xianyu", count=10)

    assert len(products) >= 1
    for p in products:
        assert p["platform"] == "xianyu"
        assert "want_count" in p


def test_scrape_pinduoduo_only() -> None:
    scraper = ProductScraper(use_real_source=False, use_sample_fallback=True, backend="text")
    products = scraper.scrape(platform="pinduoduo", count=10)

    assert len(products) >= 1
    for p in products:
        assert p["platform"] == "pinduoduo"
        assert "sales_count" in p


def test_scrape_count_limits_results() -> None:
    scraper = ProductScraper(use_real_source=False, use_sample_fallback=True, backend="text")
    products = scraper.scrape(platform="all", count=2)
    assert len(products) == 2


def test_scrape_default_count() -> None:
    scraper = ProductScraper(use_real_source=False, use_sample_fallback=True, backend="text")
    products = scraper.scrape()
    assert len(products) == 3


def test_scrape_invalid_platform_raises() -> None:
    scraper = ProductScraper(use_real_source=False, use_sample_fallback=True, backend="text")
    with pytest.raises(ScraperError, match="Invalid platform"):
        scraper.scrape(platform="taobao")


def test_scrape_invalid_count_raises() -> None:
    scraper = ProductScraper(use_real_source=False, use_sample_fallback=True, backend="text")
    with pytest.raises(ScraperError, match="count must be"):
        scraper.scrape(count=0)


def test_scrape_output_is_valid_raw_product_schema() -> None:
    scraper = ProductScraper(use_real_source=False, use_sample_fallback=True, backend="text")
    products = scraper.scrape(platform="all", count=5)

    for p in products:
        assert isinstance(p["id"], str) and p["id"]
        assert p["platform"] in ("xianyu", "pinduoduo")
        assert isinstance(p["title"], str) and p["title"]
        assert isinstance(p["price"], (int, float)) and p["price"] > 0
        assert isinstance(p["fetched_at"], str) and p["fetched_at"].endswith("Z")
        if "want_count" in p:
            assert p["want_count"] is None or isinstance(p["want_count"], int)
        if "sales_count" in p:
            assert p["sales_count"] is None or isinstance(p["sales_count"], int)
        if "raw_tags" in p:
            assert isinstance(p["raw_tags"], list)


def test_scrape_returns_empty_without_fallback_when_real_source_disabled() -> None:
    scraper = ProductScraper(use_real_source=False, use_sample_fallback=False, backend="text")
    products = scraper.scrape(platform="all", count=5)
    assert products == []


def test_scrape_accepts_explicit_backend_configuration() -> None:
    scraper = ProductScraper(use_real_source=False, use_sample_fallback=True, backend="browser")
    products = scraper.scrape(platform="all", count=2)
    assert len(products) == 2



def test_sample_fallback_marks_source_and_error_category(monkeypatch: pytest.MonkeyPatch) -> None:
    from scraper import __main__ as scraper_main

    def _fail_fetch_real_products(*args: object, **kwargs: object) -> list[dict]:
        raise scraper_main.FetchError("Playwright fetch failed for url: timeout")

    monkeypatch.setattr(scraper_main, "fetch_real_products", _fail_fetch_real_products)
    scraper = ProductScraper(use_real_source=True, use_sample_fallback=True, backend="browser")
    products = scraper.scrape(platform="all", count=2)

    assert len(products) == 2
    assert all(item["data_source"] == "sample" for item in products)
    assert all(item["backend_used"] == "sample" for item in products)
    assert all(item["source_detail"] == "sample:all" for item in products)
    assert all(item["fetch_error_category"] == "timeout" for item in products)



def test_real_scrape_result_includes_observability_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    from scraper import __main__ as scraper_main

    monkeypatch.setattr(
        scraper_main,
        "fetch_real_products",
        lambda **kwargs: [
            {
                "id": "xy-real-1",
                "platform": "xianyu",
                "title": "测试商品",
                "price": 19.9,
                "fetched_at": "2026-04-09T06:00:00Z",
                "data_source": "real",
                "backend_used": "text",
                "source_detail": "xianyu:text:keyword=收纳",
                "fetch_error_category": None,
            }
        ],
    )
    scraper = ProductScraper(use_real_source=True, use_sample_fallback=True, backend="text")
    products = scraper.scrape(platform="xianyu", count=1)

    assert products[0]["data_source"] == "real"
    assert products[0]["backend_used"] == "text"
    assert products[0]["source_detail"] == "xianyu:text:keyword=收纳"
    assert products[0]["fetch_error_category"] is None



def test_fetch_real_products_balances_all_platform_limits(monkeypatch: pytest.MonkeyPatch) -> None:
    from scraper import fetchers as fetchers_module

    captured: list[tuple[str, int, str | None]] = []

    class _FakeSource:
        def __init__(self, platform_code: str) -> None:
            self._platform_code = platform_code

        def fetch(self, limit: int, keyword: str | None = None) -> list[dict[str, object]]:
            captured.append((self._platform_code, limit, keyword))
            return [
                {
                    "id": f"{self._platform_code}-{index}",
                    "platform": self._platform_code,
                    "title": f"商品{index}",
                    "price": 9.9 + index,
                    "fetched_at": "2026-04-09T06:00:00Z",
                    "data_source": "real",
                    "backend_used": "text",
                    "source_detail": f"{self._platform_code}:text:keyword={keyword or ''}",
                    "fetch_error_category": None,
                }
                for index in range(limit)
            ]

    monkeypatch.setattr(
        fetchers_module,
        "REAL_SOURCE_FACTORIES",
        {
            "xianyu": lambda page_fetcher: _FakeSource("xianyu"),
            "pinduoduo": lambda page_fetcher: _FakeSource("pinduoduo"),
        },
    )

    products = fetch_real_products(platform="all", limit=5, backend="text", keyword="收纳")

    assert len(products) == 5
    assert sorted(limit for _, limit, _ in captured) == [2, 3]
    assert {platform for platform, _, _ in captured} == {"xianyu", "pinduoduo"}
    assert {keyword for _, _, keyword in captured} == {"收纳"}



def test_fetch_real_products_uses_actual_backend_in_source_detail() -> None:
    class _FakeFetcher(BasePageFetcher):
        backend_name = "base"

        def __init__(self) -> None:
            self.last_backend_used = "proxy"

        def fetch_text(self, url: str) -> str:
            assert "goofish.com/search" in url
            return "奶油风桌面收纳盒 ¥29.9\n168人想要"

    products = fetch_real_products(
        platform="xianyu",
        limit=1,
        backend="auto",
        fetcher=_FakeFetcher(),
        keyword="收纳",
    )

    assert len(products) == 1
    assert products[0]["backend_used"] == "proxy"
    assert products[0]["source_detail"] == "xianyu:proxy:keyword=收纳"



def test_extract_xianyu_records_reads_contextual_want_count() -> None:
    text = """
    奶油风桌面收纳盒 ¥29.9
    168人想要
    北欧风脏衣篮 ¥39.9
    96人想要
    """

    products = _extract_xianyu_records(
        text=text,
        prefix="xy-test",
        fallback_category="闲鱼搜索",
        limit=5,
        backend_used="text",
        source_detail="xianyu:text:keyword=收纳",
    )

    assert len(products) == 2
    assert products[0]["want_count"] == 168
    assert products[0]["category"] == "家居收纳"
    assert products[0]["data_source"] == "real"
    assert products[0]["backend_used"] == "text"
    assert products[0]["source_detail"] == "xianyu:text:keyword=收纳"
    assert products[1]["want_count"] == 96



def test_extract_pinduoduo_records_reads_contextual_sales_count() -> None:
    text = """
    宿舍床边折叠小夜灯 ¥29.9
    已拼1824件
    蓝牙耳机 迷你降噪通勤款 ¥59.0
    已拼356件
    """

    products = _extract_pinduoduo_records(
        text=text,
        prefix="pdd-test",
        fallback_category="拼多多搜索",
        limit=5,
        backend_used="browser",
        source_detail="pinduoduo:browser:keyword=宿舍",
    )

    assert len(products) == 2
    assert products[0]["sales_count"] == 1824
    assert products[0]["category"] == "宿舍用品"
    assert products[0]["data_source"] == "real"
    assert products[0]["backend_used"] == "browser"
    assert products[0]["source_detail"] == "pinduoduo:browser:keyword=宿舍"
    assert products[1]["sales_count"] == 356



def test_extract_signal_from_context_returns_none_when_keyword_missing() -> None:
    lines = ["奶油风桌面收纳盒 ¥29.9", "包邮", "现货"]
    assert _extract_signal_from_context(lines, index=0, keyword="已拼") is None



def test_summarize_products_aggregates_observability_fields() -> None:
    products = [
        {
            "id": "xy-real-1",
            "platform": "xianyu",
            "data_source": "real",
            "backend_used": "text",
            "fetch_error_category": None,
        },
        {
            "id": "xy-sample-1",
            "platform": "xianyu",
            "data_source": "sample",
            "backend_used": "sample",
            "fetch_error_category": "timeout",
        },
        {
            "id": "pdd-sample-1",
            "platform": "pinduoduo",
            "data_source": "sample",
            "backend_used": "sample",
            "fetch_error_category": "timeout",
        },
    ]

    summary = summarize_products(products)

    assert summary["total"] == 3
    assert summary["platforms"] == {"pinduoduo": 1, "xianyu": 2}
    assert summary["data_sources"] == {"real": 1, "sample": 2}
    assert summary["backends"] == {"sample": 2, "text": 1}
    assert summary["error_categories"] == {"none": 1, "timeout": 2}
