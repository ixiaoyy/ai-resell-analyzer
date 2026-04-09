"""抓取层模块。"""

from scraper.fetchers import fetch_real_products
from scraper.mock_data import build_sample_raw_products

__all__ = ["build_sample_raw_products", "fetch_real_products"]
