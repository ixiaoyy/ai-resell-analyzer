from __future__ import annotations

import json
from pathlib import Path

import pytest

from run_pipeline import run_pipeline


def test_pipeline_end_to_end(tmp_path: Path) -> None:
    dashboard_path = run_pipeline(platform="all", count=3, output_dir=tmp_path)

    assert dashboard_path.exists()
    rows = json.loads(dashboard_path.read_text(encoding="utf-8"))
    assert len(rows) == 3

    row = rows[0]
    assert "product_id" in row
    assert "supplier" in row
    assert "copydraft" in row
    assert row["review"]["decision"] == "pending"
    assert row["review"]["decision_options"] == ["approved", "skipped", "blacklisted"]


def test_pipeline_xianyu_only(tmp_path: Path) -> None:
    run_pipeline(platform="xianyu", count=2, output_dir=tmp_path)

    raw = json.loads((tmp_path / "01_raw.json").read_text(encoding="utf-8"))
    assert all(p["platform"] == "xianyu" for p in raw)
    assert len(raw) == 2


def test_pipeline_writes_all_stage_files(tmp_path: Path) -> None:
    run_pipeline(platform="all", count=2, output_dir=tmp_path)

    for name in ["01_raw.json", "02_analyzed.json", "03_matched.json", "03_copydrafts.json", "04_dashboard.json"]:
        assert (tmp_path / name).exists(), f"Missing stage file: {name}"
