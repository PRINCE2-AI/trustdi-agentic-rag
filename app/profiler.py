from __future__ import annotations

import csv
from pathlib import Path

from app.schemas import ColumnProfile, SchemaProfile
from app.text_utils import infer_column_type, tokenize


class SchemaProfiler:
    """Builds compact profiles from CSV files without requiring pandas."""

    def __init__(self, sample_size: int = 25) -> None:
        self.sample_size = sample_size

    def profile_csv(self, path: str | Path, dataset_id: str | None = None) -> SchemaProfile:
        file_path = Path(path)
        dataset = dataset_id or file_path.stem
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise ValueError(f"CSV has no header: {file_path}")
            rows = list(reader)
        return self.profile_rows(dataset, reader.fieldnames, rows)

    def profile_rows(
        self,
        dataset_id: str,
        fieldnames: list[str],
        rows: list[dict[str, str]],
    ) -> SchemaProfile:
        columns: list[ColumnProfile] = []
        row_count = len(rows)
        for name in fieldnames:
            values = [str(row.get(name, "") or "") for row in rows]
            sample_values = tuple(value for value in values[: self.sample_size] if value.strip())
            null_count = sum(1 for value in values if not value.strip())
            inferred_type = infer_column_type(list(sample_values))
            column_tokens = tokenize(name + " " + " ".join(sample_values[:5]))
            columns.append(
                ColumnProfile(
                    dataset_id=dataset_id,
                    name=name,
                    inferred_type=inferred_type,
                    sample_values=sample_values,
                    tokens=column_tokens,
                    null_ratio=(null_count / row_count) if row_count else 0.0,
                )
            )
        return SchemaProfile(dataset_id=dataset_id, columns=tuple(columns), row_count=row_count)

