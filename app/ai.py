from __future__ import annotations

from datetime import UTC, datetime

from app.schemas import (
    AIRecommendation,
    AnalyzedProduct,
    AssetReviewStatus,
    CopyVariant,
    ImageAsset,
    ImagePromptSpec,
    ListingCopyAsset,
    MatchedSupplier,
)
from platforms.defaults import register_default_platforms
from platforms.registry import registry

register_default_platforms()


class AIAssetBuilder:
    def build_recommendation(self, product: AnalyzedProduct, supplier: MatchedSupplier | None) -> AIRecommendation:
        sell_platform = product.platform_code or product.platform.value
        source_platform = "1688" if supplier is not None else "sample-source"
        reasoning = [
            f"{product.category_label} 类目热度趋势为 {product.trend.value}",
            f"商品潜力评分为 {product.product_score:.0f}",
        ]
        risk_flags: list[str] = []
        suggested_price_min = round(product.price * 0.95, 2)
        suggested_price_max = round(product.price * 1.15, 2)
        confidence = 0.62
        opportunity_score = min(99.0, round(product.product_score * 0.7, 2))

        if supplier is not None:
            opportunity_score = min(99.0, round(product.product_score * 0.65 + supplier.profit_est * 2.5, 2))
            confidence = 0.78 if supplier.plain_package else 0.68
            reasoning.append(f"当前货源预估利润为 {supplier.profit_est:.2f} 元")
            reasoning.append(f"推荐从 {source_platform} 方向寻找稳定供货")
            if supplier.profit_est < 5:
                risk_flags.append("利润空间偏薄")
            if not supplier.plain_package:
                risk_flags.append("无痕发货能力待确认")
            suggested_price_min = round(max(product.price, supplier.source_price * 1.35), 2)
            suggested_price_max = round(max(suggested_price_min, product.price * 1.18), 2)
        else:
            reasoning.append("当前缺少稳定货源，建议先补充供给侧信息")
            risk_flags.append("缺少供货匹配")

        return AIRecommendation(
            product_id=product.id,
            recommended_sell_platform=sell_platform,
            recommended_source_platform=source_platform,
            opportunity_score=opportunity_score,
            confidence_score=confidence,
            reasoning=reasoning,
            risk_flags=risk_flags,
            suggested_price_min=suggested_price_min,
            suggested_price_max=suggested_price_max,
            recommendation_version="ai-rule-hybrid-v1",
            review_status=AssetReviewStatus.REVIEW_REQUIRED,
            generated_at=_utc_now(),
        )

    def build_listing_copy_asset(self, product: AnalyzedProduct, recommendation: AIRecommendation) -> ListingCopyAsset:
        keywords = product.keywords[:3] or [product.category_label]
        variants = [
            CopyVariant(
                channel=recommendation.recommended_sell_platform,
                title=f"{product.title[:24]} 优先推荐",
                body=(
                    f"AI 推荐上架到 {recommendation.recommended_sell_platform}。"
                    f"核心卖点：{' / '.join(keywords)}。"
                    f"建议售价区间 ¥{recommendation.suggested_price_min:.2f}-¥{recommendation.suggested_price_max:.2f}。"
                ),
                tags=keywords,
                tone="direct-response",
            ),
            CopyVariant(
                channel=recommendation.recommended_sell_platform,
                title=f"{product.category_label} 低门槛试卖款",
                body=(
                    f"适合先做人群测试，重点突出 {product.trend.value} 趋势与性价比。"
                    f"风险提示：{'、'.join(recommendation.risk_flags) if recommendation.risk_flags else '暂无明显高风险'}。"
                ),
                tags=keywords,
                tone="social-proof",
            ),
        ]
        return ListingCopyAsset(
            product_id=product.id,
            primary_platform=recommendation.recommended_sell_platform,
            variants=variants,
            model_version="ai-copy-v1",
            review_status=AssetReviewStatus.REVIEW_REQUIRED,
            generated_at=_utc_now(),
        )

    def build_image_asset(self, product: AnalyzedProduct, recommendation: AIRecommendation) -> ImageAsset:
        prompt = (
            f"Create an e-commerce hero image for {product.title}. "
            f"Platform: {recommendation.recommended_sell_platform}. "
            f"Highlight keywords: {', '.join(product.keywords[:4]) or product.category_label}. "
            f"Keep the composition clean, conversion-oriented, and suitable for marketplace listing review."
        )
        return ImageAsset(
            product_id=product.id,
            primary_platform=recommendation.recommended_sell_platform,
            prompt_spec=ImagePromptSpec(
                scene="marketplace-hero",
                style="clean-commercial",
                prompt=prompt,
                negative_prompt="watermark, logo infringement, exaggerated claims, cluttered composition",
            ),
            preview_url=product.image_url,
            source_image_urls=[product.image_url] if product.image_url else [],
            model_version="ai-image-plan-v1",
            review_status=AssetReviewStatus.REVIEW_REQUIRED,
            generated_at=_utc_now(),
        )

    def available_sell_platforms(self) -> tuple[str, ...]:
        return registry.codes(role="sell_target")


def _utc_now() -> datetime:
    return datetime.now(UTC)
