from __future__ import annotations

import json
from typing import Any

from .docs import get_evolver_doc
from .evolver import run_surface_evolver
from .models import Task


OPENAI_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_evolver_doc",
            "description": (
                "Retrieve concise context from curated local plain-text Surface "
                "Evolver documentation in tools/docs. Use this for datafile "
                "syntax, command language, geometric elements, or related manual topics."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "enum": [
                            "datafile",
                            "syntax",
                            "elements",
                            "commands",
                            "single",
                            "toggle",
                            "constraints",
                            "quantities",
                            "energies",
                            "mound",
                        ],
                        "description": "Curated documentation page to retrieve.",
                    },
                },
                "required": ["topic"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_surface_evolver",
            "description": (
                "Run a candidate Surface Evolver .fe datafile with a command "
                "script, or with the task's public_command_script when "
                "command_script is empty or omitted. Use this to validate syntax "
                "and debug Evolver behavior."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "fe_content": {
                        "type": "string",
                        "description": "Complete contents of the candidate .fe file.",
                    },
                    "command_script": {
                        "type": "string",
                        "description": (
                            "Surface Evolver commands to run after loading the file. "
                            "Pass an empty string to use the task's "
                            "public_command_script; if this field is omitted by a "
                            "provider, the eval uses public_command_script as the "
                            "fallback. "
                            "Use this script to call commands such as gogo when "
                            "validating. Do not put quit in the .fe file; the runner "
                            "will append a quit command to this script if absent."
                        ),
                    },
                },
                "required": ["fe_content", "command_script"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_fe_file",
            "description": (
                "Submit the final Surface Evolver .fe datafile for grading. "
                "Call this exactly once when you are done."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "fe_content": {
                        "type": "string",
                        "description": "Complete contents of the final .fe file.",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Brief notes about assumptions or validation performed.",
                    },
                },
                "required": ["fe_content", "notes"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
]


def execute_tool(name: str, raw_arguments: str, task: Task) -> tuple[dict[str, Any], str | None]:
    """
    Execute a model-requested tool.

    Returns: (tool_result, submitted_fe_content_or_none)
    """
    args = json.loads(raw_arguments or "{}")
    if name == "get_evolver_doc":
        print(f"get_evolver_doc: {args}")
        return get_evolver_doc(
            topic=args["topic"],
        ), None

    if name == "run_surface_evolver":
        print(f"run_surface_evolver")
        result = run_surface_evolver(
            fe_content=args["fe_content"],
            command_script=args.get("command_script") or task.public_command_script,
        )
        print(f"run_surface_evolver: {result}")
        # Avoid feeding huge command lines back to the model.
        result.pop("argv", None)
        return result, None

    if name == "submit_fe_file":
        return {"ok": True, "message": "Submission received."}, args["fe_content"]

    return {"ok": False, "error": f"Unknown tool: {name}"}, None
