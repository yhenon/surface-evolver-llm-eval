from __future__ import annotations

import html
import math
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evolver import _ensure_quit, find_evolver


@dataclass(frozen=True)
class OffMesh:
    vertices: list[tuple[float, float, float]]
    faces: list[list[int]]


@dataclass(frozen=True)
class VisualResult:
    ok: bool
    details: dict[str, Any]


def default_visual_paths(input_path: Path) -> tuple[Path, Path]:
    if input_path.is_dir():
        return input_path / "visual.svg", input_path / "visual.off"
    return (
        input_path.with_suffix(input_path.suffix + ".visual.svg"),
        input_path.with_suffix(input_path.suffix + ".visual.off"),
    )


def create_visual_artifacts(
    fe_content: str,
    svg_path: Path,
    off_path: Path | None = None,
    timeout_s: float = 10.0,
) -> VisualResult:
    """
    Export geometry through Evolver, then render a small static SVG preview.

    The preview is deliberately generated from Evolver's OFF export instead of
    directly from the candidate text, so it reflects what Evolver actually
    loaded.
    """
    off_text_result = export_off(fe_content=fe_content, timeout_s=timeout_s)
    if not off_text_result["ok"]:
        return VisualResult(ok=False, details=off_text_result)

    off_text = off_text_result["off_text"]
    mesh = parse_off(off_text)
    svg = render_mesh_svg(mesh)
    svg_path.write_text(svg, encoding="utf-8")
    if off_path:
        off_path.write_text(off_text, encoding="utf-8")

    return VisualResult(
        ok=True,
        details={
            "svg_path": str(svg_path),
            "off_path": str(off_path) if off_path else None,
            "vertices": len(mesh.vertices),
            "faces": len(mesh.faces),
        },
    )


def export_off(fe_content: str, timeout_s: float = 10.0) -> dict[str, Any]:
    evolver = find_evolver()
    off_cmd = find_off_cmd(evolver)

    with tempfile.TemporaryDirectory(prefix="se_visual_") as tmp:
        tmpdir = Path(tmp)
        fe_path = tmpdir / "candidate.fe"
        cmd_path = tmpdir / "commands.cmd"
        off_path = tmpdir / "candidate.off"

        fe_path.write_text(fe_content, encoding="utf-8")
        cmd_path.write_text(
            _ensure_quit(
                "\n".join(
                    [
                        f'read "{evolver_string(off_cmd)}"',
                        f'do_off >>> "{evolver_string(off_path)}"',
                        "quit",
                    ]
                )
            ),
            encoding="utf-8",
        )

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
        except subprocess.TimeoutExpired as exc:
            return {
                "ok": False,
                "timed_out": True,
                "exit_code": None,
                "stdout_tail": (exc.stdout or "")[-4000:],
                "stderr_tail": (exc.stderr or "")[-4000:],
            }

        if proc.returncode != 0 or not off_path.exists():
            return {
                "ok": False,
                "timed_out": False,
                "exit_code": proc.returncode,
                "stdout_tail": proc.stdout[-4000:],
                "stderr_tail": proc.stderr[-4000:],
            }

        return {
            "ok": True,
            "timed_out": False,
            "exit_code": proc.returncode,
            "stdout_tail": proc.stdout[-4000:],
            "stderr_tail": proc.stderr[-4000:],
            "off_text": off_path.read_text(encoding="utf-8"),
        }


