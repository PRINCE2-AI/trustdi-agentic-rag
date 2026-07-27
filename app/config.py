from __future__ import annotations

import os
from dataclasses import dataclass


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    external_kb_enabled: bool = _bool_env("TRUSTDI_EXTERNAL_KB", False)
    top_k: int = int(os.getenv("TRUSTDI_TOP_K", "5"))
    confidence_threshold: float = float(os.getenv("TRUSTDI_CONFIDENCE_THRESHOLD", "0.72"))
    ambiguity_margin: float = float(os.getenv("TRUSTDI_AMBIGUITY_MARGIN", "0.08"))

    @property
    def openai_enabled(self) -> bool:
        return bool(self.openai_api_key)


def get_settings() -> Settings:
    return Settings()

