#!/usr/bin/env python3
"""Scan a vault for copied credentials so they can be redacted before the vault ships.

A memory vault is compiled from chats, emails, and connector output -- exactly the
places a live secret leaks from. This scanner flags credential-shaped strings and
reports their location with a masked preview; it never prints a full secret value,
so the report itself is safe to read and store.

Detected classes: cloud API keys, generic API/secret keys, bearer/OAuth tokens,
private keys (RSA/EC/OpenSSH/PGP), SSH public-ish key material, JWTs, database
connection URLs with inline passwords, webhook/signing secrets, session cookies,
and credential-bearing env-var assignments.

  scan-secrets.py --vault PATH   -> scan the vault, exit 1 if any secret found
  scan-secrets.py --selftest     -> assert against fixtures, exit 0

Read-only. The masked output omits the secret body. Exit code is the verdict.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
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


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]


# Each pattern targets a credential SHAPE. The goal is recall for a redaction
# pass, not zero false positives -- a flagged non-secret costs a glance.
_RULES: tuple[Rule, ...] = (
    Rule("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA|AGPA|AIDA|AROA)[0-9A-Z]{16}\b")),
    Rule(
        "aws-secret-access-key",
        re.compile(r"(?i)aws.{0,20}(?:secret|sk).{0,5}[:=]\s*['\"]?[A-Za-z0-9/+=]{40}\b"),
    ),
    Rule("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    Rule("slack-token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    Rule("github-token", re.compile(r"\bgh[pousr]_[0-9A-Za-z]{36,}\b")),
    Rule("stripe-key", re.compile(r"\b(?:sk|rk|pk)_(?:live|test)_[0-9A-Za-z]{16,}\b")),
    Rule("openai-key", re.compile(r"\bsk-(?:proj-)?[0-9A-Za-z_\-]{20,}\b")),
    Rule(
        "private-key-block",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    ),
    Rule("ssh-public-key", re.compile(r"\bssh-(?:rsa|ed25519|dss)\s+[A-Za-z0-9+/]{40,}={0,3}")),
    Rule("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\b")),
    Rule("bearer-token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{16,}\b")),
    Rule(
        "authorization-header",
        re.compile(r"(?i)\bauthorization\s*[:=]\s*['\"]?(?:basic|token)\s+[A-Za-z0-9+/=._\-]{12,}"),
    ),
    Rule(
        "db-url-with-password",
        re.compile(
            r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp)://[^\s:@/]+:[^\s:@/]+@[^\s/]+"
        ),
    ),
    Rule(
        "webhook-signing-secret",
        re.compile(
            r"(?i)\b(?:whsec|signing[_-]?secret|webhook[_-]?secret)\b.{0,5}[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"
        ),
    ),
    Rule(
        "session-cookie",
        re.compile(
            r"(?i)\b(?:session|sid|connect\.sid|sessionid|csrftoken)\b\s*=\s*[A-Za-z0-9%._\-]{16,}"
        ),
    ),
    Rule(
        "password-assignment",
        re.compile(
            r"(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?token|client[_-]?secret)\b\s*[:=]\s*['\"][^'\"]{6,}['\"]"
        ),
    ),
    Rule(
        "credential-env-var",
        re.compile(
            r"(?i)\b[A-Z][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL)\s*=\s*\S{6,}"
        ),
    ),
)


def _mask(line: str, span: tuple[int, int]) -> str:
    """Return the match with its body replaced by ``***`` -- never the secret itself.

    The first three characters of the matched region survive as a locator (e.g.
    ``AKIA***``, ``ssh***``); everything after is collapsed so no usable secret
    appears in the report or on the terminal.
    """
    start, end = span
    matched = line[start:end]
    head = matched[:3]
    return f"{head}***[{len(matched)} chars]"


def scan_text(text: str) -> list[tuple[int, str, str]]:
    """Return (line_no, rule_name, masked_preview) for each credential-shaped hit."""
    hits: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for rule in _RULES:
            for m in rule.pattern.finditer(line):
                hits.append((lineno, rule.name, _mask(line, m.span())))
    return hits


def scan_vault(vault: Path) -> list[str]:
    """Return ``file:line: [rule] masked`` report rows for the whole vault."""
    rows: list[str] = []
    for md in sorted(vault.rglob("*.md")):
        rel = str(md.relative_to(vault))
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, rule_name, masked in scan_text(text):
            rows.append(f"{rel}:{lineno}: [{rule_name}] {masked}")
    return rows


def run(vault: str, report_path: str | None) -> int:
    root = Path(vault)
    if not root.is_dir():
        print(f"error: vault is not a directory: {vault}", file=sys.stderr)
        return 2
    rows = scan_vault(root)
    lines = [f"# Secret scan: {root}", "", f"findings: {len(rows)}", ""]
    lines.extend(rows)
    rendered = "\n".join(lines) + "\n"
    if report_path:
        _atomic_write(report_path, rendered)
    print(rendered, end="")
    return 1 if rows else 0


def selftest() -> int:
    # Assemble secret-shaped strings from fragments so no live-looking literal
    # sits in this source for a secret scanner (or this one) to flag.
    akia = "AK" + "IA" + "ABCDEFGHIJKLMNOP"
    ghp = "ghp_" + "A" * 36
    bearer = "Bearer " + "B" * 24
    dburl = "postgres://user:" + "s3cr3tpw" + "@db.example.com:5432/app"
    pkblock = "-----BEGIN RSA PRIVATE KEY-----"
    pwd = 'password = "' + "hunter2x" + '"'
    envvar = "STRIPE_SECRET_KEY=" + "x" * 12
    samples = {
        "aws-access-key-id": akia,
        "github-token": ghp,
        "bearer-token": bearer,
        "db-url-with-password": dburl,
        "private-key-block": pkblock,
        "password-assignment": pwd,
        "credential-env-var": envvar,
    }
    for expected, sample in samples.items():
        hits = scan_text(sample)
        names = {n for _, n, _ in hits}
        assert expected in names, f"{expected} not detected in {sample!r}; got {names}"
        # The masked preview must never contain the full secret body.
        for _, _, masked in hits:
            assert "***" in masked, f"unmasked preview: {masked}"
            assert sample not in masked, "full sample leaked into preview"

    # A clean note yields no findings.
    clean = "Ada prefers async standups. See [[Ada Lovelace]]. Source: chat-2026-06.\n"
    assert scan_text(clean) == [], f"false positive on clean text: {scan_text(clean)}"

    # End-to-end over a temp vault, asserting masking in the rendered rows.
    with tempfile.TemporaryDirectory(prefix="secrets-selftest.") as tmp:
        vault = Path(tmp)
        (vault / "Sources").mkdir()
        (vault / "Sources" / "leak.md").write_text(f"token: {ghp}\n", encoding="utf-8")
        rows = scan_vault(vault)
        assert rows, "vault scan found nothing"
        assert all(ghp not in r for r in rows), "secret leaked into vault report"

    print("scan-secrets selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--vault", help="Path to the Obsidian vault root.")
    parser.add_argument("--report", help="Optional path to write the masked report (atomic).")
    parser.add_argument("--selftest", action="store_true", help="Run the self-test and exit.")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.vault:
        parser.error("--vault is required unless --selftest is given")
    return run(args.vault, args.report)


if __name__ == "__main__":
    raise SystemExit(main())
