from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable


Outcome = dict[str, Any]

RUN_ARTIFACT_FILENAMES = (
    "result.json",
    "run_error.json",
    "generation.json",
    "submission.fe",
    "transcript.json",
)


def has_run_artifacts(out_dir: Path) -> bool:
    return any((out_dir / name).exists() for name in RUN_ARTIFACT_FILENAMES)


def is_materialized_outcome(row: Outcome, *, keep_missing_out_dir: bool = True) -> bool:
    out_dir = row.get("out_dir")
    if not out_dir:
        return True

    path = Path(str(out_dir))
    if not path.exists() or not path.is_dir():
        return keep_missing_out_dir

    return has_run_artifacts(path)


def materialized_outcomes(
    rows: Iterable[Outcome],
    *,
    keep_missing_out_dir: bool = True,
) -> tuple[list[Outcome], list[Outcome]]:
    kept: list[Outcome] = []
    skipped: list[Outcome] = []
    for row in rows:
        if is_materialized_outcome(row, keep_missing_out_dir=keep_missing_out_dir):
            kept.append(row)
        else:
            skipped.append(row)
    return kept, skipped
