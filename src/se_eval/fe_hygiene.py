from __future__ import annotations

import re


TOP_LEVEL_COMMAND_RE = re.compile(
    r"^(?:"
    r"gogo\b|"
    r"quit\b|"
    r"q\b|"
    r"g\b|"
    r"r\b|"
    r"v\b|"
    r"u\b|"
    r"refine\b|"
    r"delete\b|"
    r"pop\b|"
    r"set\b|"
    r"unset\b|"
    r"foreach\b|"
    r"while\b|"
    r"if\b|"
    r"print\b|"
    r"printf\b|"
    r"convert_to_quantities\b|"
    r"hessian(?:_normal|_seek)?\b"
    r")"
)


def strip_comments(text: str) -> str:
    # Good enough for eval hygiene; Surface Evolver itself remains the authority.
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)
    return text


def fe_command_hygiene_failures(fe_content: str) -> list[str]:
    """
    Find commands that should not be executed from a submitted datafile.

    Submissions may define a command such as ``gogo := { ... }`` for the runner
    to invoke later, including after a bare ``read`` marker. They should not
    execute commands while the datafile loads, since that makes hidden command
    scripts order-dependent.
    """
    clean = strip_comments(fe_content)
    failures: list[str] = []

    if re.search(r"(?<![A-Za-z0-9_])quit(?![A-Za-z0-9_])", clean, flags=re.IGNORECASE):
        failures.append("datafile must not contain a quit command")

    brace_depth = 0
    for line_number, raw_line in enumerate(clean.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        lower = line.lower()
        top_level = brace_depth == 0
        is_definition = ":=" in line

        if top_level and lower.startswith("read") and lower.rstrip(";").strip() != "read":
            failures.append(
                f"line {line_number}: datafile may use a bare read marker for "
                "command definitions, but must not execute read commands while loading"
            )

        if top_level and not is_definition and TOP_LEVEL_COMMAND_RE.match(lower):
            command = lower.split(maxsplit=1)[0].rstrip(";")
            failures.append(
                f"line {line_number}: datafile must define commands for the runner, "
                f"not execute {command!r} while loading"
            )

        brace_depth += line.count("{") - line.count("}")
        brace_depth = max(brace_depth, 0)

    return failures
