from __future__ import annotations

import json
import tempfile
from pathlib import Path

import streamlit as st

from app.engine import TrustDIEngine


st.set_page_config(page_title="TrustDI Agent", page_icon="DI", layout="wide")

st.title("TrustDI Agentic RAG")
st.caption("Trustworthy and cost-efficient schema matching with adaptive retrieval, evidence, and evaluation.")

with st.sidebar:
    st.header("Run Mode")
    source_upload = st.file_uploader("Source CSV", type=["csv"])
    target_upload = st.file_uploader("Target CSV", type=["csv"])
    gold_json = st.text_area(
        "Gold mapping JSON",
        value='{"customer_email": "client_email", "order_total": "sales_amount", "order_date": "purchase_date", "region": "sales_region", "product_name": "item_title"}',
        height=120,
    )
    run_button = st.button("Run Agentic Match", type="primary")


def _save_upload(upload, directory: Path) -> Path:
    path = directory / upload.name
    path.write_bytes(upload.getbuffer())
    return path


if run_button:
    if not source_upload or not target_upload:
        st.warning("Upload both CSV files.")
        st.stop()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source_path = _save_upload(source_upload, tmp_path)
        target_path = _save_upload(target_upload, tmp_path)
        try:
            gold = json.loads(gold_json) if gold_json.strip() else None
        except json.JSONDecodeError:
            st.error("Gold mapping must be valid JSON.")
            st.stop()
        engine = TrustDIEngine()
        result = engine.match_csvs(source_path, target_path, gold=gold)

    st.subheader("Evaluation")
    st.dataframe([result.metrics], use_container_width=True)

    st.subheader("Predicted Matches")
    rows = []
    for match in result.matches:
        rows.append(
            {
                "source": match.source_column,
                "target": match.target_column,
                "decision": match.decision.value,
                "route": match.route.value,
                "confidence": match.confidence,
                "evidence_score": match.evidence_score,
                "rationale": match.rationale,
            }
        )
    st.dataframe(rows, use_container_width=True)

    st.subheader("Evidence Trace")
    for match in result.matches:
        with st.expander(f"{match.source_column} -> {match.target_column}"):
            st.write(match.rationale)
            for item in match.evidence:
                st.markdown(f"- `{item.source}` ({item.score:.2f}): {item.text}")
else:
    st.info("Upload two CSV schemas or use the sample files in `data/samples`.")
