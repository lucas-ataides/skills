---
name: xlsx
description: Generate extremely beautiful, correct spreadsheets with openpyxl — formula-driven, consistently formatted, restrained in color. Use when the user asks to create, build, or generate an .xlsx / Excel / spreadsheet, a financial model, a dashboard, a data table, or a tabular report; when numbers must be formatted, totals must compute from formulas, or a sheet must look designed rather than raw gridlines; or when a workbook needs styled headers, frozen panes, conditional formatting, or charts.
---

A spreadsheet built by typing values into cells drifts into the raw-grid wall: heavy gridlines everywhere, numbers in no consistent format, totals hard-coded so they lie the moment an input changes. A beautiful spreadsheet is built the opposite way — a clear header band, quiet zebra rows instead of a cage of borders, every number on one number format, and every total a formula that recomputes when its inputs move. Beauty and correctness are one property here: a sheet that looks designed but hard-codes its sums is neither.

Generate the workbook deterministically with openpyxl. Push styling into reused cell styles and number formats, and push results into formulas, never into typed constants. The depth bar for the design system, the archetypes, and the failure modes lives in [references/beautiful-spreadsheets.md](references/beautiful-spreadsheets.md), grounded in the [foundation](../../meta/foundation/SKILL.md) determinism doctrine.

## Steps

1. **Name the archetype and its layout.** State which spreadsheet this is — dashboard, financial model, data table, or report — and list its sheets and the inputs / calcs / outputs each holds, drawn from the archetype section in [the reference](references/beautiful-spreadsheets.md). Done when the sheet list and the inputs-calcs-outputs split are written down before any code runs.

2. **Fix the design tokens once.** Define the reused styling before adding data: one header `Font` and `PatternFill`, a zebra `PatternFill` for alternate rows, a thin border side for subtle separation, and the palette of at most three colors from the design system in [the reference](references/beautiful-spreadsheets.md). Done when every later style reads from this token set and no color is picked ad hoc per cell.

3. **Write inputs as data and outputs as formulas.** Place input cells as plain typed values in their own area, then compute the totals, ratios, and derived figures with openpyxl formula strings referencing those cells — zero hand-calculated numbers in result cells. Done when changing one input cell would update every dependent cell, and no result cell holds a literal.

4. **Apply number formats and alignment per column.** Set one `number_format` on a numeric column — currency, percent, thousands-separated integer, or date — and right-align the numbers, following the formatting rules in [the reference](references/beautiful-spreadsheets.md). Done when a numeric column carries one shared format down its length and no number renders as a raw float.

5. **Style the header band and quiet the grid.** Apply the header tokens to the top row, set sensible column widths to the content, freeze the header row with `freeze_panes`, and replace heavy gridlines with zebra fills or thin borders only. Done when the header row stays visible on scroll, columns fit their content, and the sheet shows no full-grid cage.

6. **Run the design-and-correctness review.** Check the workbook against the red-flags list in [the reference](references/beautiful-spreadsheets.md): heavy gridlines, unformatted numbers, hard-coded values, an unfrozen header, mixed number formats, magic constants. Record each hit as a defect to fix. Done when the red-flags list has a verdict and no unresolved defect remains.

7. **Verify the artifact by reopening it.** Save the `.xlsx`, reopen it with openpyxl, and confirm the sheet names, the frozen pane, and a sampled formula cell match the plan from step 1 — observe the real file rather than assume it. Done when the reopened workbook reports the expected sheets, a frozen header, and a formula (not a literal) in a checked result cell.

See also: [references/beautiful-spreadsheets.md](references/beautiful-spreadsheets.md) for deterministic openpyxl generation, the design system, the inputs-calcs-outputs separation, the archetypes, the failure modes and red flags, and a worked formula-driven example.
