from __future__ import annotations

from dataclasses import dataclass

from app.schemas import ColumnProfile, EvidenceItem
from app.text_utils import cosine_similarity, lexical_similarity, tokenize


@dataclass(frozen=True)
class KnowledgeDocument:
    source: str
    text: str
    metadata: dict[str, str]


class LocalKnowledgeBase:
    def __init__(self, documents: list[KnowledgeDocument] | None = None) -> None:
        self.documents = documents or default_knowledge_documents()

    def search(self, query: str, top_k: int = 5) -> tuple[EvidenceItem, ...]:
        scored: list[EvidenceItem] = []
        for document in self.documents:
            score = 0.65 * cosine_similarity(query, document.text)
            score += 0.35 * lexical_similarity(tuple(tokenize(query)), tuple(tokenize(document.text)))
            if score > 0:
                scored.append(
                    EvidenceItem(
                        source=document.source,
                        text=document.text,
                        score=round(score, 4),
                        metadata=dict(document.metadata),
                    )
                )
        scored.sort(key=lambda item: item.score, reverse=True)
        return tuple(scored[:top_k])

    def evidence_for_columns(
        self,
        source_column: ColumnProfile,
        target_column: ColumnProfile,
        top_k: int = 3,
    ) -> tuple[EvidenceItem, ...]:
        query = " ".join(
            [
                source_column.name,
                target_column.name,
                source_column.inferred_type.value,
                target_column.inferred_type.value,
                " ".join(source_column.sample_values[:3]),
                " ".join(target_column.sample_values[:3]),
            ]
        )
        return self.search(query, top_k=top_k)


def default_knowledge_documents() -> list[KnowledgeDocument]:
    return [
        KnowledgeDocument(
            source="local://schema-matching",
            text=(
                "Schema matching aligns attributes across datasets using column names, "
                "data types, value distributions, and external semantic evidence."
            ),
            metadata={"kind": "paper_note"},
        ),
        KnowledgeDocument(
            source="local://entity-resolution",
            text=(
                "Entity matching benefits from identifiers, emails, phone numbers, names, "
                "addresses, and graph relationships between records."
            ),
            metadata={"kind": "paper_note"},
        ),
        KnowledgeDocument(
            source="local://financial-columns",
            text=(
                "Revenue, amount, price, total, and sales columns are often semantically "
                "related when their numeric types and value ranges agree."
            ),
            metadata={"kind": "domain_note"},
        ),
        KnowledgeDocument(
            source="local://customer-columns",
            text=(
                "Customer, client, buyer, account, email, contact, and phone attributes "
                "usually describe parties in CRM and order systems."
            ),
            metadata={"kind": "domain_note"},
        ),
        KnowledgeDocument(
            source="local://temporal-columns",
            text=(
                "Date, timestamp, order_date, created_at, and event_time columns describe "
                "temporal facts and should be compared using date-like values."
            ),
            metadata={"kind": "domain_note"},
        ),
    ]

