#!/usr/bin/env python3
"""Compute a client-health score and RAG band from judged signals via a fixed rubric.

The skill's LLM does the judgment: it reads the relationship and scores each leading
signal onto a small fixed scale. This script does the arithmetic: it normalizes every
factor to 0-1, multiplies by a constant weight, sums to a 0-100 score, and maps that
score to a red/amber/green band by fixed thresholds. The number is therefore a
deterministic function of the inputs -- the same inputs.json yields the same score on
every run, and no model judgment leaks into the calculation.

Input is a JSON object of judged factors:

    {"factors": {"usage": 0-5, "sentiment": 0-5, "payment": 0-5,
                 "support_load": 0-5, "nps": -100..100, "engagement": 0-5}}

  health-score.py score <inputs.json>   -> print score, contributions, RAG; exit 0
  health-score.py --selftest            -> assert against fixtures, exit 0

Validation is at the boundary: a missing factor or an out-of-range value is rejected
with a clear message and a nonzero exit. Output is quiet -- a short report, no prose.
"""

from __future__ import annotations

import argparse
import json
import sys

# --- the rubric: the single source of truth for the calculation ---------------
#
# Each factor carries a constant weight; the weights sum to exactly 1.0 so the
# weighted, normalized score lands in [0, 1] before scaling to [0, 100]. Higher
# always means healthier, so support_load (a burden) is judged on an inverted
# scale by the rater: 5 means a light, healthy load and 0 means a crushing one.
WEIGHTS: dict[str, float] = {
    "usage": 0.20,
    "sentiment": 0.25,
    "payment": 0.20,
    "support_load": 0.10,
    "nps": 0.15,
    "engagement": 0.10,
}

# Each factor's accepted inclusive range, used both to validate input and to
# normalize the raw reading onto 0-1. The five 0-5 signals share one scale; nps
# rides the standard -100..100 scale and is normalized against it.
RANGES: dict[str, tuple[float, float]] = {
    "usage": (0.0, 5.0),
    "sentiment": (0.0, 5.0),
    "payment": (0.0, 5.0),
    "support_load": (0.0, 5.0),
    "nps": (-100.0, 100.0),
    "engagement": (0.0, 5.0),
}

# Fixed RAG thresholds on the 0-100 score. A score at or above GREEN_MIN is green;
# at or above AMBER_MIN (but below green) is amber; anything lower is red.
GREEN_MIN = 75.0
AMBER_MIN = 50.0

# The weights are an invariant, not a runtime input -- assert the sum at import so
# a future edit that breaks the rubric fails loudly rather than skewing scores.
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "rubric weights must sum to 1.0"
assert set(WEIGHTS) == set(RANGES), "every weighted factor must declare a range"


class InputError(ValueError):
    """Raised when inputs.json is malformed, incomplete, or out of range."""


def _normalize(factor: str, value: float) -> float:
    """Map a raw factor reading onto 0-1 against its declared inclusive range."""
    low, high = RANGES[factor]
    return (value - low) / (high - low)


def rag(score: float) -> str:
    """Return the RAG band for a 0-100 score by the fixed thresholds."""
    if score >= GREEN_MIN:
        return "green"
    if score >= AMBER_MIN:
        return "amber"
    return "red"


def parse_factors(payload: object) -> dict[str, float]:
    """Validate the decoded payload and return the factor map, or raise InputError."""
    if not isinstance(payload, dict):
        raise InputError("input must be a JSON object")
    factors = payload.get("factors")
    if not isinstance(factors, dict):
        raise InputError("input must hold a 'factors' object")
    missing = sorted(set(WEIGHTS) - set(factors))
    if missing:
        raise InputError(f"missing factor(s): {', '.join(missing)}")
    unknown = sorted(set(factors) - set(WEIGHTS))
    if unknown:
        raise InputError(f"unknown factor(s): {', '.join(unknown)}")
    clean: dict[str, float] = {}
    for name in WEIGHTS:
        raw = factors[name]
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise InputError(f"factor '{name}' must be a number, got {raw!r}")
        low, high = RANGES[name]
        if not (low <= raw <= high):
            raise InputError(f"factor '{name}' out of range [{low}, {high}]: {raw}")
        clean[name] = float(raw)
    return clean


