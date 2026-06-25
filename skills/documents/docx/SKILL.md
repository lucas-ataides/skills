---
name: docx
description: Generate beautiful, consistent Word documents by writing the body as Markdown and rendering it with pandoc against a reusable reference-doc style template. Use when the user asks to create, build, generate, or write a .docx / Word document, report, proposal, contract, memo, or letter; when a doc must look designed rather than default-Calibri; or when a Word file needs consistent headings, lists, tables, and styling.
---

A Word document hand-formatted paragraph by paragraph drifts into the default-Calibri wall: inconsistent headings, ad-hoc spacing, and a layout no one can restyle in one move. A beautiful document is built the opposite way — the design lives in a **reference template** of named styles, and every run reuses that one template, so the whole file shares one type scale, one spacing rhythm, and one palette, and an editor restyles it by changing the template, not every paragraph.

Generation is deterministic and split in two. The model writes only the **content** as Markdown; a shell script renders that Markdown to `.docx` with `pandoc`, applying an optional reference-doc template for the brand. The model never hand-writes document-builder code, so the same Markdown yields the same document every run. The design system the template should encode — the type scale, the two-face ceiling, the spacing rhythm, AA contrast, and the document archetypes — lives in [references/beautiful-docx.md](references/beautiful-docx.md), grounded in the [foundation](../../meta/foundation/SKILL.md) determinism doctrine.

## Steps

1. **Name the archetype and its sections.** State which document this is — report, proposal, contract, or memo — and list the sections drawn from the archetype table in [the reference](references/beautiful-docx.md). Done when the section list and the archetype are written down before any content is drafted.

2. **Write the document body as Markdown.** Compose the content in GitHub-Flavored Markdown, mapping structure to Markdown: `#`/`##` headings for the section outline, `-`/`1.` lists, and pipe tables for tabular data, with no manual font or spacing instructions in the prose. Done when the Markdown covers every named section from step 1 and carries a heading outline with no skipped level.

3. **Apply the brand through a reference template.** Produce a baseline template by running `pandoc -o reference.docx --print-default-data-file reference.docx`, restyle that file in Word to match the design system in [the reference](references/beautiful-docx.md), and save the result as the reference doc. Done when the reference `.docx` carries the type scale, the paired typefaces, and the spacing and color choices from the design system.

4. **Render deterministically with the script.** Run `scripts/render.sh <content.md> <out.docx> [reference.docx]`, passing the reference template as the third argument so the brand applies during conversion. Done when the script prints `wrote <out.docx>` and exits zero.

5. **Verify the artifact by opening it.** Inspect the rendered file with `unzip -l <out.docx>` and confirm the listing contains `word/document.xml` — observe the real file, never assume it. Done when the listing reports `word/document.xml` and the reopened document shows the expected heading hierarchy.

## Scripts

- `scripts/render.sh <content.md> <out.docx> [reference.docx]` — renders Markdown to `.docx` via `pandoc --from gfm --to docx`, adding `--reference-doc` only when a template path is given AND the file exists. A missing content file exits 2; an absent `pandoc` exits 3; a successful render prints `wrote <out.docx>`. Run `scripts/render.sh --selftest` to render a fixture and assert the output is a valid docx (the gate `tools/run_selftests.py` discovers this check).

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
