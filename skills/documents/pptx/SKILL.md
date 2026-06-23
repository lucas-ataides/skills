---
name: pptx
description: Generate beautiful, on-brand PowerPoint decks programmatically with python-pptx — a deterministic design system, not a default-template look. Use when the user asks to build, create, or generate a .pptx / PowerPoint / slide deck / presentation / pitch deck / sales deck / investor deck from data or an outline, to style or restyle slides, to apply brand tokens to a deck, or to produce slides in code rather than by hand.
---

Build the deck the way a designer does: decide the narrative and the type/color/spacing system first, then emit slides from that system with python-pptx so every slide inherits the same scale. A deck that looks designed is systematic, not inspired — the leverage is one type ramp, one restrained palette at AA contrast, a spacing grid, and one idea per slide. The default-template look is the failure to avoid.

Push the work down the determinism ladder: a python-pptx script owns geometry, color, and font (exact and repeatable), and the model owns only the words and the archetype choice per slide. Hand-nudging shapes in prose is the anti-pattern.

[references/beautiful-decks.md](references/beautiful-decks.md) carries the design system, the slide archetypes with layout specs, chart and image treatment, the failure modes, and a worked python-pptx example.

## Steps

1. **Define audience and narrative.** Name the audience, the single takeaway, and the slide-by-slide arc (one idea per slide) before opening an editor. The arc is complete when each planned slide maps to one archetype from the reference — title, section, content, data, quote, or closing — and no slide carries two ideas.

2. **Set the theme and tokens.** Pick the deck dimension (16:9 = 13.333 x 7.5 in), one type ramp (one display face, one body face, ≤2 families total), a restrained palette (one neutral ramp, one brand accent, AA-rated text pairs), and an 8pt-based spacing grid, drawing values from `../../design/brandkit/SKILL.md` and `../../design/frontend-design/SKILL.md`. The theme holds when every token is a named constant in the script, every text pair clears 4.5:1 (3:1 for large text), and the family count is ≤2.

3. **Choose an archetype per slide.** Map each slide from step 1 to a layout spec in the reference, fixing its margins, title position, and content region from the spacing grid. The mapping is done when each slide names its archetype and pulls margins and positions from grid constants, not eyeballed inches.

4. **Generate with python-pptx.** Emit the deck from a single script: construct slides, set text frames, build tables and native charts, and place images, reading geometry and color only from the step-2 token constants. Generation succeeds when the script runs without error, writes the `.pptx` through a deterministic path, and hardcodes no off-grid number.

5. **Polish to the design checklist.** Run the deck against the reference checklist — type scale, ≤2 fonts, palette and AA contrast, spacing on the grid, one idea per slide, visual hierarchy, no clip-art, no wall-of-text — and fix each failing line. Polish is complete when every checklist line holds or carries a written, justified exception.

6. **Lint the skill and verify the file opens.** Run `uv run skill-lint --strict skills/documents/pptx` and `uv run skill-docs skills/documents/pptx`, then reopen the generated deck by reloading it with `python-pptx` and counting its slides. The skill ships when lint and docs both report zero findings and the reload returns the expected slide count without raising.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