def score_factors(factors: dict[str, float]) -> tuple[float, dict[str, float]]:
    """Return the 0-100 score and each factor's point contribution to it."""
    contributions: dict[str, float] = {}
    for name in WEIGHTS:
        contributions[name] = _normalize(name, factors[name]) * WEIGHTS[name] * 100.0
    total = sum(contributions.values())
    return total, contributions


def render(score: float, contributions: dict[str, float], band: str) -> str:
    """Render the deterministic one-block report: score, contributions, RAG."""
    lines = [f"score: {score:.1f}/100", f"rag: {band}", "contributions:"]
    for name in WEIGHTS:
        lines.append(f"  {name}: {contributions[name]:.1f}")
    return "\n".join(lines) + "\n"


def run(inputs_path: str) -> int:
    """Read inputs.json, validate, compute, print the report; return an exit code."""
    try:
        with open(inputs_path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError:
        print(f"error: inputs file not found: {inputs_path}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: inputs file is not valid JSON: {exc}", file=sys.stderr)
        return 2
    try:
        factors = parse_factors(payload)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    score, contributions = score_factors(factors)
    band = rag(score)
    print(render(score, contributions, band), end="")
    return 0


def selftest() -> int:
    # An all-high input scores near the ceiling and lands green.
    high = {name: high for name, (_, high) in RANGES.items()}
    high_score, _ = score_factors(parse_factors({"factors": high}))
    assert high_score > 95.0, f"all-high score too low: {high_score}"
    assert rag(high_score) == "green", f"all-high not green: {rag(high_score)}"

    # An all-low input scores at the floor and lands red.
    low = {name: low for name, (low, _) in RANGES.items()}
    low_score, _ = score_factors(parse_factors({"factors": low}))
    assert low_score == 0.0, f"all-low score not floor: {low_score}"
    assert rag(low_score) == "red", f"all-low not red: {rag(low_score)}"

    # The same input twice yields the identical score (determinism).
    sample = {
        "factors": {
            "usage": 4,
            "sentiment": 3,
            "payment": 5,
            "support_load": 2,
            "nps": 40,
            "engagement": 3,
        }
    }
    first, _ = score_factors(parse_factors(sample))
    second, _ = score_factors(parse_factors(sample))
    assert first == second, f"nondeterministic score: {first} != {second}"

    # The RAG thresholds bucket the boundary scores as specified.
    assert rag(GREEN_MIN) == "green", "green threshold misbanded"
    assert rag(AMBER_MIN) == "amber", "amber threshold misbanded"
    assert rag(AMBER_MIN - 0.1) == "red", "below-amber not red"

    # Contributions sum to the reported score, and never exceed the weight cap.
    total, contributions = score_factors(parse_factors(sample))
    assert abs(sum(contributions.values()) - total) < 1e-9, "contributions miss total"
    for name, points in contributions.items():
        assert points <= WEIGHTS[name] * 100.0 + 1e-9, f"{name} over its cap"

    # An out-of-range value is rejected.
    try:
        parse_factors({"factors": {**sample["factors"], "usage": 9}})
    except InputError:
        pass
    else:  # pragma: no cover - the assert is the failure path
        raise AssertionError("out-of-range usage was not rejected")

    # A missing factor is rejected.
    partial = dict(sample["factors"])
    del partial["nps"]
    try:
        parse_factors({"factors": partial})
    except InputError:
        pass
    else:  # pragma: no cover - the assert is the failure path
        raise AssertionError("missing factor was not rejected")

    print("health-score selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true", help="Run the self-test and exit.")
    sub = parser.add_subparsers(dest="command")
    score_cmd = sub.add_parser("score", help="Compute the score from an inputs file.")
    score_cmd.add_argument("inputs", help="Path to inputs.json of judged factors.")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.command == "score":
        return run(args.inputs)
    parser.error("a command is required: 'score <inputs.json>' or --selftest")
    return 2  # pragma: no cover - argparse exits before this line


if __name__ == "__main__":
    raise SystemExit(main())
