# Beautiful .docx with python-docx

Concrete, opinionated practice for generating Word documents that read as designed, not defaulted. The governing idea matches the [web design rules](../../../design/web-design-guidelines/references/web-design-rules.md): **professional design is systematic, not inspired.** Pick a small set of scales once — a type ramp, a spacing rhythm, a restrained palette — encode them as named styles, then snap every paragraph to a style instead of hand-formatting it.

The grounding is the [foundation](../../../meta/foundation/SKILL.md) determinism doctrine: a script generates the file, the output is reproducible, and the design lives in data (styles) rather than in scattered judgment (inline runs). The depth bar for reviewing the result is the tech-lead standard from [code-review](../../../engineering/code-review/SKILL.md) — judge the document against what it must deliver and whether it reads as one coherent artifact, not only whether each line compiles.

---

## 1. The core practice — named styles, never ad-hoc formatting

This is the single decision that separates a beautiful document from a Calibri wall. Word documents carry a **style sheet**: named, reusable definitions of how a kind of text looks. A paragraph styled `Heading 1` inherits its font, size, color, and spacing from that one definition. Change the definition, and every `Heading 1` in the document updates at once.

Hand-formatting does the opposite. Setting `run.font.size` and `run.font.name` on individual runs scatters the same decision across hundreds of paragraphs. The result drifts — one heading at 15pt, the next at 16pt — and no one can restyle the document without touching every paragraph. A reviewer cannot trust it, and an editor cannot maintain it.

**The rule:** define a style once, apply it everywhere. Reserve a direct run-level override for a genuine one-off — a single bold word inside a sentence — and never for anything a style could own.

```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.style import WD_STYLE_TYPE

doc = Document()

# Define a named paragraph style once.
styles = doc.styles
body = styles.add_style("Body", WD_STYLE_TYPE.PARAGRAPH)
body.font.name = "Georgia"
body.font.size = Pt(11)
body.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
body.paragraph_format.line_spacing = 1.4
body.paragraph_format.space_after = Pt(8)

# Apply it by name — no inline font set on the paragraph.
doc.add_paragraph("Reusable styling, applied by name.", style="Body")
```

Modifying a **built-in** style (`Normal`, `Heading 1`, `Title`) propagates to every paragraph that already uses it, which is the cheapest way to restyle the whole document:

```python
normal = doc.styles["Normal"]
normal.font.name = "Georgia"
normal.font.size = Pt(11)
```

---

## 2. The design system — scales encoded as styles

A complete document design system is small. The whole system becomes a set of named styles defined in one place at the top of the generator.

### Type scale via styles

Pick heading and body sizes from one modular scale rather than arbitrary jumps. A practical ramp for print (roughly a 1.25 ratio):

```
11   13   16   20   26   32
```

Map the ramp onto styles, not onto inline sizes:

| Style       | Size  | Weight | Role                          |
|-------------|-------|--------|-------------------------------|
| `Title`     | 32 pt | Bold   | Cover title only              |
| `Heading 1` | 20 pt | Bold   | Section                       |
| `Heading 2` | 16 pt | Semibold | Subsection                  |
| `Body`      | 11 pt | Regular | Paragraph text               |
| `Caption`   | 9 pt  | Italic | Figure and table captions     |

Body text sits at 11pt for print (smaller strains the reader on paper). Three to four sizes carry almost any document.

### Two faces maximum

Two typefaces is the ceiling — one for headings, one for body, or a single family across both. A third face is the classic tell of an amateur layout. Use weight, not a new family, for variety inside one face. Pair by contrast: a sans heading (Calibri, Aptos, Arial) over a serif body (Georgia, Cambria) reads as intentional; two near-identical sans faces read as a mistake. Choosing a serif body alone breaks the document out of the default-Calibri look.

### Spacing rhythm

Space is the cheapest polish and the first thing amateurs get wrong. Set spacing through `paragraph_format.space_before` / `space_after` and `line_spacing` on the styles — never with empty paragraphs as spacers. A practical print rhythm:

