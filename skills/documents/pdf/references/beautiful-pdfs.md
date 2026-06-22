# Beautiful PDFs

A PDF is a *printed* artifact, not a web page that happens to scroll. The page is a fixed
canvas with hard edges, no hover, no reflow, and a reader who judges the whole spread at a
glance. The governing idea matches the [web design rules](../../../design/web-design-guidelines/references/web-design-rules.md):
**professional layout is systematic, not inspired.** Pick a small set of scales once, snap
every value to them, and the document reads as designed. The default browser "Print to PDF"
breaks all of this — that look is the failure to design, and avoiding it is the whole job.

This reference covers the deterministic toolchain, a print design system, document
archetypes, tables, the failure modes, and a worked example that renders one designed page.

---

## 1. The toolchain — pick the path that fits the document

Three deterministic generators cover almost every PDF. The choice turns on how much the
layout is *designed* versus *computed*, and on the source format.

### (a) HTML/CSS → PDF via WeasyPrint — the default for designed documents

WeasyPrint renders HTML and CSS to PDF with a real print engine: `@page` rules, named page
margins, running headers and footers, page counters, page breaks, and full control of type,
color, and spacing. This is the strongest path for any document whose value is in its
*design* — reports, proposals, invoices, one-pagers, brochures, statements.

Reach for WeasyPrint when these hold:

- The layout is visual and benefits from CSS (a type scale, a grid, brand color, a cover).
- The content is known at render time, assembled from data into an HTML template.
- A print stylesheet (`@page`, `@media print`) expresses the design more naturally than code.

```bash
# Install (CLI + library both ship in the same package).
pip install weasyprint

# Render an HTML file to PDF from the command line.
weasyprint report.html report.pdf

# Render a string or template output from Python.
python -c "from weasyprint import HTML; HTML('report.html').write_pdf('report.pdf')"
```

WeasyPrint reads CSS paged-media features that browsers ignore or implement poorly: the
`@page` at-rule with named margin boxes (`@top-center`, `@bottom-right`), the `counter(page)`
and `counter(pages)` counters for "Page 3 of 12", `string-set` for running section titles in
the header, and `break-before` / `break-inside` for page-break control. The print stylesheet
**is** the design system here.

### (b) reportlab — for programmatic, pixel-precise, or computed layouts

reportlab builds a PDF from Python primitives placed at exact coordinates. The output is
deterministic to the point. Reach for reportlab when the layout is *computed* rather than
*designed by hand*: a high-volume batch of statements, a chart or diagram drawn from data,
a label sheet, a certificate filled from a record, or any case where absolute placement and
no HTML/CSS round-trip is the requirement.

```bash
pip install reportlab
```

reportlab offers two levels: the low-level `canvas` (draw text, lines, and shapes at `(x, y)`
in points) and the high-level `platypus` flowables (`Paragraph`, `Table`, `Spacer`, `Image`
that flow down a frame and break pages automatically). Use `platypus` for flowing text and
tables; drop to `canvas` for a fixed header, a watermark, or precise marks.

### (c) pandoc — for Markdown → PDF

pandoc converts Markdown (and many other formats) to PDF through a LaTeX or HTML engine.
Reach for pandoc when the source is prose in Markdown and the goal is a clean, typeset
document without hand-built HTML: documentation, a README turned handout, an article, notes.
Drive the design with a template and a small set of variables rather than default styling.

```bash
# Markdown to PDF via a print-quality HTML engine (WeasyPrint as the backend).
pandoc report.md -o report.pdf --pdf-engine=weasyprint --css print.css

# Markdown to PDF via LaTeX (xelatex gives full font control).
pandoc report.md -o report.pdf --pdf-engine=xelatex -V mainfont="Source Serif 4"
```

### Choosing between the three

