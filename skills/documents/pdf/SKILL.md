---
name: pdf
description: Generate an extremely beautiful, designed PDF — not a default browser print-out — via a deterministic toolchain and a print design system. Use when the user asks to create, generate, build, or design a PDF, a report, a proposal, an invoice, a one-pager, or a printable document, or to turn HTML, Markdown, or data into a polished PDF.
---

Produce a PDF that reads as deliberately designed: a print artifact with a type scale, a
baseline grid, generous margins, AA contrast, and page furniture — never the default
"Print to PDF" look. The design system, the toolchain, the archetypes, the failure modes,
and a worked example live in [beautiful PDFs](references/beautiful-pdfs.md); load that
reference before building.

## Steps

1. **Name the archetype and the path.** State which archetype the output is (report,
   proposal, invoice, or one-pager) and which generator fits per the reference table:
   WeasyPrint for a designed HTML/CSS document, reportlab for a computed or precise layout,
   pandoc for Markdown source. The step is done once the archetype and the generator are
   both written down.

2. **Confirm the generator is installed.** Run the install command for the chosen path from
   the reference (for example `pip install weasyprint`), then run its `--version`. The step
   is done once the version prints with a zero exit status.

3. **Set the page system.** Define page size, margins (18–25 mm floor), the type scale, the
   baseline leading, the color palette, and the header/footer/page-number furniture — in a
   `@page` print stylesheet for WeasyPrint, or in document and style parameters for
   reportlab. The step is done once every spacing and type value maps to the scales in the
   reference, with no off-scale value remaining.

4. **Author the content against the system.** Place the content into the template or
   flowables, applying the archetype layout and the table rules (no border-soup, numerals
   right-aligned, header row repeated) from the reference. The step is done once the source
   carries break-discipline directives (`orphans`/`widows`/`break-inside` for WeasyPrint, or
   `KeepTogether`/`keepWithNext` for reportlab).

5. **Render the PDF.** Run the generator against the source. The step is done once the
   command exits zero, emits no warnings, and writes the `.pdf` file.

6. **Open and inspect the output.** Open the rendered PDF in a viewer and read the page
   count. The step is done once the file opens and the page count matches the intended
   length.

7. **Score against the design checklist.** Walk the rendered page against the final
   checklist in the reference: margins, type scale, baseline grid, AA contrast, break
   discipline, table styling, furniture, and the not-default-print test. The skill is done
   once every checklist line holds or carries a written, justified exception.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
