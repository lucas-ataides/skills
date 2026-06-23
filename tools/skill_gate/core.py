"""Detection and execution for skill-gate.

Stacks are detected from marker files; gates are run as absolute-path argv with
``shell=False`` (no injection surface), and a missing tool is reported as skipped
rather than silently passing.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import yaml

GATES_PATH = Path(__file__).with_name("gates.yaml")


class Status(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass(frozen=True)
class Gate:
    stack: str
    id: str
    category: str
    cmd: tuple[str, ...]
    install: str | None = None


@dataclass(frozen=True)
class GateResult:
    gate: Gate
    status: Status
    returncode: int | None
    detail: str


def load_gates(path: str | Path = GATES_PATH) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "stacks" not in data:
        raise ValueError(f"malformed gates file: {path}")
    return data


def _marker_present(root: Path, marker: str) -> bool:
    if "*" in marker:
        return next(iter(root.rglob(marker)), None) is not None
    return (root / marker).exists()


def detect_stacks(root: str | Path, gates: dict) -> list[str]:
    root = Path(root)
    return [
        name
        for name, spec in gates["stacks"].items()
        if any(_marker_present(root, m) for m in spec.get("markers", []))
    ]


def build_gates(stacks: list[str], gates: dict, category: str | None = None) -> list[Gate]:
    out: list[Gate] = []
    for stack in stacks:
        spec = gates["stacks"].get(stack)
        if not spec:
            continue
        for g in spec["gates"]:
            if category and g["category"] != category:
                continue
            out.append(
                Gate(
                    stack=stack,
                    id=g["id"],
                    category=g["category"],
                    cmd=tuple(g["cmd"]),
                    install=g.get("install"),
                )
            )
    return out


def run_gate(
    gate: Gate, root: str | Path, *, strict: bool = False, timeout: int = 600
) -> GateResult:
    resolved = shutil.which(gate.cmd[0])
    if resolved is None:
        status = Status.FAIL if strict else Status.SKIPPED
        return GateResult(
            gate, status, None, f"{gate.cmd[0]} not installed ({gate.install or 'n/a'})"
        )
    try:
        proc = subprocess.run(  # noqa: S603 - argv list, absolute path, shell=False
            [resolved, *gate.cmd[1:]],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return GateResult(gate, Status.ERROR, None, f"timed out after {timeout}s")
    status = Status.PASS if proc.returncode == 0 else Status.FAIL
    detail = "" if status is Status.PASS else (proc.stdout + proc.stderr).strip()[-2000:]
    return GateResult(gate, status, proc.returncode, detail)


def run_gates(gatelist: list[Gate], root: str | Path, *, strict: bool = False) -> list[GateResult]:
    return [run_gate(g, root, strict=strict) for g in gatelist]
