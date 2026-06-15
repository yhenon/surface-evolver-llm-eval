from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from openai import OpenAI

from .grader import grade_existing_submission
from .models import Task
from .tools import OPENAI_TOOLS, execute_tool


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_BASELINE = "gpt-5.5"
DEFAULT_TASK_VISIBILITY = "private"
TASK_VISIBILITY_DIRS = {
    "public": "tasks_public",
    "private": "tasks_private",
}
DEFAULT_TASKS = {
    "public": "two_bubbles_2d",
    "private": "cube_basic",
}
BASELINE_MODELS = {
    "gpt-5.5": "openai/gpt-5.5",
    "gemini-flash": "google/gemini-3.5-flash",
    "gemini-pro": "google/gemini-3.1-pro-preview",
    "deepseek": "deepseek/deepseek-v4-pro",
    "mistral": "mistralai/mistral-medium-3-5",
    "poolside": "poolside/laguna-m.1:free",
    "arcee": "arcee-ai/trinity-large-thinking",
    "qwen": "qwen/qwen3.6-35b-a3b",
    "kimi": "moonshotai/kimi-k2.7-code",
    "gemma": "google/gemma-4-31b-it",
    "grok": "x-ai/grok-build-0.1",
    "anthropic": "anthropic/claude-opus-4.8",
    "minimax": "minimax/minimax-m3"
}
REASONING_EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh")
RESPONSE_PREVIEW_CHARS = 4000

SYSTEM_PROMPT = """You are being evaluated on your ability to write valid Surface Evolver .fe files.

Rules:
- Use the documentation tool when you need Surface Evolver syntax, datafile, command, or element details.
- Use the available tool to validate your candidate file before submitting.
- The final answer must be made by calling submit_fe_file with complete .fe content.
- Do not submit Markdown fences. Submit raw file content only.
- Prefer simple, idiomatic Surface Evolver syntax.
- Do not put quit, q, or top-level evolution/print commands in the .fe file.
- If a task needs reusable Evolver commands, define them as gogo := { ... } in the .fe file, but do not call gogo there. Validation and grading scripts decide when to run it.
"""


def round_status_prompt(current_round: int, max_rounds: int) -> str:
    prompt = (
        f"Round status: current_round={current_round}, max_rounds={max_rounds}. "
        "Use the remaining rounds intentionally. If you have a valid candidate, "
        "submit it with submit_fe_file instead of continuing to reason."
    )
    if current_round == max_rounds:
        prompt += (
            " This is the final round: call submit_fe_file now with your best complete "
            ".fe file, even if it is not perfect."
        )
    return prompt


def now_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def model_slug(model: str) -> str:
    return model.replace("/", "_").replace(":", "_")


def make_openrouter_client() -> OpenAI:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is required to run evaluations through OpenRouter.")

    return OpenAI(
        api_key=api_key,
        base_url=os.environ.get("OPENROUTER_BASE_URL", OPENROUTER_BASE_URL),
        default_headers={
            "HTTP-Referer": os.environ.get("OPENROUTER_HTTP_REFERER", "https://github.com/local/se-llm-eval"),
            "X-Title": os.environ.get("OPENROUTER_APP_TITLE", "Surface Evolver LLM Eval"),
        },
    )


def reasoning_body(reasoning_effort: str | None) -> dict[str, Any]:
    if not reasoning_effort:
        return {}

    return {
        "reasoning": {
            "effort": reasoning_effort,
            "exclude": True,
        },
    }


def response_usage_dict(response: Any) -> dict[str, Any] | None:
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    if hasattr(usage, "model_dump"):
        return usage.model_dump(mode="json", exclude_none=True)
    if isinstance(usage, dict):
        return usage
    return None


def add_token_usage(totals: dict[str, int], usage: dict[str, Any], prefix: str = "") -> None:
    for key, value in usage.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, bool):
            continue
        if isinstance(value, int | float) and key.endswith("tokens"):
            totals[full_key] = totals.get(full_key, 0) + int(value)
        elif isinstance(value, dict):
            add_token_usage(totals=totals, usage=value, prefix=full_key)


class CompletionResponseError(RuntimeError):
    def __init__(self, message: str, diagnostic_path: Path) -> None:
        super().__init__(message)
        self.diagnostic_path = diagnostic_path


