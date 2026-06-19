# Surface Evolver LLM Eval

This repository benchmarks whether language models can write valid
[Surface Evolver](https://kenbrakke.com/evolver/evolver.html) `.fe` datafiles
for geometry and minimal-surface modeling tasks.

Surface Evolver is powerful, terse, and niche. A correct answer is not just a
plausible-looking text file: the model has to choose the right datafile
sections, orient elements consistently, define bodies and constraints, and
produce a file that Evolver can actually load, evolve, and measure. This eval
therefore tests tool use, domain-specific syntax, numerical validation, and
debugging under feedback.

## What The Eval Measures

Each task asks a model to create a complete Surface Evolver datafile. The model
is given a small tool environment:

- `get_evolver_doc`: retrieve curated local Surface Evolver documentation from
  `tools/docs`.
- `run_surface_evolver`: run a candidate `.fe` file against a command script and
  inspect Evolver output.
- `submit_fe_file`: submit the final raw `.fe` file through a structured tool
  call.

The point is to evaluate whether a model can use documentation and execution
feedback to produce a real artifact. The final submission is not scraped from
Markdown or prose; it must arrive as a structured tool call containing the raw
file content.

Submitted `.fe` files should describe the starting geometry and may define
reusable Evolver commands such as `gogo := { ... }`. They must not execute
commands while loading: no `quit`, bare `gogo`, `refine`, `g`, `print`, or
similar top-level commands. A bare `read` marker may be used before command
definitions, but not to execute another command file. Public and hidden command
scripts decide when to run refinement or measurement steps, and the runner
appends `quit` automatically.

## How A Run Works

For each model and task, `se_eval.run_eval` performs two stages:

1. `generate`: send the task prompt to the model, expose the tools above, allow
   up to `--max-rounds` repair rounds, and write `submission.fe` when the model
   calls `submit_fe_file`.
2. `grade`: read `submission.fe`, run deterministic static checks, run hidden
   Surface Evolver checks, and write `result.json`.

A run directory contains:

- `submission.fe`: the model's submitted datafile.
- `transcript.json`: model messages, tool calls, and tool results.
- `generation.json`: model id, rounds used, submission status, and token usage
  when available.
- `result.json`: score, pass/fail status, static check details, hidden Evolver
  output, and metric measurements.
- `visual.off` and `visual.svg`: optional Evolver-derived visual artifacts when
  grading with `--visual`.

## Scoring

The current grader uses a simple weighted score:

- `0.3`: static datafile checks pass.
- `0.3`: the hidden Surface Evolver run completes successfully.
- `0.4`: hidden metric checks pass within their tolerances.

`passed` is true only when the static checks and all dynamic checks pass. Static
checks catch obvious structural omissions, such as too few vertices, missing
sections, missing body ids, or required syntax fragments. Dynamic checks are the
authority: they load the submitted file in Surface Evolver, run task-specific
commands, print `SE_METRIC` values, and compare those values with expected
targets.

## Quick Start With Docker

Docker is the easiest way to run the eval because the image installs Surface
Evolver and the Python dependencies.

```bash
docker build -t se-llm-eval .
docker run --rm \
  -e OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
  -v "$PWD/runs:/app/runs" \
  se-llm-eval
```

Run a specific task and model:

```bash
docker run --rm \
  -e OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
  -v "$PWD/runs:/app/runs" \
  se-llm-eval python -m se_eval.run_eval \
    --task-visibility public \
    --task two_bubbles_2d \
    --baseline deepseek
```

Run all configured baselines for a task:

```bash
docker run --rm \
  -e OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
  -v "$PWD/runs:/app/runs" \
  se-llm-eval python -m se_eval.run_eval \
    --task cube_basic \
    --all-baselines
```

The helper script builds the image and runs the default task:

```bash
./run.sh
```

It reads `OPENROUTER_API_KEY` from the environment, or from a local
`.openrouter_key` file if present.

## Local Setup

Local runs require Python 3.12+ and a Surface Evolver executable. The runner
looks for `EVOLVER_BIN`, `./evolver`, `evolver`, `evolver-nox-d`, and
`evolver-nox`, in that order.

Install Python dependencies:

```bash
uv sync
```

Run a smoke check that does not call a model:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval --list-baselines
```

Run a full eval locally with the default private task set:

```bash
OPENROUTER_API_KEY=... \
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --task cube_basic \
  --baseline gpt-5.5
```

Run a public task locally:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --task-visibility public \
  --task two_bubbles_2d \
  --baseline deepseek
```

## Models

The runner uses OpenRouter's OpenAI-compatible chat completions endpoint.
Configure authentication with `OPENROUTER_API_KEY`.

List named baselines:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval --list-baselines
```

Run one named baseline:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --task cube_basic \
  --baseline deepseek
```

Override the model id directly:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --task cube_basic \
  --model openai/gpt-5.5
```

For models that support reasoning controls through OpenRouter:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --task cube_basic \
  --baseline gpt-5.5 \
  --reasoning-effort high
```

Supported environment variables:

- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`
- `OPENROUTER_BASELINE`
- `OPENROUTER_REASONING_EFFORT`
- `OPENROUTER_BASE_URL`
- `OPENROUTER_HTTP_REFERER`
- `OPENROUTER_APP_TITLE`
- `EVOLVER_BIN`
- `SE_EVAL_TASK_VISIBILITY`
- `SE_EVAL_TASK_DIR`
- `SE_EVOLVER_DOC_DIR`

## Generation And Grading Separately

Generate only:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --stage generate \
  --task cube_basic \
  --baseline deepseek
```

Re-grade an existing run without calling a model:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --stage grade \
  --task cube_basic \
  runs/20260601T183425Z_cube_basic_deepseek_deepseek-v4-pro
```

Grade a direct `.fe` file and print the result without writing JSON:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --stage grade \
  --task cube_basic \
  --no-write \
  path/to/submission.fe
```

Write Evolver-derived visual artifacts during grading:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --stage grade \
  --task cube_basic \
  --visual \
  path/to/submission.fe
```

## Matrix Runs

Use `se_eval.run_matrix` to run selected models across the public and private
task sets, grade each submission, and consolidate compact outcomes for later
plotting.

Preview the full matrix without calling models:

```bash
PYTHONPATH=src uv run python -m se_eval.run_matrix \
  --baseline deepseek \
  --task-visibility all \
  --dry-run
```

Run selected baselines on all public and private tasks:

```bash
OPENROUTER_API_KEY=... \
PYTHONPATH=src uv run python -m se_eval.run_matrix \
  --baseline deepseek \
  --baseline mistral \
  --task-visibility all
```

Each matrix run writes task/model run directories under
`runs/<timestamp>_matrix/`, plus:

- `outcomes.jsonl`: one compact row per task/model pair, suitable for pandas or
  plotting scripts.
- `summary.json`: aggregate pass rates and mean scores by model and by task,
  rewritten after each completed run.

Useful options include `--model <openrouter/model-id>` for exact model ids,
`--all-baselines`, repeated `--task <task_id>` filters, `--skip-existing` for
resuming a matrix directory, and `--results-file` / `--summary-file` for custom
consolidated output paths. When `--reasoning-effort` is set, each task/model run
directory includes `_reasoning-<effort>` and outcome rows include both
`reasoning_effort` and `model_run_label`.

To compare multiple reasoning efforts in one matrix, pass a comma-separated list
or repeat the option. Use `na` for a run that omits reasoning controls:

```bash
PYTHONPATH=src uv run python -m se_eval.run_matrix \
  --baseline gpt-5.5 \
  --task-visibility all \
  --reasoning-effort high,na,low
```

## Plotting Results

Use `se_eval.plot_results` to join one or more matrix run directories and create
plot-ready merged data plus SVG charts. If an `icons/` directory is present, the
plotter embeds provider PNG icons in the SVG charts and colors model bars by
provider. Use `--icon-dir <path>` to point at another icon directory, or
`--no-icons` to disable embedding.

Plot a single matrix run:

```bash
PYTHONPATH=src uv run python -m se_eval.plot_results \
  runs/20260610T131829Z_matrix \
  --output-dir runs/20260610T131829Z_matrix/plots
```

Join all matrix runs under `runs/`:

```bash
PYTHONPATH=src uv run python -m se_eval.plot_results \
  --output-dir runs/plots
```

Join selected matrix runs:

```bash
PYTHONPATH=src uv run python -m se_eval.plot_results \
  runs/20260610T131829Z_matrix \
  runs/<another_timestamp>_matrix \
  --output-dir runs/joined_plots
```

The plotting script writes:

- `index.html`: a small local report embedding the charts.
- `by_model.svg`: pass rate and mean score by model.
- `by_task.svg`: pass rate and mean score by task.
- `task_model_heatmap.svg`: mean score for each task/model pair.
- `merged_outcomes.jsonl` and `merged_outcomes.csv`: joined row-level data.
- `aggregates.json`: aggregate statistics by model and by task.

## Publishing The GitHub Pages Site

The public web page lives in `docs/` and is deployed by
`.github/workflows/pages.yml`. The page reads its metrics and model table from
`docs/data/aggregates.json`, and the charts are copied from the generated plot
artifacts. The refresh script also embeds the current aggregate snapshot in
`docs/index.html` so local file previews still show numbers if the browser
blocks `fetch()` for local JSON files. Row-level CSV and JSONL files are not
published for now.

After adding tasks, models, or new matrix runs, refresh the site assets with:

```bash
PYTHONPATH=src uv run python tools/update_pages_site.py --replot
```

That command regenerates `runs/plots/` from the current matrix runs under
`runs/`, then copies the public chart and aggregate artifacts into:

- `docs/assets/charts/`
- `docs/data/`

To publish a specific set of matrix directories instead of every
`runs/*_matrix` directory, pass them after `--replot`:

```bash
PYTHONPATH=src uv run python tools/update_pages_site.py --replot \
  runs/20260617T073617Z_matrix \
  runs/20260618T101305Z_matrix
```

Commit the changed files in `docs/` and push to `main`; the Pages workflow will
deploy the updated static site.

## Rescoring Existing Runs

When grading criteria change, use `se_eval.rescore_results` to re-run only the
deterministic grader on saved `submission.fe` files. This does not call models or
spend LLM credits.

Preview a rescore for one task/model pair:

```bash
PYTHONPATH=src uv run python -m se_eval.rescore_results \
  runs/20260610T131829Z_matrix \
  --task two_bubbles_2d \
  --model gpt-5.5 \
  --dry-run
```

Rescore all rows in all matrix runs under `runs/`:

```bash
PYTHONPATH=src uv run python -m se_eval.rescore_results
```

The rescore command overwrites each run's `result.json`, rewrites the source
`outcomes.jsonl`, and refreshes `summary.json`. By default it creates
`.bak-<timestamp>` copies of `outcomes.jsonl` and `summary.json` before
rewriting them. After rescoring, run `se_eval.plot_results` again to regenerate
joined plots.

## Tasks

Tasks are JSON files in `tasks_public/` and `tasks_private/`. Use
`--task-visibility public` or `--task-visibility private` to select which set to
load. Private is the default. `--task-dir` or `SE_EVAL_TASK_DIR` can still point
at an explicit directory and takes precedence over task visibility.

A task defines:

- `id`, `title`, and the user-facing `prompt`.
- `public_command_script`, which `run_surface_evolver` uses when a tool call
  leaves `command_script` empty or omitted.
- `hidden_command_script`, which the grader runs before metric checks.
- `static_checks`, such as minimum element counts, required substrings, and
  command hygiene for submitted datafiles.
- `dynamic_checks.evolver_metrics`, which are Evolver expressions with expected
  values and tolerances.

Example task families currently include:

- `cube_basic`: build a unit cube with one prescribed-volume body.
- `two_bubbles_2d`: build a two-bubble 2D string model with two prescribed
  enclosed areas and one shared internal edge.
- `bridge_two_plates`: build a liquid bridge between two constrained plates
  with contact-angle energy and content integrals.
- `bridge_three_plates`: build a liquid bridge touching three vertical plates
  arranged symmetrically at 120 degrees.

To add a task, create `tasks_public/<task_id>.json` or
`tasks_private/<task_id>.json`, make the public validation script useful but not
exhaustive, and put the real acceptance criteria in hidden Evolver metric
checks. Then run:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --task-visibility public \
  --task <task_id> \
  --baseline deepseek
```

## Documentation Tool

The documentation tool reads curated pages from `tools/docs`. The supported
topics are:

- `datafile`
- `syntax`
- `elements`
- `commands`
- `single`
- `toggle`
- `constraints`
- `quantities`
- `energies`
- `mound`

The eval-time tool does not parse HTML. To derive curated markdown-ish pages
from a local Surface Evolver manual checkout, use:

```bash
python tools/convert_evolver_docs.py /path/to/Evolver/doc \
  --topic datafile \
  --topic syntax \
  --topic elements \
  --topic commands
```

## Why Tool-Based Submission

The eval intentionally avoids asking the model to paste a `.fe` file into a
chat answer. Tool calls make the artifact boundary explicit:

- the model can retrieve only the docs exposed by the benchmark,
- candidate execution is captured in the transcript,
- the final submission is raw file content,
- grading does not depend on brittle Markdown extraction.

This also makes the benchmark closer to real agentic engineering work: read
domain docs, write a candidate, run the simulator, repair mistakes, and submit a
file that passes deterministic checks.

## License

Apache-2.0. See `LICENSE`.
