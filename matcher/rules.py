from __future__ import annotations

from datetime import datetime, timezone

from app.schemas import AnalyzedProduct, MatchedSupplier, Platform
from app.storage import load_blacklist

PLATFORM_FEE_RATE = 0.06


def match_suppliers(products: list[AnalyzedProduct]) -> list[MatchedSupplier]:
    blacklist = load_blacklist()
    matched: list[MatchedSupplier] = []
    for product in products:
        supplier = match_supplier(product, blacklist)
        if supplier is not None:
            matched.append(supplier)
    return matched


def match_supplier(product: AnalyzedProduct, blacklist: dict[str, set[str]] | None = None) -> MatchedSupplier | None:
    if product.skip_reason:
        return None

    source_price, shipping_cost, supplier_name, rating, plain_package = _supplier_profile(product)
    active_blacklist = blacklist or {"supplier": set(), "category": set()}
    if supplier_name in active_blacklist.get("supplier", set()):
        return None
    if product.category_label in active_blacklist.get("category", set()):
        return None

    fee = round(product.price * PLATFORM_FEE_RATE, 2)
    profit_est = round(product.price - source_price - shipping_cost - fee, 2)

    return MatchedSupplier(
        product_id=product.id,
        supplier_id=f"1688-{product.id}",
        supplier_name=supplier_name,
        source_price=source_price,
        moq=1 if product.platform == Platform.PINDUODUO else 2,
        shipping_cost=shipping_cost,
        profit_est=profit_est,
        plain_package=plain_package,
        supplier_rating=rating,
        matched_at=datetime.now(timezone.utc),
    )


def _supplier_profile(product: AnalyzedProduct) -> tuple[float, float, str, float, bool]:
    if "夜灯" in product.title:
        return 11.8, 3.5, "深圳光盒照明", 4.4, False
    if "脏衣篮" in product.title:
        return 16.2, 4.2, "台州简居家品", 4.5, True
    return 18.5, 4.0, "义乌简居百货", 4.7, True
