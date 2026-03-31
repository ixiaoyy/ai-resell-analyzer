from __future__ import annotations

from app.pipeline import build_candidate_bundles


def build_sample_candidates() -> list[CandidateBundle]:
    return build_candidate_bundles()
