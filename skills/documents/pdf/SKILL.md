---
name: pdf
description: Generate an extremely beautiful, designed PDF — not a default browser print-out — by writing content as Markdown and rendering it through a deterministic script. Use when the user asks to create, generate, build, or design a PDF, a report, a proposal, an invoice, a one-pager, or a printable document, or to turn Markdown or data into a polished PDF.
---

Produce a PDF that reads as deliberately designed: a print artifact with a type scale, a
baseline grid, generous margins, AA contrast, and page furniture — never the default
"Print to PDF" look. The division of labor is the point: the LLM writes only the content as
Markdown, and `scripts/render.sh` renders it deterministically through `pandoc` plus a PDF
engine. No reportlab or weasyprint code is hand-written per run — the styling lives in a CSS
file or a pandoc template the script applies. The design system, the archetypes, the failure
modes, and a worked example live in [beautiful PDFs](references/beautiful-pdfs.md); load that
reference for the design principles before styling.

## Steps

1. **Name the document type and its sections.** State which archetype the output is (report,
   proposal, invoice, or one-pager) and list the sections that archetype needs per the
   reference. The step is done once the archetype and the section list are both written down.

2. **Write the body as Markdown.** Author the content into a `content.md` file, applying the
   archetype layout and the table rules (no border-soup, numerals right-aligned, header row
   present) from the reference. The step is done once `content.md` holds the full document
   content with headings, prose, and tables in place.

3. **Choose the styling.** Decide between a CSS stylesheet (for a CSS engine such as
   weasyprint or wkhtmltopdf) and a pandoc template, then snap the page size, the margins
   (18–25 mm floor), the type scale, the leading, and the color palette to the scales in the
   [design reference](references/beautiful-pdfs.md). The step is done once every spacing and
   type value maps to a scale in the reference, with no off-scale value remaining.

4. **Render with the script.** Run `scripts/render.sh content.md out.pdf --engine ENGINE`,
   naming the chosen engine and adding `--css FILE` for a CSS engine. The step is done once
   the command prints `wrote out.pdf` and exits zero.

5. **Verify by reopening the output.** Read the first four bytes of the rendered file and
   confirm the document opens at the intended length. The step is done once `head -c 4
   out.pdf` prints `%PDF` and the page count matches the intended length.

6. **Score against the design checklist.** Walk the rendered page against the final checklist
   in the reference: margins, type scale, baseline grid, AA contrast, break discipline, table
   styling, furniture, and the not-default-print test. The skill is done once each checklist
   line holds or carries a written, justified exception.

## Scripts

- **[`scripts/render.sh`](scripts/render.sh)** — renders Markdown to PDF through `pandoc`.
  Usage: `render.sh <content.md> <out.pdf> [--engine ENGINE] [--css FILE]`. With no
  `--engine`, the script auto-detects the first available of weasyprint, wkhtmltopdf, typst,
  tectonic, xelatex, or pdflatex. The `--css` flag applies to the CSS engines (weasyprint,
  wkhtmltopdf). Run `render.sh --selftest` to self-check the toolchain.

A PDF engine must be installed for rendering: weasyprint, wkhtmltopdf, typst, or a LaTeX
engine such as xelatex or tectonic. With no engine present, `scripts/render.sh` exits non-zero
and names the engines to install, and `--selftest` skips cleanly.

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
