---
name: brandkit
description: Build or audit a coherent brand kit / design system for a founder's product or personal brand — positioning, voice, and a role-based, AA-checked, tokenized visual identity that holds across every surface. Use when the user asks to create, define, document, refresh, or audit a brand kit, brand guidelines, design system, visual identity, color palette, type scale, design tokens, or brand voice and tone; or when a product looks or sounds inconsistent across its site, app, social, and decks.
---

Define or audit a brand kit the way a design lead does: judge it as one coherent system that renders the same intent across the site, the app, social, and decks, not as a swatch page beside a font list. Coherence is the deliverable; a second brand blue, a runaway font, or a voice that drifts between channels is the defect.

Work the structure, the rules, and the failure modes in [the brand system reference](references/brand-system.md). Pin the strategy before the pixels, name every visual decision as a token, and end on criteria a reviewer can check line by line.

## Steps

1. **Pin the foundations.** State the positioning in one sentence that excludes at least one named competitor, three-to-five personality traits each pinned against an opposite, and the voice on every axis in the reference (formality, energy, warmth, humor, authority) with a say / never-say lexicon. The step is done when positioning names a differentiator a rival cannot claim, every trait carries an opposite, and the voice axes plus lexicon are written.

2. **Define the color system by role.** Name each color by its job — brand, accent, neutral scale, background, status — give each one value per theme, and pair every text-bearing role with a foreground meeting WCAG AA (4.5:1 body, 3:1 large and UI). The step is done when every color has a role and a foreground with its measured AA ratio, and no role carries a second hand-picked value.

3. **Define the type, spacing, radius, and elevation scales.** Constrain type to one or two families on a fixed size ramp with named weights; set spacing as multiples of a 4px or 8px base; map radius and elevation to named steps. The step is done when type, spacing, radius, and elevation each resolve to a named scale and no value sits off its ramp.

4. **Set logo rules, iconography, and imagery direction.** Specify the logo variants per surface, clear space as a fraction of the mark, a minimum size, and an explicit misuse list; pick one icon library and one style; name the imagery subject, treatment, and mood tied to the personality traits. The step is done when the logo carries a misuse list, icons share one library, and imagery direction is written against the traits from step 1.

5. **Name the tokens for code.** Name every value by role, not by hue — `color.brand`, not `color.blue-500` — and split primitive, semantic, and component layers so a value lives in one place. The step is done when every token names a role, the three layers are separated, and one source file is named as the single source of truth.

6. **Check consistency across surfaces, then sweep for failure modes.** Confirm one token set drives the site, app, social, decks, and email, with per-surface changes limited to density and format. Sweep the kit against the reference failure modes — inconsistent palette, no tokens, logo misuse, voice drift, contrast failures, scale leakage — and against the red-flag list. The step is done when one token set is confirmed across surfaces and every failure mode resolves to a fix or to a stated pass.

7. **Report against the criteria.** Compile the kit (or the audit) into the worked-example shape in the reference: foundations and voice on top, a token table below with a role and an AA pair on every color. The step is done when a reviewer can verify, line by line, that every color has a role plus an AA pair, every value sits on a named scale, the voice carries a lexicon, and no token is a one-off.

With a vault configured, record this skill's outcome to the second brain (opt-out; ask first if the value is unclear) — see [Feed the second brain](../../meta/foundation/SKILL.md).
