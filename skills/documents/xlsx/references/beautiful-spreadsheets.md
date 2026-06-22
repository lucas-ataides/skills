# Beautiful spreadsheets

A spreadsheet is read by a human first and a machine second. The default openpyxl
output — black gridlines on white, raw floats, typed totals — fails both readings: a
person cannot scan it, and the first input change makes the typed totals lie. This
reference sets the depth bar for a workbook that looks designed and stays correct,
grounded in the [foundation](../../../meta/foundation/SKILL.md) determinism doctrine: the
generator is a script, the styling is a fixed token set, and the results are formulas.

Beauty and correctness are not two goals here. A sheet with a restrained palette and a
hand-keyed sum is ugly the moment someone trusts that sum. Treat a hard-coded result as a
visual defect, the same class of error as a heavy gridline.

## Deterministic generation with openpyxl

The whole workbook comes out of one script, so the same inputs produce the same file on
every run. The building blocks below cover the surface openpyxl exposes.

### Workbook and worksheets

```python
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = "Dashboard"
calcs = wb.create_sheet("Calcs")
```

### Cell styles — fonts, fills, borders, alignment

openpyxl applies style objects per cell. Define each object once and reuse the reference
rather than rebuilding it per cell, so the palette stays fixed and the script stays fast.

```python
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
HEADER_FILL = PatternFill("solid", fgColor="1F3A5F")        # deep slate
ZEBRA_FILL  = PatternFill("solid", fgColor="F2F5F9")        # near-white tint
THIN_SIDE   = Side(style="thin", color="D6DCE4")
BOTTOM_RULE = Border(bottom=THIN_SIDE)
RIGHT_NUM   = Alignment(horizontal="right")
```

### Number formats

A `number_format` string controls how a stored value renders. The value stays a real
number, so a formula above it still computes; only the display changes.

| Intent | `number_format` string |
|---|---|
| Currency, no cents | `'"$"#,##0'` |
| Currency, two cents | `'"$"#,##0.00'` |
| Percent, one decimal | `'0.0%'` |
| Thousands integer | `'#,##0'` |
| Date, ISO | `'yyyy-mm-dd'` |
| Negatives in red parens | `'#,##0;[Red](#,##0)'` |

### Column widths, freeze panes

```python
ws.column_dimensions["A"].width = 28        # label column, room for text
ws.column_dimensions["B"].width = 14        # numeric column
ws.freeze_panes = "A2"                       # row 1 stays on screen while scrolling
```

### Conditional formatting

A rule recolors cells from their values, so the sheet highlights itself without a typed
verdict per row.

```python
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule

ws.conditional_formatting.add(
    "B2:B13",
    ColorScaleRule(start_type="min", start_color="FFF4F4",
                   end_type="max", end_color="2E7D32"),
)
ws.conditional_formatting.add(
    "C2:C13",
    CellIsRule(operator="lessThan", formula=["0"],
               fill=PatternFill("solid", fgColor="FCE4E4")),
)
```

### Charts

```python
from openpyxl.chart import BarChart, Reference

chart = BarChart()
chart.title = "Revenue by month"
data = Reference(ws, min_col=2, min_row=1, max_row=13)
cats = Reference(ws, min_col=1, min_row=2, max_row=13)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
ws.add_chart(chart, "E2")
```

### Named ranges and formulas

A named range turns a magic cell address into a domain word, so a formula reads like the
model it represents. A formula string is assigned to a cell exactly like a value.

```python
from openpyxl.workbook.defined_name import DefinedName

wb.defined_names.add(DefinedName("tax_rate", attr_text="Calcs!$B$1"))
ws["B14"] = "=SUM(B2:B13)"
ws["B15"] = "=B14*tax_rate"
```

## Spreadsheet design

The visual goal is a quiet sheet that a reader scans in one pass. The rules below are the
difference between a designed workbook and a raw dump.

- **A clear header style.** The top row carries one bold font on one solid fill, in white
  on a deep color, so the header reads as a band rather than as more data. The header is
  the only loud element on the sheet.
- **Zebra rows or subtle borders, not heavy grids.** A full grid cages every cell and
  drowns the data. A faint fill on alternate rows, or a single thin bottom rule under each
  row, guides the eye without the cage. Pick one of the two, never both.
- **Aligned numbers on consistent formats.** Numbers right-align so digits line up by
  place value; one column holds one `number_format` start to finish. A column that mixes
  `1200`, `$1,200`, and `1200.00` reads as three different quantities.
- **Currency and percent formatting.** A money column shows a currency format and a ratio
  column shows a percent format, both set through `number_format` rather than typed into
  the string. The stored value remains numeric for the formulas above it.
- **Freeze the header row.** `freeze_panes = "A2"` pins row 1, so the column meaning
  survives scrolling on a long table. A model with frozen labels and a frozen header row
  uses `"B2"` to pin both.
- **Sensible column widths.** Each width fits its content — a label column wide enough for
  its longest label, a numeric column sized to its formatted number. Default-width columns
  truncate text and waste space on short numbers.
- **A restrained palette.** Three colors carry the whole workbook: a dark header, a near-
  white zebra tint, and one accent for emphasis. A rainbow of fills signals decoration
  over meaning.

## Correctness as part of beauty

- **Formulas over hard-coded numbers.** A result cell holds a formula referencing its
  inputs, never a number the author computed by hand. The test: change one input, and
  every dependent figure moves. A typed total is a latent lie.
- **Input validation.** Cells that take user entry carry a data-validation rule, so a bad
  value is rejected at the boundary rather than feeding a silent miscalculation downstream.

  ```python
  from openpyxl.worksheet.datavalidation import DataValidation

  dv = DataValidation(type="decimal", operator="greaterThanOrEqual",
                      formula1="0", allow_blank=False)
  dv.error = "Enter a non-negative number."
  ws.add_data_validation(dv)
  dv.add("B2:B13")
  ```

