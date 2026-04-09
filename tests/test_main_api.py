from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import (
    AIRecommendation,
    AnalyzedProduct,
    AssetReviewStatus,
    CandidateBundle,
    CopyDraft,
    Decision,
    DecisionRecord,
    ImageAsset,
    ImagePromptSpec,
    ListingCopyAsset,
    MatchedSupplier,
    Platform,
    ProductFeatures,
    RawProduct,
    SearchHit,
    SearchSession,
    SearchStatus,
    SearchSummary,
    Trend,
)


def _candidate() -> CandidateBundle:
    analyzed = AnalyzedProduct(
        id="xy-2001",
        platform=Platform.XIANYU,
        platform_code="xianyu",
        platform_role="demand",
        title="奶油风桌面收纳盒",
        price=29.9,
        want_count=128,
        sales_count=None,
        image_url=None,
        category="家居收纳",
        fetched_at=datetime(2026, 4, 9, 6, 0, tzinfo=timezone.utc),
        raw_tags=["桌面", "收纳"],
        data_source="sample",
        backend_used="text",
        product_score=92.0,
        trend=Trend.RISING,
        keywords=["桌面", "收纳盒"],
        category_label="home",
        features=ProductFeatures(color="白色", style="ins"),
        analyzed_at=datetime(2026, 4, 9, 6, 1, tzinfo=timezone.utc),
        skip_reason=None,
    )
    supplier = MatchedSupplier(
        product_id="xy-2001",
        supplier_id="1688-2001",
        supplier_name="桌面家居工厂店",
        source_price=16.5,
        moq=1,
        shipping_cost=3.0,
        profit_est=10.4,
        plain_package=True,
        supplier_rating=4.8,
        matched_at=datetime(2026, 4, 9, 6, 2, tzinfo=timezone.utc),
    )
    copy_draft = CopyDraft(
        product_id="xy-2001",
        title="白色桌面收纳盒",
        body="奶油风桌搭必备，成色好，价格友好。",
        tags=["桌面", "收纳", "奶油风"],
        template_id="hot-trend",
        generated_at=datetime(2026, 4, 9, 6, 3, tzinfo=timezone.utc),
    )
    recommendation = AIRecommendation(
        product_id="xy-2001",
        recommended_sell_platform="xianyu",
        recommended_source_platform="1688",
        opportunity_score=88.0,
        confidence_score=0.82,
        reasoning=["供需差明显", "适合低成本试卖"],
        risk_flags=[],
        suggested_price_min=29.9,
        suggested_price_max=39.9,
        recommendation_version="ai-v1",
        review_status=AssetReviewStatus.REVIEW_REQUIRED,
        generated_at=datetime(2026, 4, 9, 6, 4, tzinfo=timezone.utc),
    )
    listing_copy_asset = ListingCopyAsset(
        product_id="xy-2001",
        primary_platform="xianyu",
        variants=[],
        model_version="ai-copy-v1",
        review_status=AssetReviewStatus.REVIEW_REQUIRED,
        generated_at=datetime(2026, 4, 9, 6, 5, tzinfo=timezone.utc),
    )
    image_asset = ImageAsset(
        product_id="xy-2001",
        primary_platform="xianyu",
        prompt_spec=ImagePromptSpec(
            scene="marketplace-hero",
            style="clean",
            prompt="白底商品主图，突出收纳盒容量",
        ),
        preview_url=None,
        source_image_urls=[],
        model_version="prompt-only-v1",
        review_status=AssetReviewStatus.REVIEW_REQUIRED,
        generated_at=datetime(2026, 4, 9, 6, 6, tzinfo=timezone.utc),
    )
    decision = DecisionRecord(
        product_id="xy-2001",
        decision=Decision.APPROVED,
        reason="already reviewed",
        decided_by="tester",
        decided_at=datetime(2026, 4, 9, 6, 7, tzinfo=timezone.utc),
    )
    return CandidateBundle(
        product=analyzed,
        supplier=supplier,
        copy_draft=copy_draft,
        decision=decision,
        ai_recommendation=recommendation,
        listing_copy_asset=listing_copy_asset,
        image_asset=image_asset,
    )



def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}



