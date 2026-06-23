# Beautiful .docx with pandoc and a reference template

Concrete, opinionated practice for generating Word documents that read as designed, not defaulted. The governing idea matches the [web design rules](../../../design/frontend-design/references/visual-rules.md): **professional design is systematic, not inspired.** Pick a small set of scales once — a type ramp, a spacing rhythm, a restrained palette — bake them into the named styles of a reusable template, then write the document as plain Markdown and let `pandoc` snap every paragraph to a style.

The grounding is the [foundation](../../../meta/foundation/SKILL.md) determinism doctrine: a shell script generates the file, the output is reproducible, and the design lives in data (the styles inside a `reference.docx`) rather than in scattered judgment (inline formatting). The depth bar for reviewing the result is the tech-lead standard from [code-review](../../../engineering/code-review/SKILL.md) — judge the document against what it must deliver and whether it reads as one coherent artifact, not only whether each line converts.

This skill splits the work in two. The author writes only the **content**, as Markdown. The script `scripts/render.sh` converts that Markdown to `.docx` with `pandoc`, and an optional `reference.docx` carries the **design**. The two never mix: the same Markdown plus the same template yields the same document every run.

---

## 1. The core practice — the design lives in the reference template

The single decision that separates a beautiful document from a Calibri wall is *where the styling lives*. Word documents carry a **style sheet**: named, reusable definitions of how a kind of text looks — `Heading 1`, `Body Text`, `Title`, `Caption`, and a default table style. A paragraph styled `Heading 1` inherits its font, size, color, and spacing from that one definition. Change the definition once, and every `Heading 1` in the document updates at once.

The pandoc workflow makes that property structural. The author never sets a font or a size on a paragraph; the Markdown carries pure structure (`#` for a section, a pipe table for tabular data). At conversion, pandoc applies a **named style** to each element. Those named styles come from one place — the `reference.docx` — so the template *is* the design system. Restyling the whole document means editing styles in that one file, never the content.

**The rule:** define the look once, in the reference template, and let the content stay style-free. Reserve a direct inline override (Markdown `**bold**` or `*italic*`) for a genuine one-off emphasis inside a sentence, never for anything a named style should own.

### Producing a baseline template to edit

A reference template starts from pandoc's own default and is then restyled in Word. Ask pandoc to emit a copy of the very `.docx` it uses internally:

```bash
pandoc -o reference.docx --print-default-data-file reference.docx
```

That command writes a `reference.docx` whose styles are pandoc's stock defaults. Open it in Word, edit the named styles to match the design system below — not the visible text, which is throwaway sample copy — and save the file in place. The styles worth editing, because pandoc maps content onto them, are at least: `Title`, `Heading 1`, `Heading 2`, `Heading 3`, `Body Text`, `First Paragraph`, `Caption`, `Block Text` (block quotes), and the table style pandoc applies to pipe tables. Editing those style *definitions* — their font, size, color, and paragraph spacing — is the whole design act; the sample text in the file is discarded at render time.

### How the authored Markdown maps to styled output

Knowing the mapping lets the author write structure-only Markdown and trust the template to dress it. Pandoc's GitHub-Flavored-Markdown reader (`--from gfm`) maps content to Word styles like this:

| Markdown the author writes        | Word style pandoc applies          |
|-----------------------------------|------------------------------------|
| `# Section`                       | `Heading 1`                        |
| `## Subsection`                   | `Heading 2`                        |
| `### Sub-subsection`              | `Heading 3`                        |
| A blank-line-separated paragraph  | `Body Text` (`First Paragraph` after a heading) |
| `- item` / `1. item`             | `List Bullet` / `List Number`      |
| `> quoted line`                   | `Block Text`                       |
| `` `code` `` / fenced block       | `Verbatim Char` / `Source Code`    |
| `| a | b |` pipe table           | the template's table style          |
| an image: `!` `[alt text]` `(chart.png)` | an inline image, then `Image Caption` for the alt text |
| `**bold**` / `*italic*`           | inline bold / italic runs           |

The author's job is to choose the right structure (a heading, not a bold line; a real table, not aligned spaces). The template's job is to make each structure look designed.

---

## 2. The design system — scales baked into the template's styles

A complete document design system is small. The whole system becomes a set of style definitions inside the `reference.docx`, set once. Treat the targets below as the values to dial into those styles in Word.

### Type scale via styles

Pick heading and body sizes from one modular scale rather than arbitrary jumps. A practical ramp for print (roughly a 1.25 ratio):

```
11   13   16   20   26   32
```

Map the ramp onto the template's styles, not onto inline sizes:

