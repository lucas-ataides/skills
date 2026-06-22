# The anatomy of a great issue

An issue is a contract between the person who wants the work and the person who does
it. A great issue lets that second person — possibly future-you, with no memory of the
conversation — pick it up cold, know when it is done, and ship it without a meeting. The
sections below are the parts that make that possible, the heuristic for cutting work too
big to finish, the taxonomy that keeps a backlog navigable, and a worked conversion.

## The parts of a well-formed issue

### Title — the outcome, not the activity

A title names the change in the world once the issue closes, not the task someone
performs. "Users can reset a forgotten password by email" beats "Add password reset":
the first asserts a verifiable end state, the second describes motion. A reader scanning
fifty titles should grasp each outcome without opening it.

- State the result, phrased so closing the issue makes the title true.
- Keep it under roughly ten words; push detail into the body.
- Avoid solution words in the title unless the solution *is* the requirement.

### Context — the why

Context is the paragraph that survives the conversation evaporating. Record the problem,
who feels it, and why now — the "while I was here" reasoning that no acceptance criterion
captures. A reader picking the issue up in three months has only this paragraph and the
criteria; the Slack thread is gone.

- Name the user or system that has the problem and the pain they hit today.
- Link the source: the discussion, the PRD, the incident, the metric that moved.
- State the cost of *not* doing it, so a triager can weigh it against everything else.

### Acceptance criteria — the definition of done

Acceptance criteria are the testable conditions that, all met, mean the issue is
finished. Without them, "done" is an opinion. Write them as observable checks — a
Given/When/Then line or a checklist a reviewer can tick — not as a restatement of the
title.

- Phrase each as a condition a reviewer can verify by observation, not by trust.
- Cover the failure paths, not only the happy path: empty input, the unauthorized
  caller, the downstream timeout.
- Aim for three to seven criteria. Fewer than two usually means the issue is underspecified;
  many more usually means it is two issues.

### Scope and non-goals

Scope draws the line around the work; non-goals name the tempting adjacent work this
issue will *not* do. An explicit non-goal stops scope creep before review and tells the
next person where the *next* issue begins.

- List what is in scope as concrete deliverables.
- List the plausible-but-excluded work as named non-goals, so nobody re-litigates it in review.

### Dependencies

Dependencies are the issues, decisions, or external facts that must land first. A reader
who knows the blocker upfront does not start work that cannot finish.

- Name each blocking issue by its link, and say what it must deliver before this can start.
- Flag external blockers (a vendor key, a design sign-off) distinctly from internal ones.

### Size estimate

A size estimate sets the reader's expectation and flags the work that needs cutting. Use
a coarse scale — XS / S / M / L, or points — never false-precision hours. A draft that
lands at L or above is the signal to split (see below).

- Estimate the whole issue as drafted, including tests and review.
- Treat L-or-larger as a flag to split, not a badge to keep.

### Labels

Labels make a backlog queryable: type, priority, and area at a minimum. The full
taxonomy is below. A draft without a type and a priority cannot be triaged.

## Splitting a large item into independently-shippable issues

