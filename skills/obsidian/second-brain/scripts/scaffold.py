#!/usr/bin/env python3
"""Scaffold a complete, spec-compliant second-brain vault — folders, control files, _tools/.

The compiler authors canonical notes; this script lays the deterministic skeleton they
land in, so every vault has the same shape, the same resumable state files, and its own
copy of the validators (a vault re-validates itself with no skill installed). Idempotent:
an existing file is never overwritten, so re-running never clobbers notes or edits.

    scaffold.py <vault-root>     create or complete the canonical vault, print what it did
    scaffold.py --selftest

Structure built: People/ Companies/ Projects/ Products/ Topics/ Decisions/ Commitments/
Procedures/ Preferences/ "Context Packs"/ Sources/ Maps/ Reports/ _tools/ + the six root
control files (README, SOURCE-MANIFEST, VALIDATION-REPORT, COMPLETION-AUDIT, INGESTION-LOG,
state.json).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from datetime import date
from pathlib import Path

FOLDERS = [
    "People",
    "Companies",
    "Projects",
    "Products",
    "Topics",
    "Decisions",
    "Commitments",
    "Procedures",
    "Preferences",
    "Context Packs",
    "Sources",
    "Maps",
    "Reports",
    "_tools",
]

VALIDATORS = [
    "validate-slugs.py",
    "validate-sources.py",
    "validate-wikilinks.py",
    "scan-secrets.py",
    "generate-manifest.py",
    "validate-artifacts.sh",
]


def _state(vault_abs: str, today: str) -> str:
    return (
        json.dumps(
            {
                "output_path": vault_abs,
                "current_phase": "scaffolded",
                "completed_phases": ["scaffold"],
                "sources_discovered": [],
                "sources_ingested": [],
                "connector_status": {},
                "batches_completed": 0,
                "canonical_notes_created": 0,
                "validation_status": "pending",
                "next_actions": ["orient: inventory sources, write Reports/ORIENTATION-REPORT.md"],
                "blockers": [],
                "scaffolded": today,
            },
            indent=2,
        )
        + "\n"
    )


def _readme(today: str) -> str:
    return f"""# Second brain

A durable, source-backed memory layer for agents and their human. Plain Markdown that
opens in Obsidian as an ordinary vault. Built {today}; maintained by the `second-brain`
skill.

## How it is organized

Canonical knowledge — one entity or fact-cluster per note, every claim source-backed:

| Folder | Holds |
| --- | --- |
| `People/` `Companies/` `Projects/` `Products/` `Topics/` `Decisions/` | declarative memory — who/what/why |
| `Procedures/` `Preferences/` `Commitments/` | procedural memory — how things are done, what is preferred, what is owed |
| `Sources/` | one note per ingested source — the provenance layer every claim traces back to |
| `Context Packs/` | pre-assembled briefings an agent loads at the start of a recurring task |
| `Maps/` | Maps of Content — index notes that keep the graph navigable |
| `Reports/` | the compiler's own output (orientation and per-phase reports) |
| `_tools/` | a copy of the validators, so this vault re-checks itself |

Root control files — the resumable state and audit trail: `SOURCE-MANIFEST.md`,
`VALIDATION-REPORT.md`, `COMPLETION-AUDIT.md`, `INGESTION-LOG.md`, `state.json`.

## How an agent should use it

1. **Retrieve cheapest-first.** Load a `Context Packs/` note for a recurring task; else
   search by entity, tag, or text; else follow a note's wikilinks and `## Sources`.
2. **Trust only what is sourced.** Every canonical claim links to a `Sources/` note or a
   `manifest:<id>` entry. A claim with no source is a defect, not knowledge.
3. **Never invent.** A gap is written as a gap. Single-source claims are flagged.
4. **Act externally only with approval.** Check `SOURCE-MANIFEST.md` for connector status;
   never send, write, or mutate anything outside this vault without explicit approval.

## Re-validate

```sh
python _tools/validate-wikilinks.py --vault .
python _tools/validate-slugs.py --vault .
python _tools/scan-secrets.py --vault .
python _tools/validate-sources.py --vault .
bash _tools/validate-artifacts.sh --vault .
```
"""


SOURCE_MANIFEST = """# Source manifest

Every source and every connector used to build this vault. A connector is ingested only
after its account/workspace is verified and recorded here.

## Connectors

| Connector | Account / user | Workspace / org | Verification method | Timestamp | Read/write | Approved |
| --- | --- | --- | --- | --- | --- | --- |
| _none yet_ | | | | | | |

## Sources

| Source id | Origin | Ingested | Sensitivity | Notes derived |
| --- | --- | --- | --- | --- |
| _none yet_ | | | | |
"""

VALIDATION_REPORT = """# Validation report

The deterministic gates run against this vault, with the exact command and its result.

| Validator | Command | Result | Remaining issues |
| --- | --- | --- | --- |
| wikilinks | `python _tools/validate-wikilinks.py --vault .` | not yet run | |
| slugs | `python _tools/validate-slugs.py --vault .` | not yet run | |
| secrets | `python _tools/scan-secrets.py --vault .` | not yet run | |
| sources | `python _tools/validate-sources.py --vault .` | not yet run | |
| artifacts | `bash _tools/validate-artifacts.sh --vault .` | not yet run | |
| manifest | `python _tools/generate-manifest.py --vault . --verify` | not yet run | |
"""

COMPLETION_AUDIT = """# Completion audit

