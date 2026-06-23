# Information architecture and conversion

A marketing site is a machine that moves a stranger from "never heard of you" to "took the
action you wanted." Information architecture (IA) is the floor plan of that machine: which
pages exist, what each one is for, how a visitor travels between them, and how search
engines crawl the whole. A site can look polished and still leak every visitor, because
clarity, a single conversion path, and a crawlable structure are judgment calls no
template makes.

The work below is ordered the way leverage runs. A site can have flawless copy on every
page and still fail, because the wrong pages exist, in the wrong order, pointing nowhere.
Visual polish ([visual-rules.md](visual-rules.md)) and usability
([ux-and-states.md](ux-and-states.md)) operate on the screen; IA operates on the site.

## 1. Audience and the one goal

Name the buyer and the single action the site exists to win before drawing a single box. A
founder site usually serves two or three audiences (the evaluator, the end user, the
economic buyer) and one primary conversion (start a trial, book a demo, buy). Secondary
conversions (subscribe, read docs) feed the primary one; a site with three co-equal
"primary" goals has none.

Red flags: a site that cannot name its buyer in one sentence; a home page selling to
"everyone"; equal visual weight on "Start free trial" and "Read our blog."

## 2. The page taxonomy — one job per page

Every page on a marketing site holds exactly one job. A page with two jobs does both
badly, and a job with no page is a gap a visitor falls through. The standard taxonomy for
a founder selling a product:

| Page | Its single job |
|------|------|
| **Home** | Answer "what is this, who is it for, why care" in five seconds, then route to the next step. The home page is a router, not an encyclopedia. |
| **Product / Features** | Convert interest into belief — show what the product does and the outcome it produces, feature tied to benefit. |
| **Pricing** | Remove the cost objection — state plans, what each unlocks, and who each fits, with a CTA per plan. |
| **Use-cases / Solutions** | Let a visitor self-identify ("this is for a team like mine") by role, industry, or job-to-be-done. |
| **About** | Build trust — the mission, the team, and why this company gets to solve this problem. |
| **Blog** | Capture search demand and nurture — top-of-funnel content that earns the visit and links inward. |
| **Docs** | Prove the product is real and reduce post-signup risk — reference and guides for evaluators and users. |
| **Contact / Demo** | Capture high-intent leads — a form, a calendar, or a sales path for buyers ready to talk. |

A pricing page that also tries to re-explain every feature has lost its job. A home page
that buries the product behind a manifesto has lost its job. Name the one job, then cut
whatever does not serve it.

## 3. Navigation and the conversion path

Navigation is not a sitemap dump — global nav is a curated set of five to seven top-level
destinations that match how a buyer decides. The path runs in three stages, and each page
sits on exactly one:

- **Awareness** — the visitor has a problem, not yet your name. Entry points: blog posts,
  use-case pages, the home hero. The job here is relevance, not the sale.
- **Consideration** — the visitor is comparing. Product, features, pricing, docs, and proof
  carry this stage. The job is belief: this solves my problem better than the alternatives.
- **Decision** — the visitor is ready. Trial signup, demo booking, and contact carry it.
  The job is to remove the last friction, not to add a new pitch.

Primary nav surfaces the consideration pages; a single persistent primary CTA (one button,
one verb, repeated in the header and footer) carries the decision stage on every page.
Utility nav (login, docs, support) lives visually subordinate so it never competes with the
primary CTA.

Red flags: a primary CTA that changes label page to page; login styled louder than "Start
trial"; the only path to pricing buried in the footer.

## 4. Message hierarchy of a landing page

A landing page (home or a campaign page) earns the scroll in a fixed order. Lead with
clarity, back it with proof, then ask. Reversing this order asks for the sale before the
visitor knows what is sold.

1. **Above the fold — clarity.** A headline naming the outcome (not the feature), a
   one-line subhead naming who it is for, and the primary CTA. A visitor must pass the
   five-second test: state what this is and whether it is for them. No clarity here means
   nothing below matters.
2. **The problem and the promise.** Name the pain in the visitor's words, then the shift
   the product delivers. This earns the right to keep going.
3. **How it works.** Three to four steps or core capabilities, each a capability bound to
   the outcome it produces — never a feature listed for its own sake.
4. **Proof.** Logos, testimonials, metrics, case studies, security badges. Proof answers
   "can I trust this," and proof placed before clarity is noise.
5. **Objection handling.** A short FAQ or comparison that defuses the top two or three
   reasons a buyer hesitates.
6. **Closing CTA.** Restate the primary action with the stakes made plain. The same verb as
   the hero, so the visitor never relearns the ask.

The rule across the page: one primary action, repeated; secondary actions stay visually
quieter so the eye always knows the main path. (The repeated single CTA applies the same
one-primary-action discipline the UX reference uses at the screen level.)

## 5. URL and IA structure for SEO

URLs encode the IA, and search engines read that structure as a map of what the site is
about. Three mechanics carry most of the value:

