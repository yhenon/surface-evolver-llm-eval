from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

from .evolver import run_surface_evolver
from .models import DynamicChecks, EvolverMetricCheck


METRIC_RE = re.compile(
    r"SE_METRIC\s+(?P<name>[A-Za-z0-9_.:-]+)\s+(?P<value>[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)"
)


@dataclass(frozen=True)
class DynamicCheckResult:
    ok: bool
    details: dict[str, Any]
    evolver: dict[str, Any]


class EvolverMetricChecker:
    def __init__(
        self,
        checks: DynamicChecks,
        setup_script: str = "",
        timeout_s: float = 10.0,
    ) -> None:
        self.checks = checks
        self.setup_script = setup_script
        self.timeout_s = timeout_s

    def run(self, fe_content: str) -> DynamicCheckResult:
        command_script = self._command_script()
        evolver = run_surface_evolver(
            fe_content=fe_content,
            command_script=command_script,
            timeout_s=self.timeout_s,
        )
        measurements = self._parse_measurements(evolver["stdout"])
        failures = self._metric_failures(measurements)

        if not evolver["ok"]:
            failures.append("Surface Evolver hidden check did not complete successfully")

        return DynamicCheckResult(
            ok=evolver["ok"] and not failures,
            details={
                "measurements": measurements,
                "failures": failures,
                "metric_checks": [
                    {
                        "name": check.name,
                        "command": check.command,
                        "expected": check.expected,
                        "tolerance": check.tolerance,
                    }
                    for check in self.checks.evolver_metrics
                ],
            },
            evolver=evolver,
        )

    def _command_script(self) -> str:
        lines: list[str] = []
        lines.extend(_setup_lines(self.setup_script))

        for check in self.checks.evolver_metrics:
            lines.append(_metric_command(check))

        lines.append("quit")
        return "\n".join(lines) + "\n"

    def _parse_measurements(self, stdout: str) -> dict[str, float]:
        measurements: dict[str, float] = {}
        for match in METRIC_RE.finditer(stdout):
            measurements[match.group("name")] = float(match.group("value"))
        return measurements

    def _metric_failures(self, measurements: dict[str, float]) -> list[str]:
        failures: list[str] = []
        for check in self.checks.evolver_metrics:
            actual = measurements.get(check.name)
            if actual is None:
                failures.append(f"missing metric: {check.name}")
                continue
            if not math.isfinite(actual):
                failures.append(f"{check.name}: expected finite value, got {actual}")
                continue
            delta = abs(actual - check.expected)
            if delta > check.tolerance:
                failures.append(
                    f"{check.name}: expected {check.expected} +/- {check.tolerance}, "
                    f"got {actual}"
                )
        return failures


def _metric_command(check: EvolverMetricCheck) -> str:
    return f'printf "SE_METRIC {check.name} %.17g\\n", {check.command}'


def _setup_lines(setup_script: str) -> list[str]:
    return [
        line
        for line in setup_script.splitlines()
        if line.strip() and line.strip().lower() not in {"q", "quit"}
    ]


def run_dynamic_checks(
    fe_content: str,
    checks: DynamicChecks,
    setup_script: str = "",
) -> DynamicCheckResult:
    return EvolverMetricChecker(checks=checks, setup_script=setup_script).run(fe_content)
