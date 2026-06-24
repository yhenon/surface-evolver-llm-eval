from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path
from typing import Any

from .grader import grade_existing_submission
from .models import Task
from .outcomes import materialized_outcomes
from .run_eval import TASK_VISIBILITY_DIRS, now_slug
from .run_matrix import write_summary


Outcome = dict[str, Any]


def discover_result_dirs(runs_root: Path) -> list[Path]:
    if not runs_root.exists():
        return []
    if (runs_root / "outcomes.jsonl").exists():
        return [runs_root]
    return sorted(path for path in runs_root.glob("*_matrix") if path.is_dir())


def outcomes_path(input_path: Path) -> Path:
    if input_path.is_dir():
        return input_path / "outcomes.jsonl"
    return input_path


def load_jsonl(path: Path) -> list[Outcome]:
    rows: list[Outcome] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[Outcome]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def task_path_for(row: Outcome) -> Path:
    explicit = row.get("task_path")
    if explicit:
        return Path(str(explicit))

    visibility = str(row.get("task_visibility") or "")
    task_id = str(row.get("task_id") or "")
    if visibility not in TASK_VISIBILITY_DIRS or not task_id:
        raise ValueError(f"Cannot resolve task path for outcome row: {row}")
    return Path(TASK_VISIBILITY_DIRS[visibility]) / f"{task_id}.json"


def update_outcome_from_grade(row: Outcome, grade: dict[str, Any], duration_s: float) -> Outcome:
    dynamic = grade.get("dynamic", {})
    static = grade.get("static", {})
    updated = dict(row)
    updated.update(
        {
            "rescore_started_at": now_slug(),
            "rescore_duration_s": round(duration_s, 3),
            "score": grade.get("score"),
            "passed": grade.get("passed"),
            "static_ok": static.get("ok"),
            "dynamic_ok": dynamic.get("ok"),
            "evolver_ok": grade.get("evolver_hidden", {}).get("ok"),
            "measurements": dynamic.get("details", {}).get("measurements", {}),
            "static_failures": static.get("details", {}).get("failures", []),
            "dynamic_failures": dynamic.get("details", {}).get("failures", []),
            "error": None,
        }
    )
    return updated


def update_outcome_from_error(row: Outcome, error: str, duration_s: float) -> Outcome:
    updated = dict(row)
    updated.update(
        {
            "rescore_started_at": now_slug(),
            "rescore_duration_s": round(duration_s, 3),
            "score": 0.0,
            "passed": False,
            "static_ok": None,
            "dynamic_ok": None,
            "evolver_ok": None,
            "measurements": {},
            "static_failures": [],
            "dynamic_failures": [],
            "error": error,
        }
    )
    return updated


def task_key(row: Outcome) -> str:
    visibility = row.get("task_visibility") or "unknown"
    task_id = row.get("task_id") or "unknown"
    return f"{visibility}/{task_id}"


def model_key(row: Outcome) -> str:
    return str(row.get("model_run_label") or row.get("model_label") or row.get("model"))


def should_rescore(row: Outcome, tasks: set[str] | None, models: set[str] | None) -> bool:
    if tasks is not None and str(row.get("task_id")) not in tasks and task_key(row) not in tasks:
        return False
    if models is not None and str(row.get("model_label")) not in models and model_key(row) not in models:
        return False
    return True


def backup_file(path: Path, suffix: str) -> Path | None:
    if not path.exists():
        return None
    backup = path.with_suffix(path.suffix + f".bak-{suffix}")
    shutil.copy2(path, backup)
    return backup


