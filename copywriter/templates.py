from __future__ import annotations

from datetime import datetime, timezone

from app.schemas import AnalyzedProduct, CopyDraft, MatchedSupplier


def build_copy_drafts(products: list[AnalyzedProduct], suppliers: dict[str, MatchedSupplier]) -> list[CopyDraft]:
    return [build_copy_draft(product, suppliers.get(product.id)) for product in products if not product.skip_reason]


def build_copy_draft(product: AnalyzedProduct, supplier: MatchedSupplier | None) -> CopyDraft:
    template_id = _select_template(product)
    title = _build_title(product)
    body = _build_body(product, supplier)
    tags = product.keywords[:3]

    return CopyDraft(
        product_id=product.id,
        title=title[:30],
        body=body,
        tags=tags,
        template_id=template_id,
        generated_at=datetime.now(timezone.utc),
    )


def _select_template(product: AnalyzedProduct) -> str:
    if "宿舍" in product.title:
        return "practical-v1"
    if product.features and product.features.style == "奶油风":
        return "life-style-v1"
    return "value-v1"


def _build_title(product: AnalyzedProduct) -> str:
    if "夜灯" in product.title:
        return "宿舍熄灯后也能安静用的小夜灯"
    if "脏衣篮" in product.title:
        return "脏衣服终于不用堆椅子上了"
    return "桌面太乱？这个小推车真能救场"


def _build_body(product: AnalyzedProduct, supplier: MatchedSupplier | None) -> str:
    profit_hint = ""
    if supplier is not None and supplier.plain_package:
        profit_hint = "支持无痕发货，转卖流程更省心。"

    if "夜灯" in product.title:
        return f"亮度柔和，不刺眼，床边一夹就能用，学习或者半夜找东西都方便，充一次能顶好几晚。{profit_hint}".strip()
    if "脏衣篮" in product.title:
        return f"可折叠不占地方，换季衣物、宿舍脏衣都能收，风格干净耐看，小空间也能立刻整洁。{profit_hint}".strip()
    return f"收纳护肤品、零食、办公小物都很顺手，轮子顺滑不占地方，租房党和小桌面都很适合。{profit_hint}".strip()
