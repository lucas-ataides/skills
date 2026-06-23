"""Parsing, types, and orchestration for skill-lint.

The linter turns the ambiguity rules described in prose into deterministic checks
over a parsed ``SkillDoc``. Rule data (patterns, thresholds, messages) lives in
``rules.yaml`` — the single source of truth — so adding a case is a data edit, not
a code change.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

import yaml

RULES_PATH = Path(__file__).with_name("rules.yaml")

_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_ALLOW_RE = re.compile(r"skill-lint:\s*allow\s+(all|[A-Z0-9, ]+)", re.IGNORECASE)
_DISABLE_RE = re.compile(r"skill-lint:\s*disable\s+(all|[A-Z0-9, ]+)", re.IGNORECASE)
_ENABLE_RE = re.compile(r"skill-lint:\s*enable\s+(all|[A-Z0-9, ]+)", re.IGNORECASE)
_SENTENCE_SPLIT = re.compile(r"(?<=[.:;!?])\s+")


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

    @property
    def rank(self) -> int:
        return {"info": 1, "warning": 2, "error": 3}[self.value]


@dataclass(frozen=True)
class Finding:
    rule_id: str
    name: str
    severity: Severity
    path: str
    line: int
    message: str
    hint: str | None = None

    def sort_key(self) -> tuple[str, int, str]:
        return (self.path, self.line, self.rule_id)


@dataclass(frozen=True)
class Line:
    number: int  # 1-indexed
    text: str
    in_code: bool


@dataclass
class SkillDoc:
    path: Path
    folder_name: str
    text: str
    lines: list[Line]
    frontmatter: dict | None
    frontmatter_error: str | None
    fm_end_line: int  # line number of closing '---', or 0 if no frontmatter
    _allow: dict[int, set[str]] = field(default_factory=dict)
    _regions: list[tuple[int, int, set[str]]] = field(default_factory=list)

    @property
    def body_lines(self) -> list[Line]:
        return [ln for ln in self.lines if ln.number > self.fm_end_line]

    @property
    def prose_lines(self) -> list[Line]:
        """Body lines outside fenced code blocks — the target of natural-language rules."""
        return [ln for ln in self.body_lines if not ln.in_code]

    def is_suppressed(self, line: int, rule_id: str) -> bool:
        allowed = self._allow.get(line)
        if allowed is not None and ("all" in allowed or rule_id in allowed):
            return True
        return any(
            start <= line <= end and ("all" in ids or rule_id in ids)
            for start, end, ids in self._regions
        )

    @classmethod
    def load(cls, path: str | Path) -> SkillDoc:
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        raw_lines = text.splitlines()
        frontmatter, fm_error, fm_end = _parse_frontmatter(raw_lines)

        lines: list[Line] = []
        in_code = False
        for idx, raw in enumerate(raw_lines, start=1):
            if _FENCE_RE.match(raw):
                lines.append(Line(idx, raw, True))
                in_code = not in_code
                continue
            lines.append(Line(idx, raw, in_code))

        doc = cls(
            path=path,
            folder_name=path.parent.name,
            text=text,
            lines=lines,
            frontmatter=frontmatter,
            frontmatter_error=fm_error,
            fm_end_line=fm_end,
        )
        _collect_suppressions(doc)
        return doc


def _parse_frontmatter(raw_lines: list[str]) -> tuple[dict | None, str | None, int]:
    if not raw_lines or raw_lines[0].strip() != "---":
        return None, "missing YAML frontmatter (file must start with '---')", 0
    for idx in range(1, len(raw_lines)):
        if raw_lines[idx].strip() == "---":
            block = "\n".join(raw_lines[1:idx])
            try:
                data = yaml.safe_load(block) or {}
            except yaml.YAMLError as exc:
                return None, f"invalid YAML frontmatter: {exc}", idx + 1
            if not isinstance(data, dict):
                return None, "frontmatter is not a mapping", idx + 1
            return data, None, idx + 1
    return None, "frontmatter opened with '---' but never closed", 0


def _split_ids(raw: str) -> set[str]:
    raw = raw.strip()
    if raw.lower() == "all":
        return {"all"}
    return {token.strip().upper() for token in raw.split(",") if token.strip()}


def _collect_suppressions(doc: SkillDoc) -> None:
    open_regions: dict[str, int] = {}  # rule_id (or 'all') -> start line
    for ln in doc.lines:
        if m := _ALLOW_RE.search(ln.text):
            doc._allow.setdefault(ln.number, set()).update(_split_ids(m.group(1)))
        if m := _DISABLE_RE.search(ln.text):
            for rid in _split_ids(m.group(1)):
                open_regions.setdefault(rid, ln.number)
        if m := _ENABLE_RE.search(ln.text):
            for rid in _split_ids(m.group(1)):
                if rid in open_regions:
                    doc._regions.append((open_regions.pop(rid), ln.number, {rid}))
    last = doc.lines[-1].number if doc.lines else 0
    for rid, start in open_regions.items():
        doc._regions.append((start, last, {rid}))


def sentences(text: str) -> list[str]:
    return [s for s in _SENTENCE_SPLIT.split(text.strip()) if s]


def load_rules(path: str | Path = RULES_PATH) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "rules" not in data or "settings" not in data:
        raise ValueError(f"malformed rules file: {path}")
    data["_by_id"] = {r["id"]: r for r in data["rules"]}
    return data
