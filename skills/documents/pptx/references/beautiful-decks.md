# Beautiful decks with pandoc

A deck earns the word *beautiful* the same way a web UI does: by being systematic, not inspired. Amateur slides pick a size here, a blue there, a margin by feel — so nothing aligns and nothing relates, and the result reads as the default template with the content poured in. A designed deck snaps every decision to a small set of scales chosen once, then repeats them on every slide.

This skill splits the work in two so each half can be made deterministic. The **design system** lives in one place — a reference template (`reference.pptx`) carrying the theme fonts, theme colors, and slide masters — and the **content** lives in a Markdown file where the model writes only words. [scripts/render.sh](../scripts/render.sh) fuses the two with one `pandoc` call, so the same Markdown and the same template yield the same deck on every run. The governing move is to push the work down the determinism ladder: the template owns geometry, color, and font (exact, repeatable, free of eyeballing), and the model owns only the prose and the choice of archetype per slide. The lineage of the design rules is Refactoring UI and the brand-system and web-design references in this repo, distilled into values baked into the template and the Markdown.

The design tokens here resolve to the same roles named in [the brand system](../../../design/brandkit/SKILL.md) and the scales named in [the web design rules](../../../design/frontend-design/SKILL.md). A deck is one more surface that inherits the kit; what changes from the website is density and presenter-scale type, never the identity values.

---

## 1. The pandoc pipeline, deterministically

`pandoc` reads a Markdown file and writes the Office Open XML that PowerPoint reads, so one command produces the same deck on every run. There is no per-slide geometry code to drift: the design lives in the template, the words live in the Markdown, and the render is one deterministic step. Three ideas cover the whole pipeline.

### The three moving parts

```
content.md          # the words — one file, headings + bullets + images + tables
   │
   ├── reference.pptx   # the design system — theme fonts, colors, slide masters
   │
   └── render.sh ──▶ pandoc --from gfm --to pptx
                       [--reference-doc reference.pptx]
                       --output out.pptx content.md
                          │
                          └──▶ out.pptx   # the deck, design applied
```

The Markdown is the only thing the model edits per deck. The template is built once per brand and reused across decks. The script never changes — it is input validation plus one `pandoc` invocation.

### The render invocation

Run the renderer exactly as the script defines it; do not call `pandoc` by hand and do not invent flags. The signature is the contract:

```
bash scripts/render.sh <content.md> <out.pptx> [reference.pptx]
```

- `<content.md>` — the authored slide source (required). A missing file exits `2`.
- `<out.pptx>` — the deck to write (required).
- `[reference.pptx]` — the design template (optional). It applies only when the path exists; a wrong or absent path falls back to pandoc's unstyled default — which is exactly the default-template look this skill exists to avoid, so always pass a real template for a finished deck.

The script also self-checks: `bash scripts/render.sh --selftest` renders a tiny two-slide deck and confirms the toolchain works, printing `pptx render selftest: ok` (or `render selftest: skipped (pandoc absent)` where `pandoc` is not installed). Under the hood the render is `pandoc --from gfm --to pptx [--reference-doc <ref>] --output <out> <src>` — `gfm` is GitHub-Flavored Markdown, so tables, fenced code, and task lists parse the way they do on GitHub. A non-zero exit means the deck was not written; the absent-`pandoc` case exits `3`.

### How Markdown maps to slides

In pandoc's Markdown-to-slides model a heading begins a new slide and the content beneath it becomes that slide's body. Two heading levels do two different jobs:

- **`#` (level 1) — a content slide.** Because the script invokes pandoc without `--slide-level`, pandoc derives the slide level from the document: the slide level is the highest heading level that has body content (text, bullets, an image, or a table) directly under it. In a deck written with `#` titles and bullets beneath each, that makes **one `#` heading equal one slide**, and the bullets, paragraph, image, or table under it become the slide body.
- **`##` (level 2) — a section divider.** A heading *above* the slide level carries no body of its own; pandoc renders it as a section-header slide that resets the viewer between acts. So if your content slides are `#`, a `##` does *not* start an ordinary content slide — it would sit below `#` in the hierarchy. To get section dividers, keep the deck's content slides at `#` and reserve a higher level for sections, or rely on the title-slide convention below. Match the level you author to the role you want; do not mix `#` content slides and `#` section slides expecting different geometry.

