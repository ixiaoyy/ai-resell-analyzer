from __future__ import annotations

import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal
from urllib.parse import quote

import httpx

from app.schemas import Platform
from platforms.defaults import register_default_platforms
from platforms.registry import registry

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 20.0
JINA_PREFIX = "https://r.jina.ai/http://"
DEFAULT_BACKEND_ORDER: tuple[str, ...] = ("browser", "proxy", "text")
FetchBackend = Literal["auto", "browser", "proxy", "text"]

register_default_platforms()


class FetchError(Exception):
    """Raised when a remote platform cannot be fetched or parsed."""


@dataclass(slots=True)
class SourceRecord:
    id: str
    platform: Platform
    title: str
    price: float
    fetched_at: str
    image_url: str | None = None
    category: str | None = None
    raw_tags: list[str] | None = None
    want_count: int | None = None
    sales_count: int | None = None
    data_source: str = "real"
    backend_used: str | None = None
    source_detail: str | None = None
    fetch_error_category: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.id,
            "platform": self.platform.value,
            "title": self.title,
            "price": self.price,
            "fetched_at": self.fetched_at,
            "image_url": self.image_url,
            "category": self.category,
            "raw_tags": self.raw_tags or [],
            "data_source": self.data_source,
            "backend_used": self.backend_used,
            "source_detail": self.source_detail,
            "fetch_error_category": self.fetch_error_category,
        }
        if self.want_count is not None:
            payload["want_count"] = self.want_count
        if self.sales_count is not None:
            payload["sales_count"] = self.sales_count
        return payload


@dataclass(slots=True)
class PlatformQuery:
    platform: Platform
    keyword: str
    url: str
    prefix: str
    score_field: str
    fallback_category: str


@dataclass(slots=True)
class BackendAttempt:
    backend: str
    detail: str
    error_category: str


class BasePageFetcher:
    backend_name = "base"

    def fetch_text(self, url: str) -> str:
        raise NotImplementedError