| Situation | Path |
| --- | --- |
| Designed report, proposal, invoice, one-pager; brand color and layout matter | WeasyPrint |
| Computed or high-volume layout; charts, labels, certificates; exact coordinates | reportlab |
| Source is Markdown prose; want a clean typeset result fast | pandoc |
| Existing web template already styled for print | WeasyPrint |

When two paths fit, default to WeasyPrint — HTML/CSS is the most legible, most editable, and
most reviewable description of a designed page.

---

## 2. The print design system

The values below are the print analogue of the web design scales. The page geometry is in
**millimetres** (or inches), and type is in **points** (1 pt = 1/72 inch). A4 is 210×297 mm;
US Letter is 8.5×11 in (216×279 mm). Snap every dimension to the scales here.

### Page and margins

- **Margins are generous, never cramped.** A designed page wants **18–25 mm** (≈ 0.7–1.0 in)
  on every side as the floor. The single loudest tell of an undesigned PDF is text crammed to
  a 10 mm edge. Wide margins read as confident and give the eye room.
- **Asymmetric margins for bound or formal documents.** A larger inside/bottom margin
  (a "gutter") balances the optical center; classic book proportions put the bottom margin
  larger than the top.
- **One content column** for prose at a controlled measure; a 12-unit grid for dense or
  multi-panel layouts (an invoice, a dashboard one-pager).

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
  (Inter, Source Sans, Helvetica) suits data, invoices, and UI-flavored documents.

### Baseline grid

Lock vertical rhythm to a **baseline grid**: choose a base unit (commonly the body leading,
e.g. 15 pt) and make every vertical measure — space above a heading, paragraph spacing, table
row height — a multiple of it. Baselines then line up across columns and down the page, which
is the difference between a typeset page and a word-processor page. In CSS, set
`line-height` to the base and express margins as multiples of it; in reportlab, set
`leading` on every paragraph style to the same base.

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
  furniture, not content.
- **Page numbers** read "Page X of Y" or a plain numeral, placed consistently (outer or
  center of the footer). The cover page carries no number.
- **A cover page** lifts any multi-page document: a generous top margin, the title at display
  size, a subtitle, the date and author, and one brand element (a rule, a logo, a color
  band). The cover sets the tone before a word is read.

### Page-break discipline (orphans and widows)

- **No orphan or widow lines.** A single line of a paragraph stranded at the foot of a page
  (orphan) or carried alone to the top of the next (widow) breaks the read. Set
  `orphans: 3; widows: 3;` in CSS; in reportlab, `KeepTogether` holds a block intact.
- **A heading never sits at the foot of a page** with its body on the next. Use
  `break-after: avoid` on headings (CSS) or `keepWithNext` on the heading style (reportlab).
- **A table row never splits across pages**, and the header row repeats on each page a long
  table spans.

---

## 3. Document archetypes

Each archetype below names the layout that reads as designed for that purpose.

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

## 4. Tables and data

Tables are where amateur PDFs collapse into a grid of boxes. Design them like data, not like a
spreadsheet:

