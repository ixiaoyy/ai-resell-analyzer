from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.schemas import AnalyzedProduct, MatchedSupplier
from copywriter import build_copy_drafts


def main() -> None:
    parser = argparse.ArgumentParser(description="为商品候选生成文案草稿")
    parser.add_argument("--products", type=Path, required=True, help="AnalyzedProduct JSON 文件路径")
    parser.add_argument("--suppliers", type=Path, required=True, help="MatchedSupplier JSON 文件路径")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data") / "copy" / "copy_latest.json",
        help="CopyDraft 输出文件路径",
    )
    args = parser.parse_args()

    product_data = json.loads(args.products.read_text(encoding="utf-8"))
    supplier_data = json.loads(args.suppliers.read_text(encoding="utf-8"))
    products = [AnalyzedProduct.model_validate(item) for item in product_data]
    suppliers = {
        supplier.product_id: supplier
        for supplier in (MatchedSupplier.model_validate(item) for item in supplier_data)
    }
    drafts = build_copy_drafts(products, suppliers)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps([draft.model_dump(mode="json") for draft in drafts], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"generated {len(drafts)} copy drafts to {args.output}")


if __name__ == "__main__":
    main()