| Style       | Size  | Weight   | Role                          |
|-------------|-------|----------|-------------------------------|
| `Title`     | 32 pt | Bold     | Cover title only              |
| `Heading 1` | 20 pt | Bold     | Section                       |
| `Heading 2` | 16 pt | Semibold | Subsection                    |
| `Heading 3` | 13 pt | Semibold | Minor heading                 |
| `Body Text` | 11 pt | Regular  | Paragraph text                |
| `Caption`   | 9 pt  | Italic   | Figure and table captions     |

Body text sits at 11pt for print; smaller strains the reader on paper. Three to four sizes carry almost any document. Set each size in Word as the named style's font size, so the ramp is enforced by the template rather than retyped per paragraph.

### Two faces maximum

Two typefaces is the ceiling — one for headings, one for body, or a single family across both. A third face is the classic tell of an amateur layout. Reach for weight, not a new family, when a heading needs more presence. Pair by contrast: a sans heading (Calibri, Aptos, Arial) over a serif body (Georgia, Cambria) reads as intentional, whereas two near-identical sans faces read as a mistake. Choosing a serif body alone breaks the document out of the default-Calibri look. Encode the two faces in the template by setting the heading styles to one family and `Body Text` to the other.

### Spacing rhythm

Space is the cheapest polish and the first thing amateurs get wrong. Set spacing through each style's *paragraph spacing* (space before, space after) and line spacing in Word — never through blank paragraphs in the Markdown, which pandoc discards or collapses anyway. A practical print rhythm to dial into the styles:

- Body line spacing `1.4`; heading line spacing `1.15`.
- Space after on `Body Text` ≈ `8pt`; space before on `Heading 1` ≈ `18pt`, on `Heading 2` ≈ `12pt`.
- A heading sits closer to the text it introduces than to the text above it, so the eye groups by section. Achieve that with more space *before* a heading than *after* it.

A blank paragraph used as a spacer is a defect: it carries no semantic meaning and drifts when content reflows. The template's per-style spacing replaces it entirely.

### Color and AA contrast

A restrained palette is one neutral plus one accent. Most of the document is near-black text on white; the accent appears on heading color, the cover, and the table-header fill. Set the accent as the font color of the heading styles and as the header-row shading of the table style in the template.

WCAG AA is the floor, exactly as on the web:

- Body and small text at **≥ 4.5:1** against its background.
- Large text (≥ 24px / 18pt, or bold ≥ 14pt) at **≥ 3:1**.

Light-gray body text on white is the most common failure: `#999999` on white measures about 2.8:1 and fails AA. A near-black such as `#1A1A1A` on white clears it comfortably. Pure black on pure white is harsh; prefer a very dark neutral. White text on an accent table-header fill passes only when the accent is dark enough — verify the pair, never assume it. A dark accent near `#0B5C8A` carries white header text above 4.5:1.

### Cover and table of contents

A cover page and a TOC are what make a long document read as a deliverable rather than a draft. Two complementary routes produce them with this workflow:

- **Cover via metadata.** A YAML metadata block at the top of the Markdown (`title:`, `subtitle:`, `author:`, `date:`) makes pandoc emit a title block styled by `Title` and the related styles. Pass `--standalone` for pandoc to render that block.
- **TOC via a pandoc flag.** Add `--toc` (optionally `--toc-depth=2`) to the conversion, and pandoc inserts a table of contents bound to the heading outline, styled by the `TOC` styles in the template.

Both routes draw their look from the named styles in the `reference.docx`, so the cover and TOC inherit the same type scale and palette as the body. The render script accepts a reference template; richer covers belong in that template's design (a styled title block, a cover background) rather than in the content.

---

## 3. Deterministic generation — the render interface

Every structural element has a deterministic conversion. The author assembles Markdown; the script renders it identically every run. The contract is one command:

```bash
scripts/render.sh <content.md> <out.docx> [reference.docx]
```

- `<content.md>` — the structure-only Markdown the author wrote.
- `<out.docx>` — the file pandoc writes.
- `[reference.docx]` — the design template; the script adds `--reference-doc` only when this path is given AND the file exists on disk.

Under the hood the script runs `pandoc --from gfm --to docx`, so it reads GitHub-Flavored Markdown and writes Word. A successful render prints `wrote <out.docx>` and exits `0`. A missing content file exits `2`; an absent `pandoc` exits `3`. The agent branches on that exit code rather than parsing prose. To prove the toolchain on a bare machine, run `scripts/render.sh --selftest`, which renders a fixture and asserts the output is a valid docx.

### Headings and paragraphs

Write the section outline as `#`/`##`/`###`, never as bold text, so pandoc applies the `Heading n` styles and the document outline stays navigable. Ordinary prose becomes `Body Text` automatically; emphasis inside a sentence uses Markdown `**bold**` or `*italic*` for a true one-off, not a style:

