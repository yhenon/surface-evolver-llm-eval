from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from openai import OpenAI

from .grader import grade_existing_submission
from .config import (
    DEFAULT_BASELINE,
    REASONING_EFFORTS,
    ConfiguredModel,
    configured_model_spec_map,
    default_provider_routing,
    model_name_from_id,
    resolve_model_name,
)
from .models import Task
from .tools import OPENAI_TOOLS, execute_tool


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_TASK_VISIBILITY = "private"
TASK_VISIBILITY_DIRS = {
    "public": "tasks_public",
    "private": "tasks_private",
}
DEFAULT_TASKS = {
    "public": "two_bubbles_2d",
    "private": "cube",
}
BASELINE_MODELS = configured_model_spec_map()
RESPONSE_PREVIEW_CHARS = 4000
RUN_ERROR_FILE = "run_error.json"
CHAT_COMPLETION_ATTEMPTS = 3
CHAT_COMPLETION_RETRY_DELAY_SECONDS = 2.0

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


def make_openrouter_client() -> OpenAI:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is required to run evaluations through OpenRouter.")

    return OpenAI(
        api_key=api_key,
        base_url=os.environ.get("OPENROUTER_BASE_URL", OPENROUTER_BASE_URL),
        default_headers={
            "HTTP-Referer": os.environ.get("OPENROUTER_HTTP_REFERER", "https://github.com/local/se-llm-eval"),
            "X-Title": os.environ.get("OPENROUTER_APP_TITLE", "Surface Evolver Bench"),
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


def extra_request_body(
    *,
    reasoning_effort: str | None,
    provider: dict[str, Any] | None,
) -> dict[str, Any]:
    body = reasoning_body(reasoning_effort)
    if provider:
        body["provider"] = json.loads(json.dumps(provider))
    return body


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


def _safe_json_value(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, list):
        return [_safe_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _safe_json_value(item) for key, item in value.items()}
    return str(value)


def classify_run_error(error: str, exc: BaseException | None = None) -> str:
    status_code = getattr(exc, "status_code", None)
    lowered = error.lower()
    exc_name = type(exc).__name__.lower() if exc is not None else ""

    if isinstance(exc, CompletionResponseError) or "malformed json" in lowered:
        return "malformed_provider_response"
    if "no submit_fe_file call" in lowered:
        return "no_submission"
    if status_code in {401, 403} or "unauthorized" in lowered or "api key" in lowered:
        return "auth"
    if status_code == 429 or "rate limit" in lowered or "too many requests" in lowered:
        if any(term in lowered for term in ("credit", "quota", "insufficient", "balance", "payment")):
            return "quota_or_credit"
        return "rate_limit"
    if any(term in lowered for term in ("credit", "quota", "insufficient", "balance", "payment")):
        return "quota_or_credit"
    if any(term in lowered for term in ("timeout", "timed out")) or "timeout" in exc_name:
        return "timeout"
    if any(term in lowered for term in ("connection", "connect", "network", "dns", "temporary failure")):
        return "connectivity"
    if status_code is not None or "api" in exc_name or "openai" in exc_name:
        return "provider_api"
    if "surface evolver" in lowered or "evolver" in lowered:
        return "grader_or_evolver"
    return "unknown"


def exception_metadata(exc: BaseException) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "type": type(exc).__name__,
        "message": str(exc),
    }
    for attr in ("status_code", "code", "type", "param"):
        value = getattr(exc, attr, None)
        if value is not None:
            metadata[attr] = _safe_json_value(value)
    response = getattr(exc, "response", None)
    if response is not None:
        metadata["response"] = {
            "status_code": _safe_json_value(getattr(response, "status_code", None)),
            "headers": _safe_json_value(dict(getattr(response, "headers", {}) or {})),
            "url": _safe_json_value(getattr(response, "url", None)),
        }
    body = getattr(exc, "body", None)
    if body is not None:
        metadata["body"] = _safe_json_value(body)
    diagnostic_path = getattr(exc, "diagnostic_path", None)
    if diagnostic_path is not None:
        metadata["diagnostic_path"] = str(diagnostic_path)
    return metadata


def write_run_error(
    *,
    out_dir: Path,
    stage: str,
    error: str,
    exc: BaseException | None = None,
    context: dict[str, Any] | None = None,
) -> Path:
    payload: dict[str, Any] = {
        "recorded_at": now_slug(),
        "stage": stage,
        "category": classify_run_error(error, exc),
        "error": error,
        "context": _safe_json_value(context or {}),
    }
    if exc is not None:
        payload["exception"] = exception_metadata(exc)
        payload["traceback"] = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    path = out_dir / RUN_ERROR_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


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
    attempt: int | None = None,
    max_attempts: int | None = None,
    retryable: bool = False,
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
        "attempt": attempt,
        "max_attempts": max_attempts,
        "retryable": retryable,
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
    attempt_suffix = f"_attempt_{attempt}" if attempt is not None else ""
    path = out_dir / f"malformed_response_round_{round_idx}{attempt_suffix}.json"
    path.write_text(json.dumps(diagnostic, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def response_body_is_blank(raw_response: Any) -> bool:
    return not raw_response.http_response.content.strip()


def create_chat_completion(
    *,
    client: OpenAI,
    out_dir: Path,
    round_idx: int,
    model: str,
    messages: list[dict[str, Any]],
    reasoning_effort: str | None,
    provider: dict[str, Any] | None,
) -> Any:
    for attempt in range(1, CHAT_COMPLETION_ATTEMPTS + 1):
        raw_response = client.chat.completions.with_raw_response.create(
            model=model,
            messages=messages,
            tools=OPENAI_TOOLS,
            tool_choice="auto",
            parallel_tool_calls=False,
            extra_body=extra_request_body(reasoning_effort=reasoning_effort, provider=provider),
        )
        try:
            return raw_response.parse()
        except JSONDecodeError as exc:
            retryable = response_body_is_blank(raw_response)
            if retryable and attempt < CHAT_COMPLETION_ATTEMPTS:
                diagnostic_path = write_malformed_response_diagnostic(
                    out_dir=out_dir,
                    round_idx=round_idx,
                    raw_response=raw_response,
                    exc=exc,
                    attempt=attempt,
                    max_attempts=CHAT_COMPLETION_ATTEMPTS,
                    retryable=True,
                )
                print(
                    "Provider returned blank malformed JSON for chat completion "
                    f"round {round_idx}, attempt {attempt}/{CHAT_COMPLETION_ATTEMPTS}; "
                    f"wrote diagnostic to {diagnostic_path} and retrying..."
                )
                time.sleep(CHAT_COMPLETION_RETRY_DELAY_SECONDS * attempt)
                continue

            diagnostic_path = write_malformed_response_diagnostic(
                out_dir=out_dir,
                round_idx=round_idx,
                raw_response=raw_response,
                exc=exc,
                attempt=attempt,
                max_attempts=CHAT_COMPLETION_ATTEMPTS,
                retryable=retryable,
            )
            raise CompletionResponseError(
                (
                    "Provider returned malformed JSON for chat completion "
                    f"round {round_idx}; wrote diagnostic to {diagnostic_path}."
                ),
                diagnostic_path=diagnostic_path,
            ) from exc

    raise AssertionError("unreachable chat completion retry state")


def generate_submission(
    task: Task,
    out_dir: Path,
    model: str,
    max_rounds: int = 8,
    reasoning_effort: str | None = None,
    provider: dict[str, Any] | None = None,
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
    generation_exception: BaseException | None = None
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
                provider=provider,
            )
        except CompletionResponseError as exc:
            generation_error = str(exc)
            generation_exception = exc
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
        "reasoning_effort": reasoning_effort,
        "provider": provider,
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
    if generation["error"]:
        generation["error_path"] = str(
            write_run_error(
                out_dir=out_dir,
                stage="generate",
                error=str(generation["error"]),
                exc=generation_exception,
                context={
                    "task_id": task.id,
                    "model": model,
                    "provider": provider,
                    "out_dir": str(out_dir),
                    "rounds_used": rounds_used,
                    "max_rounds": max_rounds,
                    "reasoning_effort": reasoning_effort,
                },
            )
        )
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
    provider: dict[str, Any] | None = None,
    write_visual: bool = False,
) -> dict[str, Any]:
    try:
        generation = generate_submission(
            task=task,
            out_dir=out_dir,
            model=model,
            max_rounds=max_rounds,
            reasoning_effort=reasoning_effort,
            provider=provider,
        )
    except Exception as exc:
        write_run_error(
            out_dir=out_dir,
            stage="generate",
            error=f"{type(exc).__name__}: {exc}",
            exc=exc,
            context={
                "task_id": task.id,
                "model": model,
                "provider": provider,
                "out_dir": str(out_dir),
                "max_rounds": max_rounds,
                "reasoning_effort": reasoning_effort,
            },
        )
        raise
    if not generation["submitted"]:
        grade = {
            "task_id": task.id,
            "score": 0.0,
            "passed": False,
            "error": generation["error"],
            "error_path": generation.get("error_path"),
        }
        (out_dir / "result.json").write_text(
            json.dumps(grade, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    else:
        try:
            grade = grade_stage(task=task, input_path=out_dir, write_visual=write_visual)
        except Exception as exc:
            write_run_error(
                out_dir=out_dir,
                stage="grade",
                error=f"{type(exc).__name__}: {exc}",
                exc=exc,
                context={
                    "task_id": task.id,
                    "model": model,
                    "provider": provider,
                    "out_dir": str(out_dir),
                    "reasoning_effort": reasoning_effort,
                },
            )
            raise

    return {"generation": generation, "grade": grade}


def resolve_model(model: str | None, baseline: str) -> str:
    return model or BASELINE_MODELS[baseline].model


def resolve_reasoning_effort(
    *,
    cli_effort: str | None,
    model_spec: ConfiguredModel | None,
) -> str | None:
    return cli_effort if cli_effort is not None else (model_spec.reasoning_effort if model_spec else None)


def normalize_baseline_arg(raw_name: str) -> str:
    name = resolve_model_name(raw_name, BASELINE_MODELS)
    if name != raw_name:
        print(
            f"warning: --baseline {raw_name!r} is deprecated; use {name!r}.",
            file=sys.stderr,
        )
    return name


def print_baselines() -> None:
    payload = {
        name: {
            "model": spec.model,
            "reasoning_effort": spec.reasoning_effort,
            "provider": spec.provider,
        }
        for name, spec in BASELINE_MODELS.items()
    }
    print(json.dumps(payload, indent=2))


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
        default=os.environ.get("OPENROUTER_BASELINE", DEFAULT_BASELINE),
        help="Configured model name to run when --model is not set.",
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
    try:
        args.baseline = normalize_baseline_arg(args.baseline)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
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

    selected_models = (
        [
            (
                name,
                spec.model,
                resolve_reasoning_effort(cli_effort=args.reasoning_effort, model_spec=spec),
                spec.provider,
            )
            for name, spec in BASELINE_MODELS.items()
        ]
        if args.all_baselines
        else [
            (
                model_name_from_id(args.model),
                args.model,
                args.reasoning_effort,
                default_provider_routing(args.model),
            )
        ]
        if args.model
        else [
            (
                args.baseline,
                resolve_model(None, args.baseline),
                resolve_reasoning_effort(cli_effort=args.reasoning_effort, model_spec=BASELINE_MODELS[args.baseline]),
                BASELINE_MODELS[args.baseline].provider,
            )
        ]
    )

    results: list[dict[str, Any]] = []
    for model_label, model, reasoning_effort, provider in selected_models:
        out_dir = output_dir(
            args=args,
            task=task,
            model_label=model_label,
            reasoning_effort=reasoning_effort,
            multi_model=len(selected_models) > 1,
        )
        if args.stage == "generate":
            result = generate_submission(
                task=task,
                out_dir=out_dir,
                model=model,
                max_rounds=args.max_rounds,
                reasoning_effort=reasoning_effort,
                provider=provider,
            )
        else:
            result = run_pipeline(
                task=task,
                out_dir=out_dir,
                model=model,
                max_rounds=args.max_rounds,
                reasoning_effort=reasoning_effort,
                provider=provider,
                write_visual=args.visual,
            )
            result = {"model": model, "out_dir": str(out_dir), **result}
        results.append(result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()

    if len(results) > 1:
        print("Summary:")
        print(json.dumps(results, indent=2, ensure_ascii=False))


def output_dir(
    args: argparse.Namespace,
    task: Task,
    model_label: str,
    reasoning_effort: str | None,
    multi_model: bool,
) -> Path:
    if args.out_dir and not multi_model:
        return args.out_dir

    label = model_label
    if args.reasoning_effort:
        label += f"_reasoning-{reasoning_effort or 'na'}"
    return Path(args.out_root) / label / f"{args.task_visibility}_{task.id}"


if __name__ == "__main__":
    main()
