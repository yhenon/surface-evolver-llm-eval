from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .fe_hygiene import fe_command_hygiene_failures


def find_evolver() -> str:
    """Find a Surface Evolver executable in common Debian/source-build locations."""
    candidates = [
        os.environ.get("EVOLVER_BIN"),
        str(Path.cwd() / "evolver"),
        "evolver",
        "evolver-nox-d",
        "evolver-nox",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists() and os.access(path, os.X_OK):
            return str(path)
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise RuntimeError(
        "Could not find Surface Evolver. Install evolver-nox or set EVOLVER_BIN."
    )


def _ensure_quit(command_script: str) -> str:
    script = command_script.strip() + "\n"
    if not re.search(r"(?im)^\s*(?:q|quit)\s*;?\s*$", script):
        script += "quit\n"
    return script


def run_surface_evolver(
    fe_content: str,
    command_script: str = "quit\n",
    timeout_s: float = 10.0,
    max_output_chars: int = 200_000,
) -> dict[str, Any]:
    """
    Run Surface Evolver on an in-memory .fe file.

    This is deliberately shell-free. The model can control Evolver commands, but
    not the shell command line. In production, run this inside a locked-down
    container with CPU/memory/time limits.
    """
    hygiene_failures = fe_command_hygiene_failures(fe_content)
    if hygiene_failures:
        return {
            "ok": False,
            "timed_out": False,
            "exit_code": None,
            "stdout": "",
            "stderr": "\n".join(hygiene_failures),
            "argv": [],
            "hygiene_failures": hygiene_failures,
        }

    evolver = find_evolver()
    with tempfile.TemporaryDirectory(prefix="se_eval_") as tmp:
        tmpdir = Path(tmp)
        fe_path = tmpdir / "candidate.fe"
        cmd_path = tmpdir / "commands.cmd"
        fe_path.write_text(fe_content, encoding="utf-8")
        cmd_path.write_text(_ensure_quit(command_script), encoding="utf-8")

        # -x exits after errors; -w exits after warnings/errors; -f reads commands.
        argv = [evolver, "-x", "-w", "-f", str(cmd_path), str(fe_path)]
        try:
            proc = subprocess.run(
                argv,
                cwd=tmpdir,
                text=True,
                input="quit\n",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_s,
                check=False,
            )
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            return {
                "ok": False,
                "timed_out": True,
                "exit_code": None,
                "stdout": (exc.stdout or "")[-max_output_chars:],
                "stderr": (exc.stderr or "")[-max_output_chars:],
                "argv": argv,
            }

    stdout = proc.stdout[-max_output_chars:]
    stderr = proc.stderr[-max_output_chars:]
    return {
        "ok": proc.returncode == 0,
        "timed_out": timed_out,
        "exit_code": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "argv": argv,
    }
