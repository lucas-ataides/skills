# Taste and anti-slop — intentional vs generic, and defeating AI slop

Taste is not a mystery and not a gift. Taste is a trained eye plus a short list of
decisions made on purpose. A polished UI and a generic one are usually built from the
same components — the difference is that every value in the polished one was chosen by a
human, and most values in the generic one were left at a default. A UI rarely fails on a
single broken rule; a UI fails by accumulating small defaults nobody decided.

This reference defines what taste is, the concrete markers that signal it, the one test
that catches its absence, the taste-killing anti-patterns, the specific tells of
AI-generated "slop," the four moves that defeat slop, the failure modes of de-slopping
itself, and two worked before/afters. The root judgment runs through all of it:

> **Does this look intentional, or does it look generic?**

A **generic** element is one no human chose — a framework default, a round number nobody
measured, a color lifted whole from a swatch, a layout that matches a thousand starter
templates. A generic screen is not ugly; generic is worse than ugly, because generic is
forgettable. It reads as software nobody cared about. AI slop is the extreme case: **the
visible average of the training set**, the most-likely design and the most-likely
sentence, the artifact everyone has already seen.

## What taste is

Taste in UI reduces to five disciplines. None requires talent; each requires a decision.

- **Restraint.** The instinct to remove, not add. A tasteful screen uses one accent color,
  one or two weights, one shadow depth. Restraint is the hardest discipline because adding
  feels like progress and removing feels like loss — yet a screen improves far more often
  by subtraction than by addition.
- **Hierarchy.** A clear visual order that tells the eye where to land first, second,
  third. Size, weight, color, and spacing encode importance. A screen with no hierarchy
  reads as a wall; a screen with inverted hierarchy (a label louder than its value) reads
  as broken.
- **Consistency.** The same decision repeated everywhere. One spacing scale, one radius,
  one set of type sizes. Inconsistency is the loudest tell of an amateur build — three
  button heights and four grays announce that no system exists.
- **Attention to detail.** The 1px misalignment, the inconsistent gap, the icon optically
  off-center. Detail is invisible when right and corrosive when wrong; a reader cannot name
  the defect but feels the result as "cheap."
- **Intentionality.** Every value traces to a reason. A 24px gap because the scale says 24,
  not because 24 felt fine. Intentionality is the meta-discipline — the other four are its
  consequences.

## How to build taste

Taste is built by deliberate input, not by waiting for inspiration.

1. **Gather references.** Keep a folder of UIs that look right. Pull from products with
   known craft — Linear, Stripe, Vercel, Things, Arc, Raycast, and the Swiss-brutalist
   reference misostack.com. A reference library converts vague aspiration into a concrete
   target to measure against.
2. **Study great products in detail.** Open one tasteful screen and measure it. Read the
   spacing values, count the type sizes, name the single accent color, note where shadows
   appear and where shadows do not. The eye trains through measurement, not through
   glancing.
3. **Name what works.** For one admired screen, write the specific reason in words — "one
   accent, everything else gray," "huge line-height on body copy," "icons all one weight."
   A reason stated in words becomes a rule the hand can apply later.
4. **Copy, then diverge.** Rebuild a screen pixel-for-pixel from a product with taste. The
   copy teaches the underlying decisions; the divergence — changing one variable at a time
   afterward — teaches which decisions carry the look. The copy-then-diverge loop is the
   fastest path from blank intuition to reliable judgment.
5. **Ship and compare.** Place a built screen beside its reference at the same zoom. The
   gap that appears is the next thing to fix. The eye that has just compared is sharper
   than the eye that has only built.

## The concrete markers of taste

Vague advice ("make it clean") helps no one. These markers are observable and binary.

- **One accent color.** A single saturated hue carries calls-to-action and active states;
  the rest of the screen lives in a neutral gray ramp. Two or three competing accents read
  as a template that shipped with sample data.
- **A real type scale.** Four to six sizes drawn from a ratio (for example
  12 / 14 / 16 / 20 / 30 / 48), not a dozen arbitrary pixel values. A genuine scale
  produces hierarchy for free; ad-hoc sizes produce mush.
- **Generous whitespace.** Padding and gaps that feel slightly too large to a beginner.
  Cramped UIs read as cheap, and the single highest-leverage upgrade on most amateur
  screens is more space around and between elements.
- **Everything aligned.** Text edges, icon centers, and card boundaries land on a shared
  grid. One stray left edge is the difference a reader registers as "off" without locating
  the cause.
