from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from app.schemas import Platform, RawProduct, SearchHit, SearchRequest, SearchSession, SearchStatus, SearchSummary
from scraper.fetchers import FetchError, fetch_real_products


class SearchStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._sessions: dict[str, SearchSession] = {}
        self._hits: dict[str, list[SearchHit]] = {}

    def create_session(self, session: SearchSession) -> SearchSession:
        with self._lock:
            self._sessions[session.id] = session
            self._hits[session.id] = []
        return session

    def update_session(self, session: SearchSession) -> SearchSession:
        with self._lock:
            self._sessions[session.id] = session
        return session

    def save_hits(self, session_id: str, hits: list[SearchHit]) -> None:
        with self._lock:
            self._hits[session_id] = list(hits)

    def get_session(self, session_id: str) -> SearchSession | None:
        with self._lock:
            return self._sessions.get(session_id)

    def get_hits(self, session_id: str) -> list[SearchHit]:
        with self._lock:
            return list(self._hits.get(session_id, []))


class SearchService:
    def __init__(self, store: SearchStore | None = None) -> None:
        self._store = store or SearchStore()

    def start_search(self, request: SearchRequest) -> SearchSession:
        now = datetime.now(timezone.utc)
        platforms = request.platforms or list(Platform)
        session = SearchSession(
            id=f"search-{uuid4().hex[:12]}",
            keyword=request.keyword.strip(),
            platforms=platforms,
            limit_per_platform=request.limit_per_platform,
            backend=request.backend,
            status=SearchStatus.PENDING,
            created_at=now,
        )
        self._store.create_session(session)
        return self._run_search(session)

    def get_session(self, session_id: str) -> SearchSession | None:
        return self._store.get_session(session_id)

    def get_hits(self, session_id: str) -> list[SearchHit]:
        return self._store.get_hits(session_id)

    def _run_search(self, session: SearchSession) -> SearchSession:
        started = session.model_copy(update={"status": SearchStatus.RUNNING, "started_at": datetime.now(timezone.utc)})
        self._store.update_session(started)

        collected_hits: list[SearchHit] = []
        errors: list[str] = []

        for platform in started.platforms:
            try:
                records = fetch_real_products(
                    platform=platform.value,
                    limit=started.limit_per_platform,
                    backend=started.backend,
                    keyword=started.keyword,
                )
            except FetchError as exc:
                errors.append(f"{platform.value}: {exc}")
                continue

            for rank, payload in enumerate(records, start=1):
                raw_product = RawProduct.model_validate(payload)
                collected_hits.append(
                    SearchHit(
                        session_id=started.id,
                        platform=platform,
                        keyword=started.keyword,
                        rank=rank,
                        product=raw_product,
                    )
                )

        summary = self._build_summary(collected_hits)
        status = SearchStatus.COMPLETED
        error_message: str | None = None
        if errors and collected_hits:
            status = SearchStatus.PARTIAL
            error_message = " | ".join(errors)
        elif errors:
            status = SearchStatus.FAILED
            error_message = " | ".join(errors)

        finished = started.model_copy(
            update={
                "status": status,
                "completed_at": datetime.now(timezone.utc),
                "hit_count": len(collected_hits),
                "summary": summary,
                "error_message": error_message,
            }
        )
        self._store.save_hits(finished.id, collected_hits)
        self._store.update_session(finished)
        return finished

    def _build_summary(self, hits: list[SearchHit]) -> SearchSummary:
        platform_counts = Counter(hit.platform.value for hit in hits)
        data_source_counts = Counter(hit.product.data_source for hit in hits)
        return SearchSummary(
            total_hits=len(hits),
            platform_counts=dict(sorted(platform_counts.items())),
            data_source_counts=dict(sorted(data_source_counts.items())),
        )



search_service = SearchService()
