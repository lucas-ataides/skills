# Beautiful PDFs

A PDF is a *printed* artifact, not a web page that happens to scroll. The page is a fixed
canvas with hard edges, no hover, no reflow, and a reader who judges the whole spread at a
glance. The governing idea matches the [web design rules](../../../design/frontend-design/references/visual-rules.md):
**professional layout is systematic, not inspired.** Pick a small set of scales once, snap
every value to them, and the document reads as designed. The default browser "Print to PDF"
breaks all of this — that look is the failure to design, and avoiding it is the whole job.

The division of labor is the point. The LLM writes only the content as Markdown;
`scripts/render.sh` renders it deterministically through `pandoc` plus a PDF engine. The
design system below is encoded **once** in a CSS stylesheet (for the HTML-based engines) or a
pandoc template (for the LaTeX engines) — never as per-run drawing code. This reference covers
the render workflow, the print design system, the Markdown-to-PDF mapping, how to express the
system as CSS, document archetypes, tables, the failure modes, and a worked example.

---

## 1. The render workflow — Markdown in, designed PDF out

One script renders every PDF: `scripts/render.sh`. It wraps a single `pandoc` invocation, so
the same Markdown plus the same stylesheet yields the same document on every run.

```bash
# Auto-detected engine, default styling.
scripts/render.sh content.md out.pdf

# Named engine plus a print stylesheet (CSS engines only).
scripts/render.sh content.md out.pdf --engine weasyprint --css print.css

# Named LaTeX engine (styling comes from a pandoc template, below).
scripts/render.sh content.md out.pdf --engine xelatex

# Self-check the toolchain (skips cleanly when no engine is installed).
scripts/render.sh --selftest
```

The interface is fixed: `render.sh <content.md> <out.pdf> [--engine ENGINE] [--css FILE]`. A
zero exit and a `wrote out.pdf` line mean success; a non-zero exit names what to fix.

### Engine auto-detection and the two engine families

With no `--engine`, the script picks the first engine present on `PATH` from this order:

```
weasyprint  wkhtmltopdf  typst  tectonic  xelatex  pdflatex
```

The engines split into two families, and the family decides how the design system is
expressed:

- **CSS engines — `weasyprint` and `wkhtmltopdf`.** These render HTML and CSS to PDF with a
  real print engine, so the `--css` stylesheet *is* the design system: `@page` rules, named
  margin boxes, running headers and footers, page counters, page-break control, and full
  control of type, color, and spacing. The `--css` flag applies only to this family. Default
  to a CSS engine for any document whose value is in its *design* — reports, proposals,
  invoices, one-pagers, brochures, statements.
- **LaTeX and typst engines — `typst`, `tectonic`, `xelatex`, `pdflatex`.** Pandoc drives
  these directly; styling comes from a **pandoc template** plus a small set of `-V` variables
  rather than CSS. The `--css` flag is ignored here. Reach for this family when LaTeX
  typesetting is the goal (dense math, footnote-heavy academic prose) or when no CSS engine is
  installed.

### Choosing the engine

| Situation | Engine family | Styling input |
| --- | --- | --- |
| Designed report, proposal, invoice, one-pager; brand color and layout matter | `weasyprint` (CSS) | `--css print.css` |
| Existing print stylesheet, or a layout that reads more naturally as CSS | `weasyprint` / `wkhtmltopdf` (CSS) | `--css print.css` |
| Heavy math, footnotes, or a LaTeX house style is required | `xelatex` / `tectonic` (LaTeX) | pandoc template + `-V` |
| Only a LaTeX or typst engine is installed | the detected LaTeX/typst engine | pandoc template + `-V` |

When two engines fit, default to `weasyprint`: HTML/CSS is the most legible, most editable, and
most reviewable description of a designed page, and the `--css` flag wires it straight into the
script. WeasyPrint reads CSS paged-media features that browsers ignore or implement poorly —
the `@page` at-rule with named margin boxes (`@top-center`, `@bottom-right`), the
`counter(page)` and `counter(pages)` counters for "Page 3 of 12", `string-set` for running
section titles in the header, and `break-before` / `break-inside` for page-break control. That
print stylesheet carries the entire design.

---

## 2. The print design system