- **Consistent radii and borders.** One corner radius (or a deliberate small set), one
  border color, one border width. A 4px card beside an 8px card beside a 16px card signals
  an absent system.
- **No default-framework look.** The screen does not announce its toolkit. Untouched
  Bootstrap blue, the stock Material elevation stack, the default Tailwind-demo gray card —
  each is a signature of "configured, not designed."

## Why slop happens — regression to the training mean

A language model samples toward the center of its distribution. The center is dense with
the most-repeated patterns, so an unguided generation lands on the median SaaS landing
page and the median blog intro every time. Three forces compound the pull:

- **Frequency bias.** The purple-gradient hero and the "in today's fast-paced world"
  opener appear in the corpus tens of thousands of times, so each is the safest next token.
- **Risk aversion.** A distinctive choice sits in the low-probability tail, and a model
  with no instruction to take a position avoids the tail by construction.
- **Absent constraints.** A real brief carries a budget, an audience, a deadline, a
  competitor to beat. A prompt that omits all four leaves nothing to push the output
  off-center, so it settles at the mean.

The corollary names the cure: slop is the *default*, not a *mistake*. Distinctive work is
the output of constraints the median lacks. Add the constraints and the average dissolves.

## Visual tells of AI-generated UI

Detection pass over a generated interface. Each tell is a token the model reached for
because the corpus reached for it first. The passes run loudest-first.

### Palette and surface tells

- **Purple-to-indigo gradients.** The signature of a thousand generated landing pages: a
  `#6366f1`-to-`#8b5cf6` diagonal on the hero, the buttons, and the icon backgrounds.
  Violet is the house color of the training mean. A real brand picks a color from its own
  meaning, not from the default Tailwind indigo ramp.
- **Glassmorphism with no reason.** Frosted translucent cards with backdrop-blur, stacked
  over a blurry gradient blob, used where a plain opaque surface would read better. The
  effect is decoration borrowed from a dribbble trend, signifying nothing about the
  content.
- **Uniform soft shadows everywhere.** The same `0 4px 6px rgba(0,0,0,0.1)` drop shadow on
  every card, button, and input, so nothing sits closer to the reader than anything else.
  Real elevation is a hierarchy; uniform shadow is wallpaper.
- **Default rounded-2xl on everything.** One border radius applied to cards, buttons,
  avatars, and images alike, because the model never chose a radius — the model accepted
  the framework default.

### Layout tells

- **The generic centered hero.** Centered headline, centered one-line subhead, two stacked
  buttons (a filled "Get started" and an outline "Learn more"), a gradient or a dashboard
  screenshot below. The exact composition of the median template. The layout is not wrong;
  the layout is anonymous.
- **The three-card feature row.** Three equal columns, each an icon in a tinted circle, a
  two-word title, and a sentence of body. Always three, because three balances visually and
  the corpus settled on three — not because the product has exactly three things worth
  saying.
- **The emoji bullet list.** Feature lists prefixed with a rocket, a checkmark, a sparkle,
  a lightning bolt. Emoji standing in for the visual hierarchy the layout failed to build.
  A rocket next to "Fast deployment" adds zero information and signals generation loudly.
- **Symmetry as a default, not a decision.** Everything centered, evenly spaced, perfectly
  balanced, because symmetry is the safe mean. Intentional design uses asymmetry and
  deliberate tension; slop never risks it.

### Content tells

- **"Lorem"-flavored filler that stayed.** Placeholder copy that reads like filler even
  after the model replaced the Latin: "Streamline your workflow with our powerful
  platform." Generic nouns, generic verbs, zero specifics, present because the model had no
  real product facts and generated plausible-sounding nothing.
- **Default shadcn with no customization.** The shadcn/ui component set dropped in at stock
  defaults — stock colors, stock spacing, stock radius, stock typography. shadcn is a
  starting point built to be themed; shipping it unthemed is shipping the demo. The tell is
  that the result looks identical to every other unthemed shadcn site.
- **Stock-everything imagery.** Abstract 3D blobs, gradient mesh backgrounds, the same
  isometric illustration style, faceless diverse-team stock photos. Imagery chosen to fill
  a slot, not to mean something.

## Taste-killing anti-patterns

These overlap the slop tells and read instantly as amateur. Treat the appearance of one as
a finding.

- **Gradient soup.** Multi-stop gradients on backgrounds, buttons, text, and borders at
  once. One restrained gradient can work; gradients everywhere read as a 2014 landing-page
  template.
- **Emoji section headers.** A rocket before "Features," a fire before "Pricing."
  Emoji-as-iconography signals a slide deck or a README, never a crafted product surface.