- **No magic constants.** A rate, a threshold, or a multiplier lives in a labeled input
  cell or a named range, so a reader sees the assumption and a formula cites it by name. A
  bare `* 0.21` buried in a formula hides the model from the person reading it.
- **A clear inputs / calcs / outputs separation.** Inputs sit in one area as plain typed
  values, calculations sit in another as formulas over those inputs, and outputs present
  the results. The reader follows the model in one direction, and an auditor finds every
  assumption in the inputs area.

## Spreadsheet archetypes

| Archetype | Holds | Design emphasis |
|---|---|---|
| **Dashboard** | A few headline figures and one or two charts | Large formatted numbers, a chart, minimal text, heavy whitespace |
| **Financial model** | Inputs area, calc rows, output totals across periods | Strict inputs / calcs / outputs split, named ranges, currency and percent formats, frozen labels and header |
| **Data table** | Many rows of records under typed columns | Header band, zebra rows, per-column number formats, frozen header, an autofilter |
| **Report** | Sections of tables with totals and a summary | Section headers, subtotal rows by formula, a restrained palette, a summary block at top |

## Failure modes

- **Heavy gridlines.** A full border grid on every cell turns the sheet into a cage and
  buries the data under lines.
- **Unformatted numbers.** Raw floats — `1200.0`, `0.213` — force the reader to decode
  scale and meaning that a `number_format` would have shown.
- **Hard-coded values.** A typed total disconnects the result from its inputs; the figure
  is correct once and wrong forever after.
- **No header freeze.** A long table scrolls its labels off-screen, and a reader loses
  which column means what.
- **Inconsistent formats.** One column carrying several number formats reads as several
  unrelated quantities stacked together.

## Red flags

- A result cell holds a literal where a formula belongs.
- A multiplier or rate appears inline in a formula with no labeled cell behind it.
- Every cell carries a border, and the data drowns under the grid.
- A numeric column mixes formats from row to row.
- The header row scrolls away because no pane is frozen.
- More than three fill colors compete for attention across the sheet.
- Columns sit at default width, truncating labels and stranding short numbers.
- Inputs, calculations, and outputs are interleaved, so an assumption hides among results.

## Worked example — one styled, formula-driven sheet

This script builds a single revenue sheet: a styled header band, zebra rows, per-column
number formats, a frozen header, a named tax rate, and totals computed by formula rather
than typed. Running it twice yields the same file.

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.workbook.defined_name import DefinedName

# --- design tokens, defined once ---
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
HEADER_FILL = PatternFill("solid", fgColor="1F3A5F")
ZEBRA_FILL  = PatternFill("solid", fgColor="F2F5F9")
BOTTOM_RULE = Border(bottom=Side(style="thin", color="D6DCE4"))
RIGHT       = Alignment(horizontal="right")
MONEY       = '"$"#,##0'
PERCENT     = '0.0%'

wb = Workbook()
ws = wb.active
ws.title = "Revenue"

# --- inputs / calcs split: the tax rate is a named input, not a magic constant ---
ws["E1"] = "Tax rate"
ws["F1"] = 0.21
ws["F1"].number_format = PERCENT
wb.defined_names.add(DefinedName("tax_rate", attr_text="Revenue!$F$1"))

# --- header band ---
headers = ["Month", "Gross", "Tax", "Net"]
for col, label in enumerate(headers, start=1):
    cell = ws.cell(row=1, column=col, value=label)
    cell.font = HEADER_FONT
    cell.fill = HEADER_FILL
    cell.alignment = RIGHT if col > 1 else Alignment(horizontal="left")

# --- data rows: gross is an input, tax and net are formulas ---
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
gross  = [42000, 45800, 51200, 49750, 53400, 58900]
for i, (month, value) in enumerate(zip(months, gross)):
    r = i + 2
    ws.cell(row=r, column=1, value=month)
    ws.cell(row=r, column=2, value=value).number_format = MONEY
    ws.cell(row=r, column=3, value=f"=B{r}*tax_rate").number_format = MONEY
    ws.cell(row=r, column=4, value=f"=B{r}-C{r}").number_format = MONEY
    fill = ZEBRA_FILL if i % 2 else None
    for col in range(1, 5):
        c = ws.cell(row=r, column=col)
        c.border = BOTTOM_RULE
        if col > 1:
            c.alignment = RIGHT
        if fill is not None:
            c.fill = fill

# --- total row: every total is a SUM formula over the column ---
total = len(months) + 2
ws.cell(row=total, column=1, value="Total").font = Font(bold=True)
for col_letter in ("B", "C", "D"):
    cell = ws[f"{col_letter}{total}"]
    cell.value = f"=SUM({col_letter}2:{col_letter}{total - 1})"
    cell.number_format = MONEY
    cell.font = Font(bold=True)
    cell.alignment = RIGHT

# --- frame: fit widths, freeze the header ---
ws.column_dimensions["A"].width = 12
for col_letter in ("B", "C", "D"):
    ws.column_dimensions[col_letter].width = 14
ws.freeze_panes = "A2"

wb.save("revenue.xlsx")
```

Verify by reopening — read the saved file back and confirm the frozen pane and that a
result cell holds a formula, not a literal:

```python
from openpyxl import load_workbook

check = load_workbook("revenue.xlsx")
sheet = check["Revenue"]
assert sheet.freeze_panes == "A2"
assert str(sheet["C2"].value).startswith("=")   # tax is a formula, not a typed number
```
