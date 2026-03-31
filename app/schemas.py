from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Platform(str, Enum):
    XIANYU = "xianyu"
    PINDUODUO = "pinduoduo"


class Trend(str, Enum):
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"


class Decision(str, Enum):
    APPROVED = "approved"
    SKIPPED = "skipped"
    BLACKLISTED = "blacklisted"


class ProductFeatures(BaseModel):
    color: str | None = None
    material: str | None = None
    style: str | None = None


class RawProduct(BaseModel):
    id: str
    platform: Platform
    title: str
    price: float = Field(ge=0)
    want_count: int | None = Field(default=None, ge=0)
    sales_count: int | None = Field(default=None, ge=0)
    image_url: str | None = None
    category: str | None = None
    fetched_at: datetime
    raw_tags: list[str] = Field(default_factory=list)


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


class CandidateBundle(BaseModel):
    product: AnalyzedProduct
    supplier: MatchedSupplier | None = None
    copy: CopyDraft | None = None
    decision: DecisionRecord | None = None
