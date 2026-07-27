from app.evaluator import evaluate_matches
from app.schemas import CandidateMatch, Decision, Route


def test_evaluator_scores_gold_mapping() -> None:
    matches = (
        CandidateMatch(
            source_column="customer_email",
            target_column="client_email",
            name_score=1.0,
            type_score=1.0,
            value_score=1.0,
            evidence_score=0.0,
            confidence=0.9,
            route=Route.DIRECT,
            decision=Decision.MATCH,
            rationale="clear",
        ),
    )
    metrics = evaluate_matches(matches, gold={"customer_email": "client_email"})
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0

