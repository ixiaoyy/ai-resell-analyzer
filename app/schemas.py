from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Platform(str, Enum):
    XIANYU = "xianyu"
    PINDUODUO = "pinduoduo"


class AssetReviewStatus(str, Enum):
    DRAFT = "draft"
    REVIEW_REQUIRED = "review_required"
    APPROVED = "approved"
    REJECTED = "rejected"


class Trend(str, Enum):
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"


class Decision(str, Enum):
    APPROVED = "approved"
    SKIPPED = "skipped"
    BLACKLISTED = "blacklisted"


class SearchStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class ProductFeatures(BaseModel):
    color: str | None = None
    material: str | None = None
    style: str | None = None


class RawProduct(BaseModel):
    id: str
    platform: Platform
    platform_code: str | None = None
    platform_role: str = "demand"
    title: str
    price: float = Field(ge=0)
    want_count: int | None = Field(default=None, ge=0)
    sales_count: int | None = Field(default=None, ge=0)
    image_url: str | None = None
    category: str | None = None
    fetched_at: datetime
    raw_tags: list[str] = Field(default_factory=list)
    data_source: str = "real"
    backend_used: str | None = None
    source_detail: str | None = None
    fetch_error_category: str | None = None


class AnalyzedProduct(RawProduct):
    product_score: float = Field(ge=0, le=100)
    trend: Trend
    keywords: list[str] = Field(default_factory=list)
    category_label: str
    features: ProductFeatures | None = None
    analyzed_at: datetime
    skip_reason: str | None = None


class MatchedSupplier(BaseModel):
    product_id: str
    supplier_id: str
    supplier_name: str
    source_price: float = Field(ge=0)
    moq: int = Field(ge=1)
    shipping_cost: float = Field(ge=0)
    profit_est: float
    plain_package: bool
    supplier_rating: float | None = Field(default=None, ge=0, le=5)
    matched_at: datetime


class CopyDraft(BaseModel):
    product_id: str
    title: str = Field(max_length=30)
    body: str
    tags: list[str] = Field(default_factory=list, max_length=5)
    template_id: str
    generated_at: datetime


class DecisionRecord(BaseModel):
    product_id: str
    decision: Decision
    reason: str | None = None
    decided_by: str
    decided_at: datetime


class AIRecommendation(BaseModel):
    product_id: str
    recommended_sell_platform: str
    recommended_source_platform: str
    opportunity_score: float = Field(ge=0, le=100)
    confidence_score: float = Field(ge=0, le=1)
    reasoning: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    suggested_price_min: float = Field(ge=0)
    suggested_price_max: float = Field(ge=0)
    recommendation_version: str = "ai-v1"
    review_status: AssetReviewStatus = AssetReviewStatus.REVIEW_REQUIRED
    generated_at: datetime


class CopyVariant(BaseModel):
    channel: str
    title: str = Field(max_length=60)
    body: str
    tags: list[str] = Field(default_factory=list, max_length=8)
    tone: str


class ListingCopyAsset(BaseModel):
    product_id: str
    primary_platform: str
    variants: list[CopyVariant] = Field(default_factory=list)
    model_version: str = "rule-based-v1"
    review_status: AssetReviewStatus = AssetReviewStatus.REVIEW_REQUIRED
    generated_at: datetime


class ImagePromptSpec(BaseModel):
    scene: str
    style: str
    prompt: str
    negative_prompt: str | None = None


class ImageAsset(BaseModel):
    product_id: str
    primary_platform: str
    prompt_spec: ImagePromptSpec
    preview_url: str | None = None
    source_image_urls: list[str] = Field(default_factory=list)
    model_version: str = "prompt-only-v1"
    review_status: AssetReviewStatus = AssetReviewStatus.REVIEW_REQUIRED
    generated_at: datetime


class CandidateBundle(BaseModel):
    product: AnalyzedProduct
    supplier: MatchedSupplier | None = None
    copy_draft: CopyDraft | None = None
    decision: DecisionRecord | None = None
    ai_recommendation: AIRecommendation | None = None
    listing_copy_asset: ListingCopyAsset | None = None
    image_asset: ImageAsset | None = None


class SearchRequest(BaseModel):
    keyword: str = Field(min_length=1, max_length=50)
    platforms: list[Platform] = Field(default_factory=list)
    limit_per_platform: int = Field(default=5, ge=1, le=20)
    backend: str = Field(default="auto", min_length=1, max_length=20)


class SearchHit(BaseModel):
    session_id: str
    platform: Platform
    keyword: str
    rank: int = Field(ge=1)
    product: RawProduct


class SearchSummary(BaseModel):
    total_hits: int = Field(ge=0)
    platform_counts: dict[str, int] = Field(default_factory=dict)
    data_source_counts: dict[str, int] = Field(default_factory=dict)


class SearchSession(BaseModel):
    id: str
    keyword: str
    platforms: list[Platform] = Field(default_factory=list)
    limit_per_platform: int = Field(ge=1, le=20)
    backend: str
    status: SearchStatus = SearchStatus.PENDING
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    hit_count: int = Field(default=0, ge=0)
    summary: SearchSummary = Field(default_factory=SearchSummary)
    error_message: str | None = None