- **No vertical rules, minimal horizontal rules.** A header underline and a thin rule above
  the totals row carry the whole structure. Replace inner gridlines with **row striping** (a
  faint neutral tint on alternate rows) or with whitespace alone. Border-soup is the failure
  mode (see the web rules' section 4).
- **Align numbers right, text left, headers to match their column.** Right-aligned numerals
  let the reader compare magnitudes down a column. Use a tabular-figures font feature so digit
  columns align.
- **Padding ≥ 6 pt inside cells**, and a row height locked to the baseline grid. Cramped cells
  read as a dump; airy cells read as a report.
- **Header row in heavier weight** on a tint, repeated on every page the table spans.
- **One emphasis per row at most.** A totals row in bold, or a flagged cell in the accent
  color, not both competing.

For charts, render to SVG or a high-DPI raster and place the image; or draw vector shapes
directly in reportlab. Either way, the chart obeys the same color budget and type scale as the
page around it — a chart in a clashing default palette undoes the design.

---

## 5. Failure modes and red flags

These are the recurring ways a PDF reads as undesigned. Each maps to a fix.

| Failure mode | Symptom | Fix |
| --- | --- | --- |
| **Default-browser-print look** | System margins, Times New Roman, blue underlined links, a URL footer | Author a real print stylesheet or template; set `@page` margins, type scale, color |
| **Cramped margins** | Text packed to a 10 mm edge, no breathing room | Floor of 18–25 mm on every side |
| **Orphan / widow lines** | A lone line stranded at a page boundary | `orphans: 3; widows: 3;` or `KeepTogether` |
| **Heading at page foot** | A heading printed with no body under it | `break-after: avoid` / `keepWithNext` |
| **Low-contrast text** | Pale gray captions that vanish on paper | Darken to AA (≥ 4.5:1); print has no backlight to rescue it |
| **Table border-soup** | Every cell fenced in gridlines | Strip inner rules; use striping or whitespace |
| **Off-scale spacing** | A 13 pt gap here, a 27 pt gap there | Snap every measure to the baseline grid |
| **Too many fonts** | Three faces and six weights with no system | Collapse to two faces; vary by weight |
| **Split table row** | A row broken across two pages | `break-inside: avoid` on rows; repeat the header |
| **Missing page furniture** | No header, footer, page number, or cover | Add running header/footer, "Page X of Y", a cover |

### Red flags — fast scan

A PDF likely needs this skill when any of these appear:

- The page looks like a printed browser window (system margins, default serif, link chrome).
- Margins under 15 mm, or text touching the trim edge.
- Lone lines stranded at the top or bottom of a page.
- Gray text that disappears against the paper (under 4.5:1).
- A table fenced in full gridlines, or numeric columns left-aligned.
- Spacing values off any consistent grid.
- Three or more typefaces.
- A multi-page document with no header, footer, page number, or cover.

---

## 6. Worked example — one designed page with WeasyPrint

This HTML and CSS renders a single, designed invoice page: a print stylesheet with `@page`
margins and a footer page counter, an 8-step spacing rhythm, a controlled type scale, AA
contrast, and a borderless line-item table with right-aligned numerals and a totals block.
Save as `invoice.html` and render with `weasyprint invoice.html invoice.pdf`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
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
       margin: 32px 0 8px; }                     /* space off the grid: 32 / 8 */

  /* Line-item table: no inner gridlines, header tint, numerals right-aligned. */
  table { width: 100%; border-collapse: collapse; font-size: 11pt; }
  thead th { background: var(--tint); text-align: left;
             padding: 8px 10px; border-bottom: 1px solid var(--line); }
  tbody td { padding: 8px 10px; border-bottom: 1px solid var(--line); }
  .num { text-align: right; font-variant-numeric: tabular-nums; }
  tr { break-inside: avoid; }                    /* a row never splits a page */

  /* Totals block: heavier weight, a rule above the grand total. */
  .totals { width: 46%; margin-left: auto; margin-top: 16px; font-size: 11pt; }
  .totals .row { display: flex; justify-content: space-between; padding: 6px 0; }
  .totals .grand { border-top: 2px solid var(--ink); margin-top: 6px;
                   padding-top: 10px; font-size: 14pt; font-weight: 700; }

  footer { margin-top: 40px; font-size: 9pt; color: var(--muted);
           border-top: 1px solid var(--line); padding-top: 10px; }
