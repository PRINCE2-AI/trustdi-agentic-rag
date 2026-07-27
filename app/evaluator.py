from __future__ import annotations

from app.schemas import CandidateMatch, Decision, IntegrationResult


def evaluate_matches(
    matches: tuple[CandidateMatch, ...],
    gold: dict[str, str] | None = None,
) -> dict[str, float]:
    accepted = {
        match.source_column: match.target_column
        for match in matches
        if match.decision in {Decision.MATCH, Decision.POSSIBLE_MATCH}
    }
    if gold:
        true_positive = sum(1 for source, target in accepted.items() if gold.get(source) == target)
        precision = true_positive / len(accepted) if accepted else 0.0
        recall = true_positive / len(gold) if gold else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    else:
        precision = recall = f1 = 0.0
    evidence_items = [item for match in matches for item in match.evidence]
    evidence_relevance = (
        sum(item.score for item in evidence_items) / len(evidence_items) if evidence_items else 0.0
    )
    review_rate = sum(1 for match in matches if match.decision == Decision.NEEDS_REVIEW) / len(matches) if matches else 0.0
    external_rate = sum(1 for match in matches if match.route.value == "external_kb") / len(matches) if matches else 0.0
    avg_confidence = sum(match.confidence for match in matches) / len(matches) if matches else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "avg_confidence": round(avg_confidence, 4),
        "evidence_relevance": round(evidence_relevance, 4),
        "review_rate": round(review_rate, 4),
        "external_kb_rate": round(external_rate, 4),
    }


def build_result(
    source_dataset: str,
    target_dataset: str,
    matches: tuple[CandidateMatch, ...],
    gold: dict[str, str] | None = None,
) -> IntegrationResult:
    return IntegrationResult(
        source_dataset=source_dataset,
        target_dataset=target_dataset,
        matches=matches,
        metrics=evaluate_matches(matches, gold=gold),
    )