def rescore_rows(
    rows: list[Outcome],
    *,
    write_result: bool,
    write_visual: bool,
    fail_fast: bool,
    tasks: set[str] | None,
    models: set[str] | None,
) -> tuple[list[Outcome], int]:
    rescored: list[Outcome] = []
    rescored_count = 0
    for row in rows:
        if not should_rescore(row, tasks, models):
            rescored.append(row)
            continue

        out_dir = Path(str(row.get("out_dir") or ""))
        start = time.monotonic()
        try:
            if not row.get("submitted", True):
                raise FileNotFoundError("Outcome row has submitted=false; no saved submission to rescore.")
            task = Task.load(task_path_for(row).stem, task_path_for(row).parent)
            grade = grade_existing_submission(
                input_path=out_dir,
                task=task,
                write_result=write_result,
                write_visual=write_visual,
            )
            updated = update_outcome_from_grade(row, grade, time.monotonic() - start)
            print(
                f"rescored {updated.get('task_visibility')}/{updated.get('task_id')} :: "
                f"{updated.get('model_run_label') or updated.get('model_label')} -> "
                f"score={updated.get('score')} passed={updated.get('passed')}"
            )
            rescored_count += 1
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            if fail_fast:
                raise
            updated = update_outcome_from_error(row, error, time.monotonic() - start)
            print(
                f"rescore error {updated.get('task_visibility')}/{updated.get('task_id')} :: "
                f"{updated.get('model_run_label') or updated.get('model_label')}: {error}"
            )
            rescored_count += 1
        rescored.append(updated)
    return rescored, rescored_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Re-run grading on saved matrix submissions without calling models, "
            "then refresh result.json, outcomes.jsonl, and summary.json."
        )
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        help="Run roots or outcomes.jsonl files. Defaults to runs/ when runs/outcomes.jsonl exists.",
    )
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=Path("runs"),
        help="Root used for default discovery when no inputs are passed.",
    )
    parser.add_argument("--visual", action="store_true", help="Regenerate visual.svg and visual.off while rescoring.")
    parser.add_argument(
        "--task",
        action="append",
        help="Only rescore this task id or visibility/task_id. Repeat to include multiple tasks.",
    )
    parser.add_argument(
        "--model",
        action="append",
        help="Only rescore this model_label or model_run_label. Repeat to include multiple models.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the grader and print changed scores, but do not overwrite result/outcome/summary files.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not create .bak-<timestamp> copies of outcomes.jsonl and summary.json before rewriting.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop at the first rescore error instead of recording it in the outcome row.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inputs = args.inputs or discover_result_dirs(args.runs_root)
    if not inputs:
        raise SystemExit(f"No outcome directories found under {args.runs_root}")

    backup_suffix = now_slug()
    changed_files: list[str] = []
    total_rows = 0
    total_rescored = 0
    task_filter = set(args.task) if args.task else None
    model_filter = set(args.model) if args.model else None
    for input_path in inputs:
        path = outcomes_path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"No outcomes JSONL found at {path}")

        rows = load_jsonl(path)
        rows, skipped_rows = materialized_outcomes(rows)
        if skipped_rows:
            print(f"Ignoring {len(skipped_rows)} empty placeholder outcome rows from {path}")
        total_rows += len(rows)
        print(f"Rescoring {len(rows)} rows from {path}")
        rescored, rescored_count = rescore_rows(
            rows,
            write_result=not args.dry_run,
            write_visual=args.visual and not args.dry_run,
            fail_fast=args.fail_fast,
            tasks=task_filter,
            models=model_filter,
        )
        total_rescored += rescored_count

        summary_path = path.parent / "summary.json"
        if not args.dry_run:
            if not args.no_backup:
                for backup_target in (path, summary_path):
                    backup = backup_file(backup_target, backup_suffix)
                    if backup is not None:
                        changed_files.append(str(backup))
            write_jsonl(path, rescored)
            write_summary(summary_path, rescored)
            changed_files.extend([str(path), str(summary_path)])

    print(
        json.dumps(
            {
                "inputs": [str(path) for path in inputs],
                "rows": total_rows,
                "rescored_rows": total_rescored,
                "dry_run": args.dry_run,
                "changed_files": changed_files,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
