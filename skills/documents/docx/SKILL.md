---
name: docx
description: Generate beautiful, consistent Word documents with python-docx by defining named styles once and reusing them. Use when the user asks to create, build, generate, or write a .docx / Word document, report, proposal, contract, memo, or letter; when a doc must look designed rather than default-Calibri; or when a Word file needs a cover, table of contents, headers, footers, or page numbers.
---

A Word document built by hand-formatting each paragraph drifts into the default-Calibri wall: inconsistent headings, ad-hoc spacing, and a layout no one can restyle in one move. A beautiful document is built the opposite way — a small set of **named styles** defined once, then applied everywhere, so the whole file shares one type scale, one spacing rhythm, and one palette, and an editor restyles it by changing the style, not every paragraph.

Generate the document deterministically with python-docx. Push formatting into named styles, not inline runs. The depth bar for the design system and its failure modes lives in [references/beautiful-docx.md](references/beautiful-docx.md), grounded in the [foundation](../../meta/foundation/SKILL.md) determinism doctrine.

## Steps

1. **Name the archetype and its sections.** State which document this is — report, proposal, contract, or memo — and list the sections it requires from the archetype table in [the reference](references/beautiful-docx.md). Done when the section list and the archetype are written down before any code runs.

2. **Define the style sheet first.** Before adding content, build the named styles the document will use: a type scale of heading levels, a body style, a caption, a table style, and the cover styles — each set on a `python-docx` style object with font, size, color, and spacing per the design system in [the reference](references/beautiful-docx.md). Done when the document carries at most two font families and every text style reads from one defined scale.

3. **Build the structure from styles, never inline.** Add each cover block, heading, paragraph, list, table, and image by applying a named style, with zero ad-hoc font or size set on an individual run. Done when no paragraph carries manual formatting that a named style could own.

4. **Set the page frame.** Configure sections, margins, and a header and footer carrying the page number field, following the section recipe in [the reference](references/beautiful-docx.md). Done when every section renders a header, a footer, and a live page number.

5. **Insert the cover and table of contents.** Add a styled cover page and a TOC field bound to the heading styles from step 2, so the TOC populates from the document outline. Done when the cover uses the cover styles and the TOC field references the named heading levels.

6. **Run the design-system review.** Check the document against the red-flags list in [the reference](references/beautiful-docx.md): a Calibri wall, manual formatting in place of styles, inconsistent heading levels, dense tables, sub-AA contrast. Record each hit as a defect to fix. Done when the red-flags list has a verdict and no unresolved defect remains.

7. **Verify the artifact by opening it.** Save the `.docx`, reopen it with python-docx, and confirm the styles, heading outline, and page count match the plan from step 1 — observe the real file, never assume it. Done when the reopened document reports the expected named styles and heading hierarchy.
