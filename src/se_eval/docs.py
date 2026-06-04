from __future__ import annotations

import os
from pathlib import Path
from typing import Any


DEFAULT_DOC_DIR = Path(__file__).resolve().parents[2] / "tools" / "docs"
MAX_DOC_CHARS = 1000000

DOC_PAGES: dict[str, tuple[str, ...]] = {
    "datafile": ("datafile.md", "datafile.txt"),
    "syntax": ("syntax.md", "syntax.txt"),
    "elements": ("elements.md", "elements.txt"),
    "commands": ("commands.md", "commands.txt"),
    "single": ("single.md", "single.txt"),
    "toggle": ("toggle.md", "toggle.txt"),
    "constraints": ("constraints.md", "constraints.txt"),
    "quantities": ("quantities.md", "quantities.txt"),
    "energies": ("energies.md", "energies.txt"),
    "mound": ("mound.md", "mound.fe", "mound.txt"),
}


def get_evolver_doc(topic: str) -> dict[str, Any]:
    doc_dir = Path(os.environ.get("SE_EVOLVER_DOC_DIR", DEFAULT_DOC_DIR))
    page_path = _resolve_page_path(doc_dir, topic)
    if page_path is None:
        return {
            "ok": False,
            "error": (
                f"No curated plain-text documentation page for topic '{topic}' "
                f"was found in {doc_dir}."
            ),
            "available_topics": available_topics(doc_dir),
        }

    text = page_path.read_text(encoding="utf-8", errors="replace").strip()
    text, truncated = _truncate(text, MAX_DOC_CHARS)
    return {
        "ok": True,
        "topic": topic,
        "source": str(page_path),
        "truncated": truncated,
        "text": text,
    }


def available_topics(doc_dir: Path | None = None) -> list[str]:
    root = doc_dir or Path(os.environ.get("SE_EVOLVER_DOC_DIR", DEFAULT_DOC_DIR))
    return [topic for topic in DOC_PAGES if _resolve_page_path(root, topic) is not None]


def _resolve_page_path(doc_dir: Path, topic: str) -> Path | None:
    for filename in DOC_PAGES.get(topic, ()):
        path = doc_dir / filename
        if path.is_file():
            return path
    return None


def _truncate(text: str, max_chars: int) -> tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    truncated = text[:max_chars].rsplit("\n", 1)[0].rstrip()
    return truncated + "\n\n[truncated]", True