- Body line spacing `1.4`; heading line spacing `1.15`.
- `space_after` on body `8pt`; `space_before` on `Heading 1` `18pt`, on `Heading 2` `12pt`.
- A heading sits closer to the text it introduces than to the text above it, so the eye groups by section.

An empty paragraph used as a spacer is a defect — it carries no semantic meaning and drifts when the content reflows.

### Color and AA contrast

A restrained palette is one neutral plus one accent. Most of the document is near-black text on white; the accent appears on heading rules, the cover, and table header fills.

WCAG AA is the floor, exactly as on the web:

- Body and small text at **≥ 4.5:1** against its background.
- Large text (≥ 24px / 18pt, or bold ≥ 14pt) at **≥ 3:1**.

Light-gray body text on white is the most common failure: `#999999` on white measures about 2.8:1 and fails AA. A near-black such as `#1A1A1A` on white clears it comfortably. Pure black on pure white is harsh; prefer a very dark neutral. White text on an accent table-header fill passes only when the accent is dark enough — verify the pair, never assume it.

### Cover and table of contents

A cover page and a TOC are what make a long document read as a deliverable rather than a draft. The cover uses the `Title` style plus a styled subtitle and metadata block. The TOC is a field bound to the heading styles, so Word populates it from the document outline (covered in section 4).

---

## 3. Deterministic generation — the python-docx primitives

Every structural element has a deterministic call. The model assembles content; python-docx renders it identically every run.

### Headings and paragraphs

`add_heading(text, level=n)` applies the built-in `Heading n` style; `add_paragraph(text, style=...)` applies a named style. Reach for runs only for inline emphasis inside otherwise-styled text:

```python
doc.add_heading("Findings", level=1)        # uses Heading 1 style
p = doc.add_paragraph("The result is ", style="Body")
run = p.add_run("significant")              # one-off inline emphasis
run.bold = True
p.add_run(" across all cohorts.")
```

### Tables

A table reads as designed when it uses a built-in table style, breathes inside its cells, and reserves rules for the header. Apply a style by name, then style the header row through the cell paragraphs (themselves styled), not by hand-formatting each cell:

```python
table = doc.add_table(rows=1, cols=3)
table.style = "Light Grid Accent 1"        # built-in, consistent borders
hdr = table.rows[0].cells
for cell, label in zip(hdr, ("Metric", "Q1", "Q2")):
    cell.paragraphs[0].text = label
    cell.paragraphs[0].style = "TableHead"  # a style you defined
```

A dense, rule-heavy table is the table equivalent of border-soup: every cell fenced, nothing breathing. Separation comes first from cell padding and a single header rule, and from a border only as a last resort.

### Images

Add images at a fixed width so the layout stays predictable across runs, and caption them with a `Caption` style:

```python
from docx.shared import Inches
doc.add_picture("chart.png", width=Inches(6.0))
doc.add_paragraph("Figure 1. Quarterly revenue.", style="Caption")
```

### Sections, margins, headers and footers

A `Section` owns page size, margins, and its header and footer. Set generous, even margins, then attach a header and footer:

```python
section = doc.sections[0]
section.top_margin = Inches(1.0)
section.bottom_margin = Inches(1.0)
section.left_margin = Inches(1.0)
section.right_margin = Inches(1.0)

header = section.header
header.paragraphs[0].text = "Quarterly Report"
header.paragraphs[0].style = header.paragraphs[0].style  # styled via Header style
```

### Page numbers

A page number is a **field**, so Word computes it at render time. python-docx has no high-level call for it, so write the field XML into a footer run once through a small helper:

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_page_number(paragraph):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)

