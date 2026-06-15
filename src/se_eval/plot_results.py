from __future__ import annotations

import argparse
import csv
import html
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


Outcome = dict[str, Any]


SUMMARY_FIELDS = (
    "matrix_id",
    "started_at",
    "task_visibility",
    "task_id",
    "task_key",
    "model_label",
    "model_run_label",
    "baseline",
    "model",
    "reasoning_effort",
    "score",
    "passed",
    "submitted",
    "static_ok",
    "dynamic_ok",
    "evolver_ok",
    "rounds_used",
    "max_rounds",
    "duration_s",
    "total_tokens",
    "prompt_tokens",
    "completion_tokens",
    "out_dir",
    "error",
)


@dataclass(frozen=True)
class Aggregate:
    key: str
    runs: int
    passed: int
    pass_rate: float
    mean_score: float
    mean_duration_s: float
    mean_total_tokens: float | None


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


def outcomes_path(input_path: Path) -> Path:
    if input_path.is_dir():
        return input_path / "outcomes.jsonl"
    return input_path


def discover_matrix_dirs(runs_root: Path) -> list[Path]:
    if not runs_root.exists():
        return []
    return sorted(path for path in runs_root.glob("*_matrix") if path.is_dir())


def read_outcomes(inputs: Iterable[Path]) -> list[Outcome]:
    outcomes: list[Outcome] = []
    for input_path in inputs:
        path = outcomes_path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"No outcomes JSONL found at {path}")
        rows = load_jsonl(path)
        for row in rows:
            row.setdefault("source_path", str(path))
        outcomes.extend(rows)
    return outcomes


def dedupe_outcomes(outcomes: Iterable[Outcome]) -> list[Outcome]:
    by_key: dict[tuple[Any, ...], Outcome] = {}
    for index, row in enumerate(outcomes):
        key = (
            row.get("out_dir") or row.get("source_path"),
            row.get("task_visibility"),
            row.get("task_id"),
            row.get("model_label"),
            row.get("started_at"),
        )
        copy = dict(row)
        copy["_input_order"] = index
        by_key[key] = copy
    return sorted(by_key.values(), key=lambda row: int(row.get("_input_order", 0)))


def task_key(row: Outcome) -> str:
    visibility = row.get("task_visibility") or "unknown"
    task_id = row.get("task_id") or "unknown"
    return f"{visibility}/{task_id}"


def model_key(row: Outcome) -> str:
    return str(row.get("model_run_label") or row.get("model_label") or row.get("model"))


def score(row: Outcome) -> float:
    value = row.get("score")
    return float(value) if value is not None else 0.0


def bool_int(value: Any) -> int:
    return int(bool(value))


def token_total(row: Outcome) -> int | None:
    usage = row.get("token_usage") or {}
    value = usage.get("total_tokens")
    return int(value) if isinstance(value, int | float) else None


def aggregate_by(outcomes: list[Outcome], key_name: str) -> list[Aggregate]:
    buckets: dict[str, list[Outcome]] = defaultdict(list)
    for row in outcomes:
        key = task_key(row) if key_name == "task" else model_key(row)
        buckets[key].append(row)

    aggregates: list[Aggregate] = []
    for key, rows in buckets.items():
        runs = len(rows)
        passed = sum(bool_int(row.get("passed")) for row in rows)
        token_values = [token_total(row) for row in rows if token_total(row) is not None]
        aggregates.append(
            Aggregate(
                key=key,
                runs=runs,
                passed=passed,
                pass_rate=passed / runs if runs else 0.0,
                mean_score=sum(score(row) for row in rows) / runs if runs else 0.0,
                mean_duration_s=sum(float(row.get("duration_s") or 0.0) for row in rows) / runs
                if runs
                else 0.0,
                mean_total_tokens=(sum(token_values) / len(token_values) if token_values else None),
            )
        )

    return sorted(aggregates, key=lambda agg: (-agg.pass_rate, -agg.mean_score, agg.key))