A horizontal rule (`---` on its own line) also forces a slide break, which is the clean way to split a long idea without inventing a heading.

Three more mappings complete the model:

- **The title slide.** When the Markdown begins with a YAML metadata block (`title:`, `subtitle:`, `author:`, `date:`), pandoc emits a dedicated title slide from the template's title layout — the cover, styled by the master, with no geometry on your part.
- **Images.** A Markdown image — `![` alt text `]` then the path in parentheses — placed under a heading becomes slide content, and pandoc positions it using the layout. Give every image real alt text — it is both the accessibility label and the picture's caption hook (section 9). Source the image large enough for the room (section 7).
- **Tables.** A GFM pipe table under a heading renders as a native PowerPoint table, styled by the template's table style — which is exactly why the template's table style must be set (section 8), since the default is the loudest tell of an auto-generated deck.

### The determinism rules for the deck

- **One template, one design system.** Every design decision — fonts, colors, master geometry — lives in `reference.pptx`, defined once and reused. A color or font chosen ad hoc per slide is the off-system value that breaks the deck.
- **Write the output through a deterministic path.** When the skill names the `out.pptx`, it takes the name from `skillkit.unique_path` rather than a hand-built timestamp, so concurrent renders never collide.
- **One archetype per slide.** Each slide maps to exactly one archetype (section 3) — title, section, content, data, quote, or closing — so every slide of a kind is identical and the deck is a composition, not a pile.

---

## 2. The deck design system

A complete deck system is small. Set each scale once — in the template's slide master and theme, and in the discipline of the Markdown — then refuse values outside it. These are the targets the `reference.pptx` must encode and the Markdown must respect.

### One type ramp

Slides read at distance, so deck type runs larger than web type, yet still sits on a modular ramp rather than ad-hoc sizes. A practical presenter-scale ramp (a ~1.25 ratio, hand-tuned):

```
14   18   22   28   36   44   54   66
```

Roles map onto the ramp: body and captions at the low end (`14`/`18`), slide titles in the middle (`36`/`44`), and a hero number or section label at the top (`54`/`66`). Body text never drops below `14pt` on a slide, because a back-row reader loses anything smaller. Bake these sizes into the master's placeholders so every slide inherits them; the Markdown then carries no font sizes at all.

### Two faces at most

One display family for titles, one body family for everything else — or a single strong family across both. A third face is the classic amateur tell. Use weight (400 / 600 / 700) for variety inside a family rather than reaching for a new font. Set both faces as the theme fonts in the template. Fonts must be installed on the rendering machine, so prefer a system or widely available family (Inter, Source Sans, system-ui) unless the deck embeds its fonts in PowerPoint.

### A restrained palette at AA contrast

The budget is the same as any surface in the kit: **one neutral ramp + one brand accent + the status hues only.**

| Role | Token | Job on a slide |
|---|---|---|
| Background | `bg` | Slide canvas (usually near-white or a deep neutral) |
| Foreground | `fg` | Body text, drawn from the neutral ramp's dark end |
| Brand | `brand` | Section fills, the lead data series, key emphasis |
| Accent | `accent` | A single highlight or a positive delta |
| Neutral 100–300 | `neutral.*` | Table tints, dividers, muted captions |
| Status | `success` / `warning` / `danger` | Deltas and callouts, by meaning only |

Set these as the theme colors in the template so every fill and text run resolves to a role, not a one-off hex. Contrast is the floor, not a finish: body text clears **4.5:1** against its background, and large text (≥ 24pt, or ≥ 19pt bold) and meaningful icons clear **3:1**. Light-gray text on white is the most common failure — a `#999` on white measures ~2.8:1 and fails, so darken until the ratio clears. Never carry meaning in hue alone; pair a colored delta with a sign or an arrow so a color-blind viewer reads it too.

### An 8pt spacing grid

Every margin, gap, and offset in the master draws from one scale built on a 4pt base doubling into an 8pt rhythm:

