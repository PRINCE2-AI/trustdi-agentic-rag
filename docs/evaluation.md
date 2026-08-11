# Evaluation Guide

TrustDI Agentic RAG includes a 30-case schema-matching evaluation set at [`data/eval_schema_cases.json`](../data/eval_schema_cases.json). The set tests direct matches, retrieval-needed matches, ambiguous cases, negative pairs, external knowledge cases, type mismatches, and graph-style relationship ambiguity.

## Evaluation Goals

| Goal | What to inspect |
| --- | --- |
| Match correctness | Whether predicted matches align with expected labels |
| Route quality | Whether easy cases use low-cost direct routing and ambiguous cases use verification |
| Evidence relevance | Whether retrieved evidence supports the match decision |
| Entity disambiguation | Whether same-type columns with different business meaning are separated |
| Cost awareness | Whether LLM-heavy paths are reserved for harder cases |
| Review routing | Whether ambiguous cases are flagged instead of guessed |

## Dataset Shape

Each item contains:

```json
{
  "id": "trustdi_agentic_011",
  "source_column": "amount",
  "target_column": "sales_amount",
  "expected_match": "ambiguous",
  "expected_route": "agentic_verify",
  "expected_evidence": ["amount", "transaction", "currency", "ambiguous"],
  "rationale": "Generic source name should not be accepted without value/profile evidence."
}
```

## Suggested Scoring

| Metric | Simple scoring rule |
| --- | --- |
| Precision | Correct predicted matches / all predicted matches |
| Recall | Correct predicted matches / all expected true matches |
| F1 | Harmonic mean of precision and recall |
| Route accuracy | Fraction of cases where route matches expected route |
| Evidence relevance | Fraction of expected evidence terms supported by retrieved context |
| Review accuracy | Fraction of ambiguous cases correctly routed to review or verification |
| False-positive rate | Non-matches incorrectly accepted as matches |

## Recommended Report Table

| Run | Precision | Recall | F1 | Route accuracy | Evidence relevance | Review rate | External-KB rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Direct baseline | TBD | TBD | TBD | TBD | N/A | N/A | N/A |
| Retrieval route | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Agentic RAG | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

Only publish observed values from a real run. Do not treat the sample dataset as broad enterprise accuracy proof.

## Acceptance Targets

For a portfolio demo, target:

- Agentic RAG improves F1 over direct-only matching.
- Ambiguous cases are routed to `agentic_verify` instead of being accepted silently.
- Negative same-type pairs such as `birth_date` vs `purchase_date` are not accepted.
- Evidence relevance is reported for every retrieval-backed decision.

## Next Upgrade

Add a benchmark runner that loads `data/eval_schema_cases.json`, runs all matching modes, and writes `outputs/schema_eval_report.json` plus a CSV summary.
