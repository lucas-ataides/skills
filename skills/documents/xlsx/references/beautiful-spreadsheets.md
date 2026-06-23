# Beautiful spreadsheets

A spreadsheet is read by a human first and a machine second. The naive output — black
gridlines on white, raw floats in every numeric column, columns left at default width —
fails the human reading: a person cannot scan it. This reference sets the depth bar for a
workbook that looks designed, grounded in the [foundation](../../../meta/foundation/SKILL.md)
determinism doctrine: the model writes a JSON spec of data and structure, and a fixed
script renders the styling the same way every run.

Beauty and correctness both flow from the same discipline here. The model decides what
the data *is*; the renderer decides how the data *looks*. Splitting those two jobs keeps
the styling identical across runs and frees the author to tune the spec — the values, the
column names, the number formats — rather than to hand-write styling code that drifts.

## How generation works

The whole workbook comes out of one script, `scripts/render.py`, so the same spec
produces the same file on every run. The author never writes styling code; the author
writes a JSON spec, and the script stamps a fixed design onto it. Tuning the look means
tuning the spec, not editing the renderer.

### The render invocation

```
scripts/render.py build <spec.json> <out.xlsx>
```

The command reads the spec, renders the styled workbook, writes it to `<out.xlsx>`, and
prints the written path on success. A non-zero exit means the spec failed boundary
validation; the stderr message names the offending sheet and field.

### The JSON spec shape

The spec is one JSON object with a non-empty `sheets` list. Each sheet entry carries a
`name`, a non-empty `columns` list, an optional `rows` list of row arrays, and an
optional `number_formats` map keyed by column name:

```json
{
  "sheets": [
    {
      "name": "Sales",
      "columns": ["Region", "Revenue", "Margin"],
      "rows": [
        ["West", 124000, 0.42],
        ["East", 98750, 0.38]
      ],
      "number_formats": {"Revenue": "\"$\"#,##0", "Margin": "0.0%"}
    }
  ]
}
```

The four keys above are the entire surface the renderer accepts. A sheet entry with any
other key is harmless, but the renderer reads only these four:

| Key | Required | Meaning |
|---|---|---|
| `name` | yes | The worksheet tab title; a non-empty string. |
| `columns` | yes | The header labels, left to right; a non-empty list of strings. Row 1 holds these. |
| `rows` | no | A list of row arrays. Each row's length must not exceed the column count. |
| `number_formats` | no | A map from a column name to an Excel `number_format` string. Every key must name a column in `columns`. |

### What the renderer validates at the boundary

The renderer rejects a malformed spec with a clear stderr message and a non-zero exit, so
a bad spec fails fast rather than producing a broken workbook:

- The spec is not a JSON object, or its `sheets` is missing, not a list, or empty.
- A sheet entry is not an object, lacks a non-empty string `name`, or lacks a non-empty
  `columns` list.
- A column label is not a string.
- A row is not a list, or a row has more cells than the sheet has columns.
- A `number_formats` key names a column absent from `columns`.

Write the spec to satisfy these rules, and a green run is guaranteed for that spec.

## The styling the renderer applies

The renderer stamps one fixed design onto every sheet. The author does not choose these
values per run; the author expresses design intent *through the spec* — the column order,
which numbers carry which format — and the renderer supplies the rest identically every
time.

| Surface | What the renderer does | Author's lever |
|---|---|---|
| **Header band** | Row 1 carries the `columns` labels in bold white Calibri 11 on a solid deep-slate fill (`#1F3A5F`). The font and fill are built once and reused for every header cell. | Order and word the `columns` so the band reads as clear, scannable labels. |
| **Frozen header** | `freeze_panes` is set to `A2`, so row 1 stays on screen while the body scrolls. | None — every rendered sheet pins its header. |
| **Column widths** | Each column is sized to its longest cell content (header or any row value), padded by 2 and clamped to the range 8–60 characters. | Keep cell values and headers honest; an over-long value widens its column up to the cap. |
| **Number formats** | Each cell in a column named in `number_formats` gets that column's `number_format` string. Body values stay real numbers; only the display changes. | Assign one format per numeric column (see the table below). |
| **Sheets** | The implicit first sheet is dropped; the spec owns every sheet, created in `sheets` order. | List sheets in reading order. |

Because the header style, the freeze, and the width logic are fixed in the script, three
of the classic design wins — a distinct header band, a frozen header row, and
content-fitted columns — come for free on every sheet. The one design surface the author
actively drives is **number formatting**, covered next.

### Number formats — the author's main design lever

A `number_format` string controls how a stored value renders without changing the value
itself. A figure stored as `124000` displayed through `"$"#,##0` reads as `$124,000`, yet
stays the integer `124000` underneath. Choose one format per numeric column and name it in
`number_formats`:

