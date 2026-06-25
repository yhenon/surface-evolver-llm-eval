from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


CHARTS = (
    "by_model.svg",
    "model_tool_usage.svg",
    "score_vs_total_tokens.svg",
    "score_vs_total_cost.svg",
    "by_task.svg",
    "task_model_heatmap.svg",
)
DATA_FILES = ("aggregates.json",)


def copy_file(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Missing source file: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def validate_aggregates(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    required = {"runs", "passed", "mean_score", "by_model", "by_task"}
    missing = sorted(required - payload.keys())
    if missing:
        raise ValueError(f"{path} is missing required keys: {', '.join(missing)}")
    return payload


def run_plotter(args: argparse.Namespace) -> None:
    env = os.environ.copy()
    src_dir = str(args.src_dir)
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{src_dir}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else src_dir
    command = [
        sys.executable,
        "-m",
        "se_eval.plot_results",
        "--runs-root",
        str(args.runs_root),
        "--output-dir",
        str(args.plots_dir),
        "--icon-dir",
        str(args.icon_dir),
    ]
    command.extend(str(path) for path in args.inputs)
    subprocess.run(command, check=True, env=env)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy generated plot artifacts into the GitHub Pages docs directory."
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        help="Optional run roots to pass to se_eval.plot_results with --replot.",
    )
    parser.add_argument("--plots-dir", type=Path, default=Path("runs/plots"))
    parser.add_argument("--docs-dir", type=Path, default=Path("docs"))
    parser.add_argument("--runs-root", type=Path, default=Path("runs"))
    parser.add_argument("--icon-dir", type=Path, default=Path("icons"))
    parser.add_argument("--src-dir", type=Path, default=Path("src"))
    parser.add_argument(
        "--replot",
        action="store_true",
        help="Regenerate plots with se_eval.plot_results before copying them into docs/.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.replot:
        run_plotter(args)

    chart_dir = args.docs_dir / "assets" / "charts"
    data_dir = args.docs_dir / "data"

    for name in CHARTS:
        copy_file(args.plots_dir / name, chart_dir / name)
    for name in DATA_FILES:
        copy_file(args.plots_dir / name, data_dir / name)

    aggregates = validate_aggregates(data_dir / "aggregates.json")
    print(
        json.dumps(
            {
                "docs_dir": str(args.docs_dir),
                "plots_dir": str(args.plots_dir),
                "runs": aggregates["runs"],
                "passed": aggregates["passed"],
                "mean_score": aggregates["mean_score"],
                "copied": [*CHARTS, *DATA_FILES],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
