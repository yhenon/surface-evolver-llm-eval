FROM python:3.12-slim-bookworm

# Surface Evolver has a Debian/Ubuntu no-X package. The binary is typically
# evolver-nox-d; we symlink an available binary to "evolver" for the runner.
RUN set -eux;     apt-get update;     apt-get install -y --no-install-recommends evolver-nox ca-certificates;     rm -rf /var/lib/apt/lists/*;     if command -v evolver-nox-d >/dev/null 2>&1; then         ln -sf "$(command -v evolver-nox-d)" /usr/local/bin/evolver;     elif command -v evolver >/dev/null 2>&1; then         ln -sf "$(command -v evolver)" /usr/local/bin/evolver;     else         echo "Surface Evolver binary not found after install" >&2; exit 1;     fi

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .
COPY src ./src
COPY tasks ./tasks

ENV PYTHONPATH=/app/src
ENV SE_EVAL_TASK_DIR=/app/tasks

# Configure OpenRouter at runtime:
# docker run --rm -e OPENROUTER_API_KEY=... -e OPENROUTER_BASELINE=gpt-5.5 se-llm-eval
CMD ["python", "-m", "se_eval.run_eval", "--task", "cube_basic"]
