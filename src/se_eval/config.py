from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path("eval_config.json")
DEFAULT_BASELINE = "gpt-5.5"

DEFAULT_MODELS = (
    ("gpt-5.5", "openai/gpt-5.5"),
    ("gemini-3.5-flash", "google/gemini-3.5-flash"),
    ("gemini-3.1-pro-preview", "google/gemini-3.1-pro-preview"),
    ("deepseek-v4-pro", "deepseek/deepseek-v4-pro"),
    ("mistral-medium-3-5", "mistralai/mistral-medium-3-5"),
    ("trinity-large-thinking", "arcee-ai/trinity-large-thinking"),
    ("qwen3.6-35b-a3b", "qwen/qwen3.6-35b-a3b"),
    ("kimi-k2.7-code", "moonshotai/kimi-k2.7-code"),
    ("gemma-4-31b-it", "google/gemma-4-31b-it"),
    ("grok-build-0.1", "x-ai/grok-build-0.1"),
    ("claude-opus-4.8", "anthropic/claude-opus-4.8"),
    ("minimax-m3", "minimax/minimax-m3"),
)

DEPRECATED_MODEL_ALIASES = {
    "deepseek": "deepseek-v4-pro",
    "gemini-flash": "gemini-3.5-flash",
    "gemini-pro": "gemini-3.1-pro-preview",
    "mistral": "mistral-medium-3-5",
    "arcee": "trinity-large-thinking",
    "qwen": "qwen3.6-35b-a3b",
    "kimi": "kimi-k2.7-code",
    "gemma": "gemma-4-31b-it",
    "grok": "grok-build-0.1",
    "anthropic": "claude-opus-4.8",
    "claude": "claude-opus-4.8",
    "minimax": "minimax-m3",
}


@dataclass(frozen=True)
class ConfiguredModel:
    name: str
    model: str


def model_name_from_id(model: str) -> str:
    return model.rsplit("/", 1)[-1].replace(":", "_")


def _default_models() -> list[ConfiguredModel]:
    return [ConfiguredModel(name=name, model=model) for name, model in DEFAULT_MODELS]


def load_configured_models(config_path: Path = DEFAULT_CONFIG_PATH) -> list[ConfiguredModel]:
    if not config_path.exists():
        return _default_models()

    payload = json.loads(config_path.read_text(encoding="utf-8"))
    raw_models = payload.get("models") if isinstance(payload, dict) else None
    if not isinstance(raw_models, list):
        raise ValueError(f"{config_path} must contain a top-level 'models' list.")

    models: list[ConfiguredModel] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_models, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"{config_path}: models[{index}] must be an object.")
        name = _required_str(raw, "name", config_path, index)
        model = _required_str(raw, "model", config_path, index)
        if name in seen:
            raise ValueError(f"{config_path}: duplicate model name {name!r}.")
        seen.add(name)
        models.append(ConfiguredModel(name=name, model=model))

    if not models:
        raise ValueError(f"{config_path} must list at least one model.")
    return models


def _required_str(raw: dict[str, Any], key: str, config_path: Path, index: int) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{config_path}: models[{index}].{key} must be a non-empty string.")
    return value.strip()


def configured_model_map(config_path: Path = DEFAULT_CONFIG_PATH) -> dict[str, str]:
    return {model.name: model.model for model in load_configured_models(config_path)}


def resolve_model_name(name: str, models: dict[str, str]) -> str:
    if name in models:
        return name
    alias_target = DEPRECATED_MODEL_ALIASES.get(name)
    if alias_target in models:
        return alias_target
    valid = ", ".join(models)
    aliases = ", ".join(sorted(DEPRECATED_MODEL_ALIASES))
    raise ValueError(f"Unknown model name {name!r}. Configured names: {valid}. Deprecated aliases: {aliases}.")
