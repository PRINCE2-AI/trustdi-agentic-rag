# Architecture

TrustDI Agent converts agentic RAG for data integration into a small production-style system.

## Pipeline

```text
Input CSVs
  -> SchemaProfiler
  -> AgenticMatcher
  -> AdaptiveRoutePlanner
  -> LocalKnowledgeBase / optional WikidataEvidenceClient
  -> ReasoningClient
  -> Evaluator
```

## Main Design Choices

- Keep profiling deterministic so tests can run without paid APIs.
- Use OpenAI only for explanatory reasoning, not for basic control flow.
- Route easy matches directly to reduce cost.
- Route ambiguous pairs through retrieval and reasoning.
- Expose evidence and metrics so the user can audit the system.

## Future Upgrades

- Add vector embeddings for local knowledge retrieval.
- Add batch entity resolution across rows.
- Add active learning from human approvals.
- Add graph database storage for accepted matches.
- Add prompt-level cost tracking by route.