The values below are the print analogue of the web design scales, and the user encodes them in
the CSS stylesheet (CSS engines) or the pandoc template (LaTeX engines). The page geometry is
in **millimetres** (or inches), and type is in **points** (1 pt = 1/72 inch). A4 is 210×297 mm;
US Letter is 8.5×11 in (216×279 mm). Snap every dimension to the scales here.

### Page and margins

- **Margins are generous, never cramped.** A designed page wants **18–25 mm** (≈ 0.7–1.0 in)
  on every side as the floor. The single loudest tell of an undesigned PDF is text crammed to
  a 10 mm edge. Wide margins read as confident and give the eye room. In CSS this is the
  `@page { margin: ... }` rule; in a LaTeX template it is the `geometry` package margins (or
  pandoc's `-V geometry:margin=22mm`).
- **Asymmetric margins for bound or formal documents.** A larger inside/bottom margin
  (a "gutter") balances the optical center; classic book proportions put the bottom margin
  larger than the top.
- **One content column** for prose at a controlled measure; a 12-unit grid for dense or
  multi-panel layouts such as an invoice or a dashboard one-pager.

### Type scale

Pick sizes from a modular ramp (≈ 1.25 ratio), tuned for print:

```
9   10.5   12   14   17   21   28   36   48
```

- **Body copy: 10.5–12 pt** for print (print resolution makes 11 pt comfortable; screen-only
  PDFs tolerate 12 pt). Below 9 pt is fine print, never body.
- **Measure: 60–80 characters per line.** On an A4 page this is what drives the body column
  width — a full-bleed line across a 210 mm page runs far past 100 characters and exhausts
  the reader. Constrain the text column, not the page.
- **Line height (leading): 1.4–1.5** for body, **1.1–1.2** for large headings. Tight leading
  on body and loose leading on a display heading both look wrong.
- **Two typefaces maximum.** One for headings, one for body, or a single family across both.
  A serif body (Source Serif, Charter, Georgia) reads well in long-form print; a clean sans
  (Inter, Source Sans, Helvetica) suits data, invoices, and UI-flavored documents. In CSS this
  is the `font-family` declarations; in a LaTeX template the `mainfont` / `sansfont` variables
  (xelatex or tectonic, which read system fonts).

### Baseline grid

Lock vertical rhythm to a **baseline grid**: choose a base unit (commonly the body leading,
e.g. 15 pt) and make every vertical measure — space above a heading, paragraph spacing, table
row height — a multiple of it. Baselines then line up across columns and down the page, which
is the difference between a typeset page and a word-processor page. In CSS, set `line-height`
to the base and express every margin as a multiple of it; in a LaTeX template, set the base
`\baselineskip` and derive spacing from it. One base unit, every measure a multiple — that is
the rule the renderer enforces only if the stylesheet states it.

### Color and contrast

- **One neutral ramp + one brand accent + semantic hues only**, matching the web color
  budget. Most of the page is near-black text on near-white paper.
- **AA contrast is the floor.** Body text and meaningful marks sit at **≥ 4.5:1** against the
  paper; large text (≥ 18 pt, or ≥ 14 pt bold) and icons at **≥ 3:1**. Light-gray captions
  are the most common print contrast failure — a `#999` on white measures ≈ 2.8:1 and fails.
  Print exaggerates low contrast because there is no backlight, so darken until the ratio
  clears AA.
- **Tints carry structure without ink-heavy borders.** A 5–8% accent tint behind a table
  header or a callout separates it more elegantly than a hard rule.
- **Mind the gamut.** Screen-vivid colors can shift on a printer; a CMYK-safe palette holds
  up. For screen-only PDFs, RGB is fine.

### Headers, footers, page numbers, cover

- **Running header / footer** carry the document title, the section, and the page number, set
  small (8–9 pt) and muted (a mid-gray), seated inside the margin box so the eye reads them as
  furniture, not content. In CSS engines this is the `@page` named margin boxes
  (`@top-center`, `@bottom-right`); in a LaTeX template it is the `fancyhdr` header/footer
  fields.
- **Page numbers** read "Page X of Y" or a plain numeral, placed consistently (outer or
  center of the footer). The cover page carries no number. CSS expresses the count with
  `counter(page)` and `counter(pages)`; a LaTeX template uses `\thepage` and `\pageref`.
- **A cover page** lifts any multi-page document: a generous top margin, the title at display
  size, a subtitle, the date and author, and one brand element (a rule, a logo, a color
  band). The cover sets the tone before a word is read. In Markdown, a level-1 title plus a
  metadata block (or a templated title page) produces it.

### Page-break discipline (orphans and widows)

- **No orphan or widow lines.** A single line of a paragraph stranded at the foot of a page
  (an orphan) or carried alone to the top of the next (a widow) breaks the read. Set
  `orphans: 3; widows: 3;` in the CSS body; a LaTeX template sets `\clubpenalty` and
  `\widowpenalty` high.
- **A heading never sits at the foot of a page** with its body on the next. Use
  `break-after: avoid` on headings in CSS; a LaTeX template relies on the `needspace` package
  or section penalties.
- **A table row never splits across pages**, and the header row repeats on each page a long
  table spans. CSS sets `break-inside: avoid` on rows; the LaTeX `longtable` environment
  repeats the header automatically.

---

## 3. The Markdown → PDF mapping

The LLM writes content as Markdown; `pandoc --from gfm` converts each construct to a styled
element the engine renders. Knowing the mapping is what lets the author target the stylesheet
without writing HTML or LaTeX by hand.

| Markdown construct | Pandoc output (CSS engine) | Style it via |
| --- | --- | --- |
| `# Title` … `###### …` | `<h1>`–`<h6>` | heading rules in the type scale |
| Paragraph text | `<p>` | body `font` + `line-height` |
| `**bold**`, `*italic*` | `<strong>`, `<em>` | weight / style only |
| `> quote` | `<blockquote>` | tint band or left rule |
| GFM table (pipes) | `<table>` / `<thead>` / `<tbody>` | the table rules in section 5 |
| Fenced code | `<pre><code>` | mono font, tint background |
| `- ` / `1. ` lists | `<ul>` / `<ol>` | indent and marker spacing |
| `![alt]\(img.png)` | `<img>` | width cap, caption styling |
| `---` | `<hr>` | a hairline rule, not a heavy bar |

Two GFM constructs carry the most design weight:

- **Headings build the hierarchy.** Use exactly one `#` for the document title, `##` for
  sections, `###` for subsections. The stylesheet maps each level to one size on the type ramp
  — never skip a level to reach a size, because the size belongs to the level, not the author's
  whim.
- **Pipe tables are the data.** Author them as GFM pipe tables with a header row; the
  stylesheet does the borderless styling, the right-alignment, and the header tint. The
  alignment colons in the GFM separator row (`---:` for right) set per-column alignment, so
  numeric columns get `---:` and read right-aligned without any HTML.

For anything CSS cannot reach from Markdown — a precise cover layout, a multi-column header
band — author that fragment as raw HTML inside the Markdown (pandoc passes HTML through to the
CSS engines) and style it from the same stylesheet, exactly as the worked example does.

---

## 4. Expressing the design system as CSS

For the CSS engines, the `--css` stylesheet replaces every per-run drawing decision with one
declarative ruleset. Each design target from section 2 maps to a CSS construct:

- **Page geometry and margins** → the `@page` at-rule: `size: A4;` and `margin: 22mm 20mm;`.
  Named margin boxes (`@bottom-center { content: ... }`) hold the running furniture.
- **Type scale and leading** → one `font` shorthand on `body` (`font: 11pt/1.5 ...`) and a size
  per heading drawn from the ramp; no off-ramp size appears anywhere.
- **Fonts** → `font-family` stacks with web-safe or bundled fallbacks; WeasyPrint embeds the
  faces it can resolve, so a serif body and a sans heading are two declarations.
- **Color and contrast** → CSS custom properties for the palette (`--ink`, `--muted`,
  `--accent`), each chosen to clear AA on paper, referenced everywhere instead of raw hexes.
- **Running headers and footers** → the `@page` margin boxes plus `counter(page)` /
  `counter(pages)` for "Page X of Y", and `string-set` to carry a running section title.
- **Tables** → `border-collapse: collapse`, a header `background` tint, hairline
  `border-bottom` rows, and `text-align: right; font-variant-numeric: tabular-nums;` on numeric
  cells (section 5).
- **Break discipline** → `orphans` / `widows` on the body, `break-after: avoid` on headings,
  `break-inside: avoid` on rows (section 2).

The worked example in section 8 is a complete such stylesheet, embedded in the page; lift its
`<style>` block into a standalone `print.css` and pass it with `--css` to reuse it across
documents.

### The LaTeX-template path

For the LaTeX and typst engines, the same targets are encoded in a **pandoc template** and a
few `-V` variables instead of CSS. Margins come from the `geometry` package, fonts from
`mainfont` / `sansfont` (under `xelatex` or `tectonic`), running furniture from `fancyhdr`, and
break discipline from `\clubpenalty` / `\widowpenalty` / `needspace`. Pass a custom template
through pandoc and set the variables; the design targets — the 18–25 mm margins, the 1.25 type
ramp, AA contrast, the baseline grid — stay identical, only the dialect changes.

---

## 5. Document archetypes

Each archetype below names the layout that reads as designed for that purpose. The author picks
the archetype, writes the sections in Markdown, and the stylesheet enforces the look.

### Report

A cover page; a running header (title left, section right) and footer (page number); a single
body column at a 65–75 character measure with generous margins; a clear heading hierarchy
(section / subsection / body) drawn from the type scale; figures and tables set apart with
whitespace and a caption. The body leads; chrome recedes.

### Proposal

Cover with the client name and date; an executive-summary block set apart by a tint or a wide
margin; scannable section headings; a pricing table near the end; a closing call to action.
The visual tone signals competence — restraint over decoration wins the deal.

### Invoice

A 12-unit grid; the issuer block and a logo top-left, the document meta (invoice number, date,
due date) top-right; a billing-address block; a line-item table with right-aligned numeric
columns and a clear totals block (subtotal, tax, total) set in heavier weight; payment terms
in the footer. Alignment of the numeric columns is the make-or-break detail.

### One-pager

A single page that must work at a glance: a strong headline, two or three supporting blocks
on a grid, one chart or metric set, and a footer with contact or source. No second page means
hierarchy does the work — the eye must find the one thing first, then the rest.

---

## 6. Tables and data

Tables are where amateur PDFs collapse into a grid of boxes. Design them like data, not like a
spreadsheet. Author the table as a GFM pipe table; the stylesheet (or template) carries the
look:

- **No vertical rules, minimal horizontal rules.** A header underline and a thin rule above
  the totals row carry the whole structure. Replace inner gridlines with **row striping** (a
  faint neutral tint on alternate rows) or with whitespace alone. Border-soup is the failure
  mode (see the web rules' section 4). In CSS this is `border-collapse: collapse` with only a
  `border-bottom` on header and rows.
- **Align numbers right, text left, headers to match their column.** Right-aligned numerals
  let the reader compare magnitudes down a column. Set the alignment in the GFM separator row
  (`---:` for a right-aligned column) and add a tabular-figures font feature
  (`font-variant-numeric: tabular-nums`) so digit columns align.
- **Padding ≥ 6 pt inside cells**, and a row height locked to the baseline grid. Cramped cells
  read as a dump; airy cells read as a report. CSS sets cell `padding`; a LaTeX template sets
  `\arraystretch` and column padding.
- **Header row in heavier weight** on a tint, repeated on every page the table spans. CSS
  styles `thead th`; LaTeX `longtable` repeats the header.
- **One emphasis per row at most.** A totals row in bold, or a flagged cell in the accent
  color, not both competing.

For charts, render to SVG or a high-DPI raster and place the image with the Markdown image
syntax (`![alt]\(chart.svg)`); WeasyPrint embeds SVG cleanly and scales it crisply. Either way, the chart obeys the same color
budget and type scale as the page around it — a chart in a clashing default palette undoes the
design.

---

## 7. Failure modes and red flags

These are the recurring ways a PDF reads as undesigned. Each maps to a fix expressed in the
stylesheet or template, never in per-run code.

| Failure mode | Symptom | Fix |
| --- | --- | --- |
| **Default-browser-print look** | System margins, Times New Roman, blue underlined links, a URL footer | Author a real print stylesheet or template; set `@page` margins, type scale, color |
| **Cramped margins** | Text packed to a 10 mm edge, no breathing room | Floor of 18–25 mm on every side (`@page margin` / `geometry`) |
| **Orphan / widow lines** | A lone line stranded at a page boundary | `orphans: 3; widows: 3;` / high `\clubpenalty` and `\widowpenalty` |
| **Heading at page foot** | A heading printed with no body under it | `break-after: avoid` / `needspace` |
| **Low-contrast text** | Pale gray captions that vanish on paper | Darken to AA (≥ 4.5:1); print has no backlight to rescue it |
| **Table border-soup** | Every cell fenced in gridlines | Strip inner rules; use striping or whitespace |
| **Off-scale spacing** | A 13 pt gap here, a 27 pt gap there | Snap every measure to the baseline grid in the stylesheet |
| **Too many fonts** | Three faces and six weights with no system | Collapse to two faces; vary by weight |
| **Split table row** | A row broken across two pages | `break-inside: avoid` on rows; repeat the header |
| **Missing page furniture** | No header, footer, page number, or cover | Add running header/footer via `@page` boxes, "Page X of Y", a cover |

### Red flags — fast scan

A PDF likely needs this skill when any of the items below appear:

- The page looks like a printed browser window (system margins, default serif, link chrome).
- Margins under 15 mm, or text touching the trim edge.
- Lone lines stranded at the top or bottom of a page.
- Gray text that disappears against the paper (under 4.5:1).
- A table fenced in full gridlines, or numeric columns left-aligned.
- Spacing values off any consistent grid.
- Three or more typefaces.
- A multi-page document with no header, footer, page number, or cover.

---

## 8. Worked example — one designed invoice page

This example is the CSS path end to end: a Markdown body the LLM writes, a print stylesheet that
encodes the design system, and the `render.sh` command that joins them. The stylesheet sets
`@page` margins and a footer page counter, an 8-step spacing rhythm, a controlled type scale,
AA contrast, and a borderless line-item table with right-aligned numerals and a totals block.

### The content (`invoice.md`)

The author writes the document as Markdown. The header band and totals block need a precise
two-column layout, so those fragments are raw HTML inside the Markdown (pandoc passes HTML
through to the CSS engines); the line items are a plain GFM pipe table with `---:` marking the
right-aligned numeric columns.

```markdown
<div class="head">
  <div class="brand">Northwind Studio<small>123 Harbor Way, Lisbon</small></div>
  <div class="meta">
    <b>Invoice #2026-0142</b><br>
    Issued 22 Jun 2026<br>
    Due 22 Jul 2026
  </div>
</div>

## Billed to

Acme Corporation &middot; 500 Market Street &middot; Porto

## Line items

| Description           |  Qty |     Rate |   Amount |
| :-------------------- | ---: | -------: | -------: |
| Brand identity system |    1 | 4,200.00 | 4,200.00 |
| Landing page design   |    3 |   900.00 | 2,700.00 |
| Print collateral      |    1 | 1,150.00 | 1,150.00 |

<div class="totals">
  <div class="row"><span>Subtotal</span><span class="num">8,050.00</span></div>
  <div class="row"><span>VAT (23%)</span><span class="num">1,851.50</span></div>
  <div class="row grand"><span>Total</span><span class="num">&euro;9,901.50</span></div>
</div>

<footer>Payment within 30 days to IBAN PT50 0000 0000 0000 0000 0000 0 &middot;
Thank you for your business.</footer>
```

### The stylesheet (`print.css`)

This is the design system as one declarative ruleset. Lift it into a standalone file and reuse
it across documents with `--css`.

```css
:root {
  --ink: #1a1a1a;        /* gray-900, body — ~16:1 on white */
  --muted: #5b5b5b;      /* gray-600 captions — ~7:1, clears AA */
  --line: #d8d8d8;       /* gray-300 hairline */
  --tint: #f4f6fb;       /* faint accent tint for the header row */
  --accent: #2b50d8;     /* brand accent — ~6:1 on white */
}

/* Print stylesheet: page geometry, margins, and a footer page counter. */
@page {
  size: A4;
  margin: 22mm 20mm;     /* generous, never cramped */
  @bottom-center {
    content: "Page " counter(page) " of " counter(pages);
    font: 9pt "Source Sans 3", Helvetica, sans-serif;
    color: #5b5b5b;
  }
}

body {
  font: 11pt/1.5 "Source Sans 3", Helvetica, sans-serif;  /* baseline leading 1.5 */
  color: var(--ink);
  orphans: 3; widows: 3;                                   /* no stranded lines */
  margin: 0;
}

/* Header band: issuer left, document meta right, on a 12-unit feel. */
.head { display: flex; justify-content: space-between; align-items: flex-start; }
.brand { font-size: 21pt; font-weight: 700; letter-spacing: -0.01em; }
.brand small { display: block; font-size: 10pt; font-weight: 400; color: var(--muted); }
.meta { text-align: right; font-size: 10pt; color: var(--muted); }
.meta b { color: var(--ink); font-size: 14pt; }

h2 { font-size: 10pt; font-weight: 600; color: var(--muted);
     text-transform: uppercase; letter-spacing: 0.06em;
     break-after: avoid;                          /* heading never stranded at a foot */
     margin: 32px 0 8px; }                         /* space off the grid: 32 / 8 */

/* Line-item table: no inner gridlines, header tint, numerals right-aligned. */
table { width: 100%; border-collapse: collapse; font-size: 11pt; }
thead th { background: var(--tint); text-align: left;
           padding: 8px 10px; border-bottom: 1px solid var(--line); }
tbody td { padding: 8px 10px; border-bottom: 1px solid var(--line); }
td[align="right"], th[align="right"] { font-variant-numeric: tabular-nums; }
tr { break-inside: avoid; }                        /* a row never splits a page */

/* Totals block: heavier weight, a rule above the grand total. */
.totals { width: 46%; margin-left: auto; margin-top: 16px; font-size: 11pt; }
.totals .row { display: flex; justify-content: space-between; padding: 6px 0; }
.totals .num { font-variant-numeric: tabular-nums; }
.totals .grand { border-top: 2px solid var(--ink); margin-top: 6px;
                 padding-top: 10px; font-size: 14pt; font-weight: 700; }

footer { margin-top: 40px; font-size: 9pt; color: var(--muted);
         border-top: 1px solid var(--line); padding-top: 10px; }
```

### The render command

```bash
scripts/render.sh invoice.md invoice.pdf --engine weasyprint --css print.css
```

The command prints `wrote invoice.pdf` and exits zero. Pandoc converts the GFM (the `---:`
columns become right-aligned cells, the `##` headings become `<h2>`), and WeasyPrint applies
`print.css` to produce the designed page.

Why this page reads as designed, named against the system:

- **Print stylesheet, not browser defaults** — `@page` sets 22×20 mm margins and a real
  "Page X of Y" footer counter (section 4), so the page never looks like a printed window.
- **Generous margins** — 22 mm top/bottom, 20 mm sides, well above the cramped floor (section 2).
- **One type scale** — 9 / 10 / 11 / 14 / 21 pt drawn from the ramp; body at 11 pt/1.5 leading
  (section 2).
- **AA contrast** — `#1a1a1a` body and `#5b5b5b` captions both clear 4.5:1 on white (section 2).
- **Borderless table** — header tint and hairline row rules replace gridlines; the quantity,
  rate, and amount columns are right-aligned with tabular figures (section 6).
- **Page-break safety** — `break-inside: avoid` keeps a line-item row whole across a page, and
  `orphans` / `widows` strand no lines (section 2 break discipline).
- **A clear totals block** — the grand total leads in heavier weight above a rule, the one
  emphasis the eye should land on (section 6).

The same document under a LaTeX engine swaps `print.css` for a pandoc template that sets the
identical targets — 22 mm `geometry` margins, an 11 pt body, `fancyhdr` page numbers,
`longtable` for the line items — proving the design system, not the tool, is what produces a
beautiful page.

---

## Final checklist

A PDF passes when each line holds or carries a written, justified exception. The procedure in
the [SKILL](../SKILL.md) ends on this list:

- [ ] **Renders** — `scripts/render.sh` produces the PDF with a zero exit status and a
      `wrote out.pdf` line, no warnings.
- [ ] **Opens** — the file opens in a viewer and the expected page count is present.
- [ ] **Margins** — every side at 18–25 mm (or the stated print spec), never cramped.
- [ ] **Type scale** — sizes from one modular ramp; body 10.5–12 pt; two faces or fewer.
- [ ] **Baseline grid** — vertical measures are multiples of the base leading.
- [ ] **Contrast** — text and meaningful marks at AA (≥ 4.5:1 / ≥ 3:1).
- [ ] **Break discipline** — no orphans or widows; no heading stranded at a page foot; no row
      split across pages.
- [ ] **Tables** — no border-soup; numerals right-aligned; header repeated on long tables.
- [ ] **Furniture** — running header/footer, page numbers, and a cover where the archetype
      calls for one.
- [ ] **Not the default-print look** — a real stylesheet or pandoc template drove the page.