- **Drop-shadow on everything.** A shadow under every card, button, input, and div. Shadow
  encodes elevation; when nothing is flat, nothing reads as raised, and the screen turns
  muddy.
- **Five competing fonts.** A heading face, a body face, a "fun" accent face, plus two more
  that crept in. Two families is the ceiling for almost every product; one family across
  weights is often stronger.
- **Generic SaaS template.** The centered hero, the three-column feature grid with circle
  icons, the pastel gradient blob, the rounded-card testimonial row. The silhouette alone
  marks the page as undifferentiated.
- **Default component-library look.** Shipping the demo theme of a UI kit untouched — stock
  colors, stock radii, stock shadows. A component library is a starting point, and leaving
  it unmodified is the most common way a build reads as generic.

## Prose tells of AI writing

The same regression-to-mean dynamic, expressed in words. The copy on a page is as much a
slop surface as the layout.

- **Hedging that drains every claim.** "This can help to potentially improve," "in many
  cases this may," "arguably one of the most." The model softens to stay safe in the
  distribution, and the softening tells the reader no human stood behind the sentence.
  Commit to the claim or cut it.
- **"In today's fast-paced world" and its family.** The throat-clearing opener that says
  nothing: "In today's digital landscape," "In an increasingly connected world," "Now more
  than ever." Pure windup. Start on the actual subject.
- **Listicle padding.** Every idea inflated into a numbered list of parallel-but-empty
  items, each a bolded phrase followed by a sentence restating the phrase. Structure
  performing thoroughness while the content stays thin.
- **Em-dash overuse.** The em dash deployed three times a paragraph as the all-purpose
  connective — for asides, for emphasis, for lists, for pauses — until the rhythm flattens
  into a single tic. One em dash lands; four in a paragraph is a fingerprint.
- **"It's not just X, it's Y."** The signature rhetorical frame of generated copy: "It's
  not just a tool, it's a platform." The construction manufactures false depth by negating
  a strawman. A reader trained on slop spots it across the room.
- **Rule-of-three everything.** "Fast, simple, and powerful." "Build, ship, and scale."
  Triads everywhere, because the triad is the corpus's favorite cadence, applied past the
  point of meaning.
- **The hollow conclusion.** "In conclusion, X is a powerful solution that can help you
  achieve your goals." A summary that restates without adding.

## The four de-slop moves — adding specificity and intention

Slop is the average; the four moves below force a non-average choice. Each move adds an
input the median lacked. Fix the structure (the bones) before the surface (the words).

1. **Inject concrete details.** Replace every generic noun with a specific one. "Powerful
   platform" becomes "a Postgres-backed job queue that retries on the worker, not the
   client." "Trusted by teams" becomes "trusted by 40 engineering teams at Series-B
   startups." Specificity is the single strongest anti-slop signal, because the training
   mean is generic by definition and a concrete fact cannot come from the mean.
2. **Take a point of view.** State an opinion the average would hedge. "We think dashboards
   are the wrong default — most teams want a feed, so that is what we ship." A stated
   position is, by construction, off-center, and a reader feels the human behind it.
3. **Impose a real constraint.** A constraint forces a decision the unconstrained mean
   never makes. Pick one: a brand color drawn from the product's meaning rather than the
   Tailwind default; a single typeface with a real reason; a hard rule that the hero
   carries no gradient and no stock illustration. The constraint, not the taste, produces
   the distinctive result.
4. **Name a reference to diverge from.** Pick a specific artifact the work should *not*
   resemble — "not another centered-hero SaaS page, more like a Bloomberg terminal" — and
   let the contrast steer the choices. Divergence from a named target beats convergence
   toward an unnamed average.

The through-line: every move replaces a missing input. The model regressed to the mean
because the brief gave it nothing to regress *away from*. Supply the detail, the opinion,
the constraint, and the anti-reference, and the average has nowhere to settle.

## Failure modes

Predictable ways a taste or de-slop pass goes wrong, each paired with its corrective.

- **Decoration mistaken for taste.** Adding shadows, gradients, and animation to "elevate"
  a screen, which buries hierarchy under noise. Corrective: subtract first; reach for
  restraint before ornament.
- **Inconsistency from local edits.** Tuning one component in isolation until it is
  beautiful and unlike everything around it. Corrective: change values at the system level
  — tokens and scales — never one component at a time.
- **Cramming over spacing.** Treating whitespace as wasted and filling it, which produces
  the cheap dense look. Corrective: increase padding and gaps until the layout feels
  slightly too airy, then stop.
