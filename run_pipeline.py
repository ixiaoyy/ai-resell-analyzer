from __future__ import annotations

# One-shot pipeline runner: scraper -> analyzer -> matcher -> copywriter -> dashboard.

import argparse
import json
from pathlib import Path

from analyzer.__main__ import ProductAnalyzer
from copywriter.__main__ import ProductCopywriter
from dashboard.__main__ import DashboardAggregator
from matcher.__main__ import SupplierMatcher
from scraper.__main__ import ProductScraper


DATA_DIR = Path("data")


def run_pipeline(platform: str, count: int, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    # Stage 1 — Scrape
    raw_path = output_dir / "01_raw.json"
    scraper = ProductScraper()
    raw_products = scraper.scrape(platform=platform, count=count)
    raw_path.write_text(json.dumps(raw_products, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[1/4] Scraped    {len(raw_products)} products  → {raw_path}")

    # Stage 2 — Analyze
    analyzed_path = output_dir / "02_analyzed.json"
    analyzer = ProductAnalyzer()
    analyzed_products = analyzer.analyze_products(raw_products)
    analyzed_path.write_text(json.dumps(analyzed_products, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[2/4] Analyzed   {len(analyzed_products)} products  → {analyzed_path}")

    # Stage 3 — Match suppliers + generate copy (independent, both depend on analyzer output)
    matched_path = output_dir / "03_matched.json"
    matcher = SupplierMatcher()
    matched_suppliers = matcher.match_products(analyzed_products)
    matched_path.write_text(json.dumps(matched_suppliers, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[3/4] Matched    {len(matched_suppliers)} suppliers → {matched_path}")

    copydrafts_path = output_dir / "03_copydrafts.json"
    copywriter = ProductCopywriter()
    copydrafts = copywriter.generate_drafts(analyzed_products)
    copydrafts_path.write_text(json.dumps(copydrafts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"      Copywriter {len(copydrafts)} drafts    → {copydrafts_path}")

    # Stage 4 — Dashboard
    dashboard_path = output_dir / "04_dashboard.json"
    aggregator = DashboardAggregator()
    rows = aggregator.build_rows(analyzed_products, matched_suppliers, copydrafts)
    dashboard_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[4/4] Dashboard  {len(rows)} rows      → {dashboard_path}")

    return dashboard_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full ai-picker pipeline end-to-end")
    parser.add_argument(
        "--platform",
        default="all",
        choices=["xianyu", "pinduoduo", "all"],
        help="Platform to scrape (default: all)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of products to scrape (default: 5)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DATA_DIR / "pipeline_run"),
        help="Directory to write pipeline outputs (default: data/pipeline_run)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_pipeline(
        platform=args.platform,
        count=args.count,
        output_dir=Path(args.output_dir),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
