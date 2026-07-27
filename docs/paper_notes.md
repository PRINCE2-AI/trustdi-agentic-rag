# Paper Notes

Paper: Towards Trustworthy and Cost-Efficient Data Integration: From Naive RAG to Agentic RAG

Link: https://arxiv.org/abs/2607.22319

## Useful Ideas

- Naive RAG can retrieve too much irrelevant context.
- Data integration tasks require trust, explainability, and cost control.
- Agentic RAG can route different tasks to different actions instead of using one fixed retrieval path.
- Schema matching and entity matching need both local structure and outside semantic knowledge.

## What TrustDI Implements

- Adaptive routing.
- Evidence-backed schema matching.
- Optional external knowledge lookup.
- LLM explanation with deterministic fallback.
- Evaluation metrics for integration quality.

