from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

import streamlit as st

from app.pipeline import build_candidate_bundles
from app.schemas import CandidateBundle, Decision, DecisionRecord
from app.storage import load_blacklist_summary, load_decisions, load_profit_summary, save_decision

DECISION_LABELS = {
    Decision.APPROVED: "通过",
    Decision.SKIPPED: "跳过",
    Decision.BLACKLISTED: "拉黑",
}

LABEL_TO_DECISION = {label: decision for decision, label in DECISION_LABELS.items()}


def _get_candidates() -> list[CandidateBundle]:
    return build_candidate_bundles()


def _decision_state_key(product_id: str) -> str:
    return f"decision-state-{product_id}"


def _decision_note_key(product_id: str) -> str:
    return f"decision-note-{product_id}"


def _load_decision(product_id: str) -> DecisionRecord | None:
    if _decision_state_key(product_id) not in st.session_state:
        st.session_state[_decision_state_key(product_id)] = load_decisions().get(product_id)
    return st.session_state.get(_decision_state_key(product_id))


def _save_decision(candidate: CandidateBundle, decision: Decision, reason: str | None) -> None:
    record = DecisionRecord(
        product_id=candidate.product.id,
        decision=decision,
        reason=reason,
        decided_by="dashboard-user",
        decided_at=datetime.now(timezone.utc),
    )
    st.session_state[_decision_state_key(candidate.product.id)] = record
    save_decision(
        record,
        supplier_name=candidate.supplier.supplier_name if candidate.supplier else None,
        category_label=candidate.product.category_label,
        profit_est=candidate.supplier.profit_est if candidate.supplier else None,
        supplier_id=candidate.supplier.supplier_id if candidate.supplier else None,
    )


def _decision_summary(candidates: list[CandidateBundle]) -> dict[Decision, int]:
    counter: Counter[Decision] = Counter()
    for candidate in candidates:
        record = _load_decision(candidate.product.id)
        if record is not None:
            counter[record.decision] += 1
    return {decision: counter.get(decision, 0) for decision in Decision}


def _filter_candidates(
    candidates: list[CandidateBundle],
    min_score: float,
    selected_platforms: list[str],
    decision_filter: str,
    keyword_query: str,
) -> list[CandidateBundle]:
    normalized_query = keyword_query.strip().lower()
    filtered: list[CandidateBundle] = []
    for candidate in candidates:
        if candidate.product.product_score < min_score:
            continue
        if candidate.product.platform.value not in selected_platforms:
            continue

        record = _load_decision(candidate.product.id)
        if decision_filter == "未处理" and record is not None:
            continue
        if decision_filter != "全部":
            expected = LABEL_TO_DECISION.get(decision_filter)
            if expected is not None and (record is None or record.decision != expected):
                continue

        if normalized_query:
            haystacks = [candidate.product.title, *candidate.product.keywords]
            if candidate.supplier:
                haystacks.append(candidate.supplier.supplier_name)
            if not any(normalized_query in text.lower() for text in haystacks):
                continue

        filtered.append(candidate)
    return filtered


def render_candidate_card(index: int, candidate: CandidateBundle) -> None:
    st.subheader(f"候选商品 {index}: {candidate.product.title}")
    left, right = st.columns(2)

    with left:
        st.metric("潜力评分", f"{candidate.product.product_score:.0f}")
        st.write(f"趋势：{candidate.product.trend.value}")
        st.write(f"平台：{candidate.product.platform.value}")
        st.write(f"售价：¥{candidate.product.price:.2f}")
        st.write(f"关键词：{' / '.join(candidate.product.keywords)}")

    with right:
        if candidate.supplier:
            st.metric("预估利润", f"¥{candidate.supplier.profit_est:.2f}")
            st.write(f"货源商家：{candidate.supplier.supplier_name}")
            st.write(f"货源价：¥{candidate.supplier.source_price:.2f}")
            st.write(f"无痕发货：{'是' if candidate.supplier.plain_package else '否'}")

    if candidate.copy:
        st.caption(f"模板：{candidate.copy.template_id}")
        st.write(candidate.copy.title)
        st.write(candidate.copy.body)
        st.write(f"标签：{'、'.join(candidate.copy.tags)}")

    decision_label = st.radio(
        "人工决策",
        options=list(LABEL_TO_DECISION.keys()),
        horizontal=True,
        key=f"decision-{candidate.product.id}",
    )
    reason = st.text_input(
        "决策备注",
        value=st.session_state.get(_decision_note_key(candidate.product.id), ""),
        key=_decision_note_key(candidate.product.id),
        placeholder="记录跳过原因、拉黑原因或通过备注",
    )

    if st.button("保存决策", key=f"save-{candidate.product.id}"):
        decision = LABEL_TO_DECISION[decision_label]
        _save_decision(candidate, decision, reason.strip() or None)
        st.success("决策已记录")

    record = _load_decision(candidate.product.id)
    if record is not None:
        st.info(
            f"已记录：{DECISION_LABELS[record.decision]} / 操作人：{record.decided_by}"
            f" / 时间：{record.decided_at.isoformat()}"
            f"{f' / 备注：{record.reason}' if record.reason else ''}"
        )

    st.divider()


def main() -> None:
    st.set_page_config(page_title="AI 选品助手", layout="wide")
    st.title("AI 选品助手 Dashboard MVP")
    st.write("优先读取 data 目录中的流水线结果；若尚未生成文件，则自动回退到内置示例数据。")

    candidates = _get_candidates()
    summary = _decision_summary(candidates)
    profit_summary = load_profit_summary()
    blacklist_summary = load_blacklist_summary()

    st.sidebar.header("概览")
    st.sidebar.write(f"候选商品数：{len(candidates)}")
    st.sidebar.write("人工审核优先，禁止自动上架。")
    st.sidebar.write(f"已通过：{summary[Decision.APPROVED]}")
    st.sidebar.write(f"已跳过：{summary[Decision.SKIPPED]}")
    st.sidebar.write(f"已拉黑：{summary[Decision.BLACKLISTED]}")
    st.sidebar.write(f"商家黑名单：{blacklist_summary['supplier_count']}")
    st.sidebar.write(f"品类黑名单：{blacklist_summary['category_count']}")
    st.sidebar.write(f"累计利润记录：{int(profit_summary['total_count'])}")
    st.sidebar.write(f"累计预估利润：¥{profit_summary['total_profit']:.2f}")

    st.sidebar.header("筛选")
    min_score = st.sidebar.slider("最低潜力评分", min_value=60, max_value=100, value=60)
    platform_options = ["xianyu", "pinduoduo"]
    selected_platforms = st.sidebar.multiselect("平台", options=platform_options, default=platform_options)
    decision_filter = st.sidebar.selectbox("决策状态", options=["全部", "未处理", *LABEL_TO_DECISION.keys()])
    keyword_query = st.sidebar.text_input("关键词检索", placeholder="商品标题 / 关键词 / 商家")

    filtered_candidates = _filter_candidates(
        candidates,
        min_score=min_score,
        selected_platforms=selected_platforms or platform_options,
        decision_filter=decision_filter,
        keyword_query=keyword_query,
    )
    st.write(f"当前筛选后候选数：{len(filtered_candidates)}")

    for index, candidate in enumerate(filtered_candidates, start=1):
        render_candidate_card(index, candidate)


if __name__ == "__main__":
    main()
