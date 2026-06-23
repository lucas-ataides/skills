# Visual rules — spacing, type, color, hierarchy, layout, depth, motion

Concrete, opinionated defaults that make a web UI read as professionally designed. Each
rule is a default; override only with a stated reason. The lineage is Refactoring UI
(Adam Wathan, Steve Schoger) and the Vercel web design guidelines, distilled into
checkable values.

The governing idea: **professional design is systematic, not inspired.** Amateur work
picks values ad hoc, so nothing aligns and nothing relates. Pick a small set of scales
once, then snap every decision to them. The default house style for this skill is
Swiss/International editorial design crossed with brutalism — a strong grid, generous
whitespace, a restrained palette, and bold typographic hierarchy. The visual rules below
serve that aesthetic; the brutalist specifics live in
[aesthetic-swiss-brutalist.md](aesthetic-swiss-brutalist.md).

---

## 1. Spacing — one 8pt scale, no exceptions

Space is the cheapest tool for polish and the first thing amateurs get wrong. Define a
single scale and forbid values outside it.

**The scale** (a 4pt base, doubling into an 8pt rhythm):

```
4   8   12   16   24   32   48   64   96   128
```

Tokenize as `space-1 … space-10`. Every margin, padding, gap, and offset takes a value
from this list. A `13px` or `27px` margin is a defect, not a fine-tune.

Rules:

- **Match space to grouping.** Related items sit closer than unrelated ones (the Gestalt
  law of proximity). A label hugs its input (`space-1`/`space-2`); a form section stands
  apart from the next (`space-8`/`space-10`).
- **Whitespace is not waste.** A cheap-looking layout usually carries too little space,
  not too much. Start generous, then tighten.
- **Inner padding under the gap to neighbors fails the eye.** A card's internal padding
  should not exceed the gap separating it from siblings, or the grouping inverts.
- **Vertical rhythm.** Stack spacing in multiples of the base so baselines line up down
  the page.

Failure mode — **inconsistent spacing**: a `15px` here, a `22px` there, a `30px` below.
The page reads as drifting because no two gaps relate. Fix: round every value to the
nearest scale step.

---

## 2. Type — a modular scale, two faces, controlled measure

### Type scale

Pick sizes from a modular scale instead of arbitrary pixel jumps. A practical ramp
(roughly a 1.25 ratio, hand-tuned for the web):

```
12   14   16   18   20   24   30   36   48   60
```

Body text sits at `16px` minimum (smaller strains most readers). Tokenize as
`text-xs … text-6xl`. A genuine scale produces hierarchy for free; a dozen ad-hoc pixel
values produce mush.

### Pairing

- **Two typefaces maximum.** One for headings, one for body — or a single family across
  both. A third face is the classic tell of an amateur layout.
- **Pair by contrast, not similarity.** A geometric sans heading over a humanist sans
  body reads as intentional; two near-identical sans faces read as a mistake.
- **Use weight for variety inside one family.** A single well-built family (Inter, Geist,
  system-ui) covering 400/500/600/700 removes most reasons to add a second face.

### Line length, line height, tracking

- **Measure: 45–75 characters per line** for body copy (`~65ch` is the sweet spot).
  Constrain with `max-width: 65ch`. Long lines lose the reader between lines; short lines
  chop rhythm.
- **Line height scales inversely with size.** Body copy wants `1.5–1.6`; large headings
  want `1.1–1.25`. Tight leading on body text reads as cramped, and loose leading on
  headings reads as unglued.
- **Letter-spacing.** Leave body at default; tighten large headings slightly (`-0.01em`
  to `-0.02em`); add a little tracking to all-caps labels.
- **Limit weights and sizes on one screen.** Three to four font sizes and two to three
  weights cover almost any interface.

Failure mode — **too many fonts**: three faces, six weights, and four sizes with no
system. The page looks loud and unplanned. Fix: collapse to one or two families and a
fixed size set.

---

## 3. Color — a restrained palette, AA contrast, semantic roles

### Palette structure

A complete, restrained palette is small:

- **One neutral ramp** of 9–10 steps from near-white to near-black
  (`gray-50 … gray-900`). Most of any professional UI is neutrals.
- **One accent / brand hue**, with a few tints and shades for hover, active, and subtle
  backgrounds.
- **Semantic colors:** success (green), warning (amber), danger (red), and an optional
  info (blue). Reserve these for meaning, never for decoration.

The budget is exactly that: neutrals + one accent + three or four semantic hues. A
palette with five unrelated brand colors reads as chaos, and two or three competing
accents read as a template that shipped with sample data.

