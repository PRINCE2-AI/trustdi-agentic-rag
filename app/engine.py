from __future__ import annotations

from pathlib import Path

from app.config import Settings, get_settings
from app.evaluator import build_result
from app.matching import AgenticMatcher
from app.profiler import SchemaProfiler
from app.schemas import IntegrationResult, SchemaProfile


class TrustDIEngine:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.profiler = SchemaProfiler()
        self.matcher = AgenticMatcher(self.settings)

    def profile_csv(self, path: str | Path, dataset_id: str | None = None) -> SchemaProfile:
        return self.profiler.profile_csv(path, dataset_id=dataset_id)

    def match_csvs(
        self,
        source_path: str | Path,
        target_path: str | Path,
        gold: dict[str, str] | None = None,
    ) -> IntegrationResult:
        source = self.profile_csv(source_path)
        target = self.profile_csv(target_path)
        return self.match_profiles(source, target, gold=gold)

    def match_profiles(
        self,
        source: SchemaProfile,
        target: SchemaProfile,
        gold: dict[str, str] | None = None,
    ) -> IntegrationResult:
        matches = self.matcher.match(source, target)
        return build_result(source.dataset_id, target.dataset_id, matches, gold=gold)

