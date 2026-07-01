#!/usr/bin/env python3
"""Render design tokens from a brand spec and check WCAG contrast, deterministically.

The determinism doctrine says the LLM chooses the brand values (judgment) and a
script emits the artifact and verifies the math (no eyeballing). This script is
that renderer and that checker: ``build`` reads a brand spec and writes
``tokens.css`` plus ``tokens.json`` the same way on every run, deriving the type
ramp and the spacing ramp from a base and a ratio; ``contrast`` computes the WCAG
2.1 contrast ratio for two colors and gates on the AA threshold.

    tokens.py build <brand.json> <out-dir>   # render tokens.css + tokens.json
    tokens.py contrast <hex1> <hex2>         # WCAG ratio + AA verdict (gates)
    tokens.py --selftest                     # build a fixture + assert the math

Spec shape (one object; every block is optional, defaults shown):

    {
      "colors": {"primary": "#1a1b1e", "accent": "#3b5bdb"},
      "type_scale": {"base": 16, "ratio": 1.25, "steps": 6},
      "spacing":    {"base": 4, "steps": 8},
      "fonts":      {"sans": "Inter", "mono": "JetBrains Mono"}
    }

A colors value must be a ``#rgb`` or ``#rrggbb`` string. ``type_scale`` derives
each step as ``base * ratio**i`` (rounded to a tenth of a pixel); ``spacing``
derives each step as ``base * i``. An unknown or malformed value is rejected at
the boundary with a clear message and a non-zero exit.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

# --- WCAG 2.1 contrast thresholds (one source for the math and the verdicts) ---
_AA_NORMAL = 4.5  # body text
_AA_LARGE = 3.0  # large text and UI boundaries

# --- type-scale step names, longest ramp first; the spec's step count slices this ---
_TYPE_STEP_NAMES = ["xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl", "5xl"]

# --- defaults, applied when a spec omits a block ---
_DEFAULT_TYPE = {"base": 16.0, "ratio": 1.25, "steps": 6}
_DEFAULT_SPACING = {"base": 4.0, "steps": 8}


def _validate_hex(value: Any, where: str) -> tuple[int, int, int]:
    """Parse a ``#rgb`` / ``#rrggbb`` string into an (r, g, b) triple, or raise ValueError."""
    if not isinstance(value, str):
        raise ValueError(f"{where} must be a hex color string, got {type(value).__name__}")
    text = value.strip()
    if not text.startswith("#"):
        raise ValueError(f"{where} must start with '#': {value!r}")
    digits = text[1:]
    if len(digits) == 3:
        digits = "".join(ch * 2 for ch in digits)
    if len(digits) != 6:
        raise ValueError(f"{where} must be #rgb or #rrggbb: {value!r}")
    try:
        channels = int(digits, 16)
    except ValueError as exc:
        raise ValueError(f"{where} has non-hex digits: {value!r}") from exc
    return (channels >> 16) & 0xFF, (channels >> 8) & 0xFF, channels & 0xFF


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    """Return the WCAG 2.1 relative luminance of an 8-bit (r, g, b) triple."""
    channels = []
    for raw in rgb:
        srgb = raw / 255.0
        linear = srgb / 12.92 if srgb <= 0.03928 else ((srgb + 0.055) / 1.055) ** 2.4
        channels.append(linear)
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(hex1: str, hex2: str) -> float:
    """Return the WCAG 2.1 contrast ratio between two hex colors (1.0 .. 21.0)."""
    lum1 = _relative_luminance(_validate_hex(hex1, "color 1"))
    lum2 = _relative_luminance(_validate_hex(hex2, "color 2"))
    lighter, darker = max(lum1, lum2), min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)


def _validate_int(block: dict, key: str, where: str, minimum: int) -> int:
    """Return an integer field at or above ``minimum``, or raise ValueError."""
    value = block.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{where}.{key} must be a number, got {value!r}")
    number = int(value)
    if number < minimum:
        raise ValueError(f"{where}.{key} must be >= {minimum}, got {number}")
    return number


def _validate_positive(block: dict, key: str, where: str) -> float:
    """Return a strictly positive numeric field, or raise ValueError."""
    value = block.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{where}.{key} must be a number, got {value!r}")
    number = float(value)
    if number <= 0:
        raise ValueError(f"{where}.{key} must be > 0, got {number}")
    return number


def _resolve_colors(spec: dict) -> dict[str, str]:
    """Validate the colors block and return a name->normalized-hex map in sorted order."""
    colors = spec.get("colors", {})
    if not isinstance(colors, dict):
        raise ValueError("'colors' must be an object")
    resolved: dict[str, str] = {}
    for name in sorted(colors):
        red, green, blue = _validate_hex(colors[name], f"colors.{name}")
        resolved[name] = f"#{red:02x}{green:02x}{blue:02x}"
    return resolved


