from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import ConfiguredModel, configured_model_spec_map


Outcome = dict[str, Any]
TaskMetadata = dict[tuple[str, str], dict[str, str | None]]

RUN_ARTIFACT_FILENAMES = (
    "result.json",
    "run_error.json",
    "generation.json",
    "submission.fe",
    "transcript.json",
)


def has_run_artifacts(out_dir: Path) -> bool:
    return any((out_dir / name).exists() for name in RUN_ARTIFACT_FILENAMES)


def load_json_file(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_task_metadata(public_task_dir: Path, private_task_dir: Path) -> TaskMetadata:
    metadata: TaskMetadata = {}
    for visibility, task_dir in (("public", public_task_dir), ("private", private_task_dir)):
        if not task_dir.exists():
            continue
        for path in sorted(task_dir.glob("*.json")):
            raw = json.loads(path.read_text(encoding="utf-8"))
            task_id = str(raw.get("id") or path.stem)
            metadata[(visibility, task_id)] = {
                "public_label": raw.get("public_label"),
                "path": str(path),
            }
    return metadata


def parse_task_dir_name(name: str) -> tuple[str, str] | None:
    visibility, separator, task_id = name.partition("_")
    if separator and visibility in {"public", "private"} and task_id:
        return visibility, task_id
    return None


def iter_run_dirs(runs_root: Path) -> list[Path]:
    if not runs_root.exists():
        return []
    if runs_root.is_dir() and parse_task_dir_name(runs_root.name) is not None and has_run_artifacts(runs_root):
        return [runs_root]
    return sorted(
        path
        for path in runs_root.rglob("*")
        if path.is_dir() and parse_task_dir_name(path.name) is not None and has_run_artifacts(path)
    )


def model_metadata_for_run_label(
    model_run_label: str,
    configured_models: dict[str, ConfiguredModel],
) -> tuple[str, ConfiguredModel | None, str | None]:
    if model_run_label in configured_models:
        model = configured_models[model_run_label]
        return model_run_label, model, model.reasoning_effort

    suffix = "_reasoning-"
    if suffix in model_run_label:
        model_label, reasoning_label = model_run_label.rsplit(suffix, 1)
        configured = configured_models.get(model_label)
        reasoning_effort = None if reasoning_label == "na" else reasoning_label
        if configured is not None:
            return model_label, configured, reasoning_effort
        return model_label, None, reasoning_effort

    return model_run_label, None, None


def zero_grade_from_generation(task_id: str, generation: dict[str, Any] | None) -> dict[str, Any] | None:
    if generation is None or generation.get("submitted"):
        return None
    return {
        "task_id": task_id,
        "score": 0.0,
        "passed": False,
        "error": generation.get("error"),
        "error_path": generation.get("error_path"),
    }


def outcome_from_run_dir(
    runs_root: Path,
    out_dir: Path,
    *,
    task_metadata: TaskMetadata,
    configured_models: dict[str, ConfiguredModel],
    matrix_id: str = "derived",
) -> Outcome | None:
    task_key = parse_task_dir_name(out_dir.name)
    if task_key is None or not has_run_artifacts(out_dir):
        return None

    visibility, task_id = task_key
    try:
        model_run_label = out_dir.parent.relative_to(runs_root).as_posix()
    except ValueError:
        model_run_label = out_dir.parent.name

    generation = load_json_file(out_dir / "generation.json")
    grade = load_json_file(out_dir / "result.json") or zero_grade_from_generation(task_id, generation) or {}
    run_error = load_json_file(out_dir / "run_error.json")
    error_context = (run_error or {}).get("context") or {}

    model_label, configured_model, inferred_reasoning_effort = model_metadata_for_run_label(
        model_run_label,
        configured_models,
    )
    task_info = task_metadata.get((visibility, task_id), {})
    dynamic = grade.get("dynamic", {})
    static = grade.get("static", {})
    token_usage = (generation or {}).get("token_usage", {})
    generated_provider = (generation or {}).get("provider")
    configured_provider = configured_model.provider if configured_model is not None else None

    error_path = None
    if run_error is not None:
        error_path = str(out_dir / "run_error.json")
    else:
        error_path = grade.get("error_path") or (generation or {}).get("error_path")

    error = (run_error or {}).get("error") or grade.get("error") or (generation or {}).get("error")
    submitted = (generation or {}).get("submitted")
    if submitted is None:
        submitted = (out_dir / "submission.fe").exists()

    return {
        "matrix_id": matrix_id,
        "started_at": (run_error or {}).get("recorded_at"),
        "duration_s": None,
        "task_visibility": visibility,
        "task_id": task_id,
        "task_public_label": task_info.get("public_label"),
        "task_path": task_info.get("path"),
        "model_label": str(error_context.get("model_label") or model_label),
        "model_run_label": str(error_context.get("model_run_label") or model_run_label),
        "baseline": error_context.get("baseline") or (model_label if configured_model is not None else None),
        "model": (generation or {}).get("model")
        or error_context.get("model")
        or (configured_model.model if configured_model is not None else model_run_label),
        "reasoning_effort": (generation or {}).get("reasoning_effort")
        or error_context.get("reasoning_effort")
        or inferred_reasoning_effort,
        "provider": generated_provider or error_context.get("provider") or configured_provider,
        "out_dir": str(out_dir),
        "submitted": bool(submitted),
        "rounds_used": (generation or {}).get("rounds_used") or error_context.get("rounds_used"),
        "max_rounds": (generation or {}).get("max_rounds") or error_context.get("max_rounds"),
        "score": grade.get("score", 0.0 if error else None),
        "passed": grade.get("passed", False if error else None),
        "static_ok": static.get("ok"),
        "dynamic_ok": dynamic.get("ok"),
        "evolver_ok": grade.get("evolver_hidden", {}).get("ok"),
        "measurements": dynamic.get("details", {}).get("measurements", {}),
        "static_failures": static.get("details", {}).get("failures", []),
        "dynamic_failures": dynamic.get("details", {}).get("failures", []),
        "token_usage": token_usage.get("totals", {}),
        "error": error,
        "error_path": error_path,
    }


def discover_outcomes_from_runs(
    runs_root: Path,
    *,
    public_task_dir: Path,
    private_task_dir: Path,
    config_path: Path,
    matrix_id: str = "derived",
) -> list[Outcome]:
    task_metadata = load_task_metadata(public_task_dir, private_task_dir)
    configured_models = configured_model_spec_map(config_path)
    outcomes: list[Outcome] = []
    for out_dir in iter_run_dirs(runs_root):
        outcome = outcome_from_run_dir(
            runs_root,
            out_dir,
            task_metadata=task_metadata,
            configured_models=configured_models,
            matrix_id=matrix_id,
        )
        if outcome is not None:
            outcomes.append(outcome)
    return outcomes