- **Hierarchy flattening.** Sizing everything close to 16px so nothing leads, which leaves
  the eye no entry point. Corrective: widen the gap between the largest and smallest type
  until the order is obvious at a glance.
- **Accent inflation.** Promoting a second and third color to "highlight more things,"
  which dilutes the one signal a user follows. Corrective: hold the line at a single
  accent; express everything else through the neutral ramp.
- **Quirk for its own sake.** Swapping the generic-average for the random-weird — a
  hard-to-read font, motion that fights the user — and calling it taste. Distinctive is not
  the same as strange. The test is intention: a distinctive choice serves the content and
  the user; a quirky one serves the designer's wish to look different. Anti-slop without a
  reason is just a different slop.
- **Specificity theater.** Adding fake specifics — invented metrics, fabricated customer
  names, a precise-sounding number with no source. A confident false detail is a
  credibility wound, where a vague true one is merely dull. Every concrete claim must be
  real.
- **Over-correction into noise.** Stripping every default until nothing is familiar — no
  recognizable button, no standard form, no convention the user already knows. Convention
  is not slop; convention is the shared vocabulary that lets a user act without learning.
  Break the conventions that flatten the work, and keep the ones that carry meaning.
- **De-slopping the words while the bones stay generic.** Rewriting the copy to read sharp
  on top of the same centered-hero, three-card, purple-gradient skeleton. The structure is
  the loudest tell, so a prose pass over a median layout leaves the slop fully visible. Fix
  the bones first.

## Red flags checklist

A single yes is a finding. Stop and reconsider the whole artifact.

- [ ] The hero is centered with a headline, a one-line subhead, and two stacked buttons
  over a gradient — the median template.
- [ ] A purple-to-indigo gradient appears on the hero, the buttons, or the icon
  backgrounds.
- [ ] Glassmorphism or backdrop-blur is decoration, not a real depth solution.
- [ ] Features arrive as a three-card row, three because three is balanced rather than
  because three facts matter.
- [ ] Emoji prefix the bullets or the section headers, standing in for visual hierarchy.
- [ ] The same border radius and the same soft shadow sit on every element.
- [ ] shadcn or another component kit ships at stock defaults, identical to every unthemed
  site.
- [ ] Imagery is an abstract 3D blob, a gradient mesh, or a faceless stock team photo
  chosen to fill a slot.
- [ ] More than two non-neutral colors appear above the fold with no single dominant
  accent.
- [ ] The type ramp contains values belonging to no ratio (13, 15, 17, 19, 22 scattered).
- [ ] Two of the same component differ in height, padding, or radius for no functional
  reason.
- [ ] The copy hedges its claims, opens on "in today's…", or runs the "it's not just X,
  it's Y" frame.
- [ ] Em dashes appear three or more times in one paragraph.
- [ ] No concrete number, product fact, or named specific appears anywhere in the copy.
- [ ] No point of view is stated; nothing in the artifact could surprise anyone.
- [ ] A reader says the screen "looks fine" but cannot say what it is — the signature of
  generic.

## Worked example A — raising a pricing card from generic to intentional

**Before (generic):**

```html
<div style="border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            padding: 16px; background: linear-gradient(#fff, #f3f3f3);
            text-align: center; font-family: Arial;">
  <h3 style="color: #6c5ce7; font-size: 22px;">🚀 Pro Plan</h3>
  <p style="font-size: 15px; color: #555;">For growing teams</p>
  <div style="font-size: 30px; color: #00b894;">$49<span style="font-size:13px;">/mo</span></div>
  <button style="background: linear-gradient(#6c5ce7, #a29bfe);
                 box-shadow: 0 2px 8px rgba(0,0,0,0.3); border-radius: 20px;
                 padding: 10px; color: white;">Get Started 🎉</button>
</div>
```

The tells, named: two accent colors (purple heading, green price) so the eye has no single
anchor; emoji in the heading and the button; gradients on the card, the price area, and
the button; a heavy shadow on both card and button; arbitrary type sizes (22 / 15 / 30 /
13) belonging to no scale; centered everything, the SaaS-template default; Arial, the
unconsidered system fallback.

**After (intentional):**

