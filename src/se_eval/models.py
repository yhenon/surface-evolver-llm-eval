from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class StaticChecks(BaseModel):
    min_vertices: int = 0
    min_edges: int = 0
    min_faces: int = 0
    min_bodies: int = 0
    required_substrings: list[str] = Field(default_factory=list)
    required_body_ids: list[int] = Field(default_factory=list)
    enforce_command_hygiene: bool = True


class EvolverMetricCheck(BaseModel):
    name: str
    command: str
    expected: float
    tolerance: float = 1e-9


class DynamicChecks(BaseModel):
    evolver_metrics: list[EvolverMetricCheck] = Field(default_factory=list)


class Task(BaseModel):
    id: str

    title: str
    prompt: str
    public_command_script: str = ""
    hidden_command_script: str = ""
    static_checks: StaticChecks = Field(default_factory=StaticChecks)
    dynamic_checks: DynamicChecks = Field(default_factory=DynamicChecks)

    @staticmethod
    def load(task_id: str, task_dir: Path) -> "Task":
        path = task_dir / f"{task_id}.json"
        if not path.exists():
            known = sorted(p.stem for p in task_dir.glob("*.json"))
            raise FileNotFoundError(f"No task {task_id!r} at {path}. Known tasks: {known}")
        return Task.model_validate_json(path.read_text())