def _resolve_type_scale(spec: dict) -> list[tuple[str, float]]:
    """Derive the type ramp from base+ratio+steps as ordered (name, px) pairs."""
    block = spec.get("type_scale", _DEFAULT_TYPE)
    if not isinstance(block, dict):
        raise ValueError("'type_scale' must be an object")
    base = _validate_positive(block, "base", "type_scale")
    ratio = _validate_positive(block, "ratio", "type_scale")
    steps = _validate_int(block, "steps", "type_scale", minimum=1)
    if steps > len(_TYPE_STEP_NAMES):
        raise ValueError(f"type_scale.steps must be <= {len(_TYPE_STEP_NAMES)}, got {steps}")
    names = _TYPE_STEP_NAMES[:steps]
    base_index = names.index("base") if "base" in names else 0
    ramp: list[tuple[str, float]] = []
    for index, name in enumerate(names):
        size = base * (ratio ** (index - base_index))
        ramp.append((name, round(size, 1)))
    return ramp


def _resolve_spacing(spec: dict) -> list[tuple[int, int]]:
    """Derive the spacing ramp from base+steps as ordered (step, px) pairs."""
    block = spec.get("spacing", _DEFAULT_SPACING)
    if not isinstance(block, dict):
        raise ValueError("'spacing' must be an object")
    base = _validate_int(block, "base", "spacing", minimum=1)
    steps = _validate_int(block, "steps", "spacing", minimum=1)
    return [(step, base * step) for step in range(1, steps + 1)]


def _resolve_fonts(spec: dict) -> dict[str, str]:
    """Validate the fonts block and return a role->family map in sorted order."""
    fonts = spec.get("fonts", {})
    if not isinstance(fonts, dict):
        raise ValueError("'fonts' must be an object")
    resolved: dict[str, str] = {}
    for role in sorted(fonts):
        family = fonts[role]
        if not isinstance(family, str) or family.strip() == "":
            raise ValueError(f"fonts.{role} must be a non-empty string, got {family!r}")
        resolved[role] = family.strip()
    return resolved


def _format_px(value: float) -> str:
    """Render a pixel value without a trailing ``.0`` so output stays stable."""
    if float(value).is_integer():
        return f"{int(value)}px"
    return f"{value}px"


def _build_token_model(spec: dict) -> dict[str, Any]:
    """Validate the whole spec and return the resolved, ordered token model."""
    if not isinstance(spec, dict):
        raise ValueError("spec must be a JSON object")
    return {
        "colors": _resolve_colors(spec),
        "type_scale": _resolve_type_scale(spec),
        "spacing": _resolve_spacing(spec),
        "fonts": _resolve_fonts(spec),
    }