### Build full ramps, not single values

A single mid-tone gray cannot serve text, borders, and backgrounds at once. Generate a
ramp by holding hue and walking lightness (and nudging saturation at the ends). Light
backgrounds pull from the `50–100` band; borders from `200–300`; body text from
`700–900`.

### Contrast — WCAG AA is the floor

- **Body and UI text: ≥ 4.5:1** against its background.
- **Large text (≥ 24px, or ≥ 18.66px bold) and meaningful icons: ≥ 3:1.**
- **Light-gray text on white is the most common contrast failure.** A `#999` on `#fff`
  measures ≈ 2.85:1 and fails. Darken until the ratio clears 4.5:1.
- **Never encode meaning in hue alone.** A red/green-only signal disappears for
  color-blind users, so pair color with an icon, label, or shape.

The thresholds are WCAG 2.1 Success Criterion 1.4.3 (Contrast Minimum, AA): 4.5:1 for
normal text, 3:1 for large text. The "large" boundary is 18pt (24px) regular or 14pt
(≈18.66px) bold.

### Saturation and temperature discipline

- Tint neutrals slightly toward the brand temperature (a hint of blue or warmth) for
  cohesion.
- Pure `#000` on pure `#fff` is harsh; prefer a very dark neutral (`gray-900`) on a
  near-white. (Brutalist surfaces are the deliberate exception — see the aesthetic
  reference.)

Failure mode — **too many colors / low contrast**: a rainbow of unrelated hues, plus
pale text that disappears. Fix: cut to one neutral ramp and one accent, then raise every
text pair to AA.

---

## 4. Visual hierarchy — size, weight, color, space (not borders)

Hierarchy tells the eye where to look first. Build it with four tools, ranked:

1. **Size** — bigger reads as more important.
2. **Weight** — heavier reads as more important; a bold `16px` can outrank a regular
   `20px`.
3. **Color / contrast** — higher contrast advances, muted recedes. Demote secondary text
   with a lighter neutral, not a smaller size alone.
4. **Space** — isolation by whitespace confers importance without any added ink.

Principles:

- **The primary action is the loudest element.** One solid, high-contrast button;
  secondary actions go ghost, outline, or plain link. Two equally loud buttons split the
  user's attention and stall the decision.
- **De-emphasize, do not only emphasize.** Often the move is dimming the supporting text
  (lighter weight, muted color), not enlarging the lead.
- **Labels are secondary to data.** "Email" should recede; the address itself leads —
  flip the default that makes labels bold and values plain.
- **Establish, then repeat.** A heading/subhead/body pattern, once set, repeats
  everywhere for free.

Failure mode — **border-soup**: every group fenced in its own box, so the screen becomes
a grid of competing rectangles. In the default editorial/Swiss style, separation order
is **whitespace first, then a background tint, then a shadow, and a border only as a last
resort.** (Brutalism inverts this on purpose: the border *is* the system. See the
aesthetic reference — that is a stated override, not border-soup.)

Failure mode — **flat hierarchy**: everything the same size, weight, and color, so
nothing leads. Fix: enlarge the one lead element and mute the rest.

---

## 5. Layout, whitespace, density

- **Grid.** Lay out on a 12-column grid with a consistent gutter (`space-6`/`space-8`).
  Twelve divides cleanly into halves, thirds, quarters. A strong, readable grid is the
  spine of the Swiss/editorial default.
- **Alignment.** Pick an edge and hold it. A strong left edge down a column beats ragged
  centering. Optical alignment beats mathematical alignment when an icon or glyph sits
  beside text.
- **Everything aligns.** Text edges, icon centers, and card boundaries land on the shared
  grid. One stray left edge reads as "off" without the viewer locating the cause.
- **Density matches context.** A marketing page breathes (large type, deep spacing); a
  data table packs tighter — but still on the same scale, never off it.
- **Constrain content width.** Full-bleed text on a wide monitor is unreadable; cap
  content containers (`max-width` ~`1100–1280px`) and cap prose at the `65ch` measure.

Failure mode — **centered everything**: every block centered, so no edge anchors the eye
and the layout wanders. Centering suits short hero copy and empty states, yet breaks down
for forms, lists, paragraphs, and dense UI. Fix: left-align body content and reserve
centering for short, isolated blocks.

---

## 6. Responsive — mobile-first, real breakpoints

- **Design the small viewport first.** Start at ~`360px`, then layer enhancements upward
  with `min-width` queries. A mobile-first base stays simple and degrades well.
- **Breakpoints** (content-driven, but these are sane defaults):