```
4   8   12   16   24   32   48   64   96
```

In inches at 96 px/in, the workhorse values are `0.083, 0.167, 0.25, 0.33, 0.5, 0.667, 1.0`. Round to clean values and reuse them when placing placeholders in the master. A `0.31in` margin beside a `0.5in` margin is the drift that makes a deck feel hand-placed.

### Generous margins and a content region

Reserve a wide, consistent outer margin on every layout — a 16:9 deck breathes at roughly `0.92in` left and right and `0.75in` top and bottom. Set the body and title placeholders inside that margin in the master, identical across layouts, and content lands in the same region on every slide — which is what makes a deck feel composed. Cramming to the edge is the single fastest way to look unfinished.

### Deck dimension

A modern deck is 16:9 (13.333 × 7.5 in). Set the slide size once in the template (PowerPoint: *Design → Slide Size → Widescreen 16:9*); every slide pandoc emits then inherits it. There is no per-deck dimension code — the template is the single source of the canvas.

### One idea per slide

A slide carries one claim. A second idea wants a second slide, not a smaller font. The discipline of one-idea-per-slide is what kills the wall-of-text failure before it starts — when a slide needs three paragraphs, the content is really three slides or belongs in a leave-behind document. This rule lives in how you write the Markdown: one `#` heading, one claim, at most five bullets.

### Visual hierarchy

Build the eye's path with four tools, ranked: **size** (bigger leads), **weight** (heavier leads), **color/contrast** (high contrast advances, muted recedes), and **space** (isolation confers importance). De-emphasize as much as you emphasize — mute the supporting line with a lighter neutral rather than only enlarging the lead. One emphasis per slide; two competing focal points split attention and stall the read. The master's title-vs-body type ramp does most of this work automatically once it is set.

### Token check

The system holds when color resolves to a theme role with an AA pair, type and spacing resolve to a named ramp in the master, the theme-font count is ≤ 2, and the Markdown carries no inline styling that fights the template.

---

## 3. Slide archetypes

Six archetypes cover almost any deck. Each names the Markdown that produces it, the layout it lands on, and the one thing it must not do. The geometry — margins, sizes, placement — comes from the template master, not from the Markdown; the Markdown only chooses the archetype and supplies the words.

### Title

The cover. One product or deck name, one subtitle, optional date and presenter — nothing else.

- **Markdown:** a leading YAML metadata block — `title:`, `subtitle:`, `author:`, `date:`. Pandoc renders it on the template's title layout.
- **Design (in the master):** left-aligned block, title `54`–`66pt` display face bold in `fg` or `brand` at the `0.92in` left edge; subtitle `22`–`28pt` body face in a muted neutral, `0.24in` below.
- **Not:** a centered title floating over a busy stock photo with low-contrast text.

### Section

A divider that resets the viewer between acts. High contrast, almost no content.

- **Markdown:** a heading *above* the slide level (a section heading) with no body beneath it — pandoc emits a section-header slide. Keep content slides at `#` and use the section convention consistently so the divider lands on the section layout.
- **Design (in the master):** full-bleed `brand` (or deep neutral) fill, one short label `44`–`54pt` reversed (`on-brand`) and left-aligned with a generous margin; an optional muted step indicator ("02 / 05").
- **Not:** a bulleted agenda — a section slide announces one act, it does not summarize.

### Content

The workhorse. A title, then one supporting idea as a short list, a two-column split, or a single statement.

- **Markdown:** a `#` heading (the title), then bullets or a short paragraph — at most five bullets, each a phrase not a sentence. The template's content layout supplies the title band and body region.
- **Design (in the master):** title `32`–`40pt` bold at the `0.92in` left edge; body `18`–`22pt` at `1.3`–`1.4` line spacing, `0.5in` below the title baseline, list items gapped on the grid.
- **Not:** a wall of full-sentence bullets; if the text wraps to three lines per bullet, split the slide with a `---` rule or a new `#`.

### Data / chart

One chart or one table, framed and labeled, making one point.

