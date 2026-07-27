from __future__ import annotations

from app.config import Settings
from app.schemas import CandidateMatch, ColumnProfile, EvidenceItem


class ReasoningClient:
    """OpenAI-backed reasoning with a deterministic local fallback."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def explain_match(
        self,
        source: ColumnProfile,
        target: ColumnProfile,
        evidence: tuple[EvidenceItem, ...],
        draft: str,
    ) -> str:
        if not self.settings.openai_enabled:
            return draft
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.settings.openai_api_key)
            evidence_text = "\n".join(f"- {item.text}" for item in evidence[:4]) or "- No evidence found"
            prompt = (
                "You are a data integration agent. Explain whether two columns should be matched. "
                "Stay grounded in the evidence and mention uncertainty when evidence is weak.\n\n"
                f"Source column: {source.name} ({source.inferred_type.value})\n"
                f"Source values: {list(source.sample_values[:5])}\n"
                f"Target column: {target.name} ({target.inferred_type.value})\n"
                f"Target values: {list(target.sample_values[:5])}\n"
                f"Evidence:\n{evidence_text}\n"
                f"Draft decision: {draft}\n\n"
                "Return one concise sentence."
            )
            response = client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=120,
            )
            content = response.choices[0].message.content
            return content.strip() if content else draft
        except Exception:
            return draft


def attach_reasoning(match: CandidateMatch, rationale: str) -> CandidateMatch:
    return CandidateMatch(
        source_column=match.source_column,
        target_column=match.target_column,
        name_score=match.name_score,
        type_score=match.type_score,
        value_score=match.value_score,
        evidence_score=match.evidence_score,
        confidence=match.confidence,
        route=match.route,
        decision=match.decision,
        rationale=rationale,
        evidence=match.evidence,
    )

