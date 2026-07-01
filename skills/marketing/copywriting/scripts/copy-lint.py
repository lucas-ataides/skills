#!/usr/bin/env python3
"""Flag the mechanical copy defects the copywriting skill once checked by hand.

The agent writes the copy and judges the message; this script enforces the rules a
checklist cannot enforce reliably -- hype and weasel words, over-long sentences,
likely passive voice, a missing call-to-action, and a per-platform length cap. Every
finding is reported with a line and column so the draft can be fixed precisely.

  copy-lint.py check FILE                 -> lint the file, exit 1 on any finding
  copy-lint.py check                      -> lint copy read from stdin
  copy-lint.py check FILE --platform x    -> also enforce the platform length cap
  copy-lint.py check FILE --cta           -> also require a call-to-action verb
  copy-lint.py --selftest                 -> assert against fixtures, exit 0

Read-only. Exit code is the verdict: 0 clean, 1 findings, 2 bad input.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass

# Hype and weasel words drain a claim of proof; the editing passes delete them by hand,
# this list makes the deletion enforceable. Each entry is matched whole-word, ignoring
# case. Kaizen: a newly discovered offender becomes a new entry plus a selftest line.
BANNED_WORDS: tuple[str, ...] = (
    "very",
    "really",
    "just",
    "actually",
    "basically",
    "simply",
    "literally",
    "quite",
    "world-class",
    "cutting-edge",
    "bleeding-edge",
    "next-level",
    "synergy",
    "synergies",
    "leverage",
    "game-changer",
    "game-changing",
    "revolutionary",
    "seamless",
    "seamlessly",
    "robust",
    "best-in-class",
    "state-of-the-art",
    "innovative",
    "powerful",
    "supercharge",
    "unleash",
    "best-of-breed",
    "turnkey",
    "frictionless",
)

# Call-to-action verbs an effective ask leads with; presence is required under --cta.
CTA_VERBS: tuple[str, ...] = (
    "buy",
    "start",
    "get",
    "try",
    "join",
    "sign",
    "subscribe",
    "book",
    "download",
    "claim",
    "grab",
    "register",
    "shop",
    "order",
    "reserve",
    "request",
    "discover",
    "learn",
    "explore",
    "see",
    "find",
    "build",
    "create",
    "unlock",
    "save",
    "apply",
    "schedule",
    "reply",
    "call",
    "contact",
)

# Per-platform character caps for a single post or caption.
PLATFORM_LIMITS: dict[str, int] = {
    "x": 280,
    "instagram": 2200,
    "linkedin": 3000,
}

# Sentence length above which a line reads as over-long for marketing copy.
MAX_SENTENCE_WORDS = 30

# A "to be" verb followed (within a short window) by a past participle reads as passive.
_BE_VERBS = r"(?:is|are|was|were|be|been|being|am)"
_PASSIVE = re.compile(
    rf"\b{_BE_VERBS}\b(?:\s+\w+){{0,2}}?\s+\b(\w+(?:ed|en|wn|nt))\b",
    re.IGNORECASE,
)
# Common -ed/-en words that are adjectives or nouns, not passive participles.
_PARTICIPLE_STOP = frozenset(
    {
        "red",
        "bed",
        "wed",
        "fed",
        "led",
        "shed",
        "sled",
        "need",
        "indeed",
        "seed",
        "speed",
        "breed",
        "creed",
        "deed",
        "freed",
        "agreed",
        "ten",
        "men",
        "hen",
        "den",
        "pen",
        "then",
        "when",
        "open",
        "even",
        "often",
        "token",
        "golden",
        "happen",
        "garden",
        "dozen",
        "down",
        "own",
        "town",
        "brown",
        "crown",
        "grown",
        "known",
        "shown",
        "thrown",
        "ant",
        "want",
        "front",
        "point",
        "count",
        "amount",
    }
)

_WORD = re.compile(r"\b[\w'-]+\b")
_SENTENCE_SPLIT = re.compile(r"[.!?]+(?:\s+|$)")


@dataclass(frozen=True)
class Finding:
    """A single mechanical defect located at a 1-based line and column."""

    line: int
    col: int
    code: str
    message: str

    def render(self) -> str:
        return f"{self.line}:{self.col}: [{self.code}] {self.message}"


def _banned_pattern() -> re.Pattern[str]:
    """Build one whole-word, case-insensitive alternation over the banned list."""
    alts = sorted(BANNED_WORDS, key=len, reverse=True)
    body = "|".join(re.escape(word) for word in alts)
    return re.compile(rf"(?<![\w-])(?:{body})(?![\w-])", re.IGNORECASE)


_BANNED_RE = _banned_pattern()


def find_banned(text: str) -> list[Finding]:
    """Flag each hype or weasel word, one finding per occurrence."""
    findings: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in _BANNED_RE.finditer(line):
            word = match.group(0)
            findings.append(
                Finding(
                    lineno,
                    match.start() + 1,
                    "hype",
                    f"hype/weasel word '{word}' -- replace with a concrete fact",
                )
            )
    return findings


def _sentences_with_offsets(line: str) -> list[tuple[int, str]]:
    """Split a single line into sentences, each paired with its 0-based start column."""
    out: list[tuple[int, str]] = []
    pos = 0
    for part in _SENTENCE_SPLIT.split(line):
        idx = line.find(part, pos) if part else pos
        if idx < 0:
            idx = pos
        if part.strip():
            out.append((idx, part))
        pos = idx + len(part)
    return out


def find_long_sentences(text: str, limit: int = MAX_SENTENCE_WORDS) -> list[Finding]:
    """Flag any sentence whose word count exceeds the limit."""
    findings: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for col, sentence in _sentences_with_offsets(line):
            count = len(_WORD.findall(sentence))
            if count > limit:
                findings.append(
                    Finding(
                        lineno,
                        col + 1,
                        "long",
                        f"sentence runs {count} words (max {limit}) -- split it",
                    )
                )
    return findings


def find_passive(text: str) -> list[Finding]:
    """Flag likely passive voice via a be-verb + past-participle heuristic."""
    findings: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in _PASSIVE.finditer(line):
            participle = match.group(1).lower()
            if participle in _PARTICIPLE_STOP or len(participle) < 4:
                continue
            findings.append(
                Finding(
                    lineno,
                    match.start() + 1,
                    "passive",
                    f"likely passive voice ('{match.group(0).strip()}') -- prefer active",
                )
            )
    return findings


def find_missing_cta(text: str) -> list[Finding]:
    """Return a single finding when no call-to-action verb appears anywhere."""
    lowered = {w.lower() for w in _WORD.findall(text)}
    if lowered & set(CTA_VERBS):
        return []
    return [
        Finding(
            1,
            1,
            "cta",
            "no call-to-action verb found -- state the action the reader must take",
        )
    ]


def find_over_limit(text: str, platform: str) -> list[Finding]:
    """Return a single finding when the text exceeds the platform character cap."""
    limit = PLATFORM_LIMITS[platform]
    length = len(text)
    if length <= limit:
        return []
    return [
        Finding(
            1,
            1,
            "length",
            f"{length} chars exceeds {platform} limit of {limit} -- cut {length - limit}",
        )
    ]


def lint(text: str, platform: str | None, require_cta: bool) -> list[Finding]:
    """Run every applicable check and return findings sorted by position."""
    findings: list[Finding] = []
    findings.extend(find_banned(text))
    findings.extend(find_long_sentences(text))
    findings.extend(find_passive(text))
    if require_cta:
        findings.extend(find_missing_cta(text))
    if platform is not None:
        findings.extend(find_over_limit(text, platform))
    return sorted(findings, key=lambda f: (f.line, f.col, f.code))


def _read_source(path: str | None) -> str:
    """Read the draft from a file, or from stdin when no path is given."""
    if path is None:
        return sys.stdin.read()
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError as exc:
        raise ValueError(f"file not found: {path}") from exc
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc


def run(path: str | None, platform: str | None, require_cta: bool) -> int:
    """Lint one source and return the exit code -- 0 clean, 1 findings, 2 bad input."""
    try:
        text = _read_source(path)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    findings = lint(text, platform, require_cta)
    if not findings:
        print("copy-lint: clean")
        return 0
    where = path if path is not None else "<stdin>"
    for finding in findings:
        print(f"{where}:{finding.render()}")
    print(f"copy-lint: {len(findings)} finding(s)", file=sys.stderr)
    return 1


def selftest() -> int:
    """Assert clean copy passes, defective copy is flagged, and the list is non-empty."""
    assert BANNED_WORDS, "banned-word list is empty"
    assert CTA_VERBS, "cta-verb list is empty"

    # Clean copy: short active sentences, a concrete fact, and a CTA verb.
    clean = "Cut onboarding to 90 seconds. Start your free trial today.\n"
    assert lint(clean, None, require_cta=True) == [], (
        f"clean copy flagged: {lint(clean, None, True)}"
    )
    assert lint(clean, "x", require_cta=True) == [], "clean copy flagged under platform x"

    # A banned word is caught with the right code.
    hype = "Our world-class platform helps teams.\n"
    codes = {f.code for f in lint(hype, None, require_cta=False)}
    assert "hype" in codes, f"banned word missed: {codes}"

    # An over-long sentence (>30 words) is caught.
    long_sentence = "We " + "ship " * 40 + "fast.\n"
    long_codes = {f.code for f in lint(long_sentence, None, require_cta=False)}
    assert "long" in long_codes, f"long sentence missed: {long_codes}"

    # Passive voice is caught; an -ed adjective is not a false positive on its own.
    passive = "The report was generated by the system.\n"
    assert "passive" in {f.code for f in lint(passive, None, False)}, "passive voice missed"

    # Missing CTA is caught only under --cta.
    no_cta = "A quiet sentence about nothing in particular here.\n"
    assert "cta" in {f.code for f in lint(no_cta, None, require_cta=True)}, "missing CTA missed"
    assert "cta" not in {f.code for f in lint(no_cta, None, require_cta=False)}, (
        "CTA flagged without flag"
    )

    # An over-limit platform-x string is flagged with the length code.
    over = "x" * 300 + "\n"
    assert "length" in {f.code for f in lint(over, "x", False)}, "over-limit string missed"
    assert lint("x" * 100, "x", False) == [], "under-limit string flagged"

    # The combined fixture from the brief: banned word + long sentence + over-limit x.
    combined = "very " + "word " * 40 + "x" * 300 + "\n"
    combined_codes = {f.code for f in lint(combined, "x", require_cta=False)}
    assert {"hype", "long", "length"} <= combined_codes, f"combined fixture: {combined_codes}"

    # Boundary: a missing file yields exit 2, not a crash.
    assert run("/no/such/copy/file.txt", None, False) == 2, "missing file did not exit 2"

    print("copy-lint selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true", help="Run the self-test and exit.")
    sub = parser.add_subparsers(dest="command")
    check = sub.add_parser("check", help="Lint a draft file (or stdin).")
    check.add_argument("file", nargs="?", help="Path to the draft; omit to read stdin.")
    check.add_argument(
        "--platform",
        choices=sorted(PLATFORM_LIMITS),
        help="Enforce the platform's max character count.",
    )
    check.add_argument(
        "--cta",
        action="store_true",
        help="Require a call-to-action verb in the copy.",
    )
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.command != "check":
        parser.error("a command is required: 'check' (or pass --selftest)")
    return run(args.file, args.platform, args.cta)


if __name__ == "__main__":
    raise SystemExit(main())