def text_preview(text: str, max_chars: int = RESPONSE_PREVIEW_CHARS) -> dict[str, Any]:
    if len(text) <= max_chars * 2:
        return {"truncated": False, "text": text}
    return {
        "truncated": True,
        "head": text[:max_chars],
        "tail": text[-max_chars:],
    }


def write_malformed_response_diagnostic(
    *,
    out_dir: Path,
    round_idx: int,
    raw_response: Any,
    exc: JSONDecodeError,
) -> Path:
    http_response = raw_response.http_response
    body = http_response.content
    body_text = body.decode(http_response.encoding or "utf-8", errors="replace")
    diagnostic = {
        "error": "Malformed JSON response from chat completion provider.",
        "exception": str(exc),
        "json_error": {
            "message": exc.msg,
            "line": exc.lineno,
            "column": exc.colno,
            "position": exc.pos,
        },
        "round": round_idx,
        "status_code": http_response.status_code,
        "reason_phrase": http_response.reason_phrase,
        "url": str(http_response.url),
        "headers": {
            "content-type": http_response.headers.get("content-type"),
            "content-length": http_response.headers.get("content-length"),
            "x-request-id": http_response.headers.get("x-request-id"),
            "cf-ray": http_response.headers.get("cf-ray"),
        },
        "body_bytes": len(body),
        "body_preview": text_preview(body_text),
    }
    path = out_dir / f"malformed_response_round_{round_idx}.json"
    path.write_text(json.dumps(diagnostic, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def create_chat_completion(
    *,
    client: OpenAI,
    out_dir: Path,
    round_idx: int,
    model: str,
    messages: list[dict[str, Any]],
    reasoning_effort: str | None,
) -> Any:
    raw_response = client.chat.completions.with_raw_response.create(
        model=model,
        messages=messages,
        tools=OPENAI_TOOLS,
        tool_choice="auto",
        parallel_tool_calls=False,
        extra_body=reasoning_body(reasoning_effort),
    )
    try:
        return raw_response.parse()
    except JSONDecodeError as exc:
        diagnostic_path = write_malformed_response_diagnostic(
            out_dir=out_dir,
            round_idx=round_idx,
            raw_response=raw_response,
            exc=exc,
        )
        raise CompletionResponseError(
            (
                "Provider returned malformed JSON for chat completion "
                f"round {round_idx}; wrote diagnostic to {diagnostic_path}."
            ),
            diagnostic_path=diagnostic_path,
        ) from exc


def generate_submission(
    task: Task,
    out_dir: Path,
    model: str,
    max_rounds: int = 8,
    reasoning_effort: str | None = None,
) -> dict[str, Any]:
    client = make_openrouter_client()
    out_dir.mkdir(parents=True, exist_ok=True)

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Task: {task.title}\n\n"
                f"{task.prompt}\n\n"
                f"Public validation command script you may use:\n"
                f"{task.public_command_script}\n"
                "A run_surface_evolver call uses this public script when its "
                "command_script argument is empty or omitted. "
                "This script is external to the .fe file. You may run it with "
                "run_surface_evolver, but do not paste its commands into the "
                "submitted datafile except for reusable command definitions such "
                "as gogo := { ... }."
            ),
        },
    ]

    transcript: list[dict[str, Any]] = []
    submitted_fe: str | None = None
    rounds_used = 0
    generation_error: str | None = None
    token_usage_totals: dict[str, int] = {}
    per_round_usage: list[dict[str, Any]] = []

    for round_idx in range(max_rounds):
        current_round = round_idx + 1
        round_status_message = {
            "role": "user",
            "content": round_status_prompt(current_round=current_round, max_rounds=max_rounds),
        }
        messages.append(round_status_message)

        print(f"Round {current_round}/{max_rounds}, sending request...")
        rounds_used = current_round
        try:
            response = create_chat_completion(
                client=client,
                out_dir=out_dir,
                round_idx=current_round,
                model=model,
                messages=messages,
                reasoning_effort=reasoning_effort,
            )
        except CompletionResponseError as exc:
            generation_error = str(exc)
            transcript.append({
                "role": "error",
                "round": current_round,
                "error": str(exc),
                "diagnostic_path": str(exc.diagnostic_path),
            })
            submitted_fe = None
            break

        usage = response_usage_dict(response)
        if usage is not None:
            add_token_usage(token_usage_totals, usage)
            per_round_usage.append({
                "round": current_round,
                "usage": usage,
            })

        msg = response.choices[0].message
        print(msg)
        msg_dict = msg.model_dump(mode="json", exclude_none=True)
        messages.append(msg_dict)
        transcript_msg = dict(msg_dict)
        transcript_msg["round"] = current_round
        if usage is not None:
            transcript_msg["usage"] = usage
        transcript.append(transcript_msg)

        tool_calls = msg.tool_calls or []
        if not tool_calls:
            # Nudge once if the model answered in prose instead of using submit_fe_file.
            messages.append({
                "role": "user",
                "content": "Please call submit_fe_file with the final raw .fe file content.",
            })
            continue

        for call in tool_calls:
            print(f"Executing tool call")
            result, maybe_submission = execute_tool(
                name=call.function.name,
                raw_arguments=call.function.arguments,
                task=task,
            )

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })
            transcript.append({
                "role": "tool",
                "round": current_round,
                "tool_call_id": call.id,
                "name": call.function.name,
                "result": result,
            })
            if maybe_submission is not None:
                submitted_fe = maybe_submission
                break

        if submitted_fe is not None:
            break

    if submitted_fe is not None:
        (out_dir / "submission.fe").write_text(submitted_fe, encoding="utf-8")

    (out_dir / "transcript.json").write_text(
        json.dumps(transcript, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    generation = {
        "task_id": task.id,
        "model": model,
        "out_dir": str(out_dir),
        "rounds_used": rounds_used,
        "max_rounds": max_rounds,
        "token_usage": {
            "available": bool(per_round_usage),
            "totals": token_usage_totals,
            "per_round": per_round_usage,
        },
        "submitted": submitted_fe is not None,
        "submission_path": str(out_dir / "submission.fe") if submitted_fe is not None else None,
        "transcript_path": str(out_dir / "transcript.json"),
        "generation_path": str(out_dir / "generation.json"),
        "error": (
            None
            if submitted_fe is not None
            else generation_error or f"No submit_fe_file call after {max_rounds} rounds."
        ),
    }
    (out_dir / "generation.json").write_text(
        json.dumps(generation, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return generation


def grade_stage(
    task: Task,
    input_path: Path,
    write_visual: bool = False,
    output_path: Path | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    return grade_existing_submission(
        input_path=input_path,
        task=task,
        output_path=output_path,
        write_result=write_result,
        write_visual=write_visual,
    )


def run_pipeline(
    task: Task,
    out_dir: Path,
    model: str,
    max_rounds: int = 8,
    reasoning_effort: str | None = None,
    write_visual: bool = False,
) -> dict[str, Any]:
    generation = generate_submission(
        task=task,
        out_dir=out_dir,
        model=model,
        max_rounds=max_rounds,
        reasoning_effort=reasoning_effort,
    )
    if not generation["submitted"]:
        grade = {
            "task_id": task.id,
            "score": 0.0,
            "passed": False,
            "error": generation["error"],
        }
        (out_dir / "result.json").write_text(
            json.dumps(grade, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    else:
        grade = grade_stage(task=task, input_path=out_dir, write_visual=write_visual)

    return {"generation": generation, "grade": grade}


def resolve_model(model: str | None, baseline: str) -> str:
    return model or BASELINE_MODELS[baseline]


def print_baselines() -> None:
    print(json.dumps(BASELINE_MODELS, indent=2))


def resolve_task_dir(task_dir: str | None, task_visibility: str) -> Path:
    if task_dir:
        return Path(task_dir)
    return Path(TASK_VISIBILITY_DIRS[task_visibility])


def resolve_task_id(task_id: str | None, task_visibility: str) -> str:
    return task_id or DEFAULT_TASKS[task_visibility]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        choices=("all", "generate", "grade"),
        default="all",
        help="Pipeline stage to run: all = generate then grade; generate = LLM only; grade = existing run/submission only.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Existing run directory or .fe path. Required with --stage grade.",
    )
    parser.add_argument("--task")
    parser.add_argument(
        "--task-visibility",
        choices=tuple(TASK_VISIBILITY_DIRS),
        default=os.environ.get("SE_EVAL_TASK_VISIBILITY", DEFAULT_TASK_VISIBILITY),
        help=(
            "Task set to load when --task-dir/SE_EVAL_TASK_DIR is not set. "
            "Defaults to private."
        ),
    )
    parser.add_argument(
        "--task-dir",
        default=os.environ.get("SE_EVAL_TASK_DIR"),
        help="Explicit task JSON directory. Overrides --task-visibility.",
    )
    parser.add_argument("--out-root", default="runs")
    parser.add_argument("--out-dir", type=Path, help="Output directory for generate/all.")
    parser.add_argument("--output", type=Path, help="Grade JSON output path for --stage grade.")
    parser.add_argument("--no-write", action="store_true", help="For --stage grade, print grade without writing result JSON.")
    parser.add_argument("--visual", action="store_true", help="Generate visual.svg and visual.off during grading.")
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENROUTER_MODEL") or os.environ.get("OPENAI_MODEL"),
        help="OpenRouter model id. Overrides --baseline.",
    )
    parser.add_argument(
        "--baseline",
        choices=BASELINE_MODELS,
        default=os.environ.get("OPENROUTER_BASELINE", DEFAULT_BASELINE),
        help="Named baseline model to run when --model is not set.",
    )
    parser.add_argument(
        "--all-baselines",
        action="store_true",
        help="Run every configured baseline for the selected task.",
    )
    parser.add_argument(
        "--reasoning-effort",
        choices=REASONING_EFFORTS,
        default=os.environ.get("OPENROUTER_REASONING_EFFORT"),
        help="Optional OpenRouter reasoning effort for models that support thinking tokens.",
    )
    parser.add_argument("--max-rounds", type=int, default=8)
    parser.add_argument("--list-baselines", action="store_true")
    args = parser.parse_args()

    if args.list_baselines:
        print_baselines()
        return

    if args.reasoning_effort and args.reasoning_effort not in REASONING_EFFORTS:
        raise SystemExit(f"--reasoning-effort must be one of: {', '.join(REASONING_EFFORTS)}")
    if args.baseline not in BASELINE_MODELS:
        raise SystemExit(f"--baseline must be one of: {', '.join(BASELINE_MODELS)}")
    if args.stage != "grade" and args.input is not None:
        raise SystemExit(
            "Positional input is only valid with --stage grade. "
            f"Unexpected input for --stage {args.stage}: {args.input}"
        )

    task = Task.load(
        resolve_task_id(args.task, args.task_visibility),
        resolve_task_dir(args.task_dir, args.task_visibility),
    )

    if args.stage == "grade":
        if args.input is None:
            raise SystemExit("--stage grade requires an input run directory or .fe path.")
        grade = grade_stage(
            task=task,
            input_path=args.input,
            write_visual=args.visual,
            output_path=args.output,
            write_result=not args.no_write,
        )
        print(json.dumps({"input": str(args.input), "grade": grade}, indent=2, ensure_ascii=False))
        return

    models = list(BASELINE_MODELS.values()) if args.all_baselines else [resolve_model(args.model, args.baseline)]

    results: list[dict[str, Any]] = []
    for model in models:
        out_dir = output_dir(args=args, task=task, model=model, multi_model=len(models) > 1)
        if args.stage == "generate":
            result = generate_submission(
                task=task,
                out_dir=out_dir,
                model=model,
                max_rounds=args.max_rounds,
                reasoning_effort=args.reasoning_effort,
            )
        else:
            result = run_pipeline(
                task=task,
                out_dir=out_dir,
                model=model,
                max_rounds=args.max_rounds,
                reasoning_effort=args.reasoning_effort,
                write_visual=args.visual,
            )
            result = {"model": model, "out_dir": str(out_dir), **result}
        results.append(result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()

    if len(results) > 1:
        print("Summary:")
        print(json.dumps(results, indent=2, ensure_ascii=False))


def output_dir(args: argparse.Namespace, task: Task, model: str, multi_model: bool) -> Path:
    if args.out_dir and not multi_model:
        return args.out_dir

    suffix = f"_{model_slug(model)}"
    if args.reasoning_effort:
        suffix += f"_reasoning-{args.reasoning_effort}"
    return Path(args.out_root) / f"{now_slug()}_{task.id}{suffix}"


if __name__ == "__main__":
    main()
