from __future__ import annotations

from collections import defaultdict

from app.schemas import CandidateMatch, ColumnProfile, SchemaProfile
from app.text_utils import lexical_similarity


class SchemaGraphMemory:
    """Small graph memory for columns, datasets, and accepted matches."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, str]] = {}
        self.edges: dict[str, dict[str, float]] = defaultdict(dict)

    def add_schema(self, schema: SchemaProfile) -> None:
        dataset_node = f"dataset:{schema.dataset_id}"
        self.nodes[dataset_node] = {"type": "dataset", "name": schema.dataset_id}
        for column in schema.columns:
            column_node = self._column_node(column)
            self.nodes[column_node] = {
                "type": "column",
                "dataset": column.dataset_id,
                "name": column.name,
                "inferred_type": column.inferred_type.value,
            }
            self.edges[dataset_node][column_node] = 1.0
            self.edges[column_node][dataset_node] = 1.0

    def add_match(self, match: CandidateMatch, source_dataset: str, target_dataset: str) -> None:
        source_node = f"column:{source_dataset}:{match.source_column}"
        target_node = f"column:{target_dataset}:{match.target_column}"
        self.edges[source_node][target_node] = match.confidence
        self.edges[target_node][source_node] = match.confidence

    def graph_hint(self, source: ColumnProfile, target: ColumnProfile) -> float:
        source_node = self._column_node(source)
        target_node = self._column_node(target)
        existing = self.edges.get(source_node, {}).get(target_node, 0.0)
        token_hint = lexical_similarity(source.tokens, target.tokens)
        type_hint = 0.15 if source.inferred_type == target.inferred_type else 0.0
        return max(existing, min(1.0, token_hint + type_hint))

    @staticmethod
    def _column_node(column: ColumnProfile) -> str:
        return f"column:{column.dataset_id}:{column.name}"