def test_candidates_and_summary_endpoints(monkeypatch: object) -> None:
    import app.main as main_module

    candidate = _candidate()
    monkeypatch.setattr(main_module, "get_candidate_bundles", lambda: [candidate])
    monkeypatch.setattr(main_module, "load_profit_summary", lambda: {"total_count": 1.0, "total_profit": 10.4})
    monkeypatch.setattr(main_module, "load_blacklist_summary", lambda: {"supplier_count": 0, "category_count": 0})

    client = TestClient(app)

    candidates_response = client.get("/api/candidates")
    assert candidates_response.status_code == 200
    candidates = candidates_response.json()
    assert len(candidates) == 1
    assert candidates[0]["product"]["id"] == "xy-2001"
    assert candidates[0]["copy_draft"]["template_id"] == "hot-trend"

    summary_response = client.get("/api/summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["candidate_count"] == 1
    assert summary["approved"] == 1
    assert summary["total_profit_est"] == 10.4
    assert summary["platform_opportunities"][0]["platform_code"] == "xianyu"

    platforms_response = client.get("/api/platforms")
    assert platforms_response.status_code == 200
    platforms = platforms_response.json()
    assert platforms[0]["candidate_count"] == 1
    assert platforms[0]["approved_count"] == 1



def test_save_candidate_decision_endpoint(monkeypatch: object) -> None:
    import app.main as main_module

    candidate = _candidate()
    saved: dict[str, object] = {}

    monkeypatch.setattr(main_module, "get_candidate_bundles", lambda: [candidate])

    def _fake_save_decision(record: DecisionRecord, **kwargs: object) -> None:
        saved["record"] = record
        saved["kwargs"] = kwargs

    monkeypatch.setattr(main_module, "save_decision", _fake_save_decision)

    client = TestClient(app)
    response = client.post(
        "/api/candidates/xy-2001/decision",
        json={"decision": "blacklisted", "reason": "bad fit", "decided_by": "api-tester"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["record"]["product_id"] == "xy-2001"
    assert payload["record"]["decision"] == "blacklisted"

    record = saved["record"]
    assert isinstance(record, DecisionRecord)
    assert record.decision is Decision.BLACKLISTED
    assert record.reason == "bad fit"

    kwargs = saved["kwargs"]
    assert kwargs == {
        "supplier_name": "桌面家居工厂店",
        "category_label": "home",
        "profit_est": 10.4,
        "supplier_id": "1688-2001",
    }



def test_save_candidate_decision_returns_not_found(monkeypatch: object) -> None:
    import app.main as main_module

    monkeypatch.setattr(main_module, "get_candidate_bundles", lambda: [])
    client = TestClient(app)

    response = client.post(
        "/api/candidates/missing-product/decision",
        json={"decision": "approved", "decided_by": "api-tester"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "not_found", "product_id": "missing-product"}


def _search_session() -> SearchSession:
    return SearchSession(
        id="search-001",
        keyword="收纳",
        platforms=[Platform.XIANYU, Platform.PINDUODUO],
        limit_per_platform=3,
        backend="text",
        status=SearchStatus.COMPLETED,
        created_at=datetime(2026, 4, 9, 7, 0, tzinfo=timezone.utc),
        started_at=datetime(2026, 4, 9, 7, 0, 1, tzinfo=timezone.utc),
        completed_at=datetime(2026, 4, 9, 7, 0, 2, tzinfo=timezone.utc),
        hit_count=1,
        summary=SearchSummary(
            total_hits=1,
            platform_counts={"xianyu": 1},
            data_source_counts={"real": 1},
        ),
        error_message=None,
    )


def _search_hit() -> SearchHit:
    return SearchHit(
        session_id="search-001",
        platform=Platform.XIANYU,
        keyword="收纳",
        rank=1,
        product=RawProduct(
            id="xy-real-0001",
            platform=Platform.XIANYU,
            title="桌面收纳盒",
            price=19.9,
            want_count=123,
            sales_count=None,
            image_url=None,
            category="闲鱼搜索:收纳",
            fetched_at=datetime(2026, 4, 9, 7, 0, tzinfo=timezone.utc),
            raw_tags=["桌面", "收纳"],
            data_source="real",
            backend_used="text",
            source_detail="xy-real",
            fetch_error_category=None,
        ),
    )


def test_search_endpoints(monkeypatch: object) -> None:
    import app.main as main_module

    session = _search_session()
    hit = _search_hit()

    class _FakeSearchService:
        def start_search(self, payload: object) -> SearchSession:
            return session

        def get_session(self, search_id: str) -> SearchSession | None:
            if search_id == session.id:
                return session
            return None

        def get_hits(self, search_id: str) -> list[SearchHit]:
            if search_id == session.id:
                return [hit]
            return []

    monkeypatch.setattr(main_module, "search_service", _FakeSearchService())
    client = TestClient(app)

    create_response = client.post(
        "/api/search",
        json={
            "keyword": "收纳",
            "platforms": ["xianyu", "pinduoduo"],
            "limit_per_platform": 3,
            "backend": "text",
        },
    )
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["status"] == "ok"
    assert created["session"]["id"] == "search-001"
    assert created["session"]["keyword"] == "收纳"

    get_response = client.get("/api/search/search-001")
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["status"] == "ok"
    assert fetched["session"]["status"] == "completed"

    hits_response = client.get("/api/search/search-001/hits")
    assert hits_response.status_code == 200
    hits_payload = hits_response.json()
    assert hits_payload["status"] == "ok"
    assert len(hits_payload["hits"]) == 1
    assert hits_payload["hits"][0]["product"]["title"] == "桌面收纳盒"


def test_search_endpoints_return_not_found(monkeypatch: object) -> None:
    import app.main as main_module

    class _FakeSearchService:
        def start_search(self, payload: object) -> SearchSession:
            return _search_session()

        def get_session(self, search_id: str) -> SearchSession | None:
            return None

        def get_hits(self, search_id: str) -> list[SearchHit]:
            return []

    monkeypatch.setattr(main_module, "search_service", _FakeSearchService())
    client = TestClient(app)

    get_response = client.get("/api/search/missing-search")
    assert get_response.status_code == 200
    assert get_response.json() == {"status": "not_found", "search_id": "missing-search"}

    hits_response = client.get("/api/search/missing-search/hits")
    assert hits_response.status_code == 200
    assert hits_response.json() == {"status": "not_found", "search_id": "missing-search"}
