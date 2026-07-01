"""Drift gate: the plugin manifest, the skills on disk, and the README count must agree.

This class of drift bit twice — a pinned version froze plugin updates, and merged-away
skills lingered in the manifest. The gate makes both structurally impossible to ship.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _disk_skills() -> set[str]:
    return {str(p.parent.relative_to(ROOT)) for p in (ROOT / "skills").rglob("SKILL.md")}


def test_manifest_matches_disk() -> None:
    manifest = {
        entry.removeprefix("./")
        for entry in json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))[
            "skills"
        ]
    }
    disk = _disk_skills()
    assert manifest == disk, (
        f"manifest-only: {sorted(manifest - disk)}; disk-only: {sorted(disk - manifest)}"
    )


def test_readme_skill_count_matches_disk() -> None:
    disk = len(_disk_skills())
    counts = {
        int(m)
        for m in re.findall(r"(\d+) skills", (ROOT / "README.md").read_text(encoding="utf-8"))
    }
    assert counts == {disk}, f"README says {sorted(counts)}, disk has {disk}"


def test_marketplace_has_no_version_pin() -> None:
    # A pinned plugin version froze updates once (the "not called natively" postmortem);
    # SHA-versioning requires the plugin entry to carry no version field.
    mp = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    assert all("version" not in p for p in mp["plugins"]), "plugin entry pins a version"