- **Topic clusters.** Group content into a pillar page (broad topic, e.g.
  `/guides/email-deliverability`) with cluster posts linking up to it
  (`/blog/spf-dkim-setup`). The pillar earns authority; the clusters feed it and rank for
  the long tail.
- **Flat, readable URLs.** `/pricing`, `/use-cases/agencies`, `/blog/post-slug`. Words over
  IDs, hyphens over underscores, shallow over deep. A URL a human can read is a URL a
  crawler can map.
- **Internal linking.** Every new page links to and from at least one relevant existing
  page, so authority flows and the crawler reaches it. Contextual in-body links beat
  generic footer links, because anchor text in context tells the engine what the target is
  about.

One canonical URL per piece of content, a descriptive title and meta per page, and a
sitemap that lists every page worth indexing.

## 6. Failure modes

- **Navigation overload.** Twelve top-level links and four dropdowns. A visitor facing too
  many choices makes none — the cost of breadth is paralysis. Cut to five to seven.
- **No clear primary CTA.** Five buttons of equal weight, or a CTA that changes meaning per
  page. The eye finds no main path, so the click never comes.
- **Orphan pages.** A page with no inbound internal link. A crawler may never reach an
  orphan, and a visitor certainly will not — the page exists only in the sitemap.
- **Keyword-stuffing.** The same phrase forced in unnaturally to rank. Modern ranking
  penalizes the practice, and a human reader bounces from copy written for a crawler.
- **Feature-listing without benefit.** A wall of capabilities and no outcome. A visitor
  reads what it does and still cannot tell what changes for them.
- **Proof-free claims.** "The best platform" with nothing behind it. An unbacked
  superlative reads as noise and lowers trust in every other claim on the page. (An
  unbacked superlative is the IA-level cousin of specificity theater in
  [taste-and-anti-slop.md](taste-and-anti-slop.md).)

## Red flags

- The site cannot state its one conversion goal in a single sentence.
- A page on the site has two jobs, or a needed job (pricing, proof, contact) has no page.
- Global nav carries more than seven top-level items.
- The primary CTA label or destination changes from one page to the next.
- A page has zero inbound internal links (an orphan).
- A landing page leads with proof or features before stating what the product is.
- URLs carry IDs, query strings, or capital letters where readable slugs belong.
- Content repeats a target keyword unnaturally instead of covering the topic.

## Worked example — a SaaS site for "PostFlow" (email scheduling for agencies)

**Audience and goal.** Buyer: an agency owner managing client social accounts. Primary
conversion: start a 14-day trial. Secondary: book a demo (for larger agencies).

**Page taxonomy and IA tree.**

```
/                         Home — router; outcome headline + trial CTA
/product                  What PostFlow does; capability → outcome
/features/scheduling      Deep feature page (cluster under /product)
/features/analytics       Deep feature page (cluster under /product)
/pricing                  Three plans, CTA per plan
/use-cases/agencies       Self-identify: "built for agencies"
/use-cases/freelancers    Self-identify: solo operators
/about                    Mission + team + trust
/blog                     Top-of-funnel demand capture
/guides/social-scheduling Pillar page; blog posts link up to it
/docs                     Product reference; proves it is real
/demo                     High-intent: book a call
```

**Conversion path.** Awareness: a `/blog` post or `/guides` pillar pulls organic search →
internal links route to `/use-cases/agencies` (consideration) → `/product` and `/pricing`
build belief → a persistent "Start free trial" button carries the decision on every page;
`/demo` catches the buyers who want a human first.

**Home-page section order (top to bottom).**

1. **Hero** — "Schedule a month of client posts in an afternoon" (outcome), subhead "Social
   scheduling built for agencies juggling many brands," primary CTA "Start free trial."
2. **Problem / promise** — the pain of juggling ten client calendars, then the shift.
3. **How it works** — three steps: connect accounts, bulk-schedule, report — each tied to
   the time it saves.
4. **Proof** — agency logos, a testimonial with a hard metric ("cut scheduling time 60%"),
   a SOC 2 badge.
5. **Use-case strip** — two cards routing to `/use-cases/agencies` and `/freelancers`.
6. **Objection FAQ** — pricing transparency, migration effort, support.
7. **Closing CTA** — "Start your free trial" again, the same verb as the hero, with a "no
   card required" reassurance.

Every section serves the one goal; the trial CTA is the only primary action, repeated at
top and bottom, with the demo path kept visually quieter.

## IA checklist

- [ ] The site states one primary conversion in a single sentence; secondary goals rank
  beneath it.
- [ ] Every needed job owns exactly one page; no page carries two jobs.
- [ ] Global nav holds seven items or fewer; the primary CTA label and destination are
  identical across pages.
- [ ] Every page sits on exactly one stage of awareness → consideration → decision.
- [ ] Each landing page leads with clarity, then proof, then the closing ask; one primary
  action repeats top and bottom.
- [ ] URLs are flat, readable slugs; no page is an orphan; pillars carry cluster links.
- [ ] A continuous click path runs entry → consideration → decision with no dead end.
