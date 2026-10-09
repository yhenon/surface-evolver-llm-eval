"""Reproduce audit observations without editing tasks, references, or the grader.

From the repository root:
  PYTHONPATH=src .venv/bin/python docs/audits/2026-09-18-tasks-audit/probe.py
"""

import hashlib
import json
from pathlib import Path
import re
import time

from se_eval.dynamic_checks import EvolverMetricChecker
from se_eval.evolver import find_evolver, run_surface_evolver
from se_eval.grader import grade_submission
from se_eval.models import Task


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).with_name("evidence.json")
results = {"evolver": find_evolver(), "sha256": {}, "baselines": {}, "probes": {}}


def reference(name):
    return (ROOT / "ground_truth_fe" / f"{name}.fe").read_text()


def task(name):
    return Task.load(name, ROOT / "tasks_audit")


def record_grade(name, task_name, content, group="probes"):
    start = time.monotonic()
    try:
        grade = grade_submission(task(task_name), content)
        result = {
            "passed": grade["passed"],
            "score": grade["score"],
            "static_failures": grade["static"]["details"]["failures"],
            "dynamic_ok": grade["dynamic"]["ok"],
            "measurements": grade["dynamic"]["details"]["measurements"],
            "dynamic_failures": grade["dynamic"]["details"]["failures"],
            "evolver_ok": grade["evolver_hidden"]["ok"],
            "stderr": grade["evolver_hidden"]["stderr_tail"],
        }
    except Exception as exc:
        result = {"exception": f"{type(exc).__name__}: {exc}"}
    result["elapsed_seconds"] = time.monotonic() - start
    results[group][name] = result
    print(name, json.dumps(result), flush=True)


for path in sorted((ROOT / "tasks_audit").glob("*.json")):
    for source in (path, ROOT / "ground_truth_fe" / f"{path.stem}.fe"):
        results["sha256"][str(source.relative_to(ROOT))] = hashlib.sha256(source.read_bytes()).hexdigest()
    record_grade(path.stem, path.stem, reference(path.stem), "baselines")

cube = reference("cube")
record_grade("cube_facets_alias", "cube", cube.replace("\nfaces\n", "\nfacets\n"))
record_grade("cube_volume_whitespace", "cube", cube.replace("volume 1", "volume    1"))
record_grade("cube_volume_expression", "cube", cube.replace("volume 1", "volume (1)"))
lines = cube.splitlines()
in_vertices = False
for index, line in enumerate(lines):
    if line == "vertices":
        in_vertices = True
        continue
    if line == "edges":
        in_vertices = False
    if in_vertices and re.match(r"^\d+ ", line):
        fields = line.split()
        fields[1] = str(int(fields[1]) + 10)
        lines[index] = " ".join(fields)
record_grade("cube_translated_x_plus_10", "cube", "\n".join(lines) + "\n")
record_grade("cube_extra_body", "cube", cube + "2 -1 -2 -3 -4 -5 -6 volume -1\n")
record_grade("cube_executes_recalc_on_load", "cube", cube + "\nread\nrecalc\n")
record_grade(
    "three_plates_equivalent_cosine", "bridge_three_plates",
    reference("bridge_three_plates").replace("cos(angle1*pi/180)", "cos(pi*angle1/180)"),
)

for name in ("pyramid_mound", "bridge_two_rods"):
    content = reference(name)
    closing = content.rfind("}")
    content = content[:closing] + "\n g 500; r; u; g 500;\n" + content[closing:]
    record_grade(name + "_extra_evolution", name, content)

# The omitted W substrate is extruded along x, so its normal has zero x
# component. Its contribution to integral x n_x dA is exactly zero.
# This alternative flux therefore measures the closed geometric volume
# without needing the missing z-based substrate content integrals.
volume_probe = """quantity audit_x_volume info_only method facet_vector_integral global
vector_integrand:
q1: x
q2: 0
q3: 0
"""
raw = run_surface_evolver(
    volume_probe + reference("w_groove"),
    'printf "AUDIT initial %.17g %.17g\\n", body[1].volume, audit_x_volume.value\n'
    'gogo\n'
    'printf "AUDIT final %.17g %.17g\\n", body[1].volume, audit_x_volume.value\n',
)
results["probes"]["w_groove_independent_volume"] = {
    "ok": raw["ok"], "stderr": raw["stderr"],
    "measurements": [line for line in raw["stdout"].splitlines() if line.startswith("AUDIT ")],
    "version": raw["stdout"].splitlines()[0],
}

# A short, bounded reproduction of the timeout output-type defect.
checker = EvolverMetricChecker(task("cube").dynamic_checks, "g 1000000\n", timeout_s=0.05)
try:
    result = checker.run(cube)
    results["probes"]["timeout_handling"] = {"ok": result.ok, "details": result.details}
except Exception as exc:
    results["probes"]["timeout_handling"] = {"exception": f"{type(exc).__name__}: {exc}"}

OUTPUT.write_text(json.dumps(results, indent=2) + "\n")
print(f"Evidence saved to {OUTPUT}")
