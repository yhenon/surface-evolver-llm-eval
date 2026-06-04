from __future__ import annotations

import re
from dataclasses import dataclass

from .models import StaticChecks


SECTION_NAMES = ("vertices", "edges", "faces", "facets", "bodies")


def strip_comments(text: str) -> str:
    # Good enough for eval hygiene; Surface Evolver itself remains the authority.
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    return text


def count_section_rows(fe_content: str) -> dict[str, int]:
    """
    Count rows following section headers until the next known section.

    This is not intended to be a full Surface Evolver parser. It catches obvious
    omissions and gives useful feedback, while the actual Evolver run catches
    syntax/semantic errors.
    """
    clean = strip_comments(fe_content).lower()
    counts = {name: 0 for name in SECTION_NAMES}

    current: str | None = None
    for raw_line in clean.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        first = line.split(maxsplit=1)[0]
        if first in SECTION_NAMES:
            current = first
            continue

        if current and re.match(r"^[+-]?\d+\b", line):
            counts[current] += 1

    # Treat "facets" as faces for Evolver variants/tasks using either term.
    counts["faces"] = max(counts["faces"], counts["facets"])
    return counts


def section_row_ids(fe_content: str) -> dict[str, set[int]]:
    clean = strip_comments(fe_content).lower()
    ids = {name: set() for name in SECTION_NAMES}

    current: str | None = None
    for raw_line in clean.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        first = line.split(maxsplit=1)[0]
        if first in SECTION_NAMES:
            current = first
            continue

        if current:
            match = re.match(r"^([+-]?\d+)\b", line)
            if match:
                ids[current].add(int(match.group(1)))

    ids["faces"] = ids["faces"] | ids["facets"]
    return ids


@dataclass(frozen=True)
class StaticCheckResult:
    ok: bool
    details: dict[str, object]


def run_static_checks(fe_content: str, checks: StaticChecks) -> StaticCheckResult:
    lower = strip_comments(fe_content).lower()
    counts = count_section_rows(fe_content)
    ids = section_row_ids(fe_content)

    failures: list[str] = []
    required_counts = {
        "vertices": checks.min_vertices,
        "edges": checks.min_edges,
        "faces": checks.min_faces,
        "bodies": checks.min_bodies,
    }
    for name, minimum in required_counts.items():
        if counts.get(name, 0) < minimum:
            failures.append(f"{name}: expected at least {minimum}, got {counts.get(name, 0)}")

    for s in checks.required_substrings:
        if s.lower() not in lower:
            failures.append(f"missing required substring: {s!r}")

    for body_id in checks.required_body_ids:
        if body_id not in ids["bodies"]:
            failures.append(f"missing required body id: {body_id}")

    return StaticCheckResult(
        ok=not failures,
        details={
            "counts": counts,
            "ids": {name: sorted(values) for name, values in ids.items()},
            "failures": failures,
        },
    )