def aggregate_task_model(outcomes: list[Outcome]) -> dict[str, dict[str, Aggregate]]:
    buckets: dict[str, dict[str, list[Outcome]]] = defaultdict(lambda: defaultdict(list))
    for row in outcomes:
        buckets[task_key(row)][model_key(row)].append(row)

    result: dict[str, dict[str, Aggregate]] = {}
    for task, model_rows in buckets.items():
        result[task] = {}
        for model, rows in model_rows.items():
            runs = len(rows)
            passed = sum(bool_int(row.get("passed")) for row in rows)
            token_values = [token_total(row) for row in rows if token_total(row) is not None]
            result[task][model] = Aggregate(
                key=model,
                runs=runs,
                passed=passed,
                pass_rate=passed / runs if runs else 0.0,
                mean_score=sum(score(row) for row in rows) / runs if runs else 0.0,
                mean_duration_s=sum(float(row.get("duration_s") or 0.0) for row in rows) / runs
                if runs
                else 0.0,
                mean_total_tokens=(sum(token_values) / len(token_values) if token_values else None),
            )
    return result


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[Outcome]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            clean = {key: value for key, value in row.items() if not key.startswith("_")}
            handle.write(json.dumps(clean, ensure_ascii=False) + "\n")


def csv_row(row: Outcome) -> dict[str, Any]:
    usage = row.get("token_usage") or {}
    return {
        "matrix_id": row.get("matrix_id"),
        "started_at": row.get("started_at"),
        "task_visibility": row.get("task_visibility"),
        "task_id": row.get("task_id"),
        "task_key": task_key(row),
        "model_label": row.get("model_label"),
        "model_run_label": row.get("model_run_label") or model_key(row),
        "baseline": row.get("baseline"),
        "model": row.get("model"),
        "reasoning_effort": row.get("reasoning_effort"),
        "score": row.get("score"),
        "passed": row.get("passed"),
        "submitted": row.get("submitted"),
        "static_ok": row.get("static_ok"),
        "dynamic_ok": row.get("dynamic_ok"),
        "evolver_ok": row.get("evolver_ok"),
        "rounds_used": row.get("rounds_used"),
        "max_rounds": row.get("max_rounds"),
        "duration_s": row.get("duration_s"),
        "total_tokens": usage.get("total_tokens"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "out_dir": row.get("out_dir"),
        "error": row.get("error"),
    }


def write_csv(path: Path, rows: list[Outcome]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(csv_row(row))


def aggregate_payload(aggregates: list[Aggregate]) -> list[dict[str, Any]]:
    return [
        {
            "key": agg.key,
            "runs": agg.runs,
            "passed": agg.passed,
            "pass_rate": agg.pass_rate,
            "mean_score": agg.mean_score,
            "mean_duration_s": agg.mean_duration_s,
            "mean_total_tokens": agg.mean_total_tokens,
        }
        for agg in aggregates
    ]


def svg_text(
    text: str,
    x: float,
    y: float,
    *,
    size: int = 12,
    anchor: str = "start",
    weight: str = "400",
    fill: str = "#18202a",
    rotate: float | None = None,
) -> str:
    transform = f' transform="rotate({rotate} {x:.2f} {y:.2f})"' if rotate is not None else ""
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" font-weight="{weight}" '
        f'text-anchor="{anchor}" fill="{fill}"{transform}>{html.escape(text)}</text>'
    )


def svg_doc(width: int, height: int, body: list[str]) -> str:
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<rect width="100%" height="100%" fill="#fbfcfd"/>',
            '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}</style>',
            *body,
            "</svg>",
            "",
        ]
    )


def metric_color(metric: str) -> str:
    return "#1b998b" if metric == "Pass rate" else "#4f6bed"