- **Markdown:** a `#` heading stating the takeaway, then either a GFM pipe table (rendered native, styled by the template's table style) or a Markdown image of a chart built upstream. A short interpretive title carries the conclusion.
- **Design:** the table inherits the template's table style — header tint, muted gridlines, body type from the ramp (section 8); a chart image fills the content region, theme-colored at the source (section 8).
- **Not:** two charts competing on one slide, or a default-styled table with banded rainbow rows.

### Quote

A single testimonial or pull-quote, set large with room to breathe.

- **Markdown:** a `#` heading (or none) and a blockquote (`> …`) for the quote, then a line of attribution. The template's body type sets the scale.
- **Design (in the master):** quote `36`–`44pt` regular or light weight in `fg`, wide margins so the line measure stays short; attribution `18`–`20pt` muted, name then role.
- **Not:** quotation-mark clip-art, or a quote so long it becomes a paragraph.

### Closing

The last slide: one call to action or a thank-you with contact details. Mirrors the title's restraint.

- **Markdown:** a `#` heading carrying the single next step, then one muted contact line. Echo the title's composition for bookend symmetry.
- **Design (in the master):** primary line `44`–`54pt`; contact `18`–`22pt` muted, one line.
- **Not:** a dense "questions?" slide stacked with logos and links.

---

## 4. Building the reference template

The template *is* the deck's design system. Build it once per brand, then reuse it across every deck. Producing it is a four-step, mostly-in-PowerPoint job; only the first step is a command.

### Step 1 — get a baseline to edit

Ask pandoc for its own default template and save it as a file you can open in PowerPoint:

```
pandoc -o reference.pptx --print-default-data-file reference.pptx
```

This writes pandoc's built-in `reference.pptx` — a minimal but valid deck whose masters and layouts are exactly the ones pandoc will populate when it renders your Markdown. Editing *this* file (rather than a deck made from scratch) guarantees the layouts you style are the layouts pandoc targets, so nothing you design gets ignored at render time.

### Step 2 — restyle the masters and theme in PowerPoint

Open `reference.pptx` in PowerPoint and edit the design, not the content. The placeholder text on the slides is throwaway; the master and theme are what carry forward.

- **Slide size:** *Design → Slide Size → Widescreen (16:9)* if it is not already 13.333 × 7.5 in (section 2).
- **Theme fonts:** *View → Slide Master → Fonts* — set the heading font and the body font to the two faces from the kit (section 2). Two families at most.
- **Theme colors:** *View → Slide Master → Colors → Customize Colors* — map the theme color slots to the kit roles: text/background to `fg`/`bg`, accent 1 to `brand`, and the rest to the neutral ramp and status hues (section 2). Every fill and text run then resolves to a role, not a literal.
- **Master and layouts:** in the master, set the title and body placeholder type sizes to the ramp (section 2), place them inside the `0.92in` / `0.75in` margins, and set list spacing on the 8pt grid. Style the table style and the section-header layout here too.

### Step 3 — save it as the design system

Save the file (keep it as `reference.pptx`, or name it per brand). That single file now encodes the type ramp, the palette at AA contrast, the spacing grid, the margins, and the table style — the entire design system in one artifact. Store it with the deck source so every render passes the same template.

### Step 4 — pass it to the render

Hand the template to the renderer as the third argument:

```
bash scripts/render.sh content.md out.pptx reference.pptx
```

Pandoc reads `reference.pptx` via `--reference-doc`, copies its masters, layouts, theme fonts, and theme colors into the output, and pours your Markdown into those styled layouts. The result inherits the whole design system without one line of geometry in the content.

A note on fonts: theme fonts apply only if the fonts are present on the machine that opens the deck — or embedded. To embed in PowerPoint: *File → Options → Save → Embed fonts in the file*, then re-save the template. Prefer widely available families to avoid the substitution that silently breaks the type ramp on someone else's machine.

---

## 5. Authoring the content Markdown

The Markdown is the model's only per-deck artifact. Keep it pure content — the template owns every visual decision, so the Markdown carries no sizes, colors, or geometry. A small, complete deck source:

```markdown
---
title: Lumen
subtitle: The one metric that moved — for founders who drown in dashboards
author: Lumen
date: 2026
---

# Why one metric beats a wall of dashboards

- Surfaces the single number that changed today
- Cuts setup to one connected source
- Replaces the daily dashboard scan with one glance

# Revenue doubled in Q3

| Quarter | Revenue ($M) |
|---|---|
| Q1 | 4.2 |
| Q2 | 5.1 |
| Q3 | 9.8 |
| Q4 | 11.0 |

# "We replaced six dashboards with one screen."

> Lumen is the first tool my whole team actually opens every morning.

— Dana Reyes, Head of Growth

# Start with one metric

One connected source. One number. Every morning.

founders@lumen.example
```

What this maps to: the YAML block becomes the **title slide**; each `#` heading becomes a **content slide** with the bullets, table, blockquote, or paragraph under it as the body; the pipe table renders as a **native table** styled by the template; the blockquote sets up the **quote** slide; the final `#` is the **closing**. Every visual property — fonts, colors, spacing, the table's header tint — comes from `reference.pptx`, so this file stays readable and re-renders identically forever.

Authoring discipline, all enforced in the Markdown rather than in code:

- **One `#`, one idea.** Each content slide opens with exactly one `#` heading carrying one claim (section 2).
- **At most five bullets, each a phrase.** A bullet that runs to a full sentence wrapping three lines is a wall-of-text tell; split the slide (section 6).
- **Interpretive titles.** A data slide's `#` states the conclusion ("Revenue doubled in Q3"), never a bare noun label ("Revenue").
- **Real alt text on every image.** Write the bracketed text as a description — "Quarterly revenue, doubling in Q3" — not a filename; the label is the accessibility text and the caption (section 9).
- **A `---` rule to split, not a shrunk font.** When one idea overflows, break it across slides with a horizontal rule; never cram by reducing size.

---

## 6. Failure modes

Each failure has a tell a reviewer catches at a glance and a concrete fix — almost always a change in the Markdown or the template, never in the renderer.

- **Wall-of-text slide.** *Tell:* paragraphs of full sentences, six-plus bullets, text wrapping three lines deep. *Fix:* one idea per slide; cut each bullet to a phrase; split with a `---` rule or a new `#`; move the prose to a leave-behind. The slide supports the speaker, it does not replace the speaker.
- **Clip-art and stock cliché.** *Tell:* cartoon icons, a businessperson-shaking-hands photo, mixed illustration styles. *Fix:* delete it from the Markdown, or replace it with one clean on-brand image and a single icon set.
- **Inconsistent spacing.** *Tell:* titles starting at a different height on each slide, gaps that vary slide to slide. *Fix:* this comes from editing geometry per slide — stop doing that. Let every slide inherit the master's placeholders; fix the spacing once in the template and every slide follows.
- **Low contrast.** *Tell:* pale gray text on white, brand-on-brand, unreadable text over a photo. *Fix:* raise every theme text/background pair to AA (4.5:1, or 3:1 for large) in the template's theme colors; for text over a photo, place the text on a dark band or use an image with a built-in scrim (section 7).
- **Default-template look.** *Tell:* pandoc's bare default theme — system fonts, flat colors, an unstyled table. *Fix:* the most common cause is forgetting the third argument. Always pass a real `reference.pptx` to `render.sh`; build it per section 4 so theme fonts, colors, and the table style are all set.
- **Too many fonts or colors.** *Tell:* three-plus typefaces, five unrelated accent hues. *Fix:* collapse the template's theme fonts to ≤ 2 families and its theme colors to the kit budget — one neutral ramp, one accent, status hues only.
- **Flat hierarchy.** *Tell:* text at one uniform size and weight, no entry point for the eye. *Fix:* set a real title-vs-body type ramp in the master so the lead element is large and the rest recedes; do not flatten everything to one size.
- **Inline styling fighting the template.** *Tell:* raw HTML, hardcoded sizes, or color spans in the Markdown overriding the theme. *Fix:* strip them — the Markdown carries content only; every visual decision belongs in `reference.pptx`.

---

## 7. Image treatment

One strong image lifts a slide; a grid of small clip-art sinks it. Treat images as a system, the same as type and color. In this pipeline an image is a Markdown image reference that pandoc places on the layout — so the discipline is about what you reference and how you prepare it, not about placement code.

- **No clip-art, ever.** Cartoon icons and stock cliché art are the loudest signal of an undesigned deck. Reference a single clean photo, a flat vector illustration in the brand style, or no image at all.
- **Preserve aspect ratio.** Reference images at their native ratio and let pandoc place them; a pre-stretched or pre-squashed source reads as broken. Crop, do not distort, when an image must fit a frame.
- **Full-bleed or framed, picked once.** Either prepare a hero image to run edge to edge with reversed text baked over a built-in scrim, or reference a framed image that sits inside the content region — and hold that choice across the deck.
- **Guarantee contrast over images.** Text on a photo needs a scrim — a darkened layer between photo and words — so the text clears AA against the busiest part of the image. Since the Markdown places no overlays, bake the scrim into the image file (export a version with a semi-transparent dark gradient) or place the text on a solid band in the layout rather than over the raw photo.
- **One icon library, one style.** When icons appear, draw them from a single set with one stroke width, colored by role (`fg` or a status hue) at the source, never a one-off hex. A second icon style breaks the deck as loudly as a second font.
- **Resolution for the room.** A projected slide is large; an image under roughly 1500 px on its long edge softens visibly. Source larger, never upscale.

---

## 8. Tables and charts on slides

Tables and charts are where the default-template look hides, because both have loud built-in styling. Each renders through the pipeline differently, and each has a rule.

### Tables — native, styled by the template

A GFM pipe table under a heading becomes a real PowerPoint table, and it inherits the **table style defined in `reference.pptx`** — which is exactly why that style must be set in the template (section 4). The default banded-row table style is the single loudest tell of an auto-generated deck.

```markdown
# Three metrics moved this quarter

| Metric        | Q2    | Q3    |
|---------------|-------|-------|
| Active teams  | 1,240 | 2,310 |
| Daily opens   | 38%   | 61%   |
| Setup time    | 12m   | 4m    |
```

Table rules:

- **Style it in the template, not per cell.** Set a restrained table style on the master once — a subtle header tint from `neutral.*`, muted or absent gridlines, body type from the ramp. Every table in every deck then inherits it.
- **One header tint, no rainbow banding.** A single quiet header fill reads as deliberate; alternating loud row colors read as the default.
- **Right-align numbers, left-align labels.** Align in the Markdown with the pipe-table colon syntax (`|---:|` for right) so columns scan cleanly.
- **Keep it small.** A slide table is a summary, not a spreadsheet — a few rows and columns. A dense grid belongs in a leave-behind or an `xlsx` export.

### Charts — build upstream, reference as a clean image

Pandoc does not generate native charts from Markdown. Build the chart upstream — a plotting library, the `xlsx` skill, or a design tool — export it as a clean image, and reference it with a Markdown image whose bracketed text is the takeaway ("Revenue doubled in Q3"). Because the chart is prepared outside the deck, all chart styling happens at the source.

Chart rules (applied where the chart is built):

- **One series leads.** Color the point you are making in `brand`; render comparison series in a single muted neutral. A chart where every series shouts in a different hue makes no point.
- **The title is the takeaway.** Put the conclusion in the slide's `#` heading and let the chart carry the evidence; the noun label belongs nowhere.
- **Subtract the junk.** Kill heavy gridlines, the chart border, and the boxed legend; mute the axis ticks. A grid of lines is noise.
- **Label sparingly.** A few direct labels on the points that matter beat a label on every bar.
- **Match the type to the question.** Trend over time wants a line or column; part-of-whole wants a single bar or — sparingly — one donut; ranking wants a sorted bar. A pie with eight slices answers nothing.
- **Export crisp and large.** Source the chart image at the room-scale resolution (section 7) so it stays sharp projected; export SVG-to-PNG at 2× where the tool allows.

---

## 9. Speaker notes and accessibility

Two finishing layers separate a deck that merely renders from one that presents well and includes everyone.

### Speaker notes

Slides carry the headline; the speaker carries the detail. Pandoc reads a fenced `notes` div under a slide and attaches it as PowerPoint speaker notes — the place for the prose you cut from the slide:

```markdown
# Why one metric beats a wall of dashboards

- Surfaces the single number that changed today
- Cuts setup to one connected source

::: notes
Open with the dashboard-fatigue stat. The three bullets are the argument;
the screenshot on the next slide is the proof. Land on "one glance."
:::
```

Notes rules:

- **Move prose off the slide and into notes.** The fix for a wall-of-text slide is often to lift the sentences into a `notes` div and leave phrases on the slide.
- **Notes are for the presenter, not the audience.** They never appear projected, so they carry the script, the data sources, and the transitions.

### Accessibility

A deck must be readable by everyone in the room and by assistive technology, not only the front row.

- **AA contrast is the floor.** Every text/background pair clears 4.5:1 (3:1 for large text and meaningful icons), set in the template's theme colors (section 2). This is the most common and most consequential miss.
- **Alt text on every image.** The bracketed alt text of a Markdown image becomes its accessibility label in the deck; write it to describe the image's point, never leave it empty.
- **Never encode meaning in color alone.** Pair a colored delta with a sign, arrow, or label so a color-blind viewer reads it too (section 2).
- **Type large enough for the back row.** Body never below `14pt`, set in the master's placeholders (section 2) — a slide that needs smaller type is carrying too much.
- **Reading order follows the source.** Pandoc lays content in document order, so write the Markdown top-to-bottom in the order you want it read; assistive tech follows that order.

---

## 10. Red flags — fast scan

A deck likely needs this skill when any of these appear:

- The pandoc default theme left in place — system fonts, flat colors, an unstyled table (the third argument to `render.sh` was forgotten).
- Three or more typefaces, or a third theme font added to the template.
- More than one accent hue competing with the brand color.
- Gray text that vanishes on its background (under 4.5:1).
- Any clip-art, or mixed illustration and icon styles.
- A bulleted slide running past five lines, or bullets wrapping three lines deep.
- A default banded-row table or a rainbow-series chart image.
- A stretched image or a squashed logo.
- Inline HTML or hardcoded styling in the Markdown overriding the template.
- Two competing focal points on one slide.
- Every slide titled with a noun label instead of a takeaway.
- Empty or missing alt text on images, or text whose only distinction is color.

---

## Final checklist

A deck passes when each line holds or carries a written, justified exception:

- [ ] **Template applied** — `render.sh` was called with a real `reference.pptx` as the third argument; the deck does not show pandoc's default theme.
- [ ] **Spacing** — margins, gaps, and offsets come from the master and map to the 8pt grid.
- [ ] **Type scale** — sizes drawn from one presenter-scale ramp set in the master; body ≥ 14pt.
- [ ] **Typefaces** — two theme fonts or fewer, installed or embedded.
- [ ] **Color budget** — theme colors are one neutral ramp + one accent + status hues only.
- [ ] **Contrast** — every theme text/background pair at AA (4.5:1 / 3:1).
- [ ] **One idea per slide** — one `#` per claim; no slide carries two; no wall of text.
- [ ] **Hierarchy** — one clear lead per slide via the master's size, weight, color, and space.
- [ ] **Margins** — a generous, consistent outer margin held across the deck via the layouts.
- [ ] **Archetypes** — each slide maps to one archetype with its Markdown form and layout.
- [ ] **Tables** — native, styled by the template, one header tint, numbers right-aligned.
- [ ] **Charts** — built upstream, one series leading, junk subtracted, exported crisp.
- [ ] **Images** — no clip-art, native aspect ratio, scrim baked in behind text on photos.
- [ ] **Speaker notes** — prose lives in `notes` divs, not on the slide face.
- [ ] **Accessibility** — alt text on every image, no meaning in color alone, reading order top-to-bottom.
- [ ] **Content purity** — the Markdown carries words only; no inline styling fights the template.
- [ ] **Opens** — the deck renders zero-exit and `unzip -l out.pptx` lists `ppt/presentation.xml`.
