from __future__ import annotations

from datetime import datetime, timezone

from app.schemas import AnalyzedProduct, Platform, ProductFeatures, RawProduct, Trend


def analyze_products(products: list[RawProduct]) -> list[AnalyzedProduct]:
    return [analyze_product(product) for product in products]


def analyze_product(product: RawProduct) -> AnalyzedProduct:
    keywords = _extract_keywords(product)
    trend = _detect_trend(product)
    features = _extract_features(product)
    score = _score_product(product, trend, features)
    skip_reason = None if score >= 60 else "热度与利润空间偏弱，暂不进入候选池"

    return AnalyzedProduct(
        **product.model_dump(),
        product_score=score,
        trend=trend,
        keywords=keywords,
        category_label=product.category or "未分类",
        features=features,
        analyzed_at=datetime.now(timezone.utc),
        skip_reason=skip_reason,
    )


def _extract_keywords(product: RawProduct) -> list[str]:
    base_keywords = [tag for tag in product.raw_tags if tag]
    title_keywords = [segment for segment in product.title.replace("/", " ").split() if len(segment) >= 2]
    merged: list[str] = []
    for keyword in [*(product.category and [product.category] or []), *base_keywords, *title_keywords]:
        if keyword not in merged:
            merged.append(keyword)
    return merged[:5]


def _detect_trend(product: RawProduct) -> Trend:
    signal = (product.want_count or 0) + (product.sales_count or 0) / 10
    if signal >= 200:
        return Trend.RISING
    if signal >= 80:
        return Trend.STABLE
    return Trend.DECLINING


def _extract_features(product: RawProduct) -> ProductFeatures:
    title = product.title
    color = next((item for item in ["米白", "白色", "黑色", "灰色"] if item in title), None)
    material = next((item for item in ["塑料", "ABS", "棉麻", "金属"] if item in title), None)
    if "奶油风" in title or "奶油风" in product.raw_tags:
        style = "奶油风"
    elif "北欧" in title or "北欧风" in product.raw_tags:
        style = "北欧风"
    else:
        style = "极简"

    if product.platform == Platform.PINDUODUO and material is None:
        material = "ABS"

    return ProductFeatures(color=color, material=material, style=style)


def _score_product(product: RawProduct, trend: Trend, features: ProductFeatures) -> float:
    score = 50.0
    score += min((product.want_count or 0) / 8, 25)
    score += min((product.sales_count or 0) / 150, 20)
    if trend == Trend.RISING:
        score += 10
    elif trend == Trend.STABLE:
        score += 4
    if features.style in {"奶油风", "北欧风"}:
        score += 6
    return round(min(score, 100), 2)
