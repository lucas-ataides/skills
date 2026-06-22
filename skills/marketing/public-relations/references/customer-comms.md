# Customer communications

A customer message is a transaction in trust. Good news spends almost nothing; hard
news — an outage, a price hike, a deprecation, a breach — draws down the balance, and
the draft decides how much. The reader does not want prose; the reader wants to know
what happened, whether it touches them, what is being done, and what to do next. Every
rule below serves that reader.

This reference covers the message types, tone calibration, the structure for hard news,
incident and crisis basics, saying sorry well, the legalese and over-promising traps,
the failure modes, the red flags, and a worked outage-apology example.

**Drafting only.** This skill produces the text. Sending — email, a public post, a
status-page update, an in-app banner — is an external mutation that changes what
customers see and cannot be taken back, so it waits on explicit user approval. The draft
goes back to the user; the user sends it.

## The message types and the job of each

| Type | The job |
|------|---------|
| Announcement | Tell customers about something new (a launch, a feature, a milestone) and prompt one action — try it, read more, upgrade. |
| Incident / outage notice | Tell affected customers, while the problem is live, what is broken, who it touches, and the current status — fast, before they ask. |
| Apology | After an incident resolves, own the failure, explain the cause plainly, and state what prevents a repeat. |
| Change / deprecation notice | Warn customers ahead of a change to price, terms, or a feature being sunset, and give them the date and the migration path. |
| Win-back | Re-engage a lapsed or churned customer with a specific reason to return — a fix, a new capability, an offer. |
| Sensitive reply | Respond one-to-one to a complaint, an escalation, a refund demand, or a public callout, defusing rather than inflaming. |

Name the type before drafting. A message that blends two types — an apology that
smuggles in a feature pitch, a deprecation notice dressed as an announcement — confuses
the reader and reads as evasive. One message, one job.

## Tone calibration

Tone is set by the news the reader is about to receive, not by the brand's default
voice. A mismatch is itself a failure: an upbeat tone on an outage reads as tone-deaf, a
funereal tone on a launch reads as odd. Three registers cover most situations.

- **Celebratory** — for launches, milestones, and wins. Warm, energetic, confident.
  Earned only when the news is genuinely good for the reader, not merely good for the
  company.
- **Apologetic and plain** — for incidents, apologies, and breaches. Direct, calm,
  unhedged, short sentences. No exclamation marks, no marketing gloss, no upsell. The
  reader is annoyed or worried; respect that.
- **Neutral and factual** — for routine changes, deprecations, and most policy notices.
  Clear, matter-of-fact, complete. Neither cheerful nor grave — just the facts and the
  next step.

Calibration heuristic: ask what the reader feels at the moment of opening. The register
matches the reader's state, not the sender's mood.

## The structure for hard news

Hard news follows a fixed five-beat order. The order front-loads what the reader needs
and ends on what the reader does, so the most anxious reader gets the answer first.

1. **Acknowledge.** Name the situation in the first sentence. State the news, not a
   preamble about how much the company values the reader.
2. **Explain plainly.** Give the cause in plain language — no jargon, no diffusion of
   responsibility. One or two sentences a non-engineer understands.
3. **State the action or remedy.** Say what is being done or has been done, concretely:
   the fix shipped, the refund issued, the credit applied, the timeline to resolution.
4. **Reassure.** Say what protects the reader going forward — the prevention, the
   safeguard, the monitoring — without promising perfection.
5. **State the next step.** Tell the reader exactly what to do, or that nothing is
   required. End on the reader's action, with a real contact for follow-up.

Lead with the news. The single most common failure in hard-news writing is burying the
lede under throat-clearing; the fix is to state the news in the first two sentences and
move every courtesy below it.

## Incident and crisis communication basics

When something is broken and customers are affected, four principles govern.

- **Speed over polish.** A short, honest "we know, we're on it, here's what we know"
  posted early beats a perfect statement posted late. Update on a cadence; say when the
  next update lands.
- **Honesty over reassurance.** State what is known and, plainly, what is not yet known.
  A false "everything is fine" that unravels in an hour costs more trust than the
  incident did.
- **No blame-shifting.** Do not blame a vendor, a cloud provider, an unnamed "third
  party", or the customer. The reader bought from this company; this company owns the
  message. Naming a root cause is fine; deflecting responsibility is not.
- **The four-part spine: what / impact / fix / prevention.** What happened, who and what
  it affected, what is being done about it, and what stops a recurrence. A status update
  carries the first three live; the follow-up apology adds the fourth once it is known.

Match the channel to the blast radius. A status page or public post fits a broad outage;
a direct message fits a problem that hit specific accounts. Sending any of these is the
user's call, made after the draft is approved.

## Saying sorry well

A real apology repairs trust; a non-apology spends more of it. The difference is
whether the message owns the failure.

- **Own it in the first person.** "We broke X" or "We were down for two hours." Direct,
  active, specific. The subject is the company and the verb is what it did.
