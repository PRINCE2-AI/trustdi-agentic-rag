# Observability Guide

TrustDI Agentic RAG should expose why a schema match was accepted, rejected, or routed to review. The goal is not only to produce matches, but to make the decision path auditable.

## Trace Fields

Use this trace shape for each candidate pair:

```json
{
  "run_id": "2026-08-11T10-30-00-trustdi-001",
  "source_column": "amount",
  "target_column": "sales_amount",
  "candidate_score": 0.0,
  "route": "agentic_verify",
  "confidence": 0.0,
  "evidence_count": 0,
  "external_kb_used": false,
  "llm_explanation_used": false,
  "decision": "review",
  "latency_ms": 0,
  "estimated_cost_usd": 0.0,
  "metrics": {
    "evidence_relevance": null,
    "route_correct": null,
    "match_correct": null
  }
}
```

Set values to `null` or `0` until a real run records them. Do not publish guessed numbers.

## Dashboard Signals

| Signal | Why it matters |
| --- | --- |
| Source and target profiles | Shows names, types, examples, and entity hints |
| Candidate score | Explains first-pass matching confidence |
| Route | Shows direct, retrieve, agentic_verify, or external_kb path |
| Evidence snippets | Shows why the match is supported or rejected |
| Confidence | Indicates whether the match needs human review |
| Review rate | Shows how often the system avoids silent guessing |
| External-KB rate | Shows dependency on outside knowledge |
| Latency and cost | Shows cost of retrieval and LLM explanations |

## Failure Types

Track these failure categories:

| Failure type | Example |
| --- | --- |
| Type mismatch | Email matched to currency |
| Same type, wrong entity | Employee ID matched to customer ID |
| Related but not equivalent | Gross revenue matched to net revenue |
| Ambiguous generic name | `amount`, `date`, `status`, or `id` |
| Acronym without evidence | ISIN, NPI, GTIN without KB support |
| Overconfident direct route | Easy-looking name accepted without checking values |

## Cost and Latency Table

| Route | Avg latency | p95 latency | Avg estimated cost | Notes |
| --- | --- | --- | --- | --- |
| direct | TBD | TBD | TBD | Low-cost deterministic route |
| retrieve | TBD | TBD | TBD | Uses local evidence retrieval |
| agentic_verify | TBD | TBD | TBD | Uses deeper verification and optional explanation |
| external_kb | TBD | TBD | TBD | Uses external source only when enabled |

## Next Upgrade

Add a trace writer that stores candidate decisions as JSONL in `outputs/trustdi_traces.jsonl`, then show route distribution, review rate, false positives, and evidence relevance in the Streamlit dashboard.
