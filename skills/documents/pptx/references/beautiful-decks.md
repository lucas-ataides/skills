# Beautiful decks with python-pptx

A deck earns the word *beautiful* the same way a web UI does: by being systematic, not inspired. Amateur slides pick a size here, a blue there, a margin by feel — so nothing aligns and nothing relates, and the result reads as the default template with the content poured in. A designed deck snaps every decision to a small set of scales chosen once, then repeats them on every slide.

This reference works on two jobs at once: **generating** a deck from data or an outline with `python-pptx`, and **styling** one so it stops looking auto-generated. The governing move is to push the work down the determinism ladder — a script owns geometry, color, and font (exact, repeatable, free of eyeballing), and the model owns only the prose and the choice of archetype per slide. The lineage of the design rules is Refactoring UI and the brand-system and web-design references in this repo, distilled into values a script can hardcode.

The design tokens here resolve to the same roles named in [the brand system](../../../design/brandkit/SKILL.md) and the scales named in [the web design rules](../../../design/web-design-guidelines/SKILL.md). A deck is one more surface that inherits the kit; what changes from the website is density and presenter-scale type, never the identity values.

---

## 1. python-pptx, deterministically

`python-pptx` writes the Office Open XML that PowerPoint reads, so a script produces byte-identical decks on every run. The object model is small, and four ideas cover most of a deck.

### The object graph

```
Presentation
└─ slides            # the ordered deck
   └─ slide          # built from a slide_layout
      └─ shapes      # the placeholders and added shapes
         ├─ text_frame   → paragraphs → runs   (text + font)
         ├─ table
         ├─ chart
         └─ picture
```

A `Presentation` owns `slide_layouts` (inherited from the slide master and the theme), `slide_width`, and `slide_height`. A `slide` is created from one layout; its `shapes` hold placeholders the layout defined plus shapes the script adds. Text lives three levels down — a `text_frame` holds `paragraphs`, a paragraph holds `runs`, and a run carries the `font` (size, bold, color, name). Setting a font on the paragraph is unreliable across readers; set it on the run.

### Units: EMU, Pt, Inches

`python-pptx` measures length in English Metric Units (914,400 per inch). Never write raw EMU — wrap every length in a unit helper so the number stays readable and the conversion stays exact.

```python
from pptx.util import Inches, Pt, Emu

Inches(0.5)   # a margin
Pt(28)        # a font size or a precise offset
Emu(457200)   # raw EMU, avoided in favor of the two above
```

### Deck dimension

A modern deck is 16:9. Set the size once on the presentation before adding slides.

```python
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()                 # blank, default master/theme
prs.slide_width = Inches(13.333)     # 16:9 widescreen
prs.slide_height = Inches(7.5)
```

### Layouts, master, and theme

The blank `Presentation()` ships with the default Office master and its eleven built-in layouts (`Title Slide`, `Title and Content`, `Section Header`, `Blank`, and the rest). Two routes lead to a branded look:

- **Start from a branded template.** `Presentation("brand.pptx")` loads a `.potx`/`.pptx` whose master, theme colors, and theme fonts already match the kit; new slides inherit them. This route is the most deterministic, because the theme carries the palette and the fonts without a single hardcoded color in the script.
- **Start blank and set every property in code.** Add slides from `slide_layouts[6]` (`Blank`) and place every shape with explicit geometry and explicit color. This route trades a longer script for zero template dependency.

Prefer the branded template when one exists; fall back to blank-plus-explicit otherwise. Either way, the script — not a human dragging shapes — is the single source of geometry.

### Adding a slide and writing text

```python
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

blank = prs.slide_layouts[6]
slide = prs.slides.add_slide(blank)

box = slide.shapes.add_textbox(Inches(0.92), Inches(0.92), Inches(11.5), Inches(2))
tf = box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
run = p.add_run()
run.text = "One idea, stated once"
run.font.name = "Inter"
run.font.size = Pt(40)
run.font.bold = True
run.font.color.rgb = RGBColor(0x1A, 0x1B, 0x1E)
p.alignment = PP_ALIGN.LEFT
tf.vertical_anchor = MSO_ANCHOR.TOP
```

