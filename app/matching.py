from __future__ import annotations

from app.config import Settings
from app.external_kb import WikidataEvidenceClient
from app.graph_memory import SchemaGraphMemory
from app.llm import ReasoningClient, attach_reasoning
from app.retrieval import LocalKnowledgeBase
from app.router import AdaptiveRoutePlanner
from app.schemas import CandidateMatch, ColumnProfile, Decision, EvidenceItem, Route, SchemaProfile
from app.text_utils import clamp, lexical_similarity


class AgenticMatcher:
    def __init__(
        self,
        settings: Settings,
        retriever: LocalKnowledgeBase | None = None,
        graph_memory: SchemaGraphMemory | None = None,
        external_client: WikidataEvidenceClient | None = None,
        reasoner: ReasoningClient | None = None,
    ) -> None:
        self.settings = settings
        self.retriever = retriever or LocalKnowledgeBase()
        self.graph_memory = graph_memory or SchemaGraphMemory()
        self.external_client = external_client or WikidataEvidenceClient(settings.external_kb_enabled)
        self.reasoner = reasoner or ReasoningClient(settings)
        self.router = AdaptiveRoutePlanner(settings)

    def match(self, source_schema: SchemaProfile, target_schema: SchemaProfile) -> tuple[CandidateMatch, ...]:
        self.graph_memory.add_schema(source_schema)
        self.graph_memory.add_schema(target_schema)
        best_matches: list[CandidateMatch] = []
        for source in source_schema.columns:
            ranked = self._rank_targets(source, target_schema.columns)
            if not ranked:
                continue
            best_target, best_base = ranked[0]
            runner_up = ranked[1][1] if len(ranked) > 1 else None
            match = self._build_match(source, best_target, best_base, runner_up)
            if match.decision in {Decision.MATCH, Decision.POSSIBLE_MATCH}:
                self.graph_memory.add_match(match, source_schema.dataset_id, target_schema.dataset_id)
            best_matches.append(match)
        return tuple(best_matches)

    def _rank_targets(
        self,
        source: ColumnProfile,
        targets: tuple[ColumnProfile, ...],
    ) -> list[tuple[ColumnProfile, float]]:
        scored: list[tuple[ColumnProfile, float]] = []
        for target in targets:
            name_score = lexical_similarity(source.name, target.name)
            type_score = self._type_score(source, target)
            value_score = self._value_score(source, target)
            graph_score = self.graph_memory.graph_hint(source, target)
            base = 0.42 * name_score + 0.23 * type_score + 0.20 * value_score + 0.15 * graph_score
            scored.append((target, round(clamp(base), 4)))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored

    def _build_match(
        self,
        source: ColumnProfile,
        target: ColumnProfile,
        base_score: float,
        runner_up_score: float | None,
    ) -> CandidateMatch:
        name_score = lexical_similarity(source.name, target.name)
        type_score = self._type_score(source, target)
        value_score = self._value_score(source, target)
        route = self.router.route(source, target, base_score, runner_up_score)
        evidence = self._collect_evidence(route, source, target)
        evidence_score = self._evidence_score(evidence)
        confidence = clamp(0.78 * base_score + 0.22 * evidence_score)
        if source.inferred_type != target.inferred_type and name_score < 0.75:
            confidence = clamp(confidence - 0.12)
        decision = self._decision(confidence, route, source, target)
        rationale = self._rationale(source, target, decision, route, confidence, evidence_score)
        match = CandidateMatch(
            source_column=source.name,
            target_column=target.name,
            name_score=round(name_score, 4),
            type_score=round(type_score, 4),
            value_score=round(value_score, 4),
            evidence_score=round(evidence_score, 4),
            confidence=round(confidence, 4),
            route=route,
            decision=decision,
            rationale=rationale,
            evidence=evidence,
        )
        if route in {Route.AGENTIC_VERIFY, Route.EXTERNAL_KB}:
            return attach_reasoning(match, self.reasoner.explain_match(source, target, evidence, rationale))
        return match

    def _collect_evidence(
        self,
        route: Route,
        source: ColumnProfile,
        target: ColumnProfile,
    ) -> tuple[EvidenceItem, ...]:
        if route == Route.DIRECT:
            return ()
        local = list(self.retriever.evidence_for_columns(source, target, top_k=self.settings.top_k))
        if route == Route.EXTERNAL_KB:
            query = f"{source.name} {target.name} data integration schema matching"
            local.extend(self.external_client.search(query, top_k=3))
        local.sort(key=lambda item: item.score, reverse=True)
        return tuple(local[: self.settings.top_k])

    @staticmethod
    def _type_score(source: ColumnProfile, target: ColumnProfile) -> float:
        if source.inferred_type == target.inferred_type:
            return 1.0
        numeric = {source.inferred_type.value, target.inferred_type.value} <= {"integer", "float"}
        return 0.72 if numeric else 0.0

    @staticmethod
    def _value_score(source: ColumnProfile, target: ColumnProfile) -> float:
        source_values = " ".join(source.sample_values[:10])
        target_values = " ".join(target.sample_values[:10])
        return lexical_similarity(source_values, target_values)

    @staticmethod
    def _evidence_score(evidence: tuple[EvidenceItem, ...]) -> float:
        if not evidence:
            return 0.0
        top_scores = [item.score for item in evidence[:3]]
        return clamp(sum(top_scores) / len(top_scores))

    def _decision(
        self,
        confidence: float,
        route: Route,
        source: ColumnProfile,
        target: ColumnProfile,
    ) -> Decision:
        if confidence >= self.settings.confidence_threshold and source.inferred_type == target.inferred_type:
            return Decision.MATCH
        if confidence >= 0.56:
            return Decision.POSSIBLE_MATCH
        if confidence <= 0.34 and route != Route.EXTERNAL_KB:
            return Decision.NO_MATCH
        return Decision.NEEDS_REVIEW

    @staticmethod
    def _rationale(
        source: ColumnProfile,
        target: ColumnProfile,
        decision: Decision,
        route: Route,
        confidence: float,
        evidence_score: float,
    ) -> str:
        return (
            f"{decision.value.replace('_', ' ').title()} via {route.value}: "
            f"{source.name} and {target.name} have confidence {confidence:.2f}, "
            f"type comparison {source.inferred_type.value}->{target.inferred_type.value}, "
            f"and evidence score {evidence_score:.2f}."
        )

