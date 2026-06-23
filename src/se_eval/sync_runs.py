from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import DEFAULT_CONFIG_PATH, configured_model_spec_map
from .run_matrix import (
    TaskSpec,
    iter_task_specs,
    reasoning_efforts_for_model,
    run_dir,
    selected_visibilities,
)
from .run_matrix import ModelSpec
from .run_eval import TASK_VISIBILITY_DIRS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the runs/<model>/<task> directory grid from configured models and available tasks."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--runs-root", type=Path, default=Path("runs"))
    parser.add_argument(
        "--task-visibility",
        choices=("public", "private", "all"),
        default="all",
        help="Task set to include. Defaults to all public and private tasks.",
    )
    parser.add_argument(
        "--task",
        action="append",
        help="Task id to include. Repeat to select multiple tasks. Defaults to all tasks.",
    )
    parser.add_argument("--public-task-dir", type=Path, default=Path(TASK_VISIBILITY_DIRS["public"]))
    parser.add_argument("--private-task-dir", type=Path, default=Path(TASK_VISIBILITY_DIRS["private"]))
    parser.add_argument(
        "--reasoning-effort",
        "--reasoning_effort",
        action="append",
        help="Optional reasoning effort suffixes to include. Same syntax as se_eval.run_matrix.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the planned directories without creating them.")
    return parser.parse_args()


def planned_dirs(args: argparse.Namespace) -> list[Path]:
    task_dirs = {
        "public": args.public_task_dir,
        "private": args.private_task_dir,
    }
    tasks: list[TaskSpec] = iter_task_specs(
        visibilities=selected_visibilities(args.task_visibility),
        task_ids=set(args.task) if args.task else None,
        task_dirs=task_dirs,
    )
    models = [
        ModelSpec(
            label=name,
            baseline=name,
            model=model.model,
            reasoning_effort=model.reasoning_effort,
            provider=model.provider,
        )
        for name, model in configured_model_spec_map(args.config).items()
    ]

    return [
        run_dir(args.runs_root, task, model, reasoning_effort)
        for model in models
        for task in tasks
        for reasoning_effort in reasoning_efforts_for_model(args, model)
    ]


def main() -> None:
    args = parse_args()
    dirs = planned_dirs(args)
    created: list[str] = []
    existing: list[str] = []

    for path in dirs:
        if path.exists():
            existing.append(str(path))
            continue
        if not args.dry_run:
            path.mkdir(parents=True, exist_ok=True)
        created.append(str(path))

    print(
        json.dumps(
            {
                "runs_root": str(args.runs_root),
                "dry_run": args.dry_run,
                "planned": len(dirs),
                "created": created,
                "existing": existing,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
