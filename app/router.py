from __future__ import annotations

from app.config import Settings
from app.schemas import ColumnProfile, Route


class AdaptiveRoutePlanner:
    """Routes easy matches cheaply and ambiguous matches through evidence agents."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def route(
        self,
        source: ColumnProfile,
        target: ColumnProfile,
        base_score: float,
        runner_up_score: float | None = None,
    ) -> Route:
        margin = base_score - (runner_up_score or 0.0)
        names_are_clear = source.name.lower() == target.name.lower() or base_score >= 0.9
        type_conflict = source.inferred_type != target.inferred_type
        if names_are_clear and not type_conflict:
            return Route.DIRECT
        if type_conflict and self.settings.external_kb_enabled:
            return Route.EXTERNAL_KB
        if margin <= self.settings.ambiguity_margin or 0.45 <= base_score < self.settings.confidence_threshold:
            return Route.AGENTIC_VERIFY
        return Route.RETRIEVE

