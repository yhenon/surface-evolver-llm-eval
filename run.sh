#!/usr/bin/env bash
set -euo pipefail

if [ -z "${OPENROUTER_API_KEY:-}" ] && [ -f .openrouter_key ]; then
  OPENROUTER_API_KEY="$(tr -d '[:space:]' < .openrouter_key)"
fi

if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "OPENROUTER_API_KEY is not set and .openrouter_key was not found." >&2
  exit 1
fi

docker build -t se-llm-eval .

docker run --rm \
  -e OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
  -e OPENROUTER_BASELINE="${OPENROUTER_BASELINE:-gpt-5.5}" \
  -e OPENROUTER_REASONING_EFFORT="${OPENROUTER_REASONING_EFFORT:-}" \
  -v "$PWD/runs:/app/runs" \
  se-llm-eval