The dominant failure of issue-writing is the item too big to finish. The fix is the
**vertical slice**: a cut through every layer that delivers a smaller but *complete* and
*shippable* increment of user value. The opposite — the horizontal slice ("all the
database work", then "all the API work", then "all the UI") — produces issues that each
depend on the next and ship value only when the last one lands.

Cut vertically against these seams, strongest first:

- **By user-visible outcome.** Carve off the thinnest path a user can actually exercise,
  end to end. "Reset password by email" ships before "reset password by SMS"; each is a
  whole journey, not a layer.
- **By workflow step.** Split a multi-step flow at its natural stages — request, then
  review, then approve — so each step ships and earns feedback alone.
- **By rule or variation.** Ship the default rule as one issue, each special case as its
  own. "Flat-rate shipping" ships before "weight-based" before "free over $50".
- **By data type or interface.** Support one input format, one entity, or one endpoint
  first; add the rest as follow-on issues.
- **By happy path, then edges.** Ship the success path as a slice, then the error and
  recovery paths as named follow-ons — each still a complete, testable increment.

The test for a good slice: it ships on its own, a user or caller can exercise it, and
deleting every other sibling slice still leaves something demonstrable. A "slice" that
ships no value until its siblings land is a horizontal layer wearing a disguise — recut it.

## Labeling and priority taxonomy

A consistent taxonomy is what makes a backlog answer questions ("what P0 bugs are open in
billing?"). Read the tracker's existing labels first and adopt them; the set below is the
default when none exists.

**Type** — what kind of work (exactly one per issue):

- `feature` — new user-facing capability.
- `bug` — behavior that violates an existing, intended contract.
- `chore` — maintenance with no user-visible change (deps, config, cleanup).
- `refactor` — internal restructuring, behavior held constant.
- `docs` — documentation only.
- `spike` — time-boxed investigation whose deliverable is an answer, not shipped code.

**Priority** — urgency and importance (exactly one per issue):

- `P0` — drop everything; production is broken or a release is blocked.
- `P1` — this cycle; important and time-sensitive.
- `P2` — soon; valuable but not urgent.
- `P3` — backlog; do it when it surfaces.

**Area** — the part of the system (one or more), such as `area/auth`, `area/billing`, or
`area/api`, drawn from the codebase's own module names.

**Status** — usually owned by the tracker's board columns (Backlog → In Progress →
Done), not by hand-applied labels. Let the board own state where the tracker provides one.

## Linking related issues

Links turn a flat list into a navigable graph. Use the tracker's native relations rather
than prose mentions, so the graph stays queryable.

- **Blocks / blocked-by** — a hard ordering: the blocker must close first.
- **Parent / child (epic ↔ task)** — group the slices of one split under a parent epic, so
  progress rolls up.
- **Related** — relevant context with no ordering constraint.
- **Duplicate** — close the later issue, point it at the canonical one, move any unique
  detail across before closing.

On GitHub, `Closes #123` in a PR body auto-closes on merge; reserve it for the PR that
actually finishes the issue. On Linear, set the relation in the issue's relations panel.

## Failure modes

The failure modes below are the recurring ways an issue fails its reader. Each maps to a part above.

- **Vague title.** "Fix the dashboard" names no outcome. The doer cannot tell when it is
  done, and a scanner cannot tell what it is. → Rewrite as a verifiable end state.
- **No acceptance criteria.** Without testable conditions, "done" is whatever the author
  later decides, and review has no spec to check against. → Add observable checks covering
  the failure paths.
- **Issue too big to finish.** An L-or-larger item stalls, blocks reviewers with a giant
  diff, and hides its true cost. → Split into vertical slices.
- **Missing context.** An issue stripped of its why forces the doer to reconstruct the
  conversation, and a triager cannot rank it. → Add the problem, the source link, and the
  cost of inaction.
- **Smuggled scope.** Two outcomes in one issue means neither has clean criteria and the
  diff is unreviewable. → Split by outcome; name the excluded work as a non-goal.
- **Horizontal slicing.** Issues cut by layer each ship zero value until the last one
  lands, and a slip anywhere blocks the whole feature. → Recut vertically.

## Red flags

Signals, while drafting, that an issue is not yet shippable:

- The title contains "and", "also", or a comma joining two outcomes.
- No link points back to a source discussion, spec, or incident.
- The acceptance criteria restate the title instead of adding testable conditions.
- The estimate is L or larger, or the author cannot estimate it at all.
- The happy path is the only path described.
- A solution is specified where a requirement belongs ("add a Redis cache" with no stated problem).
- The issue depends on a blocker that is itself unwritten or unscoped.

## Worked example: a 3-sentence request into 2–3 issues

**The source request:**

> "We need user notifications. Users should get notified when someone comments on their
> post, and they should be able to choose email or in-app. Eventually we want a daily
> digest too."

Three sentences, but at least three distinct outcomes hide inside, at different priorities
and sizes. A single "build notifications" issue would be an un-finishable L+. Cut it into
vertical slices, ship the core path first, defer the rest.

---

**Issue 1 — Users get an in-app notification when their post is commented on**

- **Context.** Authors have no way to know when their post draws a comment, so
  conversations stall and engagement drops. In-app notification is the core of the request
  from the 2026-06-18 product discussion; in-app is the thinnest end-to-end path and
  unblocks every later channel.
- **Acceptance criteria.**
  - Given a published post, when another user comments, then the author sees an unread
    in-app notification within 5 seconds.
  - The notification links to the comment and shows the commenter and a timestamp.
  - Opening the notification marks it read; the unread badge count decrements.
  - A user receives no notification for their own comment on their own post.
- **Scope.** In-app channel only; the comment-created event; the notification list UI.
- **Non-goals.** Email delivery, digest, preferences (separate issues).
- **Dependencies.** None — this slice stands alone.
- **Size.** M. **Labels.** `feature`, `P1`, `area/notifications`.

**Issue 2 — Users can also receive comment notifications by email**

- **Context.** Some authors live in their inbox, not the app, and miss in-app
  notifications entirely. Email is the second channel from the same discussion; it reuses
  the event and preference plumbing from Issue 1.
- **Acceptance criteria.**
  - Given email is the chosen channel, when a comment fires the notification event, then
    the author receives an email within one minute.
  - The email links back to the comment and respects the user's unsubscribe choice.
  - A failed send is retried and logged, never silently dropped.
- **Scope.** Email channel for the comment event; a per-user channel preference
  (in-app / email / both).
- **Non-goals.** Digest batching; channels beyond comments.
- **Dependencies.** Blocked by Issue 1 (reuses its notification event).
- **Size.** M. **Labels.** `feature`, `P2`, `area/notifications`.

**Issue 3 (spike) — Decide the daily-digest batching and scheduling approach**

- **Context.** "Eventually a daily digest" is a real want but underspecified — batching
  window, timezone handling, and per-user send time are all open. A short investigation
  de-risks the build issue that follows.
- **Acceptance criteria.**
  - A one-page note recommends a batching/scheduling approach with its trade-offs.
  - The note estimates the build issue and lists its open questions.
- **Scope.** Investigation and a written recommendation only.
- **Non-goals.** Any production code.
- **Dependencies.** Related to Issues 1 and 2; not blocked by them.
- **Size.** S. **Labels.** `spike`, `P3`, `area/notifications`.

---

The three issues ship in priority order, each delivering complete value: in-app first
(P1), email next (P2), and the digest deferred behind a cheap spike (P3) rather than
guessed at. None is larger than M, each has testable criteria, and the dependency between
1 and 2 is explicit. Drafting stops here — the issues reach the tracker only after the
user approves them.
