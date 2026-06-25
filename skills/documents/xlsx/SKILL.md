---
name: xlsx
description: Generate extremely beautiful, correct spreadsheets deterministically — the model writes a JSON spec of sheets, columns, rows, and number formats, and a Python script renders the styled workbook via openpyxl. Use when the user asks to create, build, or generate an .xlsx / Excel / spreadsheet, a data table, or a tabular report; when numbers must be consistently formatted; or when a workbook needs styled headers, frozen panes, and sized columns rather than raw gridlines.
---

A spreadsheet built by typing values into cells drifts into the raw-grid wall — heavy gridlines everywhere, numbers in no consistent format, ad-hoc per-cell styling that varies run to run. The deterministic alternative splits the work: the model decides the structure and supplies the data, and a fixed script renders the styling the same way every time. The model writes a JSON spec; `scripts/render.py` turns that spec into a workbook with one reused header style, a frozen header row, content-sized columns, and the per-column number formats the spec names.

Push every design decision into the script and every data decision into the spec. The depth bar for the design system, the archetypes, and the failure modes lives in [references/beautiful-spreadsheets.md](references/beautiful-spreadsheets.md), grounded in the [foundation](../../meta/foundation/SKILL.md) determinism doctrine.

## Steps

1. **State the workbook's purpose and its sheets.** Name which spreadsheet this is — data table or tabular report — and list the sheets with their columns, drawing the archetype from [the reference](references/beautiful-spreadsheets.md). This step ends when the sheet names and the per-sheet column lists are written down ahead of the spec.

2. **Assemble the data into a JSON spec.** Build one spec object whose `sheets` list holds an entry per sheet, each carrying a `name`, a `columns` list, a `rows` list of row arrays, and a `number_formats` map from column name to format string. Keep every row's length within the column count, and choose one format per numeric column from the table in [the reference](references/beautiful-spreadsheets.md). This step ends when the spec is valid JSON whose every row fits its columns and whose every number-format key names a real column.

3. **Render the workbook deterministically.** Run `scripts/render.py build <spec.json> <out.xlsx>` to write the styled workbook from the spec. The script applies the bold filled header, freezes the header row at `A2`, sizes columns to their content, and stamps the per-column number formats — no styling is hand-written per run. This step ends when the command exits zero and prints the written workbook path.

4. **Verify the artifact by reopening it.** Reopen the saved `.xlsx` with `openpyxl.load_workbook`, then confirm the sheet names, the header cells, a sampled data value, and the frozen pane match the spec from step 1 — observe the real file rather than assume it. This step ends when the reopened workbook reports the expected sheets, a header cell equal to its column name, a data cell equal to its spec value, and `freeze_panes` equal to `A2`.

## Scripts

`scripts/render.py` is the deterministic renderer. Define the data and structure in a JSON spec, then let the script own all styling.

- `render.py build <spec.json> <out.xlsx>` — read the spec and write a styled `.xlsx`.
- `render.py --selftest` — build an in-code fixture, reopen it, and assert the header and a data cell; this prints `skipped` when openpyxl is absent and exits zero.

The spec is one object with a non-empty `sheets` list. Each sheet entry holds a `name`, a non-empty `columns` list, an optional `rows` list of arrays, and an optional `number_formats` map keyed by column name:

```json
{
  "sheets": [
    {
      "name": "Sheet1",
      "columns": ["Region", "Q1", "Q2"],
      "rows": [["West", 10, 20], ["East", 5, 8]],
      "number_formats": {"Q1": "#,##0", "Q2": "#,##0"}
    }
  ]
}
```

The renderer validates at the boundary — a missing or empty `sheets` list, a sheet without a `name` or `columns`, a row wider than its column count, or a number-format key naming an unknown column each fail with a clear stderr message and a non-zero exit.

See also: [references/beautiful-spreadsheets.md](references/beautiful-spreadsheets.md) for the design system, the per-column number formats, the archetypes, the failure modes and red flags, and the styling the renderer applies.

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