def write_bar_chart(path: Path, title: str, aggregates: list[Aggregate]) -> None:
    max_label_len = max((len(agg.key) for agg in aggregates), default=10)
    label_width = min(max(170, max_label_len * 7 + 32), 370)
    plot_width = 520
    top = 72
    row_h = 42
    bottom = 48
    width = label_width + plot_width + 110
    height = top + max(1, len(aggregates)) * row_h + bottom
    x0 = label_width
    body: list[str] = [
        svg_text(title, 24, 34, size=20, weight="700"),
        svg_text("Pass rate", x0, 58, size=12, fill=metric_color("Pass rate")),
        svg_text("Mean score", x0 + 82, 58, size=12, fill=metric_color("Mean score")),
    ]

    for tick in range(0, 101, 25):
        x = x0 + plot_width * tick / 100
        body.append(f'<line x1="{x:.2f}" y1="{top - 12}" x2="{x:.2f}" y2="{height - bottom + 6}" stroke="#e3e7eb"/>')
        body.append(svg_text(f"{tick}%", x, height - 20, size=11, anchor="middle", fill="#667085"))

    for index, agg in enumerate(aggregates):
        y = top + index * row_h
        body.append(svg_text(agg.key, 24, y + 24, size=12))
        pass_w = plot_width * agg.pass_rate
        score_w = plot_width * agg.mean_score
        body.append(f'<rect x="{x0}" y="{y + 6}" width="{pass_w:.2f}" height="13" rx="2" fill="{metric_color("Pass rate")}"/>')
        body.append(f'<rect x="{x0}" y="{y + 23}" width="{score_w:.2f}" height="13" rx="2" fill="{metric_color("Mean score")}"/>')
        body.append(
            svg_text(
                f"{agg.passed}/{agg.runs} pass, score {agg.mean_score:.2f}",
                x0 + plot_width + 14,
                y + 26,
                size=11,
                fill="#475467",
            )
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg_doc(width, height, body), encoding="utf-8")


def heat_color(value: float | None) -> str:
    if value is None:
        return "#eef1f4"
    value = max(0.0, min(1.0, value))
    red = int(222 - 160 * value)
    green = int(235 - 40 * (1 - value))
    blue = int(226 - 130 * value)
    return f"#{red:02x}{green:02x}{blue:02x}"


def write_heatmap(path: Path, title: str, matrix: dict[str, dict[str, Aggregate]]) -> None:
    tasks = sorted(matrix)
    models = sorted({model for model_rows in matrix.values() for model in model_rows})
    max_task_len = max((len(task) for task in tasks), default=10)
    left = min(max(220, max_task_len * 7 + 32), 380)
    top = 92
    cell_w = 118
    cell_h = 42
    width = left + max(1, len(models)) * cell_w + 36
    height = top + max(1, len(tasks)) * cell_h + 54
    body: list[str] = [
        svg_text(title, 24, 34, size=20, weight="700"),
        svg_text("Cell text is mean score; small text is pass count.", 24, 58, size=12, fill="#667085"),
    ]

    for col, model in enumerate(models):
        x = left + col * cell_w + cell_w / 2
        body.append(svg_text(model, x, top - 18, size=12, anchor="middle", weight="600"))

    for row, task in enumerate(tasks):
        y = top + row * cell_h
        body.append(svg_text(task, 24, y + 26, size=12))
        for col, model in enumerate(models):
            x = left + col * cell_w
            agg = matrix.get(task, {}).get(model)
            fill = heat_color(agg.mean_score if agg else None)
            body.append(f'<rect x="{x}" y="{y}" width="{cell_w - 4}" height="{cell_h - 4}" rx="3" fill="{fill}" stroke="#ffffff"/>')
            if agg:
                body.append(svg_text(f"{agg.mean_score:.2f}", x + cell_w / 2, y + 18, size=13, anchor="middle", weight="700"))
                body.append(svg_text(f"{agg.passed}/{agg.runs}", x + cell_w / 2, y + 33, size=10, anchor="middle", fill="#475467"))
            else:
                body.append(svg_text("n/a", x + cell_w / 2, y + 24, size=11, anchor="middle", fill="#98a2b3"))

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg_doc(width, height, body), encoding="utf-8")