```html
<div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 32px;
            background: #fff; font-family: Inter, system-ui, sans-serif;">
  <h3 style="font-size: 14px; font-weight: 600; color: #6b7280;
             text-transform: uppercase; letter-spacing: 0.05em; margin: 0;">Pro</h3>
  <div style="font-size: 48px; font-weight: 700; color: #111827; margin: 16px 0 4px;">
    $49<span style="font-size: 16px; font-weight: 400; color: #6b7280;">/mo</span>
  </div>
  <p style="font-size: 16px; color: #6b7280; margin: 0 0 24px;">For growing teams</p>
  <button style="background: #4f46e5; color: #fff; border: none; border-radius: 6px;
                 padding: 12px 20px; font-size: 14px; font-weight: 600; width: 100%;">
    Get started
  </button>
</div>
```

The decisions, named: one accent (indigo) on the single action, everything else on a gray
neutral ramp; a real scale (14 / 16 / 48) that builds hierarchy, with the price as the
largest element because the price is what a buyer scans for; whitespace opened to 32px
padding and deliberate 16/24px rhythm; zero gradients and zero shadow — a single hairline
border carries the card edge; one consistent radius; left-aligned for a calmer, more
premium read; one intentional type family. The after passes every marker, and every value
traces to a reason.

The lesson generalizes: the upgrade was almost entirely **subtraction** — fewer colors,
fewer effects, fewer fonts, fewer type sizes — plus **more space** and **one clear
hierarchy**. Subtraction plus space plus hierarchy is the shape of nearly every taste
raise.

## Worked example B — de-slopping a landing section (bones and words)

A generated hero section, before:

```html
<section class="hero">
  <h1 class="gradient-text">Streamline Your Workflow</h1>
  <p>In today's fast-paced world, our powerful platform helps teams
     work smarter — not harder. It's not just a tool, it's a complete
     solution. 🚀</p>
  <div class="cta">
    <button class="btn-primary">Get Started</button>
    <button class="btn-outline">Learn More</button>
  </div>
</section>
<div class="features">
  <div class="card">⚡ Lightning Fast</div>
  <div class="card">🔒 Secure</div>
  <div class="card">📊 Powerful Analytics</div>
</div>
```

Every tell is present: the purple gradient headline, the "in today's fast-paced world"
opener, "powerful platform," the "smarter not harder" cliché, the "it's not just X, it's
Y" frame, the rocket emoji, the centered two-button hero, and the three emoji-prefixed
feature cards. The output is the training mean rendered to HTML.

Walking the detection passes and applying the four moves:

- **Visual pass:** the gradient headline and centered two-button composition are the median
  template — drop the gradient, kill the second CTA, break the symmetry. The three emoji
  cards are slop structure — replace with the two capabilities that actually differentiate,
  sized unequally.
- **Prose pass:** cut the throat-clearing opener, "powerful platform," and the "it's not
  just X" frame. Inject concrete details (move 1) and state a point of view (move 2).
- **Constraint (move 3):** a hard rule — the hero carries no gradient and no emoji, and the
  headline names what the product *does* in plain words.
- **Anti-reference (move 4):** not another centered SaaS hero; closer to a developer-tool
  docs page that respects the reader's time.

After:

```html
<section class="hero">
  <h1>Retry failed jobs on the worker, not the client.</h1>
  <p>A Postgres-backed queue for background work. We think dashboards
     are the wrong default for ops, so Reqdrain ships a live feed of
     every job, its retries, and the exact error that killed it.</p>
  <a class="btn-primary" href="/start">Read the 5-minute setup</a>
</section>
<div class="proof">
  <p>In production at 40 engineering teams. p99 enqueue latency 3ms.</p>
</div>
```

The headline now states a real capability instead of a gradient cliché. The copy carries a
concrete fact (Postgres-backed, a live feed, the error detail), a stated opinion
(dashboards are the wrong default), a real product name, and two verifiable numbers. The
single CTA names the actual next step. Nothing in the result could have come from the
training mean, because each line carries an input the mean lacked. The slop is gone — not
sanded smooth, but replaced with intention.

## Taste checklist

The work is done when each line is checkably true:

- [ ] One accent color; everything else on a neutral ramp.
- [ ] One type scale of four-to-six sizes from a ratio.
- [ ] Spacing on a single scale; two font families at most.
- [ ] Zero emoji headers or emoji bullets; shadows only where elevation is real.
- [ ] Every edge aligned to a grid; one consistent radius set.
- [ ] No purple-default gradient, no unthemed component-kit look, no centered-hero
  template silhouette.
- [ ] Copy carries at least one concrete fact and one stated point of view, no hedging or
  "it's not just X" frames.
- [ ] Every concrete claim is real (no fabricated metrics or names).
- [ ] No element reads as a default nobody chose.