```
sm  640    md  768    lg  1024    xl  1280    2xl 1536
```

- **Reflow, do not shrink.** A multi-column desktop grid collapses to one column on a
  phone; type and tap targets hold above legibility rather than scaling down past it.
- **Tap targets ≥ 44×44px.** Small touch targets fail fingers.
- **No horizontal scroll.** A sideways scrollbar at any breakpoint is a layout bug.
- **Fluid type with clamps.** `clamp()` lets headings scale between a floor and a ceiling
  without a breakpoint per size.

---

## 7. Depth and shadows — sparing, soft, consistent

This section governs the Swiss/editorial default. The brutalist direction swaps soft
shadows for hard offset shadows — covered in the aesthetic reference.

- **One elevation system.** Define a small shadow ramp (`shadow-sm`, `shadow-md`,
  `shadow-lg`) and pull from it; never hand-roll a one-off shadow.
- **Soft and low-contrast.** Real shadows are diffuse — large blur, low opacity, a slight
  downward offset. A hard, dark, offset drop shadow looks dated in this style.
- **Layer shadows for realism.** Two stacked shadows (one tight, one wide and faint) read
  more naturally than a single heavy one.
- **Elevation carries meaning.** Higher elevation = closer to the user (modals, popovers,
  dragged items). Resting cards stay low or flat.
- **Light comes from above.** Top edges catch light, bottom edges cast shadow; a subtle
  top inset highlight sells a raised surface.

Failure mode — **shadow everywhere**: every element floating on a heavy drop shadow, so
nothing reads as actually elevated. Fix: flatten resting surfaces and reserve shadow for
genuinely raised layers.

---

## 8. Motion — with purpose

- **Animate to explain, not to decorate.** Motion shows state change, directs attention,
  or confirms an action. Movement without meaning is noise.
- **Duration: 150–300ms** for most UI transitions. Faster feels broken; slower feels
  sluggish.
- **Easing.** Use ease-out for entrances (fast then settle) and ease-in for exits. Linear
  easing reads as mechanical.
- **Animate cheap properties.** Prefer `transform` and `opacity` (compositor-friendly);
  animating `width`, `height`, or `top` triggers layout and janks.
- **Respect `prefers-reduced-motion`.** A reduced-motion preference disables or shrinks
  non-essential animation, so honor it.
- **Stagger sparingly.** A small entrance stagger on a list adds polish; a long cascade
  wastes the user's time.

---

## 9. Accessibility floor for visuals

Accessibility is design quality, not a separate checklist. The interaction-level
accessibility method (keyboard, focus management, ARIA, screen readers) lives in
[ux-and-states.md](ux-and-states.md); the visual floor is here.

- **Contrast at AA** (see section 3) for text and meaningful non-text.
- **Visible focus.** Every interactive element shows a clear focus ring for keyboard
  users. Removing the outline without a replacement is an exclusion.
- **Hit area ≥ 44×44px** for touch.
- **Honor reduced motion and respect system color-scheme** (light/dark) preferences.
- **Color is never the only signal.** Pair every color-coded meaning with a label, icon,
  or shape.

---

## Red flags — fast scan

A design likely needs this section's rules when any of these appear:

- Spacing values off the scale (`13px`, `27px`, re-eyeballed margins).
- Three or more typefaces, or font sizes chosen ad hoc (13, 15, 17, 19, 22 with no
  ratio).
- More than one accent/brand hue competing for attention.
- Gray text that vanishes on its background (under 4.5:1).
- Every group boxed in its own border (border-soup) outside a deliberate brutalist
  system.
- Two or more equally loud primary buttons.
- Everything centered, including forms and body copy.
- A heavy, hard drop shadow on every element in a soft/editorial design.
- Animations that fire with no state change behind them.
- No visible focus ring on keyboard navigation.
- Body lines running the full width of a wide screen.
- Two of the same component (button, card, input) differing in height, padding, or radius
  for no functional reason.

---

## Worked example — fixing a cramped, low-hierarchy hero

### Before

```html
<section style="text-align:center; padding:10px;">
  <p style="font-size:13px; color:#aaa; margin-bottom:5px;">WELCOME</p>
  <h1 style="font-size:22px; color:#444; margin-bottom:6px;">
    The all-in-one platform for your team
  </h1>
  <p style="font-size:13px; color:#aaa; margin-bottom:9px;
            max-width:900px; margin-left:auto; margin-right:auto;">
    Plan, build, and ship in one place with dashboards, automation,
    reporting, integrations, and everything else your team could ever need.
  </p>
  <button style="font-size:13px; padding:6px 10px; border:1px solid #ccc;
                 color:#444; background:#fff;">Get started</button>
  <button style="font-size:13px; padding:6px 10px; border:1px solid #ccc;
                 color:#444; background:#fff; margin-left:6px;">Learn more</button>
</section>
```

