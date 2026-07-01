#!/usr/bin/env python3
"""Generate or verify SOURCE-MANIFEST.md from the vault's state.json connector record.

The manifest is the connector gate's ledger: before any external source is
ingested, its account/workspace/verification must be recorded. This script has
two modes:

  --verify   Check that the existing SOURCE-MANIFEST.md documents every connector
             listed in state.json and that each connector entry carries the
             required fields (account, workspace, verified, timestamp,
             capability, approval). Exit 1 on any gap. Read-only.

  --generate Emit a SOURCE-MANIFEST.md skeleton from state.json's connector
             records to a target path via an atomic write, so a half-written
             manifest is never observed. Existing fields are preserved by the
             author; this only scaffolds missing connector blocks.

  generate-manifest.py --vault PATH --verify
  generate-manifest.py --vault PATH --generate --out PATH
  generate-manifest.py --selftest

state.json shape (relevant slice):
  {"connector_status": {"<name>": {"account": "...", "workspace": "...",
   "verified": true, "timestamp": "...", "capability": "...",
   "approval": "..."}}}
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


def _atomic_write(path: str, data: str) -> None:
    """Write atomically (temp + rename); stdlib-only so this runs from a vault's _tools/."""
    import contextlib
    import os
    import tempfile

    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


_REQUIRED_FIELDS = ("account", "workspace", "verified", "timestamp", "capability", "approval")


def _load_connectors(state_path: Path) -> dict[str, dict]:
    """Return the connector_status mapping from state.json, or raise on bad input."""
    if not state_path.is_file():
        raise FileNotFoundError(f"state.json not found: {state_path}")
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"state.json is not valid JSON: {exc}") from exc
    connectors = data.get("connector_status", {})
    if not isinstance(connectors, dict):
        raise ValueError("connector_status must be an object mapping name -> fields")
    return connectors


def verify(connectors: dict[str, dict], manifest_text: str) -> list[str]:
    """Return a list of gaps: connectors absent from the manifest or missing fields."""
    gaps: list[str] = []
    for name, fields in sorted(connectors.items()):
        if name not in manifest_text:
            gaps.append(f"connector not documented in manifest: {name}")
            continue
        if not isinstance(fields, dict):
            gaps.append(f"connector {name}: state entry is not an object")
            continue
        for field in _REQUIRED_FIELDS:
            value = fields.get(field)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                gaps.append(f"connector {name}: missing required field '{field}'")
        if fields.get("verified") is not True:
            gaps.append(f"connector {name}: 'verified' is not true (account unconfirmed)")
        approval = fields.get("approval")
        if isinstance(approval, str) and approval.strip().lower() in ("", "pending", "none"):
            gaps.append(f"connector {name}: ingestion not approved (approval='{approval}')")
    return gaps


def render_manifest(connectors: dict[str, dict]) -> str:
    """Render a deterministic SOURCE-MANIFEST.md from connector records."""
    lines = [
        "# Source manifest",
        "",
        "Every external connector used to compile this vault is recorded below.",
        "A connector with the wrong account is BLOCKED and never ingested.",
        "",
    ]
    if not connectors:
        lines.append("_No connectors recorded yet._")
        lines.append("")
        return "\n".join(lines) + "\n"
    for name, fields in sorted(connectors.items()):
        fields = fields if isinstance(fields, dict) else {}
        lines.append(f"## {name}")
        lines.append("")
        lines.append(f"- id: {name}")
        for field in _REQUIRED_FIELDS:
            lines.append(f"- {field}: {fields.get(field, 'TODO')}")
        lines.append("")
    return "\n".join(lines) + "\n"


def run_verify(vault: Path) -> int:
    connectors = _load_connectors(vault / "state.json")
    manifest_path = vault / "SOURCE-MANIFEST.md"
    if not manifest_path.is_file():
        print(f"error: SOURCE-MANIFEST.md not found in {vault}", file=sys.stderr)
        return 1
    gaps = verify(connectors, manifest_path.read_text(encoding="utf-8"))
    print(f"# Manifest verification: {vault}\n")
    print(f"connectors: {len(connectors)}, gaps: {len(gaps)}\n")
    for gap in gaps:
        print(gap)
    return 1 if gaps else 0


def run_generate(vault: Path, out: Path) -> int:
    connectors = _load_connectors(vault / "state.json")
    _atomic_write(out, render_manifest(connectors))
    print(f"wrote manifest skeleton: {out} ({len(connectors)} connector(s))")
    return 0


def selftest() -> int:
    complete = {
        "gmail": {
            "account": "a@b.com",
            "workspace": "personal",
            "verified": True,
            "timestamp": "2026-06-22T10:00:00Z",
            "capability": "read",
            "approval": "user-approved",
        }
    }
    incomplete = {
        "slack": {
            "account": "",
            "workspace": "acme",
            "verified": False,
            "timestamp": "2026-06-22T10:00:00Z",
            "capability": "read",
            "approval": "pending",
        }
    }

    # A manifest naming the connector + complete fields verifies clean.
    manifest = render_manifest(complete)
    assert "gmail" in manifest, "render dropped the connector name"
    assert verify(complete, manifest) == [], (
        f"clean connector flagged: {verify(complete, manifest)}"
    )

    # Missing account, verified=false, and approval=pending each raise a gap.
    gaps = verify(incomplete, render_manifest(incomplete))
    assert any("missing required field 'account'" in g for g in gaps), gaps
    assert any("'verified' is not true" in g for g in gaps), gaps
    assert any("not approved" in g for g in gaps), gaps

    # A connector absent from the manifest text is a gap even if its fields are ok.
    assert any("not documented" in g for g in verify(complete, "# empty manifest\n")), (
        "absence missed"
    )

    # End-to-end generate then verify over a temp vault.
    with tempfile.TemporaryDirectory(prefix="manifest-selftest.") as tmp:
        vault = Path(tmp)
        (vault / "state.json").write_text(
            json.dumps({"connector_status": complete}), encoding="utf-8"
        )
        out = vault / "SOURCE-MANIFEST.md"
        assert run_generate(vault, out) == 0, "generate failed"
        assert out.is_file(), "manifest not written"
        assert run_verify(vault) == 0, "generated manifest failed its own verify"

        # Malformed state.json is rejected at the boundary.
        (vault / "state.json").write_text("{not json", encoding="utf-8")
        try:
            _load_connectors(vault / "state.json")
        except ValueError:
            pass
        else:  # pragma: no cover - selftest guard
            raise AssertionError("malformed state.json accepted")

    print("generate-manifest selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--vault", help="Path to the Obsidian vault root.")
    parser.add_argument("--verify", action="store_true", help="Verify the existing manifest.")
    parser.add_argument("--generate", action="store_true", help="Write a manifest skeleton.")
    parser.add_argument(
        "--out", help="Output path for --generate (default: <vault>/SOURCE-MANIFEST.md)."
    )
    parser.add_argument("--selftest", action="store_true", help="Run the self-test and exit.")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.vault:
        parser.error("--vault is required unless --selftest is given")
    vault = Path(args.vault)
    if not vault.is_dir():
        print(f"error: vault is not a directory: {args.vault}", file=sys.stderr)
        return 2
    if args.generate:
        out = Path(args.out) if args.out else vault / "SOURCE-MANIFEST.md"
        return run_generate(vault, out)
    if args.verify:
        return run_verify(vault)
    parser.error("choose --verify or --generate")
    return 2  # pragma: no cover - argparse exits first


if __name__ == "__main__":
    raise SystemExit(main())
