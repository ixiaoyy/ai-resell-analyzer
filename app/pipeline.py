from __future__ import annotations

import json
from pathlib import Path

from analyzer import analyze_products
from app.schemas import AnalyzedProduct, CandidateBundle, CopyDraft, MatchedSupplier, RawProduct
from app.storage import load_decisions
from copywriter import build_copy_drafts
from matcher import match_suppliers
from scraper import build_sample_raw_products

RAW_PATH = Path("data") / "raw" / "all_latest.json"
ANALYZED_PATH = Path("data") / "analyzed" / "analyzed_latest.json"
MATCHED_PATH = Path("data") / "matched" / "matched_latest.json"
COPY_PATH = Path("data") / "copy" / "copy_latest.json"


def build_pipeline_outputs(use_sample_fallback: bool = True) -> tuple[list[AnalyzedProduct], dict[str, MatchedSupplier], dict[str, CopyDraft]]:
    raw_products = _load_raw_products(use_sample_fallback=use_sample_fallback)
    analyzed_products = _load_or_build_analyzed_products(raw_products)
    candidate_products = [product for product in analyzed_products if not product.skip_reason]
    suppliers = _load_or_build_suppliers(candidate_products)
    copies = _load_or_build_copies(candidate_products, suppliers)
    return analyzed_products, suppliers, copies


def build_candidate_bundles() -> list[CandidateBundle]:
    analyzed_products, suppliers, copies = build_pipeline_outputs(use_sample_fallback=True)
    decisions = load_decisions()
    return [
        CandidateBundle(
            product=product,
            supplier=suppliers.get(product.id),
            copy=copies.get(product.id),
            decision=decisions.get(product.id),
        )
        for product in analyzed_products
        if not product.skip_reason
    ]


def _load_raw_products(use_sample_fallback: bool) -> list[RawProduct]:
    if RAW_PATH.exists():
        return [RawProduct.model_validate(item) for item in _read_json(RAW_PATH)]
    if use_sample_fallback:
        return build_sample_raw_products()
    return []


def _load_or_build_analyzed_products(raw_products: list[RawProduct]) -> list[AnalyzedProduct]:
    if ANALYZED_PATH.exists():
        return [AnalyzedProduct.model_validate(item) for item in _read_json(ANALYZED_PATH)]
    return analyze_products(raw_products)


def _load_or_build_suppliers(products: list[AnalyzedProduct]) -> dict[str, MatchedSupplier]:
    if MATCHED_PATH.exists():
        return {
            supplier.product_id: supplier
            for supplier in (MatchedSupplier.model_validate(item) for item in _read_json(MATCHED_PATH))
        }
    return {supplier.product_id: supplier for supplier in match_suppliers(products)}


def _load_or_build_copies(products: list[AnalyzedProduct], suppliers: dict[str, MatchedSupplier]) -> dict[str, CopyDraft]:
    if COPY_PATH.exists():
        return {
            draft.product_id: draft
            for draft in (CopyDraft.model_validate(item) for item in _read_json(COPY_PATH))
        }
    return {draft.product_id: draft for draft in build_copy_drafts(products, suppliers)}


def _read_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))
