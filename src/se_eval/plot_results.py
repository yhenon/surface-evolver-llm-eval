from __future__ import annotations

import argparse
import base64
import csv
import html
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .models import Task


Outcome = dict[str, Any]


SUMMARY_FIELDS = (
    "matrix_id",
    "started_at",
    "task_visibility",
    "task_id",
    "task_public_label",
    "task_key",
    "model_label",
    "model_run_label",
    "baseline",
    "model",
    "reasoning_effort",
    "reasoning_label",
    "reasoning_source",
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
    "total_cost_usd",
    "prompt_cost_usd",
    "completion_cost_usd",
    "cost_rounds",
    "assistant_turns",
    "tool_calls_total",
    "doc_tool_calls",
    "evolver_tool_calls",
    "submit_tool_calls",
    "out_dir",
    "generation_path",
    "transcript_path",
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
    total_tokens: int | None
    mean_total_tokens: float | None
    total_cost_usd: float | None
    mean_total_cost_usd: float | None
    costed_runs: int
    provider: str | None = None


PROVIDER_COLORS = {
    "openai": "#111827",
    "minimax": "#e11d48",
    "deepseek": "#5b5ce2",
    "gemini": "#4285f4",
    "gemma": "#34a853",
    "claude": "#d97757",
    "kimi": "#7c3aed",
    "grok": "#1f2937",
    "arcee": "#16a34a",
    "qwen": "#f97316",
    "z-ai": "#0f766e",
    "mistral": "#ff7000",
    "poolside": "#0ea5e9",
}


PROVIDER_ALIASES = (
    ("deepseek", ("deepseek/", "deepseek")),
    ("gemini", ("google/gemini", "gemini")),
    ("gemma", ("google/gemma", "gemma")),
    ("claude", ("anthropic/", "claude", "anthropic")),
    ("kimi", ("moonshotai/", "kimi")),
    ("grok", ("x-ai/", "grok")),
    ("arcee", ("arcee-ai/", "arcee")),
    ("qwen", ("qwen/", "qwen")),
    ("z-ai", ("z-ai/", "glm")),
    ("minimax", ("minimax/", "minimax")),
    ("mistral", ("mistralai/", "mistral")),
    ("poolside", ("poolside/", "poolside")),
    ("openai", ("openai/", "gpt-", "gpt_", "o1", "o3", "o4")),
)


TOOL_ORDER = ("get_evolver_doc", "run_surface_evolver", "submit_fe_file", "other")
TOOL_LABELS = {
    "get_evolver_doc": "Docs",
    "run_surface_evolver": "Evolver",
    "submit_fe_file": "Submit",
    "other": "Other",
}
TOOL_COLORS = {
    "get_evolver_doc": "#4f7d3f",
    "run_surface_evolver": "#275cad",
    "submit_fe_file": "#d77a28",
    "other": "#98a2b3",
}


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


def discover_result_dirs(runs_root: Path) -> list[Path]:
    if not runs_root.exists():
        return []
    if (runs_root / "outcomes.jsonl").exists():
        return [runs_root]
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


TaskLabels = dict[tuple[str, str], str]


def load_task_labels(public_task_dir: Path, private_task_dir: Path) -> TaskLabels:
    labels: TaskLabels = {}
    for visibility, task_dir in (("public", public_task_dir), ("private", private_task_dir)):
        if not task_dir.exists():
            continue
        for path in sorted(task_dir.glob("*.json")):
            task = Task.model_validate_json(path.read_text(encoding="utf-8"))
            if task.public_label:
                labels[(visibility, task.id)] = task.public_label
    return labels


def task_key(row: Outcome, task_labels: TaskLabels | None = None) -> str:
    visibility = row.get("task_visibility") or "unknown"
    task_id = row.get("task_id") or "unknown"
    row_label = row.get("task_public_label") or row.get("public_label")
    if row_label:
        return f"{visibility}/{row_label}"
    if task_labels:
        label = task_labels.get((str(visibility), str(task_id)))
        if label:
            return f"{visibility}/{label}"
    return f"{visibility}/{task_id}"


def model_key(row: Outcome) -> str:
    model = str(row.get("model") or row.get("model_run_label") or row.get("model_label"))
    label = model.rsplit("/", 1)[-1]
    reasoning = reasoning_display(row)
    if reasoning:
        return f"{label} ({reasoning})"
    return label


def reasoning_display(row: Outcome) -> str | None:
    reasoning_effort = row.get("reasoning_effort")
    if reasoning_effort and reasoning_effort != "na":
        return str(reasoning_effort)

    reasoning_label = row.get("reasoning_label")
    if reasoning_label and reasoning_label not in {"default on", "provider default", "mandatory"}:
        return str(reasoning_label)
    return None


def provider_for_row(row: Outcome) -> str | None:
    haystack = " ".join(
        str(row.get(key) or "").lower()
        for key in ("model", "model_label", "model_run_label", "baseline")
    )
    for provider, aliases in PROVIDER_ALIASES:
        if any(alias in haystack for alias in aliases):
            return provider
    return None


def score(row: Outcome) -> float:
    value = row.get("score")
    return float(value) if value is not None else 0.0


def bool_int(value: Any) -> int:
    return int(bool(value))


def numeric_value(value: Any) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    return None


def token_total(row: Outcome) -> int | None:
    usage = row.get("token_usage") or {}
    totals = usage.get("totals") if isinstance(usage.get("totals"), dict) else None
    value = (totals or usage).get("total_tokens")
    return int(value) if isinstance(value, int | float) else None


def cost_total(row: Outcome) -> float | None:
    usage = row.get("cost_usage") or {}
    return numeric_value(usage.get("total_cost_usd"))


def generation_path_for_row(row: Outcome) -> Path | None:
    generation_path = row.get("generation_path")
    if generation_path:
        return Path(str(generation_path))
    out_dir = row.get("out_dir")
    if out_dir:
        return Path(str(out_dir)) / "generation.json"
    return None


def transcript_path_for_row(row: Outcome) -> Path | None:
    transcript_path = row.get("transcript_path")
    if transcript_path:
        return Path(str(transcript_path))
    out_dir = row.get("out_dir")
    if out_dir:
        return Path(str(out_dir)) / "transcript.json"
    return None


def cost_usage_from_generation(generation: Outcome) -> dict[str, Any] | None:
    token_usage = generation.get("token_usage") or {}
    per_round = token_usage.get("per_round") or []
    total_cost = 0.0
    prompt_cost = 0.0
    completion_cost = 0.0
    cost_rounds = 0

    for round_usage in per_round:
        usage = (round_usage or {}).get("usage") or {}
        cost = numeric_value(usage.get("cost"))
        if cost is None:
            continue
        cost_rounds += 1
        total_cost += cost
        details = usage.get("cost_details") or {}
        prompt_cost += numeric_value(details.get("upstream_inference_prompt_cost")) or 0.0
        completion_cost += numeric_value(details.get("upstream_inference_completions_cost")) or 0.0

    if cost_rounds == 0:
        return None

    return {
        "available": True,
        "total_cost_usd": total_cost,
        "prompt_cost_usd": prompt_cost,
        "completion_cost_usd": completion_cost,
        "rounds": cost_rounds,
    }


def interaction_usage_from_transcript(transcript: list[Outcome]) -> dict[str, Any]:
    assistant_turns = sum(1 for item in transcript if item.get("role") == "assistant")
    tool_counts: Counter[str] = Counter()
    for item in transcript:
        if item.get("role") != "tool":
            continue
        name = str(item.get("name") or "other")
        if name not in TOOL_ORDER:
            name = "other"
        tool_counts[name] += 1

    return {
        "available": True,
        "assistant_turns": assistant_turns,
        "tool_calls_total": sum(tool_counts.values()),
        "tool_calls": {name: tool_counts.get(name, 0) for name in TOOL_ORDER},
    }


def enrich_outcomes_with_generation(outcomes: Iterable[Outcome]) -> list[Outcome]:
    enriched: list[Outcome] = []
    generation_cache: dict[Path, Outcome | None] = {}
    transcript_cache: dict[Path, list[Outcome] | None] = {}

    for row in outcomes:
        copy = dict(row)
        path = generation_path_for_row(copy)
        if path is not None:
            generation = generation_cache.get(path)
            if path not in generation_cache:
                if path.exists():
                    generation = json.loads(path.read_text(encoding="utf-8"))
                else:
                    generation = None
                generation_cache[path] = generation

            if generation is not None:
                token_usage = generation.get("token_usage") or {}
                totals = token_usage.get("totals") if isinstance(token_usage.get("totals"), dict) else {}
                if totals:
                    merged_usage = dict(copy.get("token_usage") or {})
                    for key, value in totals.items():
                        merged_usage.setdefault(key, value)
                    copy["token_usage"] = merged_usage

                cost_usage = cost_usage_from_generation(generation)
                if cost_usage:
                    copy["cost_usage"] = cost_usage
                copy.setdefault("generation_path", str(path))
                if generation.get("transcript_path"):
                    copy.setdefault("transcript_path", generation.get("transcript_path"))

        transcript_path = transcript_path_for_row(copy)
        if transcript_path is not None:
            transcript = transcript_cache.get(transcript_path)
            if transcript_path not in transcript_cache:
                if transcript_path.exists():
                    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
                else:
                    transcript = None
                transcript_cache[transcript_path] = transcript
            if transcript is not None:
                copy["interaction_usage"] = interaction_usage_from_transcript(transcript)
                copy.setdefault("transcript_path", str(transcript_path))

        enriched.append(copy)

    return enriched


def aggregate_rows(key: str, rows: list[Outcome], provider: str | None = None) -> Aggregate:
    runs = len(rows)
    passed = sum(bool_int(row.get("passed")) for row in rows)
    token_values = [value for row in rows if (value := token_total(row)) is not None]
    cost_values = [value for row in rows if (value := cost_total(row)) is not None]
    return Aggregate(
        key=key,
        runs=runs,
        passed=passed,
        pass_rate=passed / runs if runs else 0.0,
        mean_score=sum(score(row) for row in rows) / runs if runs else 0.0,
        mean_duration_s=sum(float(row.get("duration_s") or 0.0) for row in rows) / runs
        if runs
        else 0.0,
        total_tokens=(sum(token_values) if token_values else None),
        mean_total_tokens=(sum(token_values) / len(token_values) if token_values else None),
        total_cost_usd=(sum(cost_values) if cost_values else None),
        mean_total_cost_usd=(sum(cost_values) / len(cost_values) if cost_values else None),
        costed_runs=len(cost_values),
        provider=provider,
    )


def aggregate_by(outcomes: list[Outcome], key_name: str, task_labels: TaskLabels) -> list[Aggregate]:
    buckets: dict[str, list[Outcome]] = defaultdict(list)
    for row in outcomes:
        key = task_key(row, task_labels) if key_name == "task" else model_key(row)
        buckets[key].append(row)

    aggregates: list[Aggregate] = []
    for key, rows in buckets.items():
        aggregates.append(
            aggregate_rows(
                key=key,
                rows=rows,
                provider=provider_for_row(rows[0]) if key_name == "model" else None,
            )
        )

    return sorted(aggregates, key=lambda agg: (-agg.pass_rate, -agg.mean_score, agg.key))


def aggregate_task_model(outcomes: list[Outcome], task_labels: TaskLabels) -> dict[str, dict[str, Aggregate]]:
    buckets: dict[str, dict[str, list[Outcome]]] = defaultdict(lambda: defaultdict(list))
    for row in outcomes:
        buckets[task_key(row, task_labels)][model_key(row)].append(row)

    result: dict[str, dict[str, Aggregate]] = {}
    for task, model_rows in buckets.items():
        result[task] = {}
        for model, rows in model_rows.items():
            result[task][model] = aggregate_rows(
                model,
                rows,
                provider=provider_for_row(rows[0]),
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


def csv_row(row: Outcome, task_labels: TaskLabels) -> dict[str, Any]:
    usage = row.get("token_usage") or {}
    cost_usage = row.get("cost_usage") or {}
    interaction_usage = row.get("interaction_usage") or {}
    tool_calls = interaction_usage.get("tool_calls") or {}
    return {
        "matrix_id": row.get("matrix_id"),
        "started_at": row.get("started_at"),
        "task_visibility": row.get("task_visibility"),
        "task_id": row.get("task_id"),
        "task_public_label": row.get("task_public_label"),
        "task_key": task_key(row, task_labels),
        "model_label": row.get("model_label"),
        "model_run_label": model_key(row),
        "baseline": row.get("baseline"),
        "model": row.get("model"),
        "reasoning_effort": row.get("reasoning_effort"),
        "reasoning_label": row.get("reasoning_label"),
        "reasoning_source": row.get("reasoning_source"),
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
        "total_cost_usd": cost_usage.get("total_cost_usd"),
        "prompt_cost_usd": cost_usage.get("prompt_cost_usd"),
        "completion_cost_usd": cost_usage.get("completion_cost_usd"),
        "cost_rounds": cost_usage.get("rounds"),
        "assistant_turns": interaction_usage.get("assistant_turns"),
        "tool_calls_total": interaction_usage.get("tool_calls_total"),
        "doc_tool_calls": tool_calls.get("get_evolver_doc"),
        "evolver_tool_calls": tool_calls.get("run_surface_evolver"),
        "submit_tool_calls": tool_calls.get("submit_fe_file"),
        "out_dir": row.get("out_dir"),
        "generation_path": row.get("generation_path"),
        "transcript_path": row.get("transcript_path"),
        "error": row.get("error"),
    }


def write_csv(path: Path, rows: list[Outcome], task_labels: TaskLabels) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(csv_row(row, task_labels))


def aggregate_payload(aggregates: list[Aggregate]) -> list[dict[str, Any]]:
    return [
        {
            "key": agg.key,
            "runs": agg.runs,
            "passed": agg.passed,
            "pass_rate": agg.pass_rate,
            "mean_score": agg.mean_score,
            "mean_duration_s": agg.mean_duration_s,
            "total_tokens": agg.total_tokens,
            "mean_total_tokens": agg.mean_total_tokens,
            "total_cost_usd": agg.total_cost_usd,
            "mean_total_cost_usd": agg.mean_total_cost_usd,
            "costed_runs": agg.costed_runs,
            "provider": agg.provider,
        }
        for agg in aggregates
    ]


def interaction_payload(outcomes: list[Outcome]) -> list[dict[str, Any]]:
    buckets: dict[str, list[Outcome]] = defaultdict(list)
    for row in outcomes:
        if row.get("interaction_usage"):
            buckets[model_key(row)].append(row)

    rows: list[dict[str, Any]] = []
    for model, model_rows in buckets.items():
        run_count = len(model_rows)
        tool_totals: Counter[str] = Counter()
        assistant_turns = 0
        passed = 0
        score_sum = 0.0
        for row in model_rows:
            usage = row.get("interaction_usage") or {}
            assistant_turns += int(usage.get("assistant_turns") or 0)
            tool_totals.update(usage.get("tool_calls") or {})
            passed += bool_int(row.get("passed"))
            score_sum += score(row)

        rows.append(
            {
                "key": model,
                "runs": run_count,
                "passed": passed,
                "pass_rate": passed / run_count if run_count else 0.0,
                "mean_score": score_sum / run_count if run_count else 0.0,
                "provider": provider_for_row(model_rows[0]),
                "mean_assistant_turns": assistant_turns / run_count if run_count else 0.0,
                "mean_tool_calls": sum(tool_totals.values()) / run_count if run_count else 0.0,
                "mean_tool_calls_by_name": {
                    name: tool_totals.get(name, 0) / run_count if run_count else 0.0
                    for name in TOOL_ORDER
                },
            }
        )

    return sorted(rows, key=lambda row: (-float(row["pass_rate"]), -float(row["mean_score"]), str(row["key"])))


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


def load_provider_icons(icon_dir: Path | None) -> dict[str, str]:
    if icon_dir is None or not icon_dir.exists():
        return {}

    icons: dict[str, str] = {}
    for path in sorted(icon_dir.glob("*.png")):
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        icons[path.stem.lower()] = f"data:image/png;base64,{data}"
    return icons


def lighten(hex_color: str, amount: float = 0.68) -> str:
    raw = hex_color.lstrip("#")
    red = int(raw[0:2], 16)
    green = int(raw[2:4], 16)
    blue = int(raw[4:6], 16)
    red = int(red + (255 - red) * amount)
    green = int(green + (255 - green) * amount)
    blue = int(blue + (255 - blue) * amount)
    return f"#{red:02x}{green:02x}{blue:02x}"


def provider_color(provider: str | None, fallback: str = "#475467") -> str:
    return PROVIDER_COLORS.get(provider or "", fallback)


def bar_colors(agg: Aggregate) -> tuple[str, str]:
    if agg.provider:
        base = provider_color(agg.provider)
        return base, lighten(base, 0.70)
    return "#1b998b", "#4f6bed"


def svg_icon(
    provider: str | None,
    icons: dict[str, str],
    x: float,
    y: float,
    size: float,
) -> str:
    color = provider_color(provider, "#98a2b3")
    uri = icons.get(provider or "")
    if not uri:
        return f'<circle cx="{x + size / 2:.2f}" cy="{y + size / 2:.2f}" r="{size / 2 - 1:.2f}" fill="{color}"/>'
    return (
        f'<image x="{x:.2f}" y="{y:.2f}" width="{size:.2f}" height="{size:.2f}" '
        f'href="{uri}" preserveAspectRatio="xMidYMid meet"/>'
    )


def format_tokens(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 10_000:
        return f"{value / 1_000:.0f}k"
    if value >= 1_000:
        return f"{value / 1_000:.1f}k"
    return f"{int(value)}"


def format_cost(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value >= 100:
        return f"${value:.0f}"
    if value >= 1:
        return f"${value:.2f}"
    if value >= 0.01:
        return f"${value:.3f}"
    return f"${value:.5f}"


def write_bar_chart(
    path: Path,
    title: str,
    aggregates: list[Aggregate],
    *,
    icons: dict[str, str],
    show_usage: bool = False,
) -> None:
    max_label_len = max((len(agg.key) for agg in aggregates), default=10)
    icon_gutter = 34 if any(agg.provider for agg in aggregates) else 0
    label_width = min(max(180, max_label_len * 7 + 42 + icon_gutter), 430)
    plot_width = 520
    value_width = 390 if show_usage else 220
    top = 72
    row_h = 56 if show_usage else 46
    bottom = 48
    width = label_width + plot_width + value_width
    height = top + max(1, len(aggregates)) * row_h + bottom
    x0 = label_width
    body: list[str] = [
        svg_text(title, 24, 34, size=20, weight="700"),
        svg_text("Pass rate", x0, 58, size=12, fill="#475467"),
        svg_text("Mean score", x0 + 82, 58, size=12, fill="#98a2b3"),
        svg_text("Outcome", x0 + plot_width + 18, 58, size=12, fill="#475467"),
    ]
    if show_usage:
        body.append(svg_text("Total tokens / recorded cost", x0 + plot_width + 170, 58, size=12, fill="#475467"))

    for tick in range(0, 101, 25):
        x = x0 + plot_width * tick / 100
        body.append(f'<line x1="{x:.2f}" y1="{top - 12}" x2="{x:.2f}" y2="{height - bottom + 6}" stroke="#e3e7eb"/>')
        body.append(svg_text(f"{tick}%", x, height - 20, size=11, anchor="middle", fill="#667085"))

    for index, agg in enumerate(aggregates):
        y = top + index * row_h
        label_x = 24
        if agg.provider:
            body.append(svg_icon(agg.provider, icons, label_x, y + 9, 24))
            label_x += 34
        body.append(svg_text(agg.key, label_x, y + 26, size=12, weight="600"))
        pass_w = plot_width * agg.pass_rate
        score_w = plot_width * agg.mean_score
        pass_color, score_color = bar_colors(agg)
        body.append(f'<rect x="{x0}" y="{y + 7}" width="{plot_width}" height="13" rx="2" fill="#eef1f4"/>')
        body.append(f'<rect x="{x0}" y="{y + 25}" width="{plot_width}" height="13" rx="2" fill="#eef1f4"/>')
        body.append(f'<rect x="{x0}" y="{y + 7}" width="{pass_w:.2f}" height="13" rx="2" fill="{pass_color}"/>')
        body.append(f'<rect x="{x0}" y="{y + 25}" width="{score_w:.2f}" height="13" rx="2" fill="{score_color}"/>')
        body.append(
            svg_text(
                f"{agg.passed}/{agg.runs} pass, score {agg.mean_score:.2f}",
                x0 + plot_width + 18,
                y + (21 if show_usage else 28),
                size=11,
                anchor="start",
                fill="#344054",
            )
        )
        if show_usage:
            body.append(
                svg_text(
                    f"{format_tokens(agg.total_tokens)} tok, {format_cost(agg.total_cost_usd)}",
                    x0 + plot_width + 170,
                    y + 21,
                    size=11,
                    anchor="start",
                    fill="#344054",
                )
            )
            body.append(
                svg_text(
                    f"avg {format_tokens(agg.mean_total_tokens)} tok/run, {format_cost(agg.mean_total_cost_usd)}/run",
                    x0 + plot_width + 170,
                    y + 39,
                    size=10,
                    anchor="start",
                    fill="#667085",
                )
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg_doc(width, height, body), encoding="utf-8")


def write_interaction_chart(
    path: Path,
    title: str,
    rows: list[dict[str, Any]],
    *,
    icons: dict[str, str],
) -> None:
    max_label_len = max((len(str(row["key"])) for row in rows), default=10)
    icon_gutter = 34 if any(row.get("provider") for row in rows) else 0
    label_width = min(max(210, max_label_len * 7 + 42 + icon_gutter), 430)
    plot_width = 540
    value_width = 250
    top = 98
    row_h = 48
    bottom = 54
    width = label_width + plot_width + value_width
    height = top + max(1, len(rows)) * row_h + bottom
    x0 = label_width
    max_calls = max((float(row.get("mean_tool_calls") or 0.0) for row in rows), default=1.0)
    if max_calls <= 0:
        max_calls = 1.0

    body: list[str] = [
        svg_text(title, 24, 34, size=20, weight="700"),
        svg_text("Average tool calls per run, stacked by tool. Text shows average assistant turns.", 24, 58, size=12, fill="#667085"),
    ]

    legend_x = x0
    for name in TOOL_ORDER:
        body.append(f'<rect x="{legend_x:.2f}" y="72" width="11" height="11" rx="2" fill="{TOOL_COLORS[name]}"/>')
        body.append(svg_text(TOOL_LABELS[name], legend_x + 16, 82, size=11, fill="#475467"))
        legend_x += 88

    for tick in axis_ticks(max_calls):
        x = x0 + plot_width * (tick / max_calls if max_calls else 0.0)
        body.append(f'<line x1="{x:.2f}" y1="{top - 12}" x2="{x:.2f}" y2="{height - bottom + 6}" stroke="#e3e7eb"/>')
        body.append(svg_text(f"{tick:.1f}", x, height - 22, size=11, anchor="middle", fill="#667085"))
    body.append(svg_text("Tool calls / run", x0 + plot_width / 2, height - 4, size=11, anchor="middle", fill="#667085"))

    for index, row in enumerate(rows):
        y = top + index * row_h
        label_x = 24
        provider = row.get("provider")
        if provider:
            body.append(svg_icon(str(provider), icons, label_x, y + 10, 24))
            label_x += 34
        body.append(svg_text(str(row["key"]), label_x, y + 28, size=12, weight="600"))

        body.append(f'<rect x="{x0}" y="{y + 13}" width="{plot_width}" height="18" rx="2" fill="#eef1f4"/>')
        cursor = x0
        by_name = row.get("mean_tool_calls_by_name") or {}
        for name in TOOL_ORDER:
            value = float(by_name.get(name) or 0.0)
            segment_w = plot_width * value / max_calls
            if segment_w <= 0:
                continue
            body.append(
                f'<rect x="{cursor:.2f}" y="{y + 13}" width="{segment_w:.2f}" '
                f'height="18" rx="2" fill="{TOOL_COLORS[name]}"/>'
            )
            cursor += segment_w

        body.append(
            svg_text(
                f"{float(row.get('mean_assistant_turns') or 0.0):.1f} turns, "
                f"{float(row.get('mean_tool_calls') or 0.0):.1f} tools/run",
                x0 + plot_width + 18,
                y + 27,
                size=11,
                fill="#344054",
            )
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg_doc(width, height, body), encoding="utf-8")


def axis_ticks(max_value: float, count: int = 5) -> list[float]:
    if max_value <= 0:
        return [0.0]
    return [max_value * index / (count - 1) for index in range(count)]


def write_performance_scatter(
    path: Path,
    title: str,
    aggregates: list[Aggregate],
    *,
    x_value: str,
    x_label: str,
    x_format: str,
    icons: dict[str, str],
    show_frontier: bool = False,
) -> None:
    points = [
        (agg, numeric_value(getattr(agg, x_value)))
        for agg in aggregates
        if numeric_value(getattr(agg, x_value)) is not None
    ]
    left = 88
    top = 74
    plot_width = 680
    plot_height = 420
    right = 210
    bottom = 72
    width = left + plot_width + right
    height = top + plot_height + bottom
    max_x = max((value for _, value in points if value is not None), default=1.0)
    x_tick_format = format_tokens if x_format == "tokens" else format_cost
    body: list[str] = [
        svg_text(title, 24, 34, size=20, weight="700"),
        svg_text("Each point is one model aggregate.", 24, 57, size=12, fill="#667085"),
    ]

    for tick in axis_ticks(max_x):
        x = left + plot_width * (tick / max_x if max_x else 0.0)
        body.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_height}" stroke="#e3e7eb"/>')
        body.append(svg_text(x_tick_format(tick), x, top + plot_height + 25, size=11, anchor="middle", fill="#667085"))
    for tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
        y = top + plot_height * (1 - tick)
        body.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" y2="{y:.2f}" stroke="#e3e7eb"/>')
        body.append(svg_text(f"{tick:.2f}", left - 14, y + 4, size=11, anchor="end", fill="#667085"))

    body.append(f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="#98a2b3"/>')
    body.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#98a2b3"/>')
    body.append(svg_text(x_label, left + plot_width / 2, height - 18, size=12, anchor="middle", fill="#475467"))
    body.append(svg_text("Mean score", 22, top + plot_height / 2, size=12, anchor="middle", fill="#475467", rotate=-90))

    if show_frontier:
        frontier: list[tuple[Aggregate, float]] = []
        best_score = -1.0
        for agg, value in sorted(points, key=lambda item: item[1] or 0.0):
            if value is None:
                continue
            if agg.mean_score > best_score:
                frontier.append((agg, value))
                best_score = agg.mean_score

        if len(frontier) >= 2:
            coords = [
                (
                    left + plot_width * (value / max_x if max_x else 0.0),
                    top + plot_height * (1 - agg.mean_score),
                )
                for agg, value in frontier
            ]
            step_coords = [coords[0]]
            for x, y in coords[1:]:
                step_coords.append((x, step_coords[-1][1]))
                step_coords.append((x, y))
            points_attr = " ".join(f"{x:.2f},{y:.2f}" for x, y in step_coords)
            body.append(
                f'<polyline points="{points_attr}" fill="none" stroke="#111827" '
                'stroke-width="2.5" stroke-linecap="square" stroke-linejoin="miter"/>'
            )
            for x, y in coords:
                body.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#111827"/>')
            label_x, label_y = coords[-1]
            body.append(svg_text("frontier", label_x + 10, label_y - 10, size=11, weight="600", fill="#111827"))

    for agg, value in sorted(points, key=lambda item: item[1] or 0.0):
        if value is None:
            continue
        x = left + plot_width * (value / max_x if max_x else 0.0)
        y = top + plot_height * (1 - agg.mean_score)
        color = provider_color(agg.provider, "#475467")
        body.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="13" fill="#ffffff" stroke="{color}" stroke-width="2"/>')
        body.append(svg_icon(agg.provider, icons, x - 10, y - 10, 20))
        label_anchor = "end" if x > left + plot_width - 150 else "start"
        label_x = x - 18 if label_anchor == "end" else x + 18
        body.append(svg_text(agg.key, label_x, y - 4, size=11, anchor=label_anchor, weight="600"))
        body.append(svg_text(f"{agg.passed}/{agg.runs} pass", label_x, y + 12, size=10, anchor=label_anchor, fill="#667085"))

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


def model_label_lines(model: str) -> list[str]:
    if model.endswith(")") and " (" in model:
        label, reasoning = model.rsplit(" (", 1)
        return [label, f"({reasoning}"]
    return [model]


def write_heatmap(
    path: Path,
    title: str,
    matrix: dict[str, dict[str, Aggregate]],
    *,
    icons: dict[str, str],
) -> None:
    tasks = sorted(matrix)
    models = sorted({model for model_rows in matrix.values() for model in model_rows})
    providers_by_model = {
        model: next(
            (
                model_rows[model].provider
                for model_rows in matrix.values()
                if model in model_rows
            ),
            None,
        )
        for model in models
    }
    model_labels = {model: model_label_lines(model) for model in models}
    max_task_len = max((len(task) for task in tasks), default=10)
    max_model_len = max((len(line) for lines in model_labels.values() for line in lines), default=10)
    left = min(max(220, max_task_len * 7 + 32), 380)
    top = 132
    cell_w = min(max(130, max_model_len * 7 + 22), 190)
    cell_h = 42
    width = left + max(1, len(models)) * cell_w + 36
    height = top + max(1, len(tasks)) * cell_h + 54
    body: list[str] = [
        svg_text(title, 24, 34, size=20, weight="700"),
        svg_text("Cell text is mean score; small text is pass count.", 24, 58, size=12, fill="#667085"),
    ]

    for col, model in enumerate(models):
        x = left + col * cell_w + cell_w / 2
        provider = providers_by_model.get(model)
        label_lines = model_labels[model]
        body.append(svg_icon(provider, icons, x - 12, top - 72, 24))
        label_y = top - 38 if len(label_lines) > 1 else top - 28
        for index, line in enumerate(label_lines):
            body.append(
                svg_text(
                    line,
                    x,
                    label_y + index * 14,
                    size=12 if index == 0 else 11,
                    anchor="middle",
                    weight="600" if index == 0 else "500",
                    fill="#18202a" if index == 0 else "#667085",
                )
            )
        body.append(
            f'<line x1="{left + col * cell_w + 8:.2f}" y1="{top - 14}" '
            f'x2="{left + (col + 1) * cell_w - 12:.2f}" y2="{top - 14}" '
            f'stroke="{provider_color(provider, "#d0d5dd")}" stroke-width="3"/>'
        )

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
    interaction_svg: Path,
    task_svg: Path,
    heatmap_svg: Path,
    score_tokens_svg: Path,
    score_cost_svg: Path,
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
  <h2>Tool Calls And Turns</h2>
  <img src="{rel(interaction_svg)}" alt="Stacked bar chart of average tool calls and assistant turns by model">
  <h2>Performance Vs Tokens</h2>
  <img src="{rel(score_tokens_svg)}" alt="Mean score versus total tokens">
  <h2>Performance Vs Cost</h2>
  <img src="{rel(score_cost_svg)}" alt="Mean score versus recorded cost">
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
        help="Run roots or outcomes.jsonl files. Defaults to runs/ when runs/outcomes.jsonl exists.",
    )
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=Path("runs"),
        help="Root used for default discovery when no inputs are passed.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("runs/plots"))
    parser.add_argument("--public-task-dir", type=Path, default=Path("tasks_public"))
    parser.add_argument("--private-task-dir", type=Path, default=Path("tasks_private"))
    parser.add_argument(
        "--icon-dir",
        type=Path,
        default=Path("icons"),
        help="Directory containing provider PNG icons. Defaults to ./icons.",
    )
    parser.add_argument("--no-icons", action="store_true", help="Do not embed provider icons in SVG charts.")
    parser.add_argument(
        "--no-dedupe",
        action="store_true",
        help="Keep exact duplicate outcome rows. By default, duplicate rows for the same out_dir/task/model/start are collapsed.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inputs = args.inputs or discover_result_dirs(args.runs_root)
    if not inputs:
        raise SystemExit(f"No outcome directories found under {args.runs_root}")

    outcomes = read_outcomes(inputs)
    if not args.no_dedupe:
        outcomes = dedupe_outcomes(outcomes)
    if not outcomes:
        raise SystemExit("No outcome rows found.")
    outcomes = enrich_outcomes_with_generation(outcomes)

    output_dir = args.output_dir
    task_labels = load_task_labels(args.public_task_dir, args.private_task_dir)
    model_aggregates = aggregate_by(outcomes, "model", task_labels)
    task_aggregates = aggregate_by(outcomes, "task", task_labels)
    task_model = aggregate_task_model(outcomes, task_labels)
    interactions = interaction_payload(outcomes)
    icons = load_provider_icons(None if args.no_icons else args.icon_dir)

    merged_jsonl = output_dir / "merged_outcomes.jsonl"
    merged_csv = output_dir / "merged_outcomes.csv"
    aggregates_json = output_dir / "aggregates.json"
    by_model_svg = output_dir / "by_model.svg"
    interactions_svg = output_dir / "model_tool_usage.svg"
    by_task_svg = output_dir / "by_task.svg"
    heatmap_svg = output_dir / "task_model_heatmap.svg"
    score_tokens_svg = output_dir / "score_vs_total_tokens.svg"
    score_cost_svg = output_dir / "score_vs_total_cost.svg"
    report_html = output_dir / "index.html"

    write_jsonl(merged_jsonl, outcomes)
    write_csv(merged_csv, outcomes, task_labels)
    write_json(
        aggregates_json,
        {
            "runs": len(outcomes),
            "passed": sum(bool_int(row.get("passed")) for row in outcomes),
            "mean_score": sum(score(row) for row in outcomes) / len(outcomes),
            "by_model": aggregate_payload(model_aggregates),
            "by_task": aggregate_payload(task_aggregates),
            "by_model_interactions": interactions,
            "inputs": [str(path) for path in inputs],
        },
    )
    write_bar_chart(by_model_svg, "Results By Model", model_aggregates, icons=icons, show_usage=True)
    write_interaction_chart(interactions_svg, "Tool Calls And Turns By Model", interactions, icons=icons)
    write_bar_chart(by_task_svg, "Results By Task", task_aggregates, icons=icons)
    write_heatmap(heatmap_svg, "Mean Score By Task And Model", task_model, icons=icons)
    write_performance_scatter(
        score_tokens_svg,
        "Mean Score Vs Total Tokens",
        model_aggregates,
        x_value="total_tokens",
        x_label="Total tokens across all runs",
        x_format="tokens",
        icons=icons,
    )
    write_performance_scatter(
        score_cost_svg,
        "Mean Score Vs Recorded Cost",
        model_aggregates,
        x_value="total_cost_usd",
        x_label="Recorded cost across all runs",
        x_format="cost",
        icons=icons,
        show_frontier=True,
    )
    write_html_report(
        report_html,
        outcomes=outcomes,
        model_svg=by_model_svg,
        interaction_svg=interactions_svg,
        task_svg=by_task_svg,
        heatmap_svg=heatmap_svg,
        score_tokens_svg=score_tokens_svg,
        score_cost_svg=score_cost_svg,
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
                "plots": [
                    str(by_model_svg),
                    str(interactions_svg),
                    str(by_task_svg),
                    str(heatmap_svg),
                    str(score_tokens_svg),
                    str(score_cost_svg),
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