- **Banish the conditional non-apology.** "We apologize if anyone was affected" implies
  doubt that anyone was, and apologizes for the reader's feelings rather than the
  company's failure. People *were* affected — say so. Replace "we're sorry if" with
  "we're sorry that".
- **No deflection clauses.** Drop "mistakes were made" (the passive that hides the
  actor), "out of an abundance of caution" (the phrase that pre-empts blame), and any
  clause that routes the fault elsewhere.
- **Apologize once, then act.** One clear sorry, then pivot to the remedy and the
  prevention. Repeated apology reads as performance; the remedy is what the reader
  actually wants.
- **Proportion the apology to the harm.** A minor blip needs a sentence; a data breach
  or a multi-hour outage needs the full structure, a named remedy, and a concrete
  prevention.

## Avoiding legalese and over-promising

Two traps turn a sincere message hollow.

**Legalese and jargon** put distance between the company and the reader exactly when
closeness is needed. Phrases such as "we regret any inconvenience this may have caused",
"your business is important to us", and "we are committed to excellence" are filler the
reader has learned to skip. Cut them. Write the way a trusted colleague would explain
the situation across a table — plain words, short sentences, no boilerplate.

**Over-promising** mortgages future trust to buy present relief. The pledge "this will
never happen again" is a promise no team can keep, and the next incident makes a liar of
it. Promise only what the company controls: "we've added monitoring that pages us within
a minute" is a real safeguard, and "we guarantee 100% uptime forever" is a hostage to
fortune. Under-promise on the guarantee, over-deliver on the specifics of what was done.

## Failure modes

- **Defensive tone.** The message argues with the reader, justifies the company, or
  implies the reader is overreacting. Defensiveness confirms the reader's worst read.
- **Vague non-apology.** "We're sorry if you were inconvenienced" — the conditional,
  actorless apology that owns nothing. The reader notices, every time.
- **Over-promising.** A guarantee the team cannot keep ("never again", "100% uptime"),
  which the next failure converts into a broken promise.
- **Buried lede.** The news sits in paragraph three under a preamble about how valued the
  customer is. The anxious reader gives up before reaching it.
- **Corporate jargon.** Boilerplate and abstraction ("leverage", "synergies",
  "committed to excellence") that signal a press release, not a person.

## Red flags

- The first sentence does not state the news.
- The word "if" appears in the apology ("sorry if", "if you were affected").
- A vendor, provider, or the customer is named as the party at fault.
- A sentence promises something outside the team's control.
- The reader cannot tell, after one read, what to do next.
- The message contains an exclamation mark on news that is not good.
- A phrase from the boilerplate graveyard survives: "regret any inconvenience",
  "your business is important to us", "out of an abundance of caution".
- An apology smuggles in a product pitch or an upsell.

## Worked example: an outage apology

**Situation.** A SaaS product was unreachable for 3 hours and 12 minutes after a botched
database migration. The incident is resolved, and the message below is the follow-up
apology, written for email to the affected accounts.

### Before (fails the red flags)

> Subject: A note about recent service performance
>
> Dear Valued Customer,
>
> Your business is important to us. We wanted to reach out regarding some intermittent
> performance degradation that some users may have experienced earlier today. Due to
> circumstances involving a third-party infrastructure component, certain functionality
> may have been temporarily unavailable for a subset of users.
>
> We sincerely apologize for the inconvenience this may have caused. Please rest assured
> that we are committed to excellence and that a disruption like this is now behind us.
> While you're here, have you tried our new Analytics dashboard?
>
> The Team

Why it fails: the lede is buried under a courtesy opener; "some users may have
experienced" and "a subset of users" minimize a full outage; "a third-party
infrastructure component" shifts blame; "apologize for the inconvenience this may have
caused" is the conditional, actorless non-apology; the claim that the disruption is
"behind us" over-promises; the Analytics pitch is an upsell inside an apology.

### After (passes the structure)

> Subject: We were down for 3 hours today — what happened and what we did
>
> Hi [name],
>
> Our service was unavailable from 09:14 to 12:26 ET today. If you tried to sign in or
> use the API during that window, it failed. We're sorry — this was our fault, and we
> know it disrupted your day.
>
> The cause: a database migration we ran this morning locked a core table and took the
> application offline. We rolled the migration back and restored full service at 12:26.
>
> What we've changed: migrations like this one now run against a staging copy first and
> require a second engineer to sign off, and we've added an alert that pages us within a
> minute of an availability drop — far faster than today.
>
> No action is needed on your side; your data was not affected. If anything still looks
> wrong, reply to this email and it reaches our on-call team directly. We'll post the
> full incident report at [status link] by Friday.
>
> — [Name], [role]

Why it works: the subject and first two sentences state the news; the cause is plain and
owned ("our fault"); the remedy is concrete (rollback, restore time); the prevention
names real safeguards without promising perfection; the close tells the reader exactly
what to do and gives a real contact.

**Sending is the user's call.** This draft is finished text. Posting it to email, the
status page, or anywhere customers see it waits on the user's explicit go-ahead.