</style>
</head>
<body>
  <div class="head">
    <div class="brand">Northwind Studio<small>123 Harbor Way, Lisbon</small></div>
    <div class="meta">
      <b>Invoice #2026-0142</b><br>
      Issued 22 Jun 2026<br>
      Due 22 Jul 2026
    </div>
  </div>

  <h2>Billed to</h2>
  <div>Acme Corporation &middot; 500 Market Street &middot; Porto</div>

  <h2>Line items</h2>
  <table>
    <thead>
      <tr><th>Description</th><th class="num">Qty</th>
          <th class="num">Rate</th><th class="num">Amount</th></tr>
    </thead>
    <tbody>
      <tr><td>Brand identity system</td><td class="num">1</td>
          <td class="num">4,200.00</td><td class="num">4,200.00</td></tr>
      <tr><td>Landing page design</td><td class="num">3</td>
          <td class="num">900.00</td><td class="num">2,700.00</td></tr>
      <tr><td>Print collateral</td><td class="num">1</td>
          <td class="num">1,150.00</td><td class="num">1,150.00</td></tr>
    </tbody>
  </table>

  <div class="totals">
    <div class="row"><span>Subtotal</span><span class="num">8,050.00</span></div>
    <div class="row"><span>VAT (23%)</span><span class="num">1,851.50</span></div>
    <div class="row grand"><span>Total</span><span class="num">€9,901.50</span></div>
  </div>

  <footer>Payment within 30 days to IBAN PT50 0000 0000 0000 0000 0000 0 &middot;
    Thank you for your business.</footer>
</body>
</html>
```

Why this page reads as designed, named against the system:

- **Print stylesheet, not browser defaults** — `@page` sets 22×20 mm margins and a real
  "Page X of Y" footer counter (section 1a), so the page never looks like a printed window.
- **Generous margins** — 22 mm top/bottom, 20 mm sides, well above the cramped floor (section 2).
- **One type scale** — 9 / 10 / 11 / 14 / 21 pt drawn from the ramp; body at 11 pt/1.5 leading
  (section 2).
- **AA contrast** — `#1a1a1a` body and `#5b5b5b` captions both clear 4.5:1 on white (section 2).
- **Borderless table** — header tint and hairline row rules replace gridlines; quantity, rate,
  and amount columns are right-aligned with tabular figures (section 4).
- **Page-break safety** — `break-inside: avoid` keeps a line-item row whole across a page
  (section 2 break discipline).
- **A clear totals block** — the grand total leads in heavier weight above a rule, the one
  emphasis the eye should land on (section 4).

### The reportlab equivalent (computed path)

The same totals block, drawn programmatically when the layout is computed rather than authored
in HTML:

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()
doc = SimpleDocTemplate(
    "invoice.pdf", pagesize=A4,
    topMargin=22 * mm, bottomMargin=22 * mm,
    leftMargin=20 * mm, rightMargin=20 * mm,
)

rows = [
    ["Description", "Qty", "Rate", "Amount"],
    ["Brand identity system", "1", "4,200.00", "4,200.00"],
    ["Landing page design", "3", "900.00", "2,700.00"],
    ["Print collateral", "1", "1,150.00", "1,150.00"],
]
table = Table(rows, colWidths=[80 * mm, 20 * mm, 30 * mm, 30 * mm], repeatRows=1)
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f4f6fb")),  # header tint
    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1a1a1a")),  # AA on white
    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),                         # numerals right
    ("LINEBELOW", (0, 0), (-1, 0), 0.75, colors.HexColor("#d8d8d8")),
    ("LINEBELOW", (0, 1), (-1, -2), 0.5, colors.HexColor("#e8e8e8")),
    ("TOPPADDING", (0, 0), (-1, -1), 6),                          # baseline rhythm
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    # No inner vertical rules — borderless by omission.
]))

doc.build([
    Paragraph("Invoice #2026-0142", styles["Title"]),
    Spacer(1, 8 * mm),
    table,
])
```

The reportlab styling encodes the same decisions — generous margins, header tint, no vertical
rules, right-aligned numerals, baseline-aligned padding, AA color — proving the design system,
not the tool, is what produces a beautiful page.

---

## Final checklist

A PDF passes when each line holds or carries a written, justified exception. The procedure in
the [SKILL](../SKILL.md) ends on this list:

- [ ] **Renders** — the generator produces the PDF with a zero exit status and no warnings.
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
- [ ] **Not the default-print look** — a real stylesheet or template drove the page.
