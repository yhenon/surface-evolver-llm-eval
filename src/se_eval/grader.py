from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .dynamic_checks import run_dynamic_checks
from .models import Task
from .static_checks import run_static_checks
from .visual import create_visual_artifacts, default_visual_paths


def grade_submission(task: Task, fe_content: str) -> dict[str, Any]:
    static = run_static_checks(fe_content, task.static_checks)
    dynamic = run_dynamic_checks(
        fe_content=fe_content,
        checks=task.dynamic_checks,
        setup_script=task.hidden_command_script,
    )

    score = 0.0
    if static.ok:
        score += 0.3
    if dynamic.evolver["ok"]:
        score += 0.3
    if dynamic.ok:
        score += 0.4

    passed = static.ok and dynamic.ok
    return {
        "task_id": task.id,
        "score": score,
        "passed": passed,
        "static": {
            "ok": static.ok,
            "details": static.details,
        },
        "dynamic": {
            "ok": dynamic.ok,
            "details": dynamic.details,
        },
        "evolver_hidden": {
            "ok": dynamic.evolver["ok"],
            "timed_out": dynamic.evolver["timed_out"],
            "exit_code": dynamic.evolver["exit_code"],
            "stdout_tail": dynamic.evolver["stdout"][-4000:],
            "stderr_tail": dynamic.evolver["stderr"][-4000:],
        },
    }


def default_result_path(input_path: Path) -> Path:
    if input_path.is_dir():
        return input_path / "result.json"
    return input_path.with_suffix(input_path.suffix + ".result.json")


def submission_path(input_path: Path) -> Path:
    if input_path.is_dir():
        return input_path / "submission.fe"
    return input_path


def grade_existing_submission(
    input_path: Path,
    task: Task,
    output_path: Path | None = None,
    write_result: bool = True,
    write_visual: bool = False,
) -> dict[str, Any]:
    fe_path = submission_path(input_path)
    if not fe_path.exists():
        raise FileNotFoundError(f"No submission file found at {fe_path}")

    fe_content = fe_path.read_text(encoding="utf-8")
    grade = grade_submission(task, fe_content)

    if write_visual:
        svg_path, off_path = default_visual_paths(input_path)
        visual = create_visual_artifacts(
            fe_content=fe_content,
            svg_path=svg_path,
            off_path=off_path,
        )
        grade["visual"] = {
            "ok": visual.ok,
            "details": visual.details,
        }

    if write_result:
        destination = output_path or default_result_path(input_path)
        destination.write_text(
            json.dumps(grade, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return grade