```markdown
## Findings

The result is **significant** across all cohorts.
```

### Tables

A table reads as designed when it inherits a clean table style, breathes inside its cells, and reserves a rule for the header. Write a pipe table in Markdown; pandoc applies the template's table style, so the borders, padding, and header fill come from the design rather than from the content:

```markdown
| Metric  | Q1   | Q2   |
|---------|------|------|
| Revenue | 12.4 | 15.1 |
| Margin  | 0.31 | 0.34 |
```

A dense, rule-heavy table is the table equivalent of border-soup: every cell fenced, nothing breathing. Separation comes first from cell padding and a single header rule defined in the template's table style, and from a border only as a last resort. The header row in a pipe table is the first row above the `---` separator; the template decides how that row is shaded.

### Images and figures

Reference an image with Markdown image syntax and put the caption in the alt text, so pandoc emits the picture followed by a `Caption`-styled line:

```markdown
![Figure 1. Quarterly revenue.](chart.png)
```

Pandoc sizes the image from its intrinsic dimensions; to fix a width for predictable layout across runs, add a pandoc attribute:

```markdown
![Figure 1. Quarterly revenue.](chart.png){width=6in}
```

### Margins, headers, and footers

Page geometry and running header/footer text are part of the **template**, not the content. Set the page margins in the `reference.docx` (generous and even — about `1in` on each side), and put header and footer text into the template's header and footer regions in Word. Pandoc carries those regions from the reference doc into every rendered document, so one template gives every output the same frame. Markdown has no syntax for a running header; the template owns it deliberately.

### Page numbers

A page number is a Word **field**, computed at open time, and it belongs in the template's footer. Insert a `PAGE` field into the footer of the `reference.docx` once in Word (Insert → Page Number, or a `PAGE` field), then save the template. Every document rendered against that template inherits the live page number, with no per-document step.

### Table of contents

The TOC is also a field, populated from the heading outline. Two levers produce it: pass `--toc` to pandoc for it to insert the TOC, and edit the `TOC` styles in the template to control how the entries look. A reader presses F9 in Word to refresh the field after editing. Bind the depth to the outline you want with `--toc-depth=2`, so the contents list headings down to level 2.

---

## 4. Document archetypes

Each archetype is a fixed section list. Naming the archetype first fixes the structure before any styling decision, and the section list becomes the heading outline of the Markdown.

| Archetype  | Required sections (in order)                                                                 | Distinctive styling                                              |
|------------|----------------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| **Report** | Cover, TOC, executive summary, body sections (H1/H2), figures and tables, appendix            | Strong heading hierarchy, captioned figures, running header     |
| **Proposal** | Cover, summary, problem, proposed solution, scope, pricing table, timeline, terms          | Accent on the cover and pricing-table header; one clear ask      |
| **Contract** | Title block, parties, recitals, numbered clauses, signature block                          | Numbered-list clause style, conservative serif, no decoration    |
| **Memo**   | `TO / FROM / DATE / RE` header block, body, action items                                      | Compact, single section, no cover, tight spacing                 |

A report and a proposal earn a cover and a TOC; a memo never does. A contract leans on a numbered-list style for its clauses, written as a Markdown `1.` list, so the numbering stays consistent as clauses are inserted or removed. The cover comes from a YAML metadata block plus `--standalone`; the TOC comes from `--toc`.

---

## 5. Failure modes

Each failure mode below is a named defect with a fix.

- **Styling baked into the content.** Font, size, or spacing forced into the document body instead of living in the template. The file drifts and cannot be restyled in one move. Fix: strip the content to structure-only Markdown and move the look into the reference template's named styles.
- **The default-Calibri wall.** Stock styles, no palette, no cover — a document that looks like an untouched template. Fix: edit `Body Text` and the heading styles in the reference doc onto a serif-body type scale, add an accent color, and emit a cover from a metadata block.
- **Inconsistent headings.** Section titles set by bolding a line, or heading levels skipped (`#` then `###`). The outline breaks, so the TOC and navigation break with it. Fix: write `#`/`##`/`###` in order with no skipped level, so pandoc applies `Heading n` cleanly.
- **Dense tables.** Rule-heavy grids with cramped cells and no header treatment. The table fights the reader. Fix: define padding and a single header rule in the template's table style, and let every pipe table inherit it.
- **Blank paragraphs as spacers.** Empty lines standing in for spacing. The rhythm drifts on reflow, and pandoc may drop them anyway. Fix: set space-before / space-after on the styles in the template instead.
- **Sub-AA contrast.** Light-gray text that disappears on white. Fix: darken the body and caption style colors until each pair clears 4.5:1.
- **Off-scale type.** Sizes chosen ad hoc (12, 15, 17, 21) inside styles. The hierarchy reads as drift. Fix: snap every style's size to the modular ramp.
- **No template at all.** Rendering content with bare `pandoc` and no `reference.docx`, so the output carries pandoc's stock look. Fix: pass a restyled reference template as the third argument to `render.sh`.