What is wrong, named against the rules:

- **Spacing off-scale and starved** — `10px`, `5px`, `6px`, `9px` belong to no system,
  and all are too small (section 1).
- **Flat hierarchy** — heading at `22px`/`#444` barely outranks the body; the eye finds
  no entry point (section 4).
- **Low contrast** — `#aaa` on white sits near 2.5:1, well under AA (section 3).
- **Two equally weak buttons** — identical outline styling, so no primary action leads
  (section 4).
- **Measure too wide** — `max-width:900px` lets body copy run far past 75 characters
  (section 2).
- **Centered everything** — centered multi-line body copy gives the eye no left edge to
  track (section 5).

### After

```html
<section class="hero">
  <p class="hero__eyebrow">Welcome</p>
  <h1 class="hero__title">The all-in-one platform for your team</h1>
  <p class="hero__subtitle">
    Plan, build, and ship in one place — dashboards, automation,
    and reporting, together.
  </p>
  <div class="hero__actions">
    <button class="btn btn--primary">Get started</button>
    <button class="btn btn--ghost">Learn more</button>
  </div>
</section>

<style>
  .hero { max-width: 48rem; padding: 64px 24px; }          /* space-10 / space-6 */
  .hero__eyebrow {
    font-size: 14px; font-weight: 600; letter-spacing: 0.04em;
    color: var(--accent-600); margin: 0 0 12px;             /* space-3 */
  }
  .hero__title {
    font-size: 48px; line-height: 1.1; font-weight: 700;
    letter-spacing: -0.02em; color: var(--gray-900);
    margin: 0 0 16px;                                       /* space-4 */
  }
  .hero__subtitle {
    font-size: 18px; line-height: 1.6; color: var(--gray-600);
    max-width: 60ch; margin: 0 0 32px;                      /* measure + space-8 */
  }
  .hero__actions { display: flex; gap: 16px; }              /* space-4 */
  .btn { font-size: 16px; padding: 12px 24px; border-radius: 8px; }
  .btn--primary {
    background: var(--accent-600); color: #fff; font-weight: 600;
    box-shadow: var(--shadow-sm);
  }
  .btn--ghost {
    background: transparent; color: var(--gray-700);
    border: 1px solid var(--gray-300);
  }
</style>
```

What changed, and why it now reads as professional:

- **Every value on the scale** — `12 / 16 / 24 / 32 / 64` spacing, type from the modular
  ramp (`14 / 18 / 48`) (sections 1–2).
- **Strong hierarchy** — `48px` bold near-black title dominates; eyebrow and subtitle
  recede via size, weight, and muted neutrals — no borders involved (section 4).
- **AA contrast** — `gray-900` title and `gray-600` subtitle both clear 4.5:1
  (section 3).
- **One primary action** — solid accent button leads; the ghost button supports
  (section 4).
- **Controlled measure** — `max-width: 60ch` holds the subtitle inside the 45–75
  character band (section 2).
- **Restrained depth** — a single `shadow-sm` lifts the primary button; nothing else
  floats (section 7).
- **Left-aligned option ready** — drop `text-align`/centering for a left edge on denser
  pages; centering stays only for this short hero block (section 5).

---

## Visual checklist

A design passes when each line below holds or carries a written, justified exception:

- [ ] **Spacing** — every margin, padding, and gap maps to a step on the 8pt scale.
- [ ] **Type scale** — sizes drawn from one modular scale; body ≥ 16px.
- [ ] **Typefaces** — two faces or fewer.
- [ ] **Color budget** — one neutral ramp + one accent + semantic hues only.
- [ ] **Contrast** — text and meaningful non-text at AA or higher (4.5:1 / 3:1).
- [ ] **Hierarchy** — built from size, weight, color, and space; one clear primary
  action.
- [ ] **No border-soup** — separation by whitespace or tint before any border (unless the
  brutalist system is the stated choice).
- [ ] **Measure** — body copy at 45–75 characters per line.
- [ ] **Responsive** — layout intact at 360px; no horizontal scroll; tap targets ≥ 44px.
- [ ] **Depth** — one shadow tier; resting surfaces flat or low.
- [ ] **Motion** — purposeful only, 150–300ms, reduced-motion honored.
- [ ] **Alignment** — every edge lands on the shared grid; one consistent radius set.