def find_off_cmd(evolver: str) -> Path:
    candidates = [
        os.environ.get("EVOLVER_OFF_CMD"),
        str(Path(evolver).resolve().parent / "fe" / "off.cmd"),
        "/usr/share/evolver/fe/off.cmd",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists():
            return path
    raise RuntimeError("Could not find Evolver off.cmd. Set EVOLVER_OFF_CMD.")


def evolver_string(path: Path) -> str:
    return str(path).replace("\\", "\\\\").replace('"', '\\"')


def parse_off(text: str) -> OffMesh:
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not lines or lines[0] != "OFF":
        raise ValueError("OFF export did not start with OFF header")

    counts = lines[1].split()
    vertex_count = int(counts[0])
    face_count = int(counts[1])

    vertices: list[tuple[float, float, float]] = []
    for line in lines[2 : 2 + vertex_count]:
        x, y, z = line.split()[:3]
        vertices.append((float(x), float(y), float(z)))

    faces: list[list[int]] = []
    for line in lines[2 + vertex_count : 2 + vertex_count + face_count]:
        parts = line.split()
        count = int(parts[0])
        indices = [int(value) for value in parts[1:]]
        faces.append(indices[:count])

    return OffMesh(vertices=vertices, faces=faces)


def render_mesh_svg(mesh: OffMesh, width: int = 640, height: int = 480) -> str:
    projected = project_vertices(mesh.vertices)
    bounds = bounds_2d(projected)
    scale = min(
        (width - 80) / max(bounds[2] - bounds[0], 1e-9),
        (height - 80) / max(bounds[3] - bounds[1], 1e-9),
    )
    screen = [
        (
            40 + (x - bounds[0]) * scale,
            height - (40 + (y - bounds[1]) * scale),
            z,
        )
        for x, y, z in projected
    ]

    facets: list[tuple[float, str]] = []
    for face in mesh.faces:
        if len(face) < 3:
            continue
        points = [screen[index] for index in face]
        depth = sum(point[2] for point in points) / len(points)
        color = shade_face(mesh.vertices, face)
        point_text = " ".join(f"{x:.2f},{y:.2f}" for x, y, _ in points)
        facets.append(
            (
                depth,
                f'<polygon points="{point_text}" fill="{color}" stroke="#263238" '
                'stroke-width="1.4" stroke-linejoin="round"/>',
            )
        )

    facets.sort(key=lambda item: item[0])
    bbox = mesh_bounds(mesh.vertices)
    title = (
        f"Evolver visual check: {len(mesh.vertices)} vertices, "
        f"{len(mesh.faces)} facets, bbox {bbox}"
    )

    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img">',
            f"<title>{html.escape(title)}</title>",
            '<rect width="100%" height="100%" fill="#f7f7f4"/>',
            '<g shape-rendering="geometricPrecision">',
            *[facet for _, facet in facets],
            "</g>",
            f'<text x="16" y="{height - 16}" font-family="Menlo, Consolas, monospace" '
            f'font-size="12" fill="#37474f">{html.escape(title)}</text>',
            "</svg>",
            "",
        ]
    )


def project_vertices(
    vertices: list[tuple[float, float, float]]
) -> list[tuple[float, float, float]]:
    if not vertices:
        return []

    bbox = raw_bounds(vertices)
    center = (
        (bbox[0] + bbox[3]) / 2,
        (bbox[1] + bbox[4]) / 2,
        (bbox[2] + bbox[5]) / 2,
    )
    z_angle = math.radians(-35)
    x_angle = math.radians(-28)
    cz, sz = math.cos(z_angle), math.sin(z_angle)
    cx, sx = math.cos(x_angle), math.sin(x_angle)

    projected: list[tuple[float, float, float]] = []
    for x, y, z in vertices:
        x -= center[0]
        y -= center[1]
        z -= center[2]
        rx = x * cz - y * sz
        ry = x * sz + y * cz
        rz = z
        py = ry * cx - rz * sx
        pz = ry * sx + rz * cx
        projected.append((rx, py, pz))
    return projected


def shade_face(vertices: list[tuple[float, float, float]], face: list[int]) -> str:
    normal = face_normal([vertices[index] for index in face])
    light = normalize((0.35, -0.45, 0.82))
    intensity = max(0.0, dot(normal, light))
    base = 150 + int(70 * intensity)
    return f"rgb({base},{min(base + 18, 235)},{min(base + 34, 245)})"


def face_normal(points: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    nx = ny = nz = 0.0
    for idx, current in enumerate(points):
        nxt = points[(idx + 1) % len(points)]
        nx += (current[1] - nxt[1]) * (current[2] + nxt[2])
        ny += (current[2] - nxt[2]) * (current[0] + nxt[0])
        nz += (current[0] - nxt[0]) * (current[1] + nxt[1])
    return normalize((nx, ny, nz))


def normalize(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    length = math.sqrt(dot(vector, vector))
    if length == 0:
        return (0.0, 0.0, 1.0)
    return (vector[0] / length, vector[1] / length, vector[2] / length)


def dot(
    left: tuple[float, float, float],
    right: tuple[float, float, float],
) -> float:
    return left[0] * right[0] + left[1] * right[1] + left[2] * right[2]


def bounds_2d(points: list[tuple[float, float, float]]) -> tuple[float, float, float, float]:
    return (
        min(point[0] for point in points),
        min(point[1] for point in points),
        max(point[0] for point in points),
        max(point[1] for point in points),
    )


def raw_bounds(vertices: list[tuple[float, float, float]]) -> tuple[float, float, float, float, float, float]:
    return (
        min(vertex[0] for vertex in vertices),
        min(vertex[1] for vertex in vertices),
        min(vertex[2] for vertex in vertices),
        max(vertex[0] for vertex in vertices),
        max(vertex[1] for vertex in vertices),
        max(vertex[2] for vertex in vertices),
    )


def mesh_bounds(vertices: list[tuple[float, float, float]]) -> str:
    bounds = raw_bounds(vertices)
    return (
        f"x[{bounds[0]:.3g},{bounds[3]:.3g}] "
        f"y[{bounds[1]:.3g},{bounds[4]:.3g}] "
        f"z[{bounds[2]:.3g},{bounds[5]:.3g}]"
    )