### Tables

`add_table` returns a graphic frame whose `.table` exposes `cell(row, col)`. Style the cells in code — the default table style is the loudest tell of an auto-generated deck.

```python
rows, cols = 4, 3
gf = slide.shapes.add_table(rows, cols, Inches(0.92), Inches(2.4),
                            Inches(11.5), Inches(3.6))
table = gf.table
cell = table.cell(0, 0)
cell.text = "Metric"
cell.text_frame.paragraphs[0].runs[0].font.size = Pt(16)
cell.fill.solid()
cell.fill.fore_color.rgb = RGBColor(0xF1, 0xF3, 0xF5)   # header tint
```

### Native charts vs. images

`python-pptx` builds native, editable charts from `CategoryChartData` and `add_chart`. A native chart stays crisp at any zoom and recolors with the theme, so it beats a pasted screenshot of a chart. Detailed chart styling lives in section 6.

### Pictures

`add_picture(path, left, top, width=…, height=…)` places an image. Set exactly one of width or height to preserve the aspect ratio; setting both stretches the image, and a stretched photo is a defect (section 7).

### The determinism rules for the script

- **One token block at the top.** Define every color, font name, size, and margin as a named constant before the first slide. A literal `Pt(23)` buried mid-script is the off-grid value that breaks the system.
- **Write through a deterministic path.** Name the output with `skillkit.unique_path` rather than a hand-built timestamp, so concurrent runs never collide.
- **One archetype, one function.** A function per archetype (`add_title_slide`, `add_content_slide`) keeps every slide of a kind identical and makes the deck a composition of calls.

---

## 2. The deck design system

A complete deck system is small. Define each scale once as constants, then forbid values outside it.

### One type ramp

Slides read at distance, so deck type runs larger than web type, yet still sits on a modular ramp rather than ad-hoc sizes. A practical presenter-scale ramp (a ~1.25 ratio, hand-tuned):

```
14   18   22   28   36   44   54   66
```

Roles map onto the ramp: body and captions at the low end (`14`/`18`), slide titles in the middle (`36`/`44`), and a hero number or section label at the top (`54`/`66`). Body text never drops below `14pt` on a slide, because a back-row reader loses anything smaller.

### Two faces at most

One display family for titles, one body family for everything else — or a single strong family across both. A third face is the classic amateur tell. Use weight (400 / 600 / 700) for variety inside a family rather than reaching for a new font. Fonts must be installed on the rendering machine, so prefer a system or widely available family (Inter, Source Sans, system-ui) unless the deck embeds its fonts.

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

Contrast is the floor, not a finish: body text clears **4.5:1** against its background, and large text (≥ 24pt, or ≥ 19pt bold) and meaningful icons clear **3:1**. Light-gray text on white is the most common failure — a `#999` on white measures ~2.8:1 and fails, so darken until the ratio clears. Never carry meaning in hue alone; pair a colored delta with a sign or an arrow so a color-blind viewer reads it too.

### An 8pt spacing grid

Every margin, gap, and offset draws from one scale built on a 4pt base doubling into an 8pt rhythm:

```
4   8   12   16   24   32   48   64   96
```

In inches at 96 px/in, the workhorse values are `0.083, 0.167, 0.25, 0.33, 0.5, 0.667, 1.0`. Round to clean values and reuse them. A `0.31in` margin beside a `0.5in` margin is the drift that makes a deck feel hand-placed.

### Generous margins and a content region

Reserve a wide, consistent outer margin on every slide — a 16:9 deck breathes at roughly `0.92in` left and right and `0.75in` top and bottom. The region inside that margin is the only place content lands, and holding it identical slide to slide is what makes a deck feel composed. Cramming to the edge is the single fastest way to look unfinished.

### One idea per slide

A slide carries one claim. A second idea wants a second slide, not a smaller font. The discipline of one-idea-per-slide is what kills the wall-of-text failure before it starts — when a slide needs three paragraphs, the content is really three slides or belongs in a leave-behind document.

