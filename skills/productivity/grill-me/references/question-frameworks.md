# Question frameworks

A grill extracts the knowledge only the user holds. The docs and code already answer
what they answer; the grill spends every question on a **gap** — a point the existing
material leaves open. Ask **one at a time**, ground each question in what exists, record
each answer, and stop at **saturation**, when new answers stop changing the document.

The question types below are ordered by leverage. The early types convert a vague
request into a shape; the later types harden that shape against failure.

## The question taxonomy

### 1. Clarifying — what does the request actually mean?

The first gap is usually the request itself. A vague request hides several readings.

- What does this word mean here — "fast", "secure", "users", "done"?
- Which of these two readings did you intend?
- What is in scope, and what is explicitly out?

Use when: the request names an outcome without naming the thing that produces it.

### 2. Constraint — what fences the solution in?

A constraint the user holds in their head but never wrote down is the most common cause
of a wrong build.

- What must this never do? What is the hard limit — latency, budget, size, headcount?
- What existing system must it not break?
- What is fixed by a decision already made elsewhere?

Use when: the docs describe behavior but not its boundaries.

### 3. Assumption-surfacing — what is being taken for granted?

An unstated assumption is a gap wearing a disguise. Name it, then test whether it holds.

- This seems to assume X — is that true, and always?
- What are you treating as given that a new reader would not know?
- What happens the day that assumption stops holding?

Use when: a step in the request rests on an unspoken precondition.

### 4. Edge-case — where does the happy path end?

The happy path is the easy half. The knowledge worth extracting lives at the edges.

- What happens on empty, zero, one, or the maximum?
- What happens on the malformed input, the duplicate, the concurrent request?
- Who hits the rare case, and how often?

Use when: the request describes the typical flow and stops there.

### 5. Trade-off — what is being traded for what?

A silent trade-off becomes a surprise in production. Force it into the open.

- This buys speed at the cost of memory — is that the trade you want?
- What would you give up to get this, and what would you refuse to give up?
- Of correctness, cost, and time, which yields first under pressure?

Use when: two desirable properties pull against each other and only one can win.

### 6. Prioritization — what matters most when not everything fits?

Most requests cannot have everything. The ranking is knowledge only the user holds.

- If only one of these ships this quarter, which one?
- What is the floor — the version below which this is not worth shipping?
- Rank these five by the pain of losing each.

Use when: the request lists several wants without an order.

### 7. "What would make this fail?" — the pre-mortem question

The sharpest question imagines the feature already broken and asks why.

- Picture this live and failing badly — what went wrong?
- What is the input, the user, or the load that breaks it?
- What would make you regret building it this way?

Use when: the shape is settled and the remaining gap is risk.

## Techniques for surfacing tacit knowledge

Tacit knowledge resists direct questions. These techniques pull it into words.

- **Concrete examples over abstractions.** Trade a principle for an instance: not "how
  should errors behave" but "walk me through what the user sees when the upload fails
  mid-transfer." A concrete case forces the buried detail to the surface.
- **Ask for a number.** A qualitative answer hides a decision. Convert "it should be
  fast" into "fast means a response under how many milliseconds?" The number is the
  specification; the adjective is not.
- **The five-whys.** Chase a requirement down to its root by asking "why" up to five
  times. The surface request ("add a retry button") often sits atop a deeper need ("the
  job silently dies and nobody notices") that reshapes the spec.
- **Contrast cases.** Probe a boundary by pairing a case with its near-opposite: "this
  user gets access — name a user who must not." The pair locates the line the single
  case left fuzzy.
- **Play back the answer.** Restate what was said in your own words and ask whether the
  restatement is right. A wrong playback exposes a gap the original answer hid.

## Grounding a question in what exists

A grounded question proves it read the material before it asked. Grounding earns the
user's answer and keeps the grill off ground the docs already cover.

- Quote the line that prompts the question: "the spec says retries are capped at three —
  what happens on the fourth failure?"
- Confirm the read before extending it: "the code defaults the timeout to 30 seconds —
  is that deliberate, or inherited?"
- Re-asking an answered point burns trust. Before posing a question, check it against the
  docs; a question the material already settles is **muda** — cut it.

The discipline: read first, locate the gap, and ask only into the gap. A question whose
answer is already on the page signals the grill skipped the reading.

## When to stop — saturation

A grill ends at **saturation**, not at exhaustion of the asker. Saturation is the point
where new answers stop changing the document.

Read these signals together:

- Recent answers confirm what the document already says rather than adding to it.
- Every gap named at the start has a recorded answer.
- A new reader could build from the document without asking the user a further question.

Two failure modes bracket saturation. Stopping early leaves a gap that becomes a wrong
assumption downstream. Grinding past saturation extracts restatements of settled points
and wastes the user's attention. The document changing — or no longer changing — is the
gauge.

## Anti-patterns

- **The leading question.** "You'd want it cached, right?" plants the answer and extracts
  the asker's belief, not the user's knowledge. Ask open: "how should repeat reads
  behave?"
- **The batch.** Five questions in one message split the user's attention and yield five
  shallow answers. One question, then the answer, then the next — that order keeps each
  answer sharp.
- **Accepting the vague.** "It should be intuitive" is an opinion until a number or a
  concrete case pins it to a decision. An abstract answer left abstract is a gap that
  only looks closed.
- **Interrogating without recording.** A great answer that lands only in the chat is lost
  the moment the session ends. The record is the deliverable; an unrecorded answer is
  wasted breath.
- **Re-asking the docs.** A question the existing material already answers signals the
  grill skipped its reading and spends the user's patience on nothing.

## Worked example

A vague feature request becomes a spec through a short, grounded grill. Each question
targets one gap; each answer is recorded before the next question.

> **Request:** "Let users export their data."

**Read first.** The codebase has a `User` model and a `Report` model; no export path
exists. Gaps: what data, which format, how delivered, what scale, who is allowed.

**Q1 (clarifying).** "The request says 'their data' — does that mean the user's profile,
their reports, or everything tied to their account?"
→ *"Their reports only."* Recorded: scope = reports.

**Q2 (clarifying, ask for a number).** "Which format, and roughly how many reports does a
heavy user hold?"
→ *"CSV, and a heavy user has about 50,000 reports."* Recorded: format = CSV; scale ≈
50k rows.

**Q3 (edge-case).** "At 50,000 rows the export will not be instant — should it download
synchronously, or generate in the background and notify when ready?"
→ *"Background, then email a link."* Recorded: async generation, email delivery.

**Q4 (constraint).** "How long should that download link stay valid?"
→ *"24 hours, then it expires."* Recorded: link TTL = 24h.

**Q5 (assumption-surfacing).** "This assumes a user only exports their own reports —
should an admin be able to export on another user's behalf?"
→ *"No. Self-service only."* Recorded: authorization = owner only.

**Q6 (what would make this fail).** "Picture this live and failing — what is the worst
case?"
→ *"Two exports at once from one user hammering the database."* Recorded: rate-limit to
one concurrent export per user.

**Saturation.** The next question would re-confirm scope or format — answers already in
the document. The spec now states what data, the format, the delivery, the link
lifetime, the authorization rule, and the rate limit. No gap from the read remains. The
grill stops.

The vague request became a buildable spec in six questions because each one targeted a
named gap, stayed grounded in the model and the prior answers, and was recorded the
moment it landed.