Maps each hard gate to its evidence. The vault is complete only when every row passes.

| Requirement | Status | Evidence | Notes |
| --- | --- | --- | --- |
| 0 placeholder source references | pending | VALIDATION-REPORT.md | |
| 0 broken internal wikilinks | pending | VALIDATION-REPORT.md | |
| 0 empty slugs / invalid paths | pending | VALIDATION-REPORT.md | |
| 0 copied secrets or credentials | pending | VALIDATION-REPORT.md | |
| every canonical note has provenance | pending | VALIDATION-REPORT.md | |
| every connector documented in SOURCE-MANIFEST.md | pending | SOURCE-MANIFEST.md | |
| README explains organization + agent use | pass | README.md | written at scaffold |
| state.json + INGESTION-LOG.md current | pending | state.json | |
| opens as a normal Obsidian vault | pass | folder layout | written at scaffold |
"""

INGESTION_LOG = """# Ingestion log

One entry per batch: what was read, what was authored, and the resulting state. The job
resumes from this file plus `state.json` — read both before doing new work.

## scaffold
- Vault skeleton created. No sources ingested yet.
"""


def _write_if_absent(path: Path, content: str) -> bool:
    """Create the file with content only when it does not exist. Returns True if written."""
    if path.exists():
        return False
    tmp: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", dir=str(path.parent), delete=False, encoding="utf-8"
        ) as fd:
            tmp = Path(fd.name)
            fd.write(content)
        tmp.replace(path)
    except BaseException:
        if tmp is not None:
            tmp.unlink(missing_ok=True)
        raise
    return True


def scaffold(root: Path) -> list[str]:
    """Build the canonical vault under ``root``. Idempotent; returns a log of actions."""
    root.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    log: list[str] = []

    for folder in FOLDERS:
        (root / folder).mkdir(parents=True, exist_ok=True)
    log.append(f"folders: {len(FOLDERS)} ensured")

    files = {
        "README.md": _readme(today),
        "SOURCE-MANIFEST.md": SOURCE_MANIFEST,
        "VALIDATION-REPORT.md": VALIDATION_REPORT,
        "COMPLETION-AUDIT.md": COMPLETION_AUDIT,
        "INGESTION-LOG.md": INGESTION_LOG,
        "state.json": _state(str(root.resolve()), today),
    }
    written = [name for name, content in files.items() if _write_if_absent(root / name, content)]
    log.append(f"control files: {len(written)} written, {len(files) - len(written)} kept")

    here = Path(__file__).resolve().parent
    tools = root / "_tools"
    copied = 0
    for name in VALIDATORS:
        src, dst = here / name, tools / name
        if src.is_file() and not dst.exists():
            shutil.copy2(src, dst)
            copied += 1
    log.append(f"_tools: {copied} validators copied, {len(VALIDATORS) - copied} kept/absent")
    return log


def selftest() -> int:
    with tempfile.TemporaryDirectory(prefix="scaffold-selftest.") as tmp:
        root = Path(tmp) / "vault"
        scaffold(root)

        for folder in FOLDERS:
            assert (root / folder).is_dir(), f"missing folder {folder}"
        for name in (
            "README.md",
            "SOURCE-MANIFEST.md",
            "VALIDATION-REPORT.md",
            "COMPLETION-AUDIT.md",
            "INGESTION-LOG.md",
            "state.json",
        ):
            assert (root / name).is_file(), f"missing control file {name}"

        state = json.loads((root / "state.json").read_text())
        for key in (
            "output_path",
            "current_phase",
            "completed_phases",
            "sources_discovered",
            "sources_ingested",
            "connector_status",
            "batches_completed",
            "canonical_notes_created",
            "validation_status",
            "next_actions",
            "blockers",
        ):
            assert key in state, f"state.json missing key {key}"

        # the copied validators must be present and run standalone (portability)
        assert (root / "_tools" / "validate-slugs.py").is_file(), "validators not copied"

        # idempotency: a user edit survives a re-scaffold
        (root / "README.md").write_text("EDITED\n", encoding="utf-8")
        scaffold(root)
        assert (root / "README.md").read_text() == "EDITED\n", "re-scaffold clobbered a file"

        # the scaffolded vault passes the artifact gate
        artifacts = Path(__file__).resolve().parent / "validate-artifacts.sh"
        result = subprocess.run(
            ["bash", str(artifacts), "--vault", str(root)], capture_output=True, text=True
        )
        assert result.returncode == 0, f"artifact gate failed:\n{result.stdout}{result.stderr}"

    print("scaffold selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("vault", nargs="?", help="Vault root to create or complete.")
    parser.add_argument("--selftest", action="store_true", help="Run the self-test and exit.")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.vault:
        parser.error("a vault root is required unless --selftest is given")
    for line in scaffold(Path(args.vault)):
        print(f"  {line}")
    print(f"vault ready: {Path(args.vault).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
