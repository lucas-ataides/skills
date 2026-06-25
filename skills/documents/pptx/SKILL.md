---
name: pptx
description: Generate beautiful, on-brand PowerPoint decks from Markdown content rendered by pandoc — a deterministic design system, not a default-template look. Use when the user asks to build, create, or generate a .pptx / PowerPoint / slide deck / presentation / pitch deck / sales deck / investor deck from data or an outline, to style or restyle slides, to apply brand tokens to a deck, or to produce slides as content rather than by hand.
---

Build the deck the way a designer does. Decide the narrative and the type/color/spacing system first, then write the slides as content and let a script render them so every slide inherits the same scale. A deck that looks designed is systematic, not inspired — the leverage is one type ramp, one restrained palette at AA contrast, a spacing grid, and one idea per slide. The default-template look is the failure to avoid.

Push the work down the determinism ladder. The model owns only the words and the archetype choice per slide; a reference template owns geometry, color, and font (exact and repeatable), and [scripts/render.sh](scripts/render.sh) owns the render so the same Markdown yields the same deck. Hand-writing python-pptx geometry every run is the anti-pattern this skill removes.

[references/beautiful-decks.md](references/beautiful-decks.md) carries the design system, the slide archetypes with layout specs, chart and image treatment, and the failure modes. Treat that reference as the source of design judgment; treat `render.sh` as the source of the render.

## Steps

1. **Outline the deck.** Name the audience, the single takeaway, and the slide-by-slide arc, one idea per slide, before opening an editor. The arc is complete once each planned slide maps to one archetype from the reference — title, section, content, data, quote, or closing — and no slide carries two ideas.

2. **Write the slides as Markdown.** Emit one file where a level-1 heading (`#`) starts each slide and bullets or a short statement carry that slide's single idea, drawing the narrative and the wording from step 1. This step is the model's content work. The draft is done once every slide opens with one `#` heading, every body holds one claim as phrases rather than full paragraphs, and no slide runs past five bullets.

3. **Apply brand and design via a reference template.** Produce a baseline template with `pandoc -o reference.pptx --print-default-data-file reference.pptx`, then restyle that baseline once in PowerPoint — theme colors, theme fonts, slide masters — to the tokens named in `../../design/brandkit/SKILL.md` and `../../design/frontend-design/SKILL.md`, keeping the design principles in [references/beautiful-decks.md](references/beautiful-decks.md). The template is ready once the master carries one type ramp, every text pair clears AA contrast (4.5:1, or 3:1 for large text), and the family count is at most two.

4. **Render the deck.** Run `bash scripts/render.sh <content.md> <out.pptx> [reference.pptx]`, passing the step-3 template as the third argument so the brand applies. The render succeeds once the script prints `wrote <out.pptx>` and exits zero.

5. **Verify by reopening.** Run `unzip -l <out.pptx>` and read the archive listing. The deck is valid once the listing shows `ppt/presentation.xml`.

6. **Polish to the design checklist.** Run the deck against the reference checklist — type scale, two fonts or fewer, palette and AA contrast, spacing on the grid, one idea per slide, visual hierarchy, no clip-art, no wall-of-text — and revise each failing line in the Markdown or the template. Polish is complete once every checklist line holds or carries a written, justified exception.

## Scripts

- [scripts/render.sh](scripts/render.sh) — render a Markdown deck to `.pptx` with pandoc. Usage: `render.sh <content.md> <out.pptx> [reference.pptx]`. A missing content file exits 2; an absent `pandoc` exits 3. The reference template applies only when the given path exists, so a wrong path falls back to the unstyled render. Run `bash scripts/render.sh --selftest` to confirm the renderer works on this machine; the selftest prints `pptx render selftest: ok` and exits zero, or prints `render selftest: skipped (pandoc absent)` where pandoc is not installed.

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
