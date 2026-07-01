---
name: frontend-design
description: Design or review web UI as one discipline — visual system, UX and usability, taste and anti-slop, and information architecture with conversion/SEO. Default aesthetic is Swiss/editorial crossed with brutalism, WCAG AA floor. Use when building or restyling a landing page, marketing site, dashboard, app screen, form, or component; when a UI looks amateur, cramped, generic, templated, or AI-slop; when fixing missing states, weak hierarchy, contrast or keyboard gaps, or traffic that never converts.
---

Front-of-house design is one discipline, not four loosely related ones. A screen earns
its keep only when the visual system, the usability, the taste, and the site structure all
hold at once: tidy pixels over an invisible empty state still fail the user, and a polished
component on the wrong page pointing nowhere still leaks every visitor. Treat each rule
below as a default to follow unless a stated reason overrides it.

The default aesthetic this skill reaches for is **Swiss/International editorial design
crossed with brutalism** — a strong grid, generous whitespace, a restrained palette, bold
typographic hierarchy, raw and honest structure, and high contrast (reference site:
misostack.com). WCAG AA is a floor that holds even in the brutalist direction (4.5:1
normal text, 3:1 large text). For brand-level positioning, voice, and tokens that span
every surface, see [../brandkit/SKILL.md](../brandkit/SKILL.md).

The depth lives in five references; load the ones a task touches before judging or
building:

- [references/visual-rules.md](references/visual-rules.md) — spacing, type, color,
  hierarchy, layout, depth, motion, and the visual accessibility floor.
- [references/ux-and-states.md](references/ux-and-states.md) — Nielsen heuristics,
  affordances, forms, the five system states, feedback, navigation, and interaction-level
  accessibility.
- [references/taste-and-anti-slop.md](references/taste-and-anti-slop.md) — the
  intentional-vs-generic test, the markers of taste, and the visual and prose tells of AI
  slop with the moves that defeat them.
- [references/aesthetic-swiss-brutalist.md](references/aesthetic-swiss-brutalist.md) — the
  default house style, where it fits and where it does not, and an accessible worked
  example.
- [references/information-architecture.md](references/information-architecture.md) — page
  taxonomy, the conversion path, landing-page message hierarchy, and SEO structure.

## Steps

1. **Frame the surface, the user, and the one goal.** State the surface under design
   (landing page, dashboard, form, component, or whole site), the primary user, and the
   single job the surface exists to complete, then load the references the task touches.
   For a multi-page site, name the one primary conversion per
   [references/information-architecture.md](references/information-architecture.md). Done
   when the surface, its user, and its single primary action (or site-level conversion) are
   each written in one sentence, and no two actions both claim "primary."

2. **Lock the visual system.** Adopt one 8pt spacing scale, one modular type scale capped
   at two typefaces, and a restrained palette (one neutral ramp, one accent, semantic
   hues), per [references/visual-rules.md](references/visual-rules.md); then choose the
   aesthetic, defaulting to the Swiss-brutalist house style in
   [references/aesthetic-swiss-brutalist.md](references/aesthetic-swiss-brutalist.md)
   unless the brief or a trust-sensitive audience calls for a calmer treatment. Done when
   every margin, padding, gap, and font-size maps to a named scale step with zero off-scale
   values, the palette sits within budget, and the chosen aesthetic is named.

3. **Build hierarchy and verify contrast.** Rank elements by importance and express that
   rank through size, weight, color, and whitespace rather than borders, giving the surface
   exactly one primary action; then check every text-on-background pair, including text on
   an accent, with a contrast checker rather than the eye — brandkit's `tokens.py contrast
   <fg> <bg>` is the deciding gate, with `axe` or Lighthouse as advisory second opinions.
   Done when the primary action is the most prominent
   element, no separation relies on a border that whitespace or a tint could carry (outside a
   stated brutalist system), and the checker reports every pair at WCAG AA or higher (4.5:1
   body, 3:1 large).

4. **Complete the UX — states, forms, feedback, navigation.** Inventory the loading, empty,
   error, partial, and success state of every data view; give each form persistent labels,
   inline validation, and preserved input; confirm every write; and mark the current
   location in navigation, per
   [references/ux-and-states.md](references/ux-and-states.md). Done when no data view sits
   at success-only, each form field carries a visible label and a per-field error path,
   every write raises a visible confirmation, and every destructive action has a
   confirmation or an undo.

5. **Wire accessibility and responsive behavior.** Verify keyboard reach and order, a
   visible and managed focus ring, native semantics with ARIA only for the gaps, tap
   targets of at least 44×44px, a mobile-first layout, and no signal carried by color
   alone. Done when every interactive control activates from the keyboard with a visible
   focus ring, the layout holds at 360px wide with no horizontal scroll, and no meaning
   rests on color alone.

6. **Run the taste and anti-slop pass.** Judge every element against the
   intentional-vs-generic test and scan for the visual and prose slop tells in
   [references/taste-and-anti-slop.md](references/taste-and-anti-slop.md) — purple-default
   gradients, the centered two-button hero, three-card rows, emoji headers, unthemed
   component-kit defaults, hedging copy, and the "it's not just X, it's Y" frame. Done when
   no element reads as a default nobody chose, no slop tell survives, and any concrete claim
   in the copy is real.

7. **Review against the conversion path and report by severity.** For a site, walk it as the
   buyer from an awareness entry point to the primary conversion and resolve every IA red
   flag (navigation overload, no clear CTA, orphan pages, keyword-stuffing); then label each
   finding blocker, major, or minor, tied to the principle it failed and the user task or
   conversion it endangers, and pair it with the observable condition that closes it. Done
   when a continuous click path runs entry → consideration → decision (for a site) and every
   finding carries a severity, a cause, and a verifiable fix condition.

Frontend code is code — pass the [appsec](../../engineering/appsec/SKILL.md) gate before it ships.

With a vault configured, prime from the second brain before starting and feed the outcome after (opt-out; the prime is read-only, ask before writing) — see [the second-brain protocol](../../meta/foundation/SKILL.md).
