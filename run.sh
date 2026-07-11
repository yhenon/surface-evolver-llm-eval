#!/usr/bin/env bash
set -euo pipefail

API_PROVIDER="${SE_EVAL_API_PROVIDER:-}"
if [ -z "$API_PROVIDER" ]; then
  if [ -n "${OPENAI_API_KEY:-}" ] || [ -f .openai_key ]; then
    API_PROVIDER="openai"
  else
    API_PROVIDER="openrouter"
  fi
fi

KEY_ENV="OPENROUTER_API_KEY"
KEY_FILE=".openrouter_key"
if [ "$API_PROVIDER" = "openai" ]; then
  KEY_ENV="OPENAI_API_KEY"
  KEY_FILE=".openai_key"
fi

if [ -z "${!KEY_ENV:-}" ] && [ -f "$KEY_FILE" ]; then
  export "$KEY_ENV=$(tr -d '[:space:]' < "$KEY_FILE")"
fi

if [ -z "${!KEY_ENV:-}" ]; then
  echo "$KEY_ENV is not set and $KEY_FILE was not found." >&2
  exit 1
fi

docker build -t se-llm-eval .

docker run --rm \
  -e SE_EVAL_API_PROVIDER="$API_PROVIDER" \
  -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-}" \
  -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
  -e OPENROUTER_BASELINE="${OPENROUTER_BASELINE:-gpt-5.5}" \
  -e OPENROUTER_REASONING_EFFORT="${OPENROUTER_REASONING_EFFORT:-}" \
  -v "$PWD/runs:/app/runs" \
  se-llm-eval