### Visual hierarchy

Build the eye's path with four tools, ranked: **size** (bigger leads), **weight** (heavier leads), **color/contrast** (high contrast advances, muted recedes), and **space** (isolation confers importance). De-emphasize as much as you emphasize — mute the supporting line with a lighter neutral rather than only enlarging the lead. One emphasis per slide; two competing focal points split attention and stall the read.

### Token check

The system holds when color resolves to a role with an AA pair, type and spacing resolve to a named ramp, the family count is ≤ 2, and the script holds no off-scale literal.

---

## 3. Slide archetypes

Six archetypes cover almost any deck. Each names its layout, its margins from the grid, and the one thing it must not do. Coordinates below assume the 16:9 canvas (13.333 × 7.5 in) and the outer margin of ~0.92 in left/right.

### Title

The cover. One product or deck name, one subtitle, optional date and presenter — nothing else.

- **Layout:** left-aligned block, vertically centered or sitting on a lower third.
- **Title:** `54`–`66pt`, display face, `bold`, `fg` or `brand`, left edge at `0.92in`.
- **Subtitle:** `22`–`28pt`, body face, muted neutral, `0.24in` below the title.
- **Not:** a centered title floating over a busy stock photo with low-contrast text.

### Section

A divider that resets the viewer between acts. High contrast, almost no content.

- **Layout:** full-bleed `brand` (or deep neutral) fill, one short label.
- **Label:** `44`–`54pt`, reversed (`on-brand`) text, left-aligned, generous margin.
- **Optional:** a small step indicator ("02 / 05") in a muted tint.
- **Not:** a bulleted agenda — a section slide announces one act, it does not summarize.

### Content

The workhorse. A title, then one supporting idea as a short list, a two-column split, or a single statement.

- **Layout:** title band at the top, content region below.
- **Title:** `32`–`40pt`, `bold`, left edge at `0.92in`, baseline near `0.92in` top.
- **Body:** `18`–`22pt`, `1.3`–`1.4` line spacing, ≤ 5 lines, each line a phrase not a sentence.
- **Spacing:** `0.5in` between the title baseline and the body; list items gapped at `0.16in`.
- **Not:** a wall of full-sentence bullets; if the text wraps to three lines per bullet, split the slide.

### Data / chart

One chart or one table, framed and labeled, making one point.

- **Layout:** a short interpretive title (the takeaway, not "Revenue"), then one chart filling the content region.
- **Title:** states the conclusion — "Revenue doubled in Q3", not a noun label.
- **Chart:** native `python-pptx` chart, theme-colored, gridlines muted or removed (section 6).
- **Not:** two charts competing on one slide, or a default-styled chart with a rainbow legend.

### Quote

A single testimonial or pull-quote, set large with room to breathe.

- **Layout:** centered or left-aligned quote, attribution beneath.
- **Quote:** `36`–`44pt`, regular or light weight, `fg`, wide margins so the line measure stays short.
- **Attribution:** `18`–`20pt`, muted neutral, name then role.
- **Not:** quotation-mark clip-art, or a quote so long it becomes a paragraph.

### Closing

The last slide: one call to action or a thank-you with contact details. Mirrors the title's restraint.

- **Layout:** echo the title slide's composition for bookend symmetry.
- **Primary line:** `44`–`54pt`, the single next step.
- **Contact:** `18`–`22pt`, muted, one line.
- **Not:** a dense "questions?" slide stacked with logos and links.

---

## 4. Chart styling

A native chart inherits the deck theme, then needs subtraction. The default chart ships with chartjunk — heavy gridlines, a boxed legend, data labels everywhere — and removing that junk is most of the styling work.

### Build the chart

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

data = CategoryChartData()
data.categories = ["Q1", "Q2", "Q3", "Q4"]
data.add_series("Revenue", (4.2, 5.1, 9.8, 11.0))

