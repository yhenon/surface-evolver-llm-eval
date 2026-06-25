# Surface Evolver Bench

<p align="center">
  <img src="docs/assets/illustrations/1.png" alt="Rendered Surface Evolver geometry example" width="23%">
  <img src="docs/assets/illustrations/2.png" alt="Rendered minimal surface geometry example" width="23%">
  <img src="docs/assets/illustrations/3.png" alt="Rendered Surface Evolver bridge example" width="23%">
  <img src="docs/assets/illustrations/4.png" alt="Rendered Surface Evolver capillary surface example" width="23%">
</p>

<p align="center"><em>Rendered Surface Evolver examples: simulated liquid in green, solid constraints in orange.</em></p>

How good are large language models at writing complex physical simulations in a
custom data format?

Surface Evolver Bench asks models to write complete
[Surface Evolver](https://kenbrakke.com/evolver/evolver.html) `.fe` datafiles
for liquid surfaces shaped by geometry, constraints, contact angles, gravity,
and volume/area terms. The generated file is not judged by vibes or by another
model: it has to load in Evolver, run through hidden scripts, and match measured
physical quantities from reference solutions.

[Surface Evolver](https://kenbrakke.com/evolver/evolver.html) is a tool
released in 1992 (!) for modeling liquid surfaces. It is useful for tasks such
as studying solder deposition on chips, modeling liquid fuel tanks, or designing
lab-on-a-chip networks. A simulation is defined using Evolver's custom datafile
syntax: vertices, edges, faces, bodies, constraints, energies, and boundary
integrals.

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
- `run_error.json`: written when generation or grading errors out, with a
  coarse category such as `malformed_provider_response`, `connectivity`,
  `quota_or_credit`, `rate_limit`, `no_submission`, or `grader_or_evolver`.
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
    --baseline deepseek-v4-pro
```

Run all configured baselines for a task:

```bash
docker run --rm \
  -e OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
  -v "$PWD/runs:/app/runs" \
  se-llm-eval python -m se_eval.run_eval \
    --task-visibility public \
    --task two_bubbles_2d \
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

Run a full eval locally with the default private task directory:

```bash
OPENROUTER_API_KEY=... \
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --baseline gpt-5.5
```

Run a public task locally:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --task-visibility public \
  --task two_bubbles_2d \
  --baseline deepseek-v4-pro
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
  --task-visibility public \
  --task two_bubbles_2d \
  --baseline deepseek-v4-pro
```

Override the model id directly:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --task-visibility public \
  --task two_bubbles_2d \
  --model openai/gpt-5.5
```

For models that support reasoning controls through OpenRouter:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --task-visibility public \
  --task two_bubbles_2d \
  --baseline gpt-5.5 \
  --reasoning-effort high
```

Named models in `eval_config.json` can also declare a default
`reasoning_effort`:

```json
{
  "name": "gpt-5.5-high",
  "model": "openai/gpt-5.5",
  "reasoning_effort": "high"
}
```

When no reasoning option is passed, the runner uses the configured model's
`reasoning_effort`. If neither the CLI nor config sets one, the request omits
the OpenRouter `reasoning` object and the provider default applies.

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
  --task-visibility public \
  --task two_bubbles_2d \
  --baseline deepseek-v4-pro
```

Re-grade an existing run without calling a model:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --stage grade \
  --task-visibility private \
  --task <task_id> \
  runs/deepseek-v4-pro/private_<task_id>
```

Grade a direct `.fe` file and print the result without writing JSON:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --stage grade \
  --task-visibility public \
  --task two_bubbles_2d \
  --no-write \
  path/to/submission.fe
```

Write Evolver-derived visual artifacts during grading:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --stage grade \
  --task-visibility public \
  --task two_bubbles_2d \
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
  --baseline deepseek-v4-pro \
  --task-visibility all \
  --dry-run
```

Run selected baselines on all public and private tasks:

```bash
OPENROUTER_API_KEY=... \
PYTHONPATH=src uv run python -m se_eval.run_matrix \
  --baseline deepseek-v4-pro \
  --baseline mistral-medium-3-5 \
  --task-visibility all
```

Matrix runs now use stable, incrementally fillable paths:

```text
runs/<model-name>/<visibility>_<task-id>/
```

For example, DeepSeek's configured run for the public two-bubble task lives at
`runs/deepseek-v4-pro/public_two_bubbles_2d/`. The run directories are the
canonical source of truth. Compact aggregate files are derived from those
artifacts:

- `summary.json`: aggregate pass rates and mean scores by model and by task,
  rewritten after each completed run.
- `runs/plots/merged_outcomes.jsonl` and `runs/plots/merged_outcomes.csv`:
  optional plot/export artifacts suitable for pandas.

Useful options include `--model <openrouter/model-id>` for exact model ids,
`--all-baselines`, repeated `--task <task_id>` filters, `--skip-existing` for
incrementally filling directories that lack both `result.json` and
`run_error.json`, and `--summary-file` for a custom derived summary path.
Configured reasoning defaults keep the configured model name in run directories.
Explicit `--reasoning-effort` matrix overrides use `_reasoning-<effort>` or
`_reasoning-na` suffixes so comparisons do not collide; derived plot/export rows
include `reasoning_effort` and `model_run_label`.

Create the model/task directory grid without calling models:

```bash
PYTHONPATH=src uv run python -m se_eval.sync_runs
```

The model list comes from `eval_config.json`. Use full configured model names
such as `deepseek-v4-pro`; older short aliases like `deepseek` still resolve for
now but are deprecated.

To compare multiple reasoning efforts in one matrix, either add separate config
entries such as `gpt-5.5-medium` and `gpt-5.5-high`, or pass a comma-separated
list / repeat the option. Use `na` for a run that omits reasoning controls:

```bash
PYTHONPATH=src uv run python -m se_eval.run_matrix \
  --baseline gpt-5.5 \
  --task-visibility all \
  --reasoning-effort high,na,low
```

## Plotting Results

Use `se_eval.plot_results` to join one or more run roots and create
plot-ready merged data plus SVG charts. If an `icons/` directory is present, the
plotter embeds provider PNG icons in the SVG charts and colors model bars by
provider. Use `--icon-dir <path>` to point at another icon directory, or
`--no-icons` to disable embedding.

Plot the default stable runs root:

```bash
PYTHONPATH=src uv run python -m se_eval.plot_results \
  --output-dir runs/plots
```

Plot a specific run root:

```bash
PYTHONPATH=src uv run python -m se_eval.plot_results \
  runs \
  --output-dir runs/joined_plots
```

The plotting script writes:

- `index.html`: a small local report embedding the charts.
- `by_model.svg`: pass rate, mean score, total tokens, and recorded cost by model.
- `model_tool_usage.svg`: average assistant turns and stacked tool calls by model.
- `score_vs_total_tokens.svg`: mean score versus total tokens by model.
- `score_vs_total_cost.svg`: mean score versus recorded inference cost by model,
  with a stepped efficient frontier.
- `pass_rate_vs_total_tokens.svg`: pass rate versus total tokens by model.
- `pass_rate_vs_total_cost.svg`: pass rate versus recorded inference cost by
  model, with a stepped efficient frontier.
- `by_task.svg`: pass rate and mean score by task.
- `task_model_heatmap.svg`: mean score for each task/model pair.
- `merged_outcomes.jsonl` and `merged_outcomes.csv`: joined row-level data,
  including reasoning labels, token/cost fields, and interaction counts when
  `generation.json` and `transcript.json` are available.
- `aggregates.json`: aggregate statistics by model and by task, including
  total/mean token and recorded-cost values.

## Publishing The GitHub Pages Site

The public web page lives in `docs/` and is deployed by
`.github/workflows/pages.yml`. The charts are copied from the generated plot
artifacts, and `docs/data/aggregates.json` is published as the compact aggregate
snapshot. Row-level CSV and JSONL files are not published for now.

After adding tasks, models, or run results, refresh the site assets with:

```bash
PYTHONPATH=src uv run python tools/update_pages_site.py --replot
```

That command regenerates `runs/plots/` from the current run artifacts under
`runs/`, then copies the public chart and aggregate artifacts into:

- `docs/assets/charts/`
- `docs/data/`

To publish from a specific run root instead of the default `runs/`, pass it
after `--replot`:

```bash
PYTHONPATH=src uv run python tools/update_pages_site.py --replot \
  runs/some_matrix
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
  runs \
  --task two_bubbles_2d \
  --model gpt-5.5 \
  --dry-run
```

Rescore all runs under `runs/`:

```bash
PYTHONPATH=src uv run python -m se_eval.rescore_results
```

The rescore command overwrites each submitted run's `result.json` and refreshes
the derived `summary.json`. By default it creates a `.bak-<timestamp>` copy of
`summary.json` before rewriting it. After rescoring, run `se_eval.plot_results`
again to regenerate joined plots.

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

- `two_bubbles_2d`: build a two-bubble 2D string model with two prescribed
  enclosed areas and one shared internal edge.
- droplet tasks with contact-angle energy and content integrals.
- bridge tasks with liquid surfaces spanning constrained solid supports.
- groove and well tasks with liquid surfaces shaped by channel-like
  constraints.

To add a task, create `tasks_public/<task_id>.json` or
`tasks_private/<task_id>.json`, make the public validation script useful but not
exhaustive, and put the real acceptance criteria in hidden Evolver metric
checks. Then run:

```bash
PYTHONPATH=src uv run python -m se_eval.run_eval \
  --task-visibility public \
  --task <task_id> \
  --baseline deepseek-v4-pro
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
