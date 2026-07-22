#!/usr/bin/env python3
"""Deterministic Simplified Technical English (ASD-STE100) gate for Markdown prose.

The agent writes the documentation; this script holds it to the mechanical STE rules, so
readability is a verdict, not an opinion. Checked per prose sentence (code fences, inline
code, frontmatter, headings, and tables are skipped):

  STE01  sentence longer than 25 words (procedures aim for 20; 25 is the hard cap)
  STE02  paragraph longer than 6 sentences
  STE03  passive voice (a be-verb plus a past participle)
  STE04  perfect tense (has/have/had plus a past participle) — STE uses simple tenses
  STE05  unapproved word or phrase (the curated substitution list below)
  STE06  sentence opens with a gerund — start an instruction with the imperative verb

The word list is this skill's own, in the spirit of the STE dictionary (one word, one
meaning, the short common verb wins); the judgment rules that no script can hold live in
references/simplified-technical-english.md.

    ste-lint.py check <file.md> [file.md ...]
    ste-lint.py --selftest
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MAX_SENTENCE_WORDS = 25
MAX_PARAGRAPH_SENTENCES = 6

# Unapproved -> approved. Phrases first (matched before single words), all case-insensitive.
UNAPPROVED: dict[str, str] = {
    "in order to": "to",
    "prior to": "before",
    "subsequent to": "after",
    "in the event that": "if",
    "with the exception of": "except",
    "a number of": "some",
    "at this point in time": "now",
    "carry out": "do",
    "make sure": "ensure that the condition is stated and checked",
    "utilize": "use",
    "utilization": "use",
    "commence": "start",
    "terminate": "stop",
    "perform": "do",
    "accomplish": "do",
    "demonstrate": "show",
    "indicate": "show",
    "leverage": "use",
    "facilitate": "help",
    "additionally": "also",
    "consequently": "so",
    "approximately": "about",
    "sufficient": "enough",
    "modification": "change",
    "functionality": "function",
    "subsequently": "then",
    "endeavor": "try",
    "ascertain": "find out",
    "regarding": "about",
    "concerning": "about",
}

_BE = r"(?:am|is|are|was|were|be|been|being)"
_HAVE = r"(?:has|have|had)"
_IRREGULAR = (
    "begun|broken|brought|built|bought|caught|chosen|done|drawn|driven|eaten|fallen|felt|"
    "flown|found|frozen|given|gone|grown|heard|held|hidden|hit|hurt|kept|known|laid|led|"
    "left|lost|made|meant|met|paid|put|read|risen|run|said|seen|sent|set|shown|sold|spent|"
    "spoken|stolen|stood|taught|thought|thrown|told|understood|won|worn|written"
)
_PARTICIPLE = rf"(?:\w{{3,}}ed|{_IRREGULAR})"
_PASSIVE = re.compile(rf"\b{_BE}\s+(?:\w+ly\s+)?{_PARTICIPLE}\b", re.IGNORECASE)
_PERFECT = re.compile(rf"\b{_HAVE}\s+(?:\w+ly\s+)?{_PARTICIPLE}\b", re.IGNORECASE)

# Sentence-initial -ing words that are not gerund openers.
_ING_OK = {"during", "nothing", "something", "anything", "everything", "string", "sterling"}

# One precompiled alternation for the whole word list — longest first, so a phrase wins
# over any word it contains. Compiled once from the constant dict above; no per-sentence
# pattern construction.
_UNAPPROVED_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in sorted(UNAPPROVED, key=len, reverse=True)) + r")\b"
)

_ABBREV = re.compile(r"\b(?:e\.g|i\.e|etc|vs|cf)\.$", re.IGNORECASE)
_INLINE_CODE = re.compile(r"`[^`]*`")
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def prose_lines(markdown: str) -> list[tuple[int, str]]:
    """Extract checkable prose lines: skip fences, frontmatter, headings, tables, comments."""
    out: list[tuple[int, str]] = []
    in_fence = False
    in_front = False
    for i, raw in enumerate(markdown.splitlines(), 1):
        line = raw.strip()
        if i == 1 and line == "---":
            in_front = True
            continue
        if in_front:
            if line == "---":
                in_front = False
            continue
        if line.startswith("```") or line.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or not line:
            out.append((i, ""))  # keep blanks: they delimit paragraphs
            continue
        if line.startswith(("#", "|", "<!--", "[//]")):
            out.append((i, ""))
            continue
        line = re.sub(r"^(?:[-*+]|\d+\.)\s+", "", line)  # list markers
        line = line.lstrip("> ")
        line = _LINK.sub(r"\1", line)  # keep link text, drop the URL
        line = _INLINE_CODE.sub("code", line)  # a code span counts as one word
        out.append((i, line))
    return out


def sentences(text: str) -> list[str]:
    """Split prose into sentences, tolerating common abbreviations."""
    parts: list[str] = []
    buf = ""
    for chunk in re.split(r"(?<=[.!?])\s+", text):
        buf = f"{buf} {chunk}".strip() if buf else chunk
        if _ABBREV.search(buf):
            continue
        if buf:
            parts.append(buf)
            buf = ""
    if buf:
        parts.append(buf)
    return [p for p in parts if re.search(r"\w", p)]


def check_text(markdown: str) -> list[tuple[int, str, str]]:
    """Return (line, rule, message) violations for one document."""
    violations: list[tuple[int, str, str]] = []
    lines = prose_lines(markdown)

    # Paragraphs: consecutive non-blank prose lines.
    para: list[tuple[int, str]] = []

    def flush_paragraph() -> None:
        if not para:
            return
        text = " ".join(t for _, t in para)
        count = len(sentences(text))
        if count > MAX_PARAGRAPH_SENTENCES:
            violations.append(
                (
                    para[0][0],
                    "STE02",
                    f"paragraph has {count} sentences (max {MAX_PARAGRAPH_SENTENCES})",
                )
            )
        para.clear()

    for line_no, text in lines:
        if not text:
            flush_paragraph()
            continue
        para.append((line_no, text))
        for sent in sentences(text):
            words = re.findall(r"[\w'-]+", sent)
            if len(words) > MAX_SENTENCE_WORDS:
                violations.append(
                    (
                        line_no,
                        "STE01",
                        f"sentence has {len(words)} words (max {MAX_SENTENCE_WORDS})",
                    )
                )
            if _PASSIVE.search(sent):
                violations.append(
                    (line_no, "STE03", f"passive voice: {_PASSIVE.search(sent).group(0)!r}")
                )
            if _PERFECT.search(sent):
                violations.append(
                    (line_no, "STE04", f"perfect tense: {_PERFECT.search(sent).group(0)!r}")
                )
            lowered = sent.lower()
            for match in _UNAPPROVED_RE.finditer(lowered):
                bad = match.group(1)
                violations.append(
                    (line_no, "STE05", f"unapproved {bad!r} — use {UNAPPROVED[bad]!r}")
                )
            first = words[0].lower() if words else ""
            if first.endswith("ing") and len(first) > 4 and first not in _ING_OK:
                violations.append(
                    (
                        line_no,
                        "STE06",
                        f"sentence opens with the gerund {first!r} — start with the imperative verb",
                    )
                )
    flush_paragraph()
    return violations


def cmd_check(paths: list[str]) -> int:
    any_violation = False
    for p in paths:
        path = Path(p)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"ste-lint: cannot read {p!r}: {exc}", file=sys.stderr)
            return 2
        for line, rule, msg in check_text(text):
            print(f"{p}:{line}: [{rule}] {msg}")
            any_violation = True
    if any_violation:
        return 1
    print(f"ste-lint: {len(paths)} file(s) clean")
    return 0


def selftest() -> int:
    v = check_text("The tool creates the file.\n")
    assert v == [], f"clean sentence flagged: {v}"

    long = "word " * 26
    assert any(r == "STE01" for _, r, _ in check_text(long)), "26-word sentence not flagged"
    ok25 = "word " * 25
    assert not check_text(ok25.strip() + "."), "25-word sentence wrongly flagged"

    seven = " ".join(["This is one."] * 7)
    assert any(r == "STE02" for _, r, _ in check_text(seven)), "7-sentence paragraph not flagged"

    assert any(r == "STE03" for _, r, _ in check_text("The file is created by the tool.")), (
        "passive missed"
    )
    assert any(r == "STE04" for _, r, _ in check_text("The team has installed the pump.")), (
        "perfect missed"
    )
    got = check_text("Utilize the tool in order to start.")
    assert sum(1 for _, r, _ in got if r == "STE05") == 2, f"unapproved count wrong: {got}"
    assert any(r == "STE06" for _, r, _ in check_text("Removing the cover, turn the valve.")), (
        "gerund opener missed"
    )
    assert not check_text("During the test, turn the valve."), "'During' wrongly flagged as gerund"

    fenced = "```\nutilize whatever has been done\n```\nUse the tool.\n"
    assert check_text(fenced) == [], "code fence not skipped"
    inline = "Run `utilize_all --has-been` to start the test.\n"
    assert check_text(inline) == [], "inline code not skipped"
    front = "---\ndescription: this has been utilized in order to work\n---\n\nUse the tool.\n"
    assert check_text(front) == [], "frontmatter not skipped"
    assert check_text("| has been | utilized |\n") == [], "table row not skipped"

    print("ste-lint selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ste-lint", description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true", help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="cmd")
    cp = sub.add_parser("check", help="Check Markdown files against the mechanical STE rules.")
    cp.add_argument("files", nargs="+")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.cmd == "check":
        return cmd_check(args.files)
    parser.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
