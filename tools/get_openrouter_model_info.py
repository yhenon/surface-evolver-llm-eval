from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


OPENROUTER_API_BASE = "https://openrouter.ai"
OPENROUTER_MODELS_URL = f"{OPENROUTER_API_BASE}/api/v1/models"


def fetch_json(url: str, label: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "surface-evolver-llm-eval/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.URLError as exc:
        raise SystemExit(f"failed to fetch OpenRouter {label}: {exc}") from exc


def fetch_models() -> list[dict[str, Any]]:
    payload = fetch_json(OPENROUTER_MODELS_URL, "models")

    models = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(models, list):
        raise SystemExit("OpenRouter response did not contain a models data list.")
    return [model for model in models if isinstance(model, dict)]


def endpoint_details_url(model: dict[str, Any], model_id: str) -> str:
    links = model.get("links")
    details = links.get("details") if isinstance(links, dict) else None
    if isinstance(details, str) and details:
        return urllib.parse.urljoin(OPENROUTER_API_BASE, details)

    quoted_model = urllib.parse.quote(model_id, safe="/:")
    return f"{OPENROUTER_MODELS_URL}/{quoted_model}/endpoints"


def fetch_endpoints(model: dict[str, Any], model_id: str) -> list[dict[str, Any]]:
    payload = fetch_json(endpoint_details_url(model, model_id), f"endpoints for {model_id}")
    data = payload.get("data") if isinstance(payload, dict) else None
    endpoints = data.get("endpoints") if isinstance(data, dict) else None
    if not isinstance(endpoints, list):
        raise SystemExit(f"OpenRouter response did not contain an endpoints list for {model_id}.")
    return [endpoint for endpoint in endpoints if isinstance(endpoint, dict)]


def provider_summary(endpoint: dict[str, Any]) -> dict[str, Any]:
    pricing = endpoint.get("pricing")
    supported_parameters = endpoint.get("supported_parameters") or []
    if not isinstance(pricing, dict):
        pricing = {}
    if not isinstance(supported_parameters, list):
        supported_parameters = []

    return {
        "name": endpoint.get("provider_name"),
        "tag": endpoint.get("tag"),
        "status": endpoint.get("status"),
        "quantization": endpoint.get("quantization"),
        "context_length": endpoint.get("context_length"),
        "max_completion_tokens": endpoint.get("max_completion_tokens"),
        "pricing": pricing,
        "supported_parameters": supported_parameters,
    }


def reasoning_summary(model: dict[str, Any], endpoints: list[dict[str, Any]]) -> dict[str, Any]:
    reasoning = model.get("reasoning")
    supported_parameters = model.get("supported_parameters") or []
    if not isinstance(reasoning, dict):
        reasoning = {}
    if not isinstance(supported_parameters, list):
        supported_parameters = []

    supported_efforts = reasoning.get("supported_efforts")
    if not isinstance(supported_efforts, list):
        supported_efforts = None

    default_effort = reasoning.get("default_effort")
    default_enabled = reasoning.get("default_enabled")
    mandatory = reasoning.get("mandatory")
    supports_reasoning = bool(reasoning) or "reasoning" in supported_parameters or "include_reasoning" in supported_parameters

    if isinstance(default_effort, str):
        default = default_effort
        config_value = default_effort
    elif default_enabled is False:
        default = "none"
        config_value = "none"
    elif default_enabled is True:
        default = "enabled"
        config_value = None
    elif mandatory is True:
        default = "mandatory"
        config_value = None
    elif supports_reasoning:
        default = "unspecified"
        config_value = None
    else:
        default = "none"
        config_value = "none"

    return {
        "id": model.get("id"),
        "name": model.get("name"),
        "supports_reasoning": supports_reasoning,
        "default": default,
        "config_reasoning_effort": config_value,
        "supported_efforts": supported_efforts,
        "default_effort": default_effort,
        "default_enabled": default_enabled,
        "mandatory": mandatory,
        "supported_parameters": supported_parameters,
        "providers": [provider_summary(endpoint) for endpoint in endpoints],
    }


def find_model(models: list[dict[str, Any]], model_id: str) -> dict[str, Any] | None:
    for model in models:
        if model.get("id") == model_id:
            return model
    return None


def close_matches(models: list[dict[str, Any]], model_id: str, limit: int = 8) -> list[str]:
    needle = model_id.lower()
    matches = [
        str(model.get("id"))
        for model in models
        if needle in str(model.get("id") or "").lower()
    ]
    return matches[:limit]


def print_text(summary: dict[str, Any]) -> None:
    print(f"{summary['id']}: {summary.get('name') or 'unknown name'}")
    print(f"  supports reasoning: {yes_no(summary['supports_reasoning'])}")
    print(f"  default: {summary['default']}")
    if summary.get("supported_efforts"):
        print(f"  available efforts: {', '.join(summary['supported_efforts'])}")
    else:
        print("  available efforts: n/a")
    config_value = summary.get("config_reasoning_effort")
    if config_value is not None:
        print(f"  suggested eval_config reasoning_effort: {config_value}")
    else:
        print("  suggested eval_config reasoning_effort: n/a")

    providers = summary.get("providers") or []
    if providers:
        provider_labels = [
            provider_label(provider)
            for provider in providers
            if isinstance(provider, dict)
        ]
        print(f"  available providers: {', '.join(provider_labels)}")
        print("  provider order values:")
        for provider in providers:
            if not isinstance(provider, dict):
                continue
            tag = provider.get("tag")
            if not tag:
                continue
            print(f"    - {tag}{provider_details(provider)}")
    else:
        print("  available providers: n/a")


def provider_label(provider: dict[str, Any]) -> str:
    name = provider.get("name") or "unknown provider"
    tag = provider.get("tag")
    if tag:
        return f"{name} ({tag})"
    return str(name)


def provider_details(provider: dict[str, Any]) -> str:
    details: list[str] = []
    status = provider.get("status")
    quantization = provider.get("quantization")
    context_length = provider.get("context_length")
    max_completion_tokens = provider.get("max_completion_tokens")

    if status is not None:
        details.append(f"status={status}")
    if quantization:
        details.append(f"quantization={quantization}")
    if context_length is not None:
        details.append(f"context={context_length}")
    if max_completion_tokens is not None:
        details.append(f"max_completion={max_completion_tokens}")

    if details:
        return f" ({', '.join(details)})"
    return ""


def yes_no(value: Any) -> str:
    return "yes" if value else "no"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show OpenRouter reasoning defaults, available efforts, and providers for model ids."
    )
    parser.add_argument("models", nargs="+", help="OpenRouter model id, e.g. poolside/laguna-m.1")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--no-providers",
        action="store_true",
        help="Do not fetch per-model endpoint/provider details.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    models = fetch_models()

    summaries: list[dict[str, Any]] = []
    missing: dict[str, list[str]] = {}
    for model_id in args.models:
        model = find_model(models, model_id)
        if model is None:
            missing[model_id] = close_matches(models, model_id)
            continue
        endpoints = [] if args.no_providers else fetch_endpoints(model, model_id)
        summaries.append(reasoning_summary(model, endpoints))

    if args.json:
        print(json.dumps({"models": summaries, "missing": missing}, indent=2, sort_keys=True))
    else:
        for index, summary in enumerate(summaries):
            if index:
                print()
            print_text(summary)
        for model_id, matches in missing.items():
            print(f"\n{model_id}: not found", file=sys.stderr)
            if matches:
                print(f"  close matches: {', '.join(matches)}", file=sys.stderr)

    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