def write_html_report(
    path: Path,
    *,
    outcomes: list[Outcome],
    model_svg: Path,
    task_svg: Path,
    heatmap_svg: Path,
    aggregates_path: Path,
    csv_path: Path,
    jsonl_path: Path,
) -> None:
    rel = lambda target: html.escape(target.name)
    content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Surface Evolver Eval Results</title>
  <style>
    body {{ margin: 28px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #18202a; }}
    h1 {{ font-size: 24px; margin: 0 0 8px; }}
    h2 {{ font-size: 18px; margin: 28px 0 10px; }}
    p {{ color: #475467; }}
    a {{ color: #275cad; }}
    img {{ display: block; max-width: 100%; border: 1px solid #e3e7eb; margin: 10px 0 22px; }}
    .links a {{ margin-right: 14px; }}
  </style>
</head>
<body>
  <h1>Surface Evolver Eval Results</h1>
  <p>{len(outcomes)} joined model/task outcomes.</p>
  <p class="links">
    <a href="{rel(csv_path)}">CSV</a>
    <a href="{rel(jsonl_path)}">JSONL</a>
    <a href="{rel(aggregates_path)}">Aggregates JSON</a>
  </p>
  <h2>By Model</h2>
  <img src="{rel(model_svg)}" alt="Results by model">
  <h2>By Task</h2>
  <img src="{rel(task_svg)}" alt="Results by task">
  <h2>Task By Model</h2>
  <img src="{rel(heatmap_svg)}" alt="Task/model heatmap">
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Join one or more matrix result directories and plot task/model outcomes."
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        help="Matrix directories or outcomes.jsonl files. Defaults to all runs/*_matrix directories.",
    )
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=Path("runs"),
        help="Root used for default discovery when no inputs are passed.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("runs/plots"))
    parser.add_argument(
        "--no-dedupe",
        action="store_true",
        help="Keep exact duplicate outcome rows. By default, duplicate rows for the same out_dir/task/model/start are collapsed.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inputs = args.inputs or discover_matrix_dirs(args.runs_root)
    if not inputs:
        raise SystemExit(f"No matrix directories found under {args.runs_root}")

    outcomes = read_outcomes(inputs)
    if not args.no_dedupe:
        outcomes = dedupe_outcomes(outcomes)
    if not outcomes:
        raise SystemExit("No outcome rows found.")

    output_dir = args.output_dir
    model_aggregates = aggregate_by(outcomes, "model")
    task_aggregates = aggregate_by(outcomes, "task")
    task_model = aggregate_task_model(outcomes)

    merged_jsonl = output_dir / "merged_outcomes.jsonl"
    merged_csv = output_dir / "merged_outcomes.csv"
    aggregates_json = output_dir / "aggregates.json"
    by_model_svg = output_dir / "by_model.svg"
    by_task_svg = output_dir / "by_task.svg"
    heatmap_svg = output_dir / "task_model_heatmap.svg"
    report_html = output_dir / "index.html"

    write_jsonl(merged_jsonl, outcomes)
    write_csv(merged_csv, outcomes)
    write_json(
        aggregates_json,
        {
            "runs": len(outcomes),
            "passed": sum(bool_int(row.get("passed")) for row in outcomes),
            "mean_score": sum(score(row) for row in outcomes) / len(outcomes),
            "by_model": aggregate_payload(model_aggregates),
            "by_task": aggregate_payload(task_aggregates),
            "inputs": [str(path) for path in inputs],
        },
    )
    write_bar_chart(by_model_svg, "Results By Model", model_aggregates)
    write_bar_chart(by_task_svg, "Results By Task", task_aggregates)
    write_heatmap(heatmap_svg, "Mean Score By Task And Model", task_model)
    write_html_report(
        report_html,
        outcomes=outcomes,
        model_svg=by_model_svg,
        task_svg=by_task_svg,
        heatmap_svg=heatmap_svg,
        aggregates_path=aggregates_json,
        csv_path=merged_csv,
        jsonl_path=merged_jsonl,
    )

    print(
        json.dumps(
            {
                "inputs": [str(path) for path in inputs],
                "runs": len(outcomes),
                "output_dir": str(output_dir),
                "report": str(report_html),
                "plots": [str(by_model_svg), str(by_task_svg), str(heatmap_svg)],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
