from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import Task
from .run_eval import (
    BASELINE_MODELS,
    DEFAULT_BASELINE,
    REASONING_EFFORTS,
    TASK_VISIBILITY_DIRS,
    model_slug,
    now_slug,
    run_pipeline,
)


TASK_VISIBILITIES = ("public", "private")


@dataclass(frozen=True)
class TaskSpec:
    visibility: str
    task_id: str
    path: Path


@dataclass(frozen=True)
class ModelSpec:
    label: str
    model: str
    baseline: str | None = None


NO_REASONING_EFFORT_ALIASES = {"na", "n/a", "default", "unset"}


def iter_task_specs(
    visibilities: list[str],
    task_ids: set[str] | None,
    task_dirs: dict[str, Path],
) -> list[TaskSpec]:
    specs: list[TaskSpec] = []
    for visibility in visibilities:
        task_dir = task_dirs[visibility]
        if not task_dir.exists():
            raise FileNotFoundError(f"Task directory does not exist: {task_dir}")

        for path in sorted(task_dir.glob("*.json")):
            task_id = path.stem
            if task_ids is not None and task_id not in task_ids:
                continue
            specs.append(TaskSpec(visibility=visibility, task_id=task_id, path=path))

    if not specs:
        filters = sorted(task_ids) if task_ids is not None else "all"
        raise SystemExit(f"No tasks matched visibility={visibilities}, task={filters}")

    return specs


def selected_visibilities(task_visibility: str) -> list[str]:
    if task_visibility == "all":
        return list(TASK_VISIBILITIES)
    return [task_visibility]


def selected_models(args: argparse.Namespace) -> list[ModelSpec]:
    specs: list[ModelSpec] = []

    baselines = list(BASELINE_MODELS) if args.all_baselines else args.baseline
    if not baselines and not args.model:
        baselines = [DEFAULT_BASELINE]

    for baseline in baselines or []:
        specs.append(
            ModelSpec(
                label=baseline,
                baseline=baseline,
                model=BASELINE_MODELS[baseline],
            )
        )

    for model in args.model or []:
        specs.append(
            ModelSpec(
                label=model_slug(model),
                model=model,
            )
        )

    deduped: list[ModelSpec] = []
    seen: set[tuple[str, str | None]] = set()
    for spec in specs:
        key = (spec.model, spec.baseline)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(spec)

    return deduped


def selected_reasoning_efforts(args: argparse.Namespace) -> list[str | None]:
    raw_efforts = args.reasoning_effort or []
    if not raw_efforts:
        return [None]

    efforts: list[str | None] = []
    seen: set[str | None] = set()
    valid_efforts = set(REASONING_EFFORTS)
    for raw_group in raw_efforts:
        for raw_effort in raw_group.split(","):
            effort = raw_effort.strip().lower()
            if not effort:
                raise SystemExit("--reasoning-effort contains an empty value.")
            if effort in NO_REASONING_EFFORT_ALIASES:
                normalized: str | None = None
            elif effort in valid_efforts:
                normalized = effort
            else:
                valid_values = ", ".join([*REASONING_EFFORTS, "na"])
                raise SystemExit(f"--reasoning-effort must contain only: {valid_values}")

            if normalized in seen:
                continue
            seen.add(normalized)
            efforts.append(normalized)

    return efforts


def model_run_label(model: ModelSpec, reasoning_effort: str | None) -> str:
    label = model.label
    if reasoning_effort:
        label += f"_reasoning-{reasoning_effort}"
    return label


def run_dir(matrix_dir: Path, task: TaskSpec, model: ModelSpec, reasoning_effort: str | None) -> Path:
    return matrix_dir / f"{task.visibility}_{task.task_id}" / model_run_label(model, reasoning_effort)