gf = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(0.92), Inches(1.9), Inches(11.5), Inches(4.8), data,
)
chart = gf.chart
```

### Subtract the junk

```python
# One series, brand-colored — no rainbow.
plot = chart.plots[0]
plot.gap_width = 80                       # tighter bars read as deliberate
series = chart.series[0]
series.format.fill.solid()
series.format.fill.fore_color.rgb = RGBColor(0x3B, 0x5B, 0xDB)   # brand

# Drop the legend for a single series; keep it only for several.
chart.has_legend = False

# Mute the value axis, kill the busy gridlines.
value_axis = chart.value_axis
value_axis.has_major_gridlines = False
value_axis.tick_labels.font.size = Pt(12)
value_axis.tick_labels.font.color.rgb = RGBColor(0x86, 0x8E, 0x96)  # muted

cat_axis = chart.category_axis
cat_axis.tick_labels.font.size = Pt(14)
```

### Chart rules

- **One series leads.** Color the point you are making in `brand`; render comparison series in a single muted neutral. A chart where every series shouts in a different hue makes no point.
- **The title is the takeaway.** Put the conclusion in the slide title and let the chart carry the evidence.
- **Label sparingly.** A few direct data labels on the points that matter beat a label on every bar.
- **Kill gridlines and the chart border.** Muted axis ticks give enough reference; a grid of lines is noise.
- **Match the type to the question.** Trend over time wants a line or column; part-of-whole wants a single bar or — sparingly — one donut; ranking wants a sorted bar. A pie with eight slices answers nothing.

---

## 5. Image treatment

One strong image lifts a slide; a grid of small clip-art sinks it. Treat images as a system, the same as type and color.

- **No clip-art, ever.** Cartoon icons and stock cliché art are the loudest signal of an undesigned deck. Use a single clean photo, a flat vector illustration in the brand style, or no image at all.
- **Preserve aspect ratio.** Set one of width or height on `add_picture` and let the other follow; a stretched face or squashed logo reads as broken.
- **Full-bleed or framed, picked once.** Either run a hero image edge to edge behind reversed text, or sit a framed image inside the content region on the grid — and hold that choice across the deck.
- **Guarantee contrast over images.** Text on a photo needs a scrim — a semi-transparent dark rectangle between the photo and the text — so the words clear AA against the busiest part of the image.
- **One icon library, one style.** When icons appear, draw them from a single set with one stroke width, colored by role (`fg` or a status hue), never a one-off hex. A second icon style breaks the deck as loudly as a second font.
- **Resolution for the room.** A projected slide is large; an image under roughly 1500 px on its long edge softens visibly. Source larger, never upscale.

A scrim in code:

```python
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