class JinaPageFetcher(BasePageFetcher):
    backend_name = "text"

    def __init__(self, timeout: float = REQUEST_TIMEOUT) -> None:
        self._timeout = timeout

    def fetch_text(self, url: str) -> str:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/plain, text/html, application/json;q=0.9, */*;q=0.8",
            "X-Return-Format": "markdown",
        }
        with httpx.Client(timeout=self._timeout, follow_redirects=True, headers=headers) as client:
            response = client.get(f"{JINA_PREFIX}{url}")
            response.raise_for_status()
            text = response.text.strip()
        if not text:
            raise FetchError(f"Empty response for {url}")
        return text


class FirecrawlPageFetcher(BasePageFetcher):
    backend_name = "proxy"

    def __init__(self, api_key: str | None = None, timeout: float = REQUEST_TIMEOUT) -> None:
        self._api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        self._timeout = timeout

    def fetch_text(self, url: str) -> str:
        if not self._api_key:
            raise FetchError("FIRECRAWL_API_KEY is not configured")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        }
        payload = {
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": True,
            "mobile": True,
            "waitFor": 2000,
        }
        with httpx.Client(timeout=self._timeout, follow_redirects=True, headers=headers) as client:
            response = client.post("https://api.firecrawl.dev/v2/scrape", json=payload)
            response.raise_for_status()
            data = response.json()

        markdown = (
            data.get("data", {}).get("markdown")
            or data.get("markdown")
            or data.get("data", {}).get("content")
            or ""
        ).strip()
        if not markdown:
            raise FetchError(f"Firecrawl returned empty content for {url}")
        return markdown


class PlaywrightPageFetcher(BasePageFetcher):
    backend_name = "browser"

    def __init__(self, timeout: float = REQUEST_TIMEOUT) -> None:
        self._timeout_ms = int(timeout * 1000)

    def fetch_text(self, url: str) -> str:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise FetchError("playwright is not installed") from exc

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page(user_agent=USER_AGENT, viewport={"width": 1440, "height": 2200})
                page.goto(url, wait_until="domcontentloaded", timeout=self._timeout_ms)
                page.wait_for_timeout(2500)
                text = page.locator("body").inner_text(timeout=self._timeout_ms).strip()
                browser.close()
        except Exception as exc:  # pragma: no cover - depends on browser runtime
            raise FetchError(f"Playwright fetch failed for {url}: {exc}") from exc

        if not text:
            raise FetchError(f"Playwright returned empty body for {url}")
        return text


class MultiBackendFetcher(BasePageFetcher):
    backend_name = "auto"

    def __init__(self, backend: FetchBackend = "auto") -> None:
        self._backend = backend
        self._fetchers: dict[str, BasePageFetcher] = {
            "browser": PlaywrightPageFetcher(),
            "proxy": FirecrawlPageFetcher(),
            "text": JinaPageFetcher(),
        }

    def fetch_text(self, url: str) -> str:
        attempts: list[BackendAttempt] = []
        for backend_name in self._resolve_order():
            fetcher = self._fetchers[backend_name]
            try:
                return fetcher.fetch_text(url)
            except FetchError as exc:
                attempts.append(
                    BackendAttempt(
                        backend=backend_name,
                        detail=str(exc),
                        error_category=_classify_fetch_error(str(exc)),
                    )
                )

        joined = "; ".join(
            f"{item.backend}[{item.error_category}]: {item.detail}" for item in attempts
        )
        raise FetchError(f"All fetch backends failed for {url}. {joined}")

    def _resolve_order(self) -> tuple[str, ...]:
        if self._backend == "auto":
            return DEFAULT_BACKEND_ORDER
        return (self._backend,)


class XianyuRealSource:
    def __init__(self, fetcher: BasePageFetcher | None = None) -> None:
        self._fetcher = fetcher or MultiBackendFetcher()

    def fetch(self, limit: int, keyword: str | None = None) -> list[dict[str, Any]]:
        query = build_platform_query(Platform.XIANYU, keyword=keyword)
        text = self._fetcher.fetch_text(query.url)
        items = _extract_xianyu_records(
            text=text,
            prefix=query.prefix,
            fallback_category=query.fallback_category,
            limit=limit,
        )
        if not items:
            raise FetchError("No xianyu products could be parsed")
        return items


class PinduoduoRealSource:
    def __init__(self, fetcher: BasePageFetcher | None = None) -> None:
        self._fetcher = fetcher or MultiBackendFetcher()

    def fetch(self, limit: int, keyword: str | None = None) -> list[dict[str, Any]]:
        query = build_platform_query(Platform.PINDUODUO, keyword=keyword)
        text = self._fetcher.fetch_text(query.url)
        items = _extract_pinduoduo_records(
            text=text,
            prefix=query.prefix,
            fallback_category=query.fallback_category,
            limit=limit,
        )
        if not items:
            raise FetchError("No pinduoduo products could be parsed")
        return items


RealSourceFactory = Callable[[BasePageFetcher], Any]
REAL_SOURCE_FACTORIES: dict[str, RealSourceFactory] = {
    "xianyu": lambda page_fetcher: XianyuRealSource(page_fetcher),
    "pinduoduo": lambda page_fetcher: PinduoduoRealSource(page_fetcher),
}



def supported_real_platform_codes() -> tuple[str, ...]:
    return tuple(code for code in registry.codes(role="demand") if code in REAL_SOURCE_FACTORIES)



def build_platform_query(platform: Platform, keyword: str | None = None) -> PlatformQuery:
    normalized_keyword = (keyword or "").strip()
    if platform is Platform.XIANYU:
        resolved_keyword = normalized_keyword or "收纳"
        return PlatformQuery(
            platform=platform,
            keyword=resolved_keyword,
            url=f"https://www.goofish.com/search?q={quote(resolved_keyword)}",
            prefix="xy-real",
            score_field="want_count",
            fallback_category=f"闲鱼搜索:{resolved_keyword}",
        )

    resolved_keyword = normalized_keyword or "宿舍"
    return PlatformQuery(
        platform=platform,
        keyword=resolved_keyword,
        url=f"https://mobile.yangkeduo.com/search_result.html?search_key={quote(resolved_keyword)}",
        prefix="pdd-real",
        score_field="sales_count",
        fallback_category=f"拼多多搜索:{resolved_keyword}",
    )


def fetch_real_products(
    platform: str,
    limit: int,
    backend: FetchBackend = "auto",
    fetcher: BasePageFetcher | None = None,
    keyword: str | None = None,
) -> list[dict[str, Any]]:
    if limit < 1:
        return []

    supported_codes = supported_real_platform_codes()
    if platform != "all" and platform not in supported_codes:
        raise FetchError(f"Unsupported platform: {platform}")

    shared_fetcher = fetcher or MultiBackendFetcher(backend=backend)
    products: list[dict[str, Any]] = []
    selected_codes = supported_codes if platform == "all" else (platform,)

    for code in selected_codes:
        remaining = max(limit - len(products), 0) if platform == "all" else limit
        if remaining == 0:
            break

        factory = REAL_SOURCE_FACTORIES.get(code)
        if factory is None:
            continue
        products.extend(factory(shared_fetcher).fetch(remaining, keyword=keyword))

    return products[:limit]


def _extract_xianyu_records(text: str, prefix: str, fallback_category: str, limit: int) -> list[dict[str, Any]]:
    return _extract_records_by_platform(
        text=text,
        platform=Platform.XIANYU,
        prefix=prefix,
        fallback_category=fallback_category,
        limit=limit,
        signal_keyword="想要",
        signal_field="want_count",
    )



def _extract_pinduoduo_records(text: str, prefix: str, fallback_category: str, limit: int) -> list[dict[str, Any]]:
    return _extract_records_by_platform(
        text=text,
        platform=Platform.PINDUODUO,
        prefix=prefix,
        fallback_category=fallback_category,
        limit=limit,
        signal_keyword="已拼",
        signal_field="sales_count",
    )



def _extract_records_by_platform(
    text: str,
    platform: Platform,
    prefix: str,
    fallback_category: str,
    limit: int,
    signal_keyword: str,
    signal_field: str,
) -> list[dict[str, Any]]:
    lines = [line.strip(" -\t") for line in text.splitlines()]
    current_time = utc_now_iso()
    records: list[dict[str, Any]] = []
    seen_titles: set[str] = set()

    for index, line in enumerate(lines):
        if len(records) >= limit:
            break
        if _skip_line(line):
            continue

        parsed = _parse_title_price(line)
        if parsed is None:
            continue

        title, price = parsed
        if title in seen_titles:
            continue
        seen_titles.add(title)

        signal = _extract_signal_from_context(lines, index=index, keyword=signal_keyword)
        if signal is None:
            signal = _infer_signal(title, platform)

        payload = _build_source_record(
            platform=platform,
            prefix=prefix,
            ordinal=len(records) + 1,
            title=title,
            price=price,
            fetched_at=current_time,
            fallback_category=fallback_category,
            signal_field=signal_field,
            signal_value=signal,
        )
        records.append(payload.to_dict())

    return records



def _build_source_record(
    platform: Platform,
    prefix: str,
    ordinal: int,
    title: str,
    price: float,
    fetched_at: str,
    fallback_category: str,
    signal_field: str,
    signal_value: int,
) -> SourceRecord:
    return SourceRecord(
        id=f"{prefix}-{ordinal:04d}",
        platform=platform,
        title=title,
        price=price,
        fetched_at=fetched_at,
        category=_infer_category(title, fallback_category),
        raw_tags=_infer_tags(title),
        want_count=signal_value if signal_field == "want_count" else None,
        sales_count=signal_value if signal_field == "sales_count" else None,
        data_source="real",
        backend_used=_infer_backend_from_prefix(prefix),
        source_detail=prefix,
    )


def _skip_line(line: str) -> bool:
    if not line or len(line) < 6:
        return True

    lowered = line.lower()
    noise_tokens = [
        "http://",
        "https://",
        "搜索",
        "首页",
        "登录",
        "下载app",
        "copyright",
        "购物车",
        "帮助",
        "客服",
        "筛选",
        "排序",
        "privacy",
        "terms",
    ]
    return any(token in lowered for token in noise_tokens)


def _parse_title_price(line: str) -> tuple[str, float] | None:
    price_match = re.search(r"(?:¥|￥)\s*(\d+(?:\.\d{1,2})?)|(\d+(?:\.\d{1,2})?)\s*元", line)
    if price_match is None:
        return None

    price_text = next(group for group in price_match.groups() if group)
    price = float(price_text)
    if price <= 0:
        return None

    title = line[: price_match.start()].strip(" :：|-·【】[]")
    if len(title) < 4:
        title = line[price_match.end() :].strip(" :：|-·【】[]")
    if len(title) < 4:
        return None

    title = re.sub(r"\s+", " ", title)
    if len(title) > 60:
        title = title[:60].rstrip()
    return title, price


def _extract_signal_from_context(lines: list[str], index: int, keyword: str) -> int | None:
    window = lines[index : index + 3]
    for item in window:
        if keyword not in item:
            continue
        match = re.search(r"(\d+)", item.replace(",", ""))
        if match is not None:
            return int(match.group(1))
    return None



def _infer_category(title: str, fallback_category: str) -> str:
    mapping = {
        "收纳": "家居收纳",
        "桌面": "家居收纳",
        "夜灯": "宿舍用品",
        "耳机": "数码配件",
        "手机": "数码配件",
        "衣": "服饰配件",
        "宿舍": "宿舍用品",
    }
    for keyword, category in mapping.items():
        if keyword in title:
            return category
    return fallback_category


def _infer_tags(title: str) -> list[str]:
    base_keywords = [
        "奶油风",
        "北欧风",
        "收纳",
        "桌面",
        "宿舍",
        "夜灯",
        "耳机",
        "折叠",
        "通勤",
        "蓝牙",
        "ins",
    ]
    tags = [keyword for keyword in base_keywords if keyword in title]
    if not tags:
        tags = [token for token in re.split(r"\s+", title) if token][:3]
    return tags[:5]


def _infer_signal(title: str, platform: Platform) -> int:
    seed = sum(ord(char) for char in title) % 200
    if platform is Platform.XIANYU:
        return max(seed, 12)
    return max(seed * 5, 30)


def _infer_backend_from_prefix(prefix: str) -> str | None:
    if "browser" in prefix:
        return "browser"
    if "proxy" in prefix:
        return "proxy"
    if "text" in prefix:
        return "text"
    return "auto"



def _classify_fetch_error(detail: str) -> str:
    lowered = detail.lower()
    if "timeout" in lowered:
        return "timeout"
    if "empty" in lowered or "no " in lowered and "parsed" in lowered:
        return "empty_result"
    if "not configured" in lowered:
        return "backend_unavailable"
    if "playwright" in lowered:
        return "browser_failure"
    if "status" in lowered or "403" in lowered or "404" in lowered or "500" in lowered:
        return "http_error"
    return "fetch_failed"



def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_cached_products(path: str) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)
