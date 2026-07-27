from __future__ import annotations

import os
from typing import Any

from app.schemas import EvidenceItem


class WikidataEvidenceClient:
    """Optional public API lookup for semantic hints.

    The project remains fully usable without network access. Set
    TRUSTDI_EXTERNAL_KB=true to enable this at runtime.
    """

    def __init__(self, enabled: bool = False, timeout: int = 8) -> None:
        self.enabled = enabled
        self.timeout = timeout

    def search(self, query: str, top_k: int = 3) -> tuple[EvidenceItem, ...]:
        if not self.enabled:
            return ()
        endpoint = os.getenv("WIKIDATA_SEARCH_URL", "https://www.wikidata.org/w/api.php")
        params: dict[str, Any] = {
            "action": "wbsearchentities",
            "language": "en",
            "format": "json",
            "limit": top_k,
            "search": query,
        }
        try:
            import requests

            response = requests.get(endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return ()
        items: list[EvidenceItem] = []
        for index, item in enumerate(payload.get("search", [])[:top_k]):
            label = item.get("label", "")
            description = item.get("description", "")
            concept_id = item.get("id", "")
            if not label and not description:
                continue
            items.append(
                EvidenceItem(
                    source=f"https://www.wikidata.org/wiki/{concept_id}" if concept_id else "wikidata",
                    text=f"{label}: {description}",
                    score=round(1.0 - index * 0.15, 4),
                    metadata={"kind": "wikidata", "id": concept_id},
                )
            )
        return tuple(items)