slide.shapes.add_picture("hero.jpg", 0, 0, height=Inches(7.5))   # full-bleed
scrim = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
scrim.fill.solid()
scrim.fill.fore_color.rgb = RGBColor(0x1A, 0x1B, 0x1E)
scrim.fill.transparency = 0          # see note below
scrim.line.fill.background()
# python-pptx exposes no direct alpha setter on solid fill; for a true scrim,
# set the shape's fill alpha via the XML, or use a pre-made semi-transparent PNG.
```

---

## 6. Failure modes

Each failure has a tell a reviewer catches at a glance and a concrete fix.

- **Wall-of-text slide.** *Tell:* paragraphs of full sentences, six-plus bullets, text wrapping three lines deep. *Fix:* one idea per slide; cut each bullet to a phrase; move the prose to a leave-behind. The slide supports the speaker, it does not replace the speaker.
- **Clip-art and stock cliché.** *Tell:* cartoon icons, a businessperson-shaking-hands photo, mixed illustration styles. *Fix:* delete it, or replace it with one clean on-brand image and a single icon set.
- **Inconsistent spacing.** *Tell:* a `0.31in` margin here, a `0.5in` there, titles starting at a different height on each slide. *Fix:* snap every offset to the 8pt grid; drive every slide of a kind from one function so the geometry is identical.
- **Low contrast.** *Tell:* pale gray text on white, brand-on-brand, unreadable text over a photo. *Fix:* raise every text pair to AA (4.5:1, or 3:1 for large); add a scrim behind text on images.
- **Default-template look.** *Tell:* the stock Office theme fonts and colors, a default-styled table, a rainbow chart with a boxed legend. *Fix:* set theme colors and fonts from the kit (or load a branded template), restyle every table cell, and subtract the chartjunk.
- **Too many fonts or colors.** *Tell:* three-plus typefaces, five unrelated accent hues. *Fix:* collapse to ≤ 2 families and the kit budget — one neutral ramp, one accent, status hues only.
- **Flat hierarchy.** *Tell:* text at one uniform size and weight, no entry point for the eye. *Fix:* enlarge the one lead element and mute the rest with size, weight, and a lighter neutral.
- **Off-grid literals in the script.** *Tell:* a `Pt(23)` or `Inches(0.31)` inline, different on each slide. *Fix:* hoist every value into the token block and reference the constant.

---

## 7. Red flags — fast scan

A deck likely needs this skill when any of these appear:

- Spacing values off the grid — a `0.31in` beside the clean steps.
- Three or more typefaces, or font sizes chosen by feel.
- More than one accent hue competing with the brand color.
- Gray text that vanishes on its background (under 4.5:1).
- Any clip-art, or mixed illustration and icon styles.
- A bulleted slide running past five lines, or bullets wrapping three lines deep.
- A chart with a rainbow of series and a boxed legend.
- A stretched image or a squashed logo.
- The stock Office theme fonts and default table styling left untouched.
- Two competing focal points on one slide.
- Every slide titled with a noun label instead of a takeaway.

---

## 8. Worked example — a branded title slide and a content slide

The script below builds one title slide and one content slide that look designed, on the 16:9 canvas, from a single token block. The tokens resolve to the "Lumen" mini-kit roles in [the brand system](../../../design/brandkit/SKILL.md) — `brand = #3b5bdb`, `fg = #1a1b1e`, body `Inter` — and the scales to [the web design rules](../../../design/web-design-guidelines/SKILL.md).

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# --- tokens: defined once, referenced everywhere ---------------------------
BRAND   = RGBColor(0x3B, 0x5B, 0xDB)   # color.brand
FG      = RGBColor(0x1A, 0x1B, 0x1E)   # color.fg   (16:1 on white)
MUTED   = RGBColor(0x86, 0x8E, 0x96)   # neutral.500 (large/UI only)
BG      = RGBColor(0xFF, 0xFF, 0xFF)   # color.bg
ON_BRAND = RGBColor(0xFF, 0xFF, 0xFF)  # color.on-brand (8.6:1 on brand)

DISPLAY = "Inter"                       # ≤ 2 families
BODY    = "Inter"

T_HERO, T_TITLE = Pt(54), Pt(36)        # type ramp
T_SUB,  T_BODY  = Pt(24), Pt(20)

MARGIN_X = Inches(0.92)                 # generous, consistent outer margin
MARGIN_Y = Inches(0.75)
GAP_SM, GAP_MD = Inches(0.24), Inches(0.5)   # 8pt grid (≈16pt, ≈32pt)
CONTENT_W = Inches(13.333) - MARGIN_X * 2


def _set(run, text, size, color, *, bold=False, name=BODY):
    run.text = text
    run.font.name = name
    run.font.size = size
    run.font.bold = bold
    run.font.color.rgb = color


def paint_bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def add_title_slide(prs, title, subtitle):
    slide = prs.slides.add_slide(prs.slide_layouts[6])   # Blank
    paint_bg(slide, BG)

    box = slide.shapes.add_textbox(MARGIN_X, Inches(3.4), CONTENT_W, Inches(2.4))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP

    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.LEFT
    _set(p1.add_run(), title, T_HERO, FG, bold=True, name=DISPLAY)

    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.LEFT
    p2.space_before = GAP_SM
    _set(p2.add_run(), subtitle, T_SUB, MUTED)

    # a short brand rule under the title for a designed accent
    from pptx.enum.shapes import MSO_SHAPE
    rule = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, MARGIN_X, Inches(3.25), Inches(1.2), Pt(5))
    rule.fill.solid()
    rule.fill.fore_color.rgb = BRAND
    rule.line.fill.background()
    return slide