footer = doc.sections[0].footer
add_page_number(footer.paragraphs[0])
```

### Table of contents field

The TOC is also a field. Write the `TOC` instruction bound to heading levels 1–2; Word renders the entries from the outline when the document opens (the user presses F9 to refresh):

```python
def add_toc(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar"); begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
    instr.text = r'TOC \o "1-2" \h \z \u'    # outline levels 1-2, hyperlinked
    sep = OxmlElement("w:fldChar"); sep.set(qn("w:fldCharType"), "separate")
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    for el in (begin, instr, sep, end):
        run._r.append(el)
```

---

## 4. Document archetypes

Each archetype is a fixed section list. Naming the archetype first fixes the structure before any styling decision.

| Archetype  | Required sections (in order)                                                                 | Distinctive styling                                              |
|------------|----------------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| **Report** | Cover, TOC, executive summary, body sections (H1/H2), figures and tables, appendix            | Strong heading hierarchy, captioned figures, running header     |
| **Proposal** | Cover, summary, problem, proposed solution, scope, pricing table, timeline, terms          | Accent on the cover and pricing-table header; one clear ask      |
| **Contract** | Title block, parties, recitals, numbered clauses, signature block                          | Auto-numbered clause style, conservative serif, no decoration    |
| **Memo**   | `TO / FROM / DATE / RE` header block, body, action items                                      | Compact, single section, no cover, tight spacing                 |

A report and a proposal earn a cover and TOC; a memo never does. A contract leans on a numbered list style for its clauses, so the numbering stays consistent as clauses are inserted or removed.

---

## 5. Failure modes

Each failure mode below is a named defect with a fix.

- **Manual formatting instead of styles.** Font and size set on individual runs across the document. The file drifts and cannot be restyled. Fix: move the formatting into a named style and apply it by name.
- **The default-Calibri wall.** Stock `Normal`, stock headings, no palette, no cover — a document that looks like an untouched template. Fix: redefine `Normal` and the heading styles onto a serif-body type scale, add a cover and an accent.
- **Inconsistent headings.** Section titles set by bolding body text, or heading levels skipped (H1 then H3). The outline breaks, so the TOC and navigation break with it. Fix: apply the built-in `Heading n` styles in order, with no skipped level.
- **Dense tables.** Rule-heavy grids with cramped cells and no header treatment. The table fights the reader. Fix: apply a built-in table style, add cell padding, and reserve a rule for the header row.
- **Empty paragraphs as spacers.** Blank lines standing in for spacing. The rhythm drifts on reflow. Fix: set `space_before` / `space_after` on the styles instead.
- **Sub-AA contrast.** Light-gray text that disappears on white. Fix: darken text until the pair clears 4.5:1.
- **Off-scale type.** Sizes chosen ad hoc (12, 15, 17, 21). The hierarchy reads as drift. Fix: snap every size to the modular ramp.

---

## 6. Red flags — fast scan

A document needs this skill when any of these appear:

- Default Calibri body with no palette and no cover — the untouched-template look.
- Heading sizes or body sizes chosen ad hoc, off any scale.
- More than two typefaces, or a third face smuggled into a table or caption.
- Gray text under 4.5:1 against its background.
- Section titles made by bolding a body paragraph instead of a heading style.
- Skipped heading levels (H1 straight to H3), breaking the outline and TOC.
- Tables fully fenced in heavy rules with cramped cells.
- Empty paragraphs used to create vertical space.
- Inline `font.size` / `font.name` repeated across many paragraphs.
- A multi-page document with no header, footer, or page number.

---

## 7. Worked example — a designed report section

This generator defines the full style sheet first, then builds one cover-plus-section using only named styles, a live page number, and a TOC field. The helpers `add_page_number` and `add_toc` from section 3 are reused.

```python
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH

ACCENT = RGBColor(0x0B, 0x5C, 0x8A)   # dark accent — white text on it clears AA
INK    = RGBColor(0x1A, 0x1A, 0x1A)   # near-black body — ~13:1 on white

def define_styles(doc):
    """The whole design system, defined once."""
    normal = doc.styles["Normal"]
    normal.font.name = "Georgia"      # serif body breaks the Calibri wall
    normal.font.size = Pt(11)
    normal.font.color.rgb = INK
    normal.paragraph_format.line_spacing = 1.4
    normal.paragraph_format.space_after = Pt(8)

    for name, size, before in (("Heading 1", 20, 18), ("Heading 2", 16, 12)):
        h = doc.styles[name]
        h.font.name = "Calibri"        # sans heading paired by contrast
        h.font.size = Pt(size)
        h.font.color.rgb = ACCENT
        h.font.bold = True
        h.paragraph_format.line_spacing = 1.15
        h.paragraph_format.space_before = Pt(before)
        h.paragraph_format.space_after = Pt(6)

    title = doc.styles["Title"]
    title.font.name = "Calibri"
    title.font.size = Pt(32)
    title.font.color.rgb = INK
    title.font.bold = True

    cap = doc.styles.add_style("Caption", WD_STYLE_TYPE.PARAGRAPH)
    cap.font.name = "Georgia"
    cap.font.size = Pt(9)
    cap.font.italic = True
    cap.font.color.rgb = RGBColor(0x55, 0x55, 0x55)   # ~7:1 on white, AA-safe

def build_cover(doc):
    t = doc.add_paragraph("Quarterly Business Review", style="Title")
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = doc.add_paragraph("Fiscal Year 2026 · Q2", style="Body")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

def build_section(doc):
    doc.add_heading("Executive Summary", level=1)
    doc.add_paragraph(
        "Revenue grew across every cohort this quarter.", style="Normal")
    doc.add_heading("Revenue by Segment", level=2)

    table = doc.add_table(rows=1, cols=3)
    table.style = "Light Grid Accent 1"
    for cell, label in zip(table.rows[0].cells, ("Segment", "Q1", "Q2")):
        cell.paragraphs[0].text = label
    doc.add_paragraph("Table 1. Revenue by segment ($M).", style="Caption")

def build_report(path):
    doc = Document()
    define_styles(doc)

    section = doc.sections[0]
    for side in ("top", "bottom", "left", "right"):
        setattr(section, f"{side}_margin", Inches(1.0))
    add_page_number(section.footer.paragraphs[0])   # helper from section 3

    build_cover(doc)
    doc.add_heading("Contents", level=1)
    add_toc(doc.add_paragraph())                     # helper from section 3
    doc.add_page_break()
    build_section(doc)

    doc.save(path)

build_report("quarterly_review.docx")
```

What makes this read as designed, named against the system:

- **Styles defined first** — `define_styles` owns the whole look, so a restyle is one edit (section 1).
- **Two faces, paired by contrast** — Calibri headings over a Georgia body, no third face (section 2).
- **One type scale** — `32 / 20 / 16 / 11 / 9`, drawn from the modular ramp, set on styles (section 2).
- **AA contrast** — near-black body and dark-accent headings both clear 4.5:1 on white (section 2).
- **Spacing through styles** — `space_before` / `space_after` on the styles, with no empty-paragraph spacers (section 2).
- **Cover, TOC, header/footer, page number** — the deliverable frame, built from fields (sections 3–4).
- **No inline formatting** — content carries named styles only; the lone run override is reserved for true inline emphasis (section 1).

---

## Final checklist

The document passes when each line holds or carries a written, justified exception:

- [ ] **Named styles** — text styled by name; no inline `font.size` / `font.name` repeated across paragraphs.
- [ ] **Type scale** — sizes drawn from one modular ramp; body at 11pt for print.
- [ ] **Typefaces** — two faces or fewer; a serif or paired body, not the default Calibri wall.
- [ ] **Spacing** — set through `space_before` / `space_after` on styles; zero empty-paragraph spacers.
- [ ] **Contrast** — body and small text at AA (4.5:1); large text at 3:1.
- [ ] **Heading outline** — built-in `Heading n` styles applied in order, no skipped level.
- [ ] **Tables** — a built-in table style, padded cells, a single header rule — no border-soup.
- [ ] **Frame** — even margins, a header and footer, and a live page-number field on every section.
- [ ] **Cover and TOC** — present for a report or proposal, bound to the heading styles; omitted for a memo.
- [ ] **Archetype** — the section list matches the named archetype.
- [ ] **Verified** — the saved file reopens with the expected styles and heading hierarchy.