def summarize_outcome(
    *,
    matrix_id: str,
    task_spec: TaskSpec,
    model_spec: ModelSpec,
    out_dir: Path,
    started_at: str,
    duration_s: float,
    reasoning_effort: str | None,
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    generation = (result or {}).get("generation", {})
    grade = (result or {}).get("grade", {})
    dynamic = grade.get("dynamic", {})
    static = grade.get("static", {})
    token_usage = generation.get("token_usage", {})

    return {
        "matrix_id": matrix_id,
        "started_at": started_at,
        "duration_s": round(duration_s, 3),
        "task_visibility": task_spec.visibility,
        "task_id": task_spec.task_id,
        "task_path": str(task_spec.path),
        "model_label": model_spec.label,
        "model_run_label": model_run_label(model_spec, reasoning_effort),
        "baseline": model_spec.baseline,
        "model": model_spec.model,
        "reasoning_effort": reasoning_effort,
        "out_dir": str(out_dir),
        "submitted": generation.get("submitted", False),
        "rounds_used": generation.get("rounds_used"),
        "max_rounds": generation.get("max_rounds"),
        "score": grade.get("score", 0.0 if error else None),
        "passed": grade.get("passed", False if error else None),
        "static_ok": static.get("ok"),
        "dynamic_ok": dynamic.get("ok"),
        "evolver_ok": grade.get("evolver_hidden", {}).get("ok"),
        "measurements": dynamic.get("details", {}).get("measurements", {}),
        "static_failures": static.get("details", {}).get("failures", []),
        "dynamic_failures": dynamic.get("details", {}).get("failures", []),
        "token_usage": token_usage.get("totals", {}),
        "error": error or generation.get("error"),
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def write_summary(path: Path, outcomes: list[dict[str, Any]]) -> None:
    by_model: dict[str, dict[str, Any]] = {}
    by_task: dict[str, dict[str, Any]] = {}

    for outcome in outcomes:
        model_key = outcome.get("model_run_label") or outcome["model_label"]
        task_key = f"{outcome['task_visibility']}/{outcome['task_id']}"

        model_bucket = by_model.setdefault(model_key, {"runs": 0, "passed": 0, "score_sum": 0.0})
        task_bucket = by_task.setdefault(task_key, {"runs": 0, "passed": 0, "score_sum": 0.0})

        for bucket in (model_bucket, task_bucket):
            bucket["runs"] += 1
            bucket["passed"] += int(bool(outcome.get("passed")))
            bucket["score_sum"] += float(outcome.get("score") or 0.0)

    for bucket in list(by_model.values()) + list(by_task.values()):
        runs = bucket["runs"]
        bucket["pass_rate"] = bucket["passed"] / runs if runs else 0.0
        bucket["mean_score"] = bucket["score_sum"] / runs if runs else 0.0
        del bucket["score_sum"]

    write_json(
        path,
        {
            "runs": len(outcomes),
            "passed": sum(int(bool(outcome.get("passed"))) for outcome in outcomes),
            "mean_score": (
                sum(float(outcome.get("score") or 0.0) for outcome in outcomes) / len(outcomes)
                if outcomes
                else 0.0
            ),
            "by_model": by_model,
            "by_task": by_task,
            "outcomes": outcomes,
        },
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run selected models across public/private task sets, grade each run, "
            "and consolidate plotting-friendly outcomes."
        )
    )
    parser.add_argument(
        "--task-visibility",
        choices=("public", "private", "all"),
        default="all",
        help="Task set to run. Defaults to all public and private tasks.",
    )
    parser.add_argument(
        "--task",
        action="append",
        help="Task id to include. Repeat to select multiple tasks. Defaults to all tasks in the selected visibilities.",
    )
    parser.add_argument("--public-task-dir", type=Path, default=Path(TASK_VISIBILITY_DIRS["public"]))
    parser.add_argument("--private-task-dir", type=Path, default=Path(TASK_VISIBILITY_DIRS["private"]))
    parser.add_argument(
        "--baseline",
        action="append",
        choices=BASELINE_MODELS,
        help=f"Named baseline to run. Repeat to select multiple. Defaults to {DEFAULT_BASELINE!r}.",
    )
    parser.add_argument(
        "--all-baselines",
        action="store_true",
        help="Run every configured named baseline.",
    )
    parser.add_argument(
        "--model",
        action="append",
        help="Exact OpenRouter model id to run. Repeat to select multiple.",
    )
    parser.add_argument(
        "--reasoning-effort",
        "--reasoning_effort",
        action="append",
        help=(
            "Optional OpenRouter reasoning effort for models that support thinking tokens. "
            "Repeat or pass a comma-separated list to expand the matrix, e.g. high,na,low. "
            "Use na to omit reasoning controls for that run."
        ),
    )
    parser.add_argument("--max-rounds", type=int, default=8)
    parser.add_argument("--out-root", type=Path, default=Path("runs"))
    parser.add_argument(
        "--matrix-dir",
        type=Path,
        help="Directory for this matrix run. Defaults to runs/<timestamp>_matrix.",
    )
    parser.add_argument(
        "--results-file",
        type=Path,
        help="JSONL file for one compact outcome per model/task run. Defaults inside --matrix-dir.",
    )
    parser.add_argument(
        "--summary-file",
        type=Path,
        help="Summary JSON file rewritten after each completed run. Defaults inside --matrix-dir.",
    )
    parser.add_argument("--visual", action="store_true", help="Generate visual.svg and visual.off while grading.")
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip model/task pairs whose run directory already has result.json.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop at the first failed model/task pair instead of recording the error and continuing.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned model/task matrix without calling models or writing results.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    matrix_id = now_slug()
    matrix_dir = args.matrix_dir or args.out_root / f"{matrix_id}_matrix"
    results_file = args.results_file or matrix_dir / "outcomes.jsonl"
    summary_file = args.summary_file or matrix_dir / "summary.json"

    task_dirs = {
        "public": args.public_task_dir,
        "private": args.private_task_dir,
    }
    tasks = iter_task_specs(
        visibilities=selected_visibilities(args.task_visibility),
        task_ids=set(args.task) if args.task else None,
        task_dirs=task_dirs,
    )
    models = selected_models(args)
    reasoning_efforts = selected_reasoning_efforts(args)

    planned = [
        {
            "task_visibility": task.visibility,
            "task_id": task.task_id,
            "model_label": model.label,
            "model_run_label": model_run_label(model, reasoning_effort),
            "baseline": model.baseline,
            "model": model.model,
            "reasoning_effort": reasoning_effort,
            "out_dir": str(run_dir(matrix_dir, task, model, reasoning_effort)),
        }
        for task in tasks
        for model in models
        for reasoning_effort in reasoning_efforts
    ]

    if args.dry_run:
        print(json.dumps({"matrix_dir": str(matrix_dir), "planned": planned}, indent=2, ensure_ascii=False))
        return

    print(f"Writing outcomes to {results_file}")
    print(f"Writing summary to {summary_file}")

    outcomes: list[dict[str, Any]] = load_jsonl(results_file) if args.skip_existing else []
    if outcomes:
        print(f"Loaded {len(outcomes)} existing outcomes from {results_file}")

    for item in planned:
        task_spec = next(
            task
            for task in tasks
            if task.visibility == item["task_visibility"] and task.task_id == item["task_id"]
        )
        model_spec = next(
            model
            for model in models
            if model.label == item["model_label"] and model.model == item["model"]
        )
        reasoning_effort = item["reasoning_effort"]
        out_dir = Path(item["out_dir"])

        if args.skip_existing and (out_dir / "result.json").exists():
            print(
                "Skipping existing run: "
                f"{task_spec.visibility}/{task_spec.task_id} :: "
                f"{model_run_label(model_spec, reasoning_effort)}"
            )
            continue

        print(
            f"Running {task_spec.visibility}/{task_spec.task_id} :: "
            f"{model_run_label(model_spec, reasoning_effort)}"
        )
        start = time.monotonic()
        started_at = now_slug()
        error: str | None = None
        result: dict[str, Any] | None = None

        try:
            task = Task.load(task_spec.task_id, task_spec.path.parent)
            result = run_pipeline(
                task=task,
                out_dir=out_dir,
                model=model_spec.model,
                max_rounds=args.max_rounds,
                reasoning_effort=reasoning_effort,
                write_visual=args.visual,
            )
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            if args.fail_fast:
                raise
            print(
                "Recorded error for "
                f"{task_spec.visibility}/{task_spec.task_id} :: "
                f"{model_run_label(model_spec, reasoning_effort)}: {error}"
            )

        outcome = summarize_outcome(
            matrix_id=matrix_id,
            task_spec=task_spec,
            model_spec=model_spec,
            out_dir=out_dir,
            started_at=started_at,
            duration_s=time.monotonic() - start,
            reasoning_effort=reasoning_effort,
            result=result,
            error=error,
        )
        outcomes.append(outcome)
        append_jsonl(results_file, outcome)
        write_summary(summary_file, outcomes)
        print(json.dumps(outcome, indent=2, ensure_ascii=False))

    print(
        json.dumps(
            {
                "matrix_dir": str(matrix_dir),
                "results_file": str(results_file),
                "summary_file": str(summary_file),
                "runs": len(outcomes),
                "passed": sum(int(bool(outcome.get("passed"))) for outcome in outcomes),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
