from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class ColumnType(str, Enum):
    TEXT = "text"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"
    EMAIL = "email"
    BOOLEAN = "boolean"
    UNKNOWN = "unknown"


class Route(str, Enum):
    DIRECT = "direct"
    RETRIEVE = "retrieve"
    AGENTIC_VERIFY = "agentic_verify"
    EXTERNAL_KB = "external_kb"


class Decision(str, Enum):
    MATCH = "match"
    POSSIBLE_MATCH = "possible_match"
    NO_MATCH = "no_match"
    NEEDS_REVIEW = "needs_review"


@dataclass(frozen=True)
class ColumnProfile:
    dataset_id: str
    name: str
    inferred_type: ColumnType
    sample_values: tuple[str, ...]
    tokens: tuple[str, ...]
    null_ratio: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["inferred_type"] = self.inferred_type.value
        return data


@dataclass(frozen=True)
class SchemaProfile:
    dataset_id: str
    columns: tuple[ColumnProfile, ...]
    row_count: int

    def get_column(self, name: str) -> ColumnProfile:
        for column in self.columns:
            if column.name == name:
                return column
        raise KeyError(f"Column not found: {name}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "row_count": self.row_count,
            "columns": [column.to_dict() for column in self.columns],
        }


@dataclass(frozen=True)
class EvidenceItem:
    source: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CandidateMatch:
    source_column: str
    target_column: str
    name_score: float
    type_score: float
    value_score: float
    evidence_score: float
    confidence: float
    route: Route
    decision: Decision
    rationale: str
    evidence: tuple[EvidenceItem, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["route"] = self.route.value
        data["decision"] = self.decision.value
        data["evidence"] = [item.to_dict() for item in self.evidence]
        return data


@dataclass(frozen=True)
class IntegrationResult:
    source_dataset: str
    target_dataset: str
    matches: tuple[CandidateMatch, ...]
    metrics: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_dataset": self.source_dataset,
            "target_dataset": self.target_dataset,
            "matches": [match.to_dict() for match in self.matches],
            "metrics": self.metrics,
        }