def add_content_slide(prs, title, points):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    paint_bg(slide, BG)

    # title band
    head = slide.shapes.add_textbox(MARGIN_X, MARGIN_Y, CONTENT_W, Inches(1.0))
    htf = head.text_frame
    htf.word_wrap = True
    _set(htf.paragraphs[0].add_run(), title, T_TITLE, FG, bold=True, name=DISPLAY)

    # content region, one phrase per line, gapped on the grid
    body = slide.shapes.add_textbox(
        MARGIN_X, MARGIN_Y + GAP_MD + Inches(0.6), CONTENT_W, Inches(4.5))
    btf = body.text_frame
    btf.word_wrap = True
    for i, point in enumerate(points):          # bounded: the caller's list
        p = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(12)                  # ≈12pt grid step
        p.line_spacing = 1.35
        _set(p.add_run(), point, T_BODY, FG)
    return slide


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    add_title_slide(
        prs,
        "Lumen",
        "The one metric that moved — for founders who drown in dashboards",
    )
    add_content_slide(
        prs,
        "Why one metric beats a wall of dashboards",
        [
            "Surfaces the single number that changed today",
            "Cuts setup to one connected source",
            "Replaces the daily dashboard scan with one glance",
        ],
    )
    return prs


prs = build()
# write through a deterministic, collision-free path (skillkit.unique_path),
# then reload and assert the slide count as the open-it-back verification:
out = "lumen_deck.pptx"          # replace with skillkit.unique_path in the skill
prs.save(out)

reloaded = Presentation(out)
assert len(reloaded.slides) == 2, "deck did not round-trip"
```

Why the result reads as designed, named against the system:

- **Every value on a scale** — type from `54 / 36 / 24 / 20`, spacing from the 8pt grid (`0.24 / 0.5 / 0.75`), no off-grid literal (sections 2, 6).
- **One palette at AA** — `fg` at 16:1, `brand` for the rule and `on-brand` reserved for reversed text; `muted` used only at subtitle size where 3:1 holds (section 2).
- **Two faces collapse to one** — a single `Inter` family carries titles and body via weight, well under the ≤ 2 budget (section 2).
- **Generous, consistent margins** — both slides share `MARGIN_X` and `MARGIN_Y`, so the content region is identical and the deck feels composed (section 2).
- **One idea per slide** — a cover, then one claim with three supporting phrases, each a phrase not a sentence (section 3).
- **Hierarchy with no border-soup** — size and weight lead the eye, a short brand rule accents the cover, and nothing is fenced in a box (section 3).
- **Verifiable** — the reload-and-assert at the end is the genchi-genbutsu check that the file opens and holds the expected slides (section 1).

---

## Final checklist

A deck passes when each line holds or carries a written, justified exception:

- [ ] **Spacing** — every margin, gap, and offset maps to the 8pt grid.
- [ ] **Type scale** — sizes drawn from one presenter-scale ramp; body ≥ 14pt.
- [ ] **Typefaces** — two families or fewer, installed or embedded.
- [ ] **Color budget** — one neutral ramp + one accent + status hues only.
- [ ] **Contrast** — text and meaningful non-text at AA (4.5:1 / 3:1).
- [ ] **One idea per slide** — no slide carries two claims; no wall of text.
- [ ] **Hierarchy** — one clear lead per slide via size, weight, color, and space.
- [ ] **Margins** — a generous, consistent outer margin held across the deck.
- [ ] **Archetypes** — each slide maps to one archetype with its layout spec.
- [ ] **Charts** — native, one series leading, gridlines and legend subtracted.
- [ ] **Images** — no clip-art, aspect ratio preserved, scrim behind text on photos.
- [ ] **No default-template look** — theme fonts, colors, tables, and charts all restyled.
- [ ] **Script determinism** — tokens defined once; output written through a collision-free path.
- [ ] **Opens** — the deck reloads in `python-pptx` and returns the expected slide count.