| Intent | `number_format` string |
|---|---|
| Currency, no cents | `"$"#,##0` |
| Currency, two cents | `"$"#,##0.00` |
| Percent, one decimal | `0.0%` |
| Thousands integer | `#,##0` |
| Plain integer | `0` |
| Date, ISO | `yyyy-mm-dd` |
| Negatives in red parens | `#,##0;[Red](#,##0)` |

Two rules of thumb keep a numeric column honest: pick the format from the intent of the
column, and apply it to the whole column by naming that one column once in
`number_formats`. A column that mixes `1200`, `$1,200`, and `1200.00` across rows reads as
three different quantities; one format per column removes that ambiguity.

Note that the percent format expects a ratio. A margin of 42% is stored as `0.42` and
displayed through `0.0%` as `42.0%`; storing `42` instead would render as `4200.0%`.

## Spreadsheet design

The visual goal is a quiet sheet that a reader scans in one pass. The principles below are
renderer-agnostic — each holds whatever tool produces the file — and the notes say how the
current renderer delivers or constrains each one.

- **A clear header style.** The top row carries one bold font on one solid fill, white on
  a deep color, so the header reads as a band rather than as more data. The header is the
  only loud element on the sheet. The renderer delivers this from the `columns` list; the
  author's job is to word and order those labels well.
- **Aligned, consistently formatted numbers.** One column holds one number format start to
  finish, so digits read at one scale down the column. The author secures this by naming
  each numeric column once in `number_formats`. Per-cell horizontal alignment is not a
  surface the renderer sets today (see limitations); rely on consistent formats to make a
  numeric column scan cleanly.
- **Currency and percent formatting.** A money column shows a currency format and a ratio
  column shows a percent format, both expressed through `number_formats` rather than typed
  into the cell text. The stored value stays numeric, so the figure remains a real number.
- **A frozen header row.** Pinning row 1 keeps the column meaning visible on a long table.
  The renderer freezes at `A2` on every sheet, so a long table never scrolls its labels
  off-screen.
- **Sensible column widths.** Each width fits its content — a label column wide enough for
  its longest label, a numeric column sized to its formatted number. The renderer derives
  each width from the longest cell in the column, so default-width truncation does not
  happen; the only tuning lever is the cell content itself, since an outlier value widens
  its column up to the 60-character cap.
- **A restrained palette.** A designed sheet leans on whitespace and one strong header
  color rather than a rainbow of fills. The renderer enforces restraint structurally: it
  paints exactly one fill, the header's deep slate, and adds no other color.

## Sheet organization

Structure carries as much meaning as styling. The principles below shape how the author
lays out columns, rows, and sheets in the spec.

- **One concept per sheet.** Each sheet in the `sheets` list holds one coherent table —
  one dataset, one report section. Splitting unrelated tables across sheets keeps each one
  scannable; the renderer creates the sheets in list order, so list them in reading order.
- **Header first, data below.** Row 1 is always the header band, and the body starts at
  row 2. The author supplies the header through `columns` and the body through `rows`; the
  renderer wires this layout and freezes the boundary at `A2`.
- **Columns in reading order.** Place the label or key column first and the figures to its
  right, left to right in the order a reader scans. Column order in the spec is column
  order in the sheet.
- **Totals as explicit rows (current approach).** A total belongs in its own labeled row at
  the foot of the table. Because the renderer does not compute formulas (see limitations),
  a total is a value the author places in a `rows` entry — for example a final row
  `["Total", 222750, ""]`. Treat such a precomputed total as data that must be recomputed
  whenever its inputs change, since the renderer will not refresh it.

## Accessibility

A spreadsheet that only a sighted scanner can read is half-built. The practices below keep
a workbook legible to assistive tooling and to colorblind readers.

- **Meaningful header labels.** A screen reader announces the column header with each cell,
  so a clear word in `columns` ("Revenue", not "R") makes every cell self-describing.
- **Do not encode meaning in color alone.** The renderer's single fill is decorative
  framing for the header, not a data signal, so no information is lost to a reader who
  cannot distinguish the slate. Keep it that way: carry meaning in the values and labels,
  never in a fill a colorblind reader would miss.
- **Numbers stay numeric.** Storing a figure as a real number with a display format (not as
  pre-formatted text like `"$124,000"`) lets assistive tools and downstream tools read the
  value, not a string. The `number_formats` approach preserves this by design.
- **One header row.** A single, frozen header row gives assistive tooling an unambiguous
  label row to associate with each column. The renderer's fixed `A2` freeze and row-1
  header deliver exactly this.

## Spreadsheet archetypes

