#!/usr/bin/env python3
"""Build a deterministic daily content radar from browser-observed trend signals.

The browser reads the trend surfaces (X, Instagram, TikTok) and the agent records what it
saw into a captures JSON — that observation is judgment. This script does the rest
mechanically: it scores every captured post by the save-and-share signal (which predicts
reach far better than likes), ranks them, groups the trends by platform, and renders an
identical-shaped Markdown report every run. So a daily routine produces a stable artifact,
not a differently-organized blob each morning.

    trends.py report <captures.json>     render the ranked daily radar (Markdown)
    trends.py --selftest

Captures JSON:
    {"niche": "...", "captured_at": "2026-06-24",
     "trends": [{"platform": "x|instagram|tiktok", "topic": "...", "why_now": "...",
                 "angle": "..."}],
     "posts":  [{"platform": "...", "surface": "...", "format": "...", "hook": "...",
                 "structure": "...", "likes": 0, "reposts": 0, "comments": 0,
                 "saves": 0, "shares": 0}]}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PLATFORMS = ("x", "instagram", "tiktok")

# Saves, shares, and reposts distribute a post; likes are vanity. Ranking is lexicographic
# on that order — the distribution signal first, conversation (comments) next, likes last —
# so a high-like low-save post can never outrank a bookmarkable one however large the raw
# like count. This makes mechanical the judgment the viral-research reference states in prose.
DISTRIBUTION = ("saves", "shares", "reposts")


def _count(post: dict, field: str) -> int:
    value = post.get(field, 0)
    return value if isinstance(value, int) and value >= 0 else 0


def engagement_score(post: dict) -> int:
    """The distribution signal: saves + shares + reposts. The reach predictor; likes excluded."""
    return sum(_count(post, field) for field in DISTRIBUTION)


def rank_posts(posts: list[dict]) -> list[dict]:
    """Sort by distribution, then comments, then likes, then hook — stable and like-proof."""
    return sorted(
        posts,
        key=lambda p: (
            -engagement_score(p),
            -_count(p, "comments"),
            -_count(p, "likes"),
            str(p.get("hook", "")),
        ),
    )


def group_trends(trends: list[dict]) -> dict[str, list[dict]]:
    """Group trend rows by platform, in the canonical platform order."""
    grouped: dict[str, list[dict]] = {p: [] for p in PLATFORMS}
    for t in trends:
        grouped.setdefault(t.get("platform", "other"), []).append(t)
    return grouped


def render_report(captures: dict) -> str:
    """Render the daily radar deterministically: trends by platform, then ranked posts."""
    niche = captures.get("niche", "—")
    date = captures.get("captured_at", "—")
    trends = group_trends(captures.get("trends") or [])
    posts = rank_posts(captures.get("posts") or [])

    lines = [f"# Daily content radar — {niche} — {date}", ""]

    lines.append("## Trends by platform")
    for platform in PLATFORMS:
        lines.append(f"### {platform.title()}")
        rows = trends.get(platform) or []
        if not rows:
            lines.append("- _nothing captured_")
        for t in rows:
            why = t.get("why_now", "—")
            angle = t.get("angle", "—")
            lines.append(f"- **{t.get('topic', '—')}** — why now: {why}; angle: {angle}")
        lines.append("")

    lines.append("## Top post patterns (ranked by save/share signal)")
    if not posts:
        lines.append("- _nothing captured_")
    for i, p in enumerate(posts, 1):
        sig = (
            f"saves {_count(p, 'saves')}, shares {_count(p, 'shares')}, "
            f"reposts {_count(p, 'reposts')}, comments {_count(p, 'comments')}, "
            f"likes {_count(p, 'likes')}"
        )
        lines.append(
            f"{i}. [{p.get('platform', '?')}/{p.get('format', '?')}] "
            f'"{p.get("hook", "—")}" — distribution {engagement_score(p)} ({sig})'
        )
        if p.get("structure"):
            lines.append(f"   structure: {p['structure']}")
    lines.append("")

    lines.append("## What to post today")
    lines.append(
        "Adapt the top-ranked patterns into the niche per the viral-research filters "
        "(earned authority, buyer pain, product adjacency): keep the skeleton, replace every "
        "organ, draft a primary and an alternate hook, then gate the drafts with "
        "`content-lint.py` before anything is posted. Nothing here is posted automatically."
    )
    return "\n".join(lines) + "\n"


def cmd_report(path: str) -> int:
    try:
        captures = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"trends: cannot read captures {path!r}: {exc}", file=sys.stderr)
        return 2
    if not isinstance(captures, dict):
        print("trends: captures must be a JSON object", file=sys.stderr)
        return 2
    print(render_report(captures), end="")
    return 0


def selftest() -> int:
    high = {"hook": "save this", "saves": 10, "likes": 1, "platform": "x", "format": "thread"}
    low = {"hook": "nice", "saves": 0, "likes": 5000, "platform": "x", "format": "post"}
    assert engagement_score(high) == 10, engagement_score(high)
    assert engagement_score(low) == 0
    # the bookmarkable post outranks the high-like one despite 500x fewer likes
    ranked = rank_posts([low, high])
    assert ranked[0]["hook"] == "save this", "save/share signal did not win"

    # missing/garbage fields are treated as zero, not a crash
    assert engagement_score({"saves": "x", "likes": -3}) == 0

    grouped = group_trends([{"platform": "tiktok", "topic": "t"}, {"platform": "x", "topic": "x"}])
    assert list(grouped) == ["x", "instagram", "tiktok"] and grouped["tiktok"][0]["topic"] == "t"

    report = render_report({
        "niche": "devtools", "captured_at": "2026-06-24",
        "trends": [{"platform": "tiktok", "topic": "AI agents", "why_now": "launch", "angle": "fit"}],
        "posts": [high, low],
    })
    assert "Daily content radar — devtools" in report
    assert "### Tiktok" in report and "AI agents" in report
    assert report.index('"save this"') < report.index('"nice"'), "report not ranked"
    assert "What to post today" in report and "content-lint.py" in report

    # empty captures still render every section, no crash
    empty = render_report({})
    assert "### X" in empty and "_nothing captured_" in empty

    print("trends selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="trends", description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true", help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="cmd")
    rp = sub.add_parser("report", help="Render the ranked daily radar from a captures JSON.")
    rp.add_argument("captures")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.cmd == "report":
        return cmd_report(args.captures)
    parser.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