---

## 6. Red flags — fast scan

A document needs this skill when any of these appear:

- Default Calibri body with no palette and no cover — the untouched-template look.
- Heading sizes or body sizes chosen ad hoc, off any scale.
- More than two typefaces, or a third face smuggled into a table or caption.
- Gray text under 4.5:1 against its background.
- Section titles made by bolding a line instead of a heading.
- Skipped heading levels (`#` straight to `###`), breaking the outline and TOC.
- Tables fully fenced in heavy rules with cramped cells.
- Blank paragraphs used to create vertical space.
- Formatting forced into the document body instead of the reference template.
- A multi-page document with no header, footer, or page number in the template.

---

## 7. Worked example — a designed report

This example shows the two halves of the workflow: the structure-only Markdown the author writes, and the conversion that dresses it in the template. The template, prepared once as in section 1, already carries the type scale, the paired faces, the spacing, the palette, the margins, and a footer page-number field.

The content — `report.md` — is pure structure, with a metadata block for the cover and not one font or size in sight:

```markdown
---
title: Quarterly Business Review
subtitle: Fiscal Year 2026 · Q2
author: Finance Team
date: 2026-06-23
---

# Executive Summary

Revenue grew across **every cohort** this quarter.

## Revenue by Segment

| Segment    | Q1   | Q2   |
|------------|------|------|
| Enterprise | 8.1  | 9.7  |
| Mid-market | 4.3  | 5.4  |

![Table 1. Revenue by segment ($M).](segments.png){width=6in}
```

The conversion turns that into a designed `.docx`, applying the brand from `reference.docx`:

```bash
scripts/render.sh report.md quarterly_review.docx reference.docx
```

For a cover and a contents page, pandoc's standalone and TOC behavior is what produces them; when richer control is needed, run pandoc directly with the same template:

```bash
pandoc --from gfm --to docx --standalone --toc --toc-depth=2 \
  --reference-doc reference.docx --output quarterly_review.docx report.md
```

What makes the result read as designed, named against the system:

- **Design in the template** — `reference.docx` owns the whole look, so a restyle is one edit to that file (section 1).
- **Content free of formatting** — `report.md` carries structure only; the lone inline override is reserved for true emphasis (section 1).
- **Two faces, paired by contrast** — a sans heading family over a serif body, set in the template's styles, no third face (section 2).
- **One type scale** — `32 / 20 / 16 / 13 / 11 / 9`, drawn from the modular ramp and dialed into the styles (section 2).
- **AA contrast** — near-black body and a dark-accent heading color both clear 4.5:1 on white (section 2).
- **Spacing through styles** — space-before / space-after set on the template's styles, with zero blank-paragraph spacers (section 2).
- **Cover, TOC, header/footer, page number** — the deliverable frame, from the metadata block, `--toc`, and the template's footer field (sections 2–3).
- **Deterministic render** — `render.sh` owns the conversion, so the same Markdown plus the same template yields the same document every run (section 3).

---

## Final checklist

The document passes when each line holds or carries a written, justified exception:

- [ ] **Design in the template** — the look lives in `reference.docx`; the content carries no font, size, or spacing instruction.
- [ ] **Type scale** — every style's size is drawn from one modular ramp; body at 11pt for print.
- [ ] **Typefaces** — two faces or fewer in the template; a serif or paired body, not the default Calibri wall.
- [ ] **Spacing** — set through space-before / space-after on the template's styles; zero blank-paragraph spacers.
- [ ] **Contrast** — body and small text at AA (4.5:1); large text at 3:1.
- [ ] **Heading outline** — `#`/`##`/`###` written in order, no skipped level, so pandoc applies `Heading n` cleanly.
- [ ] **Tables** — a clean table style in the template, padded cells, a single header rule — no border-soup.
- [ ] **Frame** — even margins, a header and footer, and a live page-number field all set in the template.
- [ ] **Cover and TOC** — present for a report or proposal, from a metadata block and `--toc`; omitted for a memo.
- [ ] **Archetype** — the section list matches the named archetype.
- [ ] **Verified** — the rendered file reopens with the expected styles and heading hierarchy (`unzip -l <out.docx>` lists `word/document.xml`).
