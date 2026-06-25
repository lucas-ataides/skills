---
name: brandkit
description: Build or audit a coherent brand kit / design system for a founder's product or personal brand — positioning, voice, and a role-based, AA-checked, tokenized visual identity that holds across every surface. Use when the user asks to create, define, document, refresh, or audit a brand kit, brand guidelines, design system, visual identity, color palette, type scale, design tokens, or brand voice and tone; or when a product looks or sounds inconsistent across its site, app, social, and decks.
---

Define or audit a brand kit the way a design lead does: judge it as one coherent system that renders the same intent across the site, the app, social, and decks, not as a swatch page beside a font list. Coherence is the deliverable; a second brand blue, a runaway font, or a voice that drifts between channels is the defect.

The judgment is yours — the positioning, the palette, the voice. The rendering is not. A script emits the design tokens and checks WCAG contrast, so the type ramp, the spacing ramp, and every AA verdict come out the same on every run. Hand-emitting tokens by keystroke or judging contrast by eye is the anti-pattern this skill removes; see [Scripts](#scripts).

Work the structure, the rules, and the failure modes in [the brand system reference](references/brand-system.md). Pin the strategy before the pixels, name every visual decision as a token, and end on criteria a reviewer can check line by line.

## Steps

1. **Pin the foundations.** State the positioning in one sentence that excludes at least one named competitor, three-to-five personality traits each pinned against an opposite, and the voice on every axis in the reference (formality, energy, warmth, humor, authority) with a say / never-say lexicon. The step is done when positioning names a differentiator a rival cannot claim, every trait carries an opposite, and the voice axes plus lexicon are written.

2. **Choose the color system by role.** Name each color by its job — brand, accent, neutral scale, background, status — and give each one value per theme. Pair every text-bearing role with a foreground that targets WCAG AA (4.5:1 body, 3:1 large and UI). The step is done when every color has a role and a chosen foreground, and no role carries a second hand-picked value.

3. **Choose the type, spacing, radius, and elevation scales.** Constrain type to one or two families and pick a base size with a ratio (1.250 is a safe default); set the spacing base to 4px or 8px; map radius and elevation to named steps. The script derives the type ramp and the spacing ramp from the base and the ratio in the next step, so record the base, the ratio, and the step counts rather than typing each size. The step is done when type, spacing, radius, and elevation each resolve to a named scale and no value sits off its ramp.

4. **Write the decisions into `brand.json`.** Record the chosen colors, the type base and ratio and steps, the spacing base and steps, and the font families in a `brand.json` matching the spec shape in [Scripts](#scripts). The step is done when `brand.json` parses as JSON and carries a colors block plus a type_scale block plus a spacing block plus a fonts block.

5. **Render the tokens with the script.** Run `scripts/tokens.py build brand.json <out-dir>` to render `tokens.css` and `tokens.json` from the spec. A non-zero exit means the spec is malformed — read the boundary message, fix `brand.json`, and re-run. The step is done when the command exits zero and `<out-dir>/tokens.css` plus `<out-dir>/tokens.json` exist.

6. **Verify every text pair against AA with the script — never by eye.** Run `scripts/tokens.py contrast <foreground> <background>` once per text-bearing pairing named in step 2. A non-zero exit marks a pairing that misses AA-normal; re-pick that foreground or background and re-run the same check. The step is done when each text pairing has a recorded ratio and every pairing exits zero on AA-normal.

7. **Set logo rules, iconography, and imagery direction.** Specify the logo variants per surface, clear space as a fraction of the mark, a minimum size, and an explicit misuse list; pick one icon library and one style; name the imagery subject, treatment, and mood tied to the personality traits. The step is done when the logo carries a misuse list, icons share one library, and imagery direction is written against the traits from step 1.

8. **Name the tokens for code.** Name every value by role, not by hue — `color.brand`, not `color.blue-500` — and split primitive, semantic, and component layers so a value lives in one place. The rendered `tokens.json` from step 5 is the single source of truth that downstream surfaces consume. The step is done when every token names a role, the three layers are separated, and `tokens.json` is named as the single source.

9. **Check consistency across surfaces, then sweep for failure modes.** Confirm one token set drives the site, app, social, decks, and email, with per-surface changes limited to density and format. Sweep the kit against the reference failure modes — inconsistent palette, no tokens, logo misuse, voice drift, contrast failures, scale leakage — and against the red-flag list. The step is done when one token set is confirmed across surfaces and every failure mode resolves to a fix or to a stated pass.

10. **Report against the criteria.** Compile the kit (or the audit) into the worked-example shape in the reference: foundations and voice on top, a token table below with a role and the script-measured AA ratio on every color. The step is done when a reviewer can verify, line by line, that every color has a role plus a script-checked AA pair, every value sits on a named scale derived by the script, the voice carries a lexicon, and no token is a one-off.

## Scripts

`scripts/tokens.py` renders the deterministic artifacts and gates the contrast math, so the agent decides the values and the script produces the output.

- `tokens.py build <brand.json> <out-dir>` — read the brand spec and render `tokens.css` (CSS custom properties such as `--color-primary`, `--space-2`, `--font-scale-base`) plus `tokens.json`. The same spec renders byte-identical output on every run. A malformed spec exits non-zero with a boundary message.
- `tokens.py contrast <hex1> <hex2>` — compute the WCAG 2.1 contrast ratio and print the AA verdicts (≥4.5 normal text, ≥3.0 large text and UI). The command exits non-zero when the pair misses AA-normal, so a failing text pairing blocks rather than slips through.
- `tokens.py --selftest` — build an in-code fixture and assert the artifacts and the contrast math. The selftest gate runs this in CI.

The spec is one JSON object; every block is optional and falls back to a documented default:

```json
{
  "colors": {"primary": "#1a1b1e", "accent": "#3b5bdb", "bg": "#ffffff"},
  "type_scale": {"base": 16, "ratio": 1.25, "steps": 6},
  "spacing": {"base": 4, "steps": 8},
  "fonts": {"sans": "Inter", "mono": "JetBrains Mono"}
}
```

A colors value is a `#rgb` or `#rrggbb` string. The `type_scale` block derives each step as `base * ratio**i`; the `spacing` block derives each step as `base * i`. Run `tokens.py build --help` for the full interface.

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