def _render_css(model: dict[str, Any]) -> str:
    """Render the token model as CSS custom properties under a ``:root`` block."""
    lines = [
        "/* Generated by tokens.py — do not edit by hand. */",
        "/* Re-run: scripts/tokens.py build <brand.json> <out-dir> */",
        ":root {",
    ]
    for name, value in model["colors"].items():
        lines.append(f"  --color-{name}: {value};")
    for name, size in model["type_scale"]:
        lines.append(f"  --font-scale-{name}: {_format_px(size)};")
    for step, size in model["spacing"]:
        lines.append(f"  --space-{step}: {_format_px(size)};")
    for role, family in model["fonts"].items():
        lines.append(f"  --font-{role}: {family};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def _render_json(model: dict[str, Any]) -> str:
    """Render the token model as a stable, sorted JSON document."""
    document = {
        "color": dict(model["colors"]),
        "font-scale": {name: _format_px(size) for name, size in model["type_scale"]},
        "space": {str(step): _format_px(size) for step, size in model["spacing"]},
        "font": dict(model["fonts"]),
    }
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def _atomic_write(path: Path, content: str) -> None:
    """Write ``content`` to ``path`` so a reader never sees a half-written file."""
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        Path(tmp_name).replace(path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def build(spec_path: Path, out_dir: Path) -> int:
    """Read a brand spec, render tokens.css + tokens.json into ``out_dir``, return an exit code."""
    if not spec_path.is_file():
        print(f"error: brand spec not found: {spec_path}", file=sys.stderr)
        return 2
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: brand spec is not valid JSON: {exc}", file=sys.stderr)
        return 2
    try:
        model = _build_token_model(spec)
    except ValueError as exc:
        print(f"error: invalid brand spec: {exc}", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write(out_dir / "tokens.css", _render_css(model))
    _atomic_write(out_dir / "tokens.json", _render_json(model))
    token_count = (
        len(model["colors"])
        + len(model["type_scale"])
        + len(model["spacing"])
        + len(model["fonts"])
    )
    print(f"wrote tokens: {out_dir}/tokens.css + tokens.json ({token_count} tokens)")
    return 0


def contrast(hex1: str, hex2: str) -> int:
    """Print the WCAG ratio and AA verdicts; return non-zero when AA-normal fails."""
    try:
        ratio = contrast_ratio(hex1, hex2)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    normal = "pass" if ratio >= _AA_NORMAL else "FAIL"
    large = "pass" if ratio >= _AA_LARGE else "FAIL"
    print(
        f"contrast {hex1} on {hex2}: {ratio:.2f}:1  "
        f"AA-normal {normal} (>={_AA_NORMAL})  AA-large/UI {large} (>={_AA_LARGE})"
    )
    return 0 if ratio >= _AA_NORMAL else 1


_FIXTURE_SPEC = {
    "colors": {"primary": "#1a1b1e", "accent": "#3b5bdb", "bg": "#ffffff"},
    "type_scale": {"base": 16, "ratio": 1.25, "steps": 6},
    "spacing": {"base": 4, "steps": 8},
    "fonts": {"sans": "Inter", "mono": "JetBrains Mono"},
}


def selftest() -> int:
    """Build the fixture into a temp dir and assert the artifacts and the contrast math."""
    # Boundary validation rejects a malformed hex value.
    try:
        _validate_hex("1a1b1e", "color")
    except ValueError:
        pass
    else:
        print("tokens selftest: FAIL (missing-hash hex accepted)", file=sys.stderr)
        return 1

    # Boundary validation rejects a missing-required spacing key.
    try:
        _resolve_spacing({"spacing": {"base": 4}})
    except ValueError:
        pass
    else:
        print("tokens selftest: FAIL (missing spacing.steps accepted)", file=sys.stderr)
        return 1

    # Black on white is the maximum WCAG ratio, 21:1.
    extreme = contrast_ratio("#000000", "#ffffff")
    if not math.isclose(extreme, 21.0, abs_tol=0.05):
        print(f"tokens selftest: FAIL (black/white ratio was {extreme:.3f})", file=sys.stderr)
        return 1

    # A low-contrast pair fails the AA-normal gate (non-zero exit).
    if contrast("#777777", "#888888") == 0:
        print("tokens selftest: FAIL (low-contrast pair passed AA)", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="tokens-selftest.") as tmp:
        spec_path = Path(tmp) / "brand.json"
        out_dir = Path(tmp) / "out"
        spec_path.write_text(json.dumps(_FIXTURE_SPEC), encoding="utf-8")

        if build(spec_path, out_dir) != 0:
            print("tokens selftest: FAIL (build did not exit zero)", file=sys.stderr)
            return 1

        css_path = out_dir / "tokens.css"
        json_path = out_dir / "tokens.json"
        if not css_path.is_file() or not json_path.is_file():
            print("tokens selftest: FAIL (token files missing)", file=sys.stderr)
            return 1

        css = css_path.read_text(encoding="utf-8")
        if "--color-primary: #1a1b1e;" not in css:
            print("tokens selftest: FAIL (known color token absent from CSS)", file=sys.stderr)
            return 1
        if "--space-2: 8px;" not in css:
            print("tokens selftest: FAIL (derived spacing token absent from CSS)", file=sys.stderr)
            return 1
        if "--font-scale-base: 16px;" not in css:
            print("tokens selftest: FAIL (base type token absent from CSS)", file=sys.stderr)
            return 1

        document = json.loads(json_path.read_text(encoding="utf-8"))
        if document.get("color", {}).get("primary") != "#1a1b1e":
            print("tokens selftest: FAIL (known color token absent from JSON)", file=sys.stderr)
            return 1

        # Determinism: a second build of the same spec yields byte-identical output.
        second_dir = Path(tmp) / "out2"
        build(spec_path, second_dir)
        if (second_dir / "tokens.css").read_text(encoding="utf-8") != css:
            print("tokens selftest: FAIL (build was not deterministic)", file=sys.stderr)
            return 1

    print("tokens selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true", help="Run the self-test and exit.")
    sub = parser.add_subparsers(dest="command")

    build_parser = sub.add_parser("build", help="Render tokens.css + tokens.json from a spec.")
    build_parser.add_argument("spec", help="Path to the brand JSON spec.")
    build_parser.add_argument("out", help="Output directory for the token files.")

    contrast_parser = sub.add_parser("contrast", help="WCAG ratio + AA verdict for two colors.")
    contrast_parser.add_argument("hex1", help="First color, #rgb or #rrggbb (e.g. foreground).")
    contrast_parser.add_argument("hex2", help="Second color, #rgb or #rrggbb (e.g. background).")

    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.command == "build":
        return build(Path(args.spec), Path(args.out))
    if args.command == "contrast":
        return contrast(args.hex1, args.hex2)
    parser.error("choose a command: 'build', 'contrast', or '--selftest'")
    return 2  # pragma: no cover - argparse exits first


if __name__ == "__main__":
    raise SystemExit(main())