| Archetype | Holds | Design emphasis | Fit with this renderer |
|---|---|---|---|
| **Data table** | Many rows of records under typed columns | Header band, per-column number formats, frozen header, fitted widths | Direct fit — the renderer's fixed design is built for this archetype. |
| **Tabular report** | Sections of records with totals and a summary | Section structure, per-column formats, a restrained palette, totals at the foot | Good fit — model each section as a sheet and place precomputed totals as explicit rows. |
| **Dashboard** | Headline figures and one or two charts | Large formatted numbers, a chart, heavy whitespace | Partial — formatted headline figures work; charts do not (see limitations). |
| **Financial model** | Inputs, calc rows, output totals across periods | Inputs / calcs / outputs split, named ranges, live formulas | Limited — the live-formula and named-range parts are unsupported (see limitations); only a precomputed snapshot renders. |

## Failure modes

- **Unformatted numbers.** Raw floats — `1200.0`, `0.213` — force the reader to decode
  scale and meaning that a `number_format` would have shown. Name each numeric column in
  `number_formats` to fix this.
- **Inconsistent formats.** One column carrying several number formats reads as several
  unrelated quantities stacked together. One format per column, named once, removes the
  ambiguity.
- **A ratio stored as a whole number.** A margin entered as `42` and formatted with `0.0%`
  renders as `4200.0%`. Store the ratio as `0.42` so the percent format reads correctly.
- **A wrong-width column from an outlier value.** One very long cell widens its whole
  column up to the 60-character cap. Trim or restructure an outlier value rather than
  letting it stretch the column.
- **A row wider than its columns.** A `rows` entry with more cells than `columns` fails
  boundary validation. Keep every row within the column count.
- **A stale precomputed total.** A total typed into a `rows` entry is correct only for the
  inputs at the time it was written; changing an input without recomputing the total leaves
  a figure that silently lies.

## Red flags

- A numeric column has no entry in `number_formats`, so it renders as raw floats.
- A numeric column mixes formats — the same column named with conflicting intent across
  attempts, or values pre-formatted as text in some rows and numeric in others.
- A percent column stores whole numbers instead of ratios.
- A money figure is stored as a string like `"$124,000"` instead of a number with a
  currency format, breaking both the display logic and downstream reading.
- A precomputed total sits in the data with no note that it must be recomputed when inputs
  change.
- A single sheet crams several unrelated tables together instead of splitting them across
  sheets.
- A header label is cryptic ("R", "Q1x"), so a screen reader announces nothing meaningful.

## Current limitations

The renderer is deliberately small: it stamps one fixed, deterministic design and reads
only the four spec keys above. Several techniques a richer spreadsheet might use are *not*
supported today. Each is called out plainly here so the author designs within the tool
rather than expecting a feature that is absent:

- **No formulas.** The renderer writes values, not formula strings. A total, a tax line, or
  any derived figure must be computed by the author and placed as a literal value in
  `rows`. There is no live `=SUM(...)` and no recalculation; a precomputed figure is a
  snapshot that the author must refresh when inputs change.
- **No named ranges.** A rate or threshold cannot be bound to a domain name for a formula
  to cite; the renderer has no named-range surface.
- **No data validation.** Cells cannot carry an entry-rejection rule. The boundary
  validation lives in the renderer (rejecting a malformed *spec*), not in the produced
  *workbook* (constraining a future human's typing).
- **No conditional formatting.** A cell cannot recolor itself from its value; color scales
  and value-driven highlighting are unavailable. The only fill the renderer paints is the
  fixed header band.
- **No charts.** Bar, line, and other charts are not emitted, so the dashboard archetype
  renders its figures but not its visuals.
- **No zebra banding, borders, or per-cell alignment.** The renderer applies no alternate-
  row fills, no cell borders, and sets no horizontal alignment. Numeric columns scan
  cleanly through consistent number formats and content-fitted widths rather than through
  banding or right-alignment.
- **No multi-area inputs / calcs / outputs layout.** Without formulas or named ranges, the
  renderer cannot wire a calculation area to an inputs area. A model can be rendered only as
  a flat, precomputed table of values.

When a workbook genuinely needs one of the above — live formulas, charts, validation — that
need is a signal to extend `scripts/render.py` and its spec under the
[script standard](../../../meta/foundation/references/script-standard.md), not to hand-write
styling outside the deterministic path.

## Verify by reopening

After a build, confirm the artifact against the spec by reopening the saved `.xlsx` and
observing the real file rather than assuming the render — the Genchi Genbutsu discipline
from the [foundation](../../../meta/foundation/SKILL.md). A reopened workbook should report
the spec's sheet names, a header cell equal to its column label, a sampled body cell equal
to its spec value, `freeze_panes` equal to `A2`, and a formatted column carrying its
`number_format` string. The renderer's own `--selftest` exercises exactly these checks on
an in-code fixture and exits zero (printing `skipped` when the rendering library is
absent), so running the self-test is the fastest confidence check that the renderer
behaves on this machine.
