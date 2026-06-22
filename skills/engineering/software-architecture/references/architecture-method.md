# Architecture method

A tech lead designs against **constraints and quality attributes first**, technology
second. The structure is whatever satisfies the dominant attributes at the stated
scale for the lowest complexity and cost. Every choice trades one attribute for
another; the job is to make the trade deliberate and to record it.

This reference expands the seven-step procedure in SKILL.md, supplies the menus the
steps point at, and closes with a worked example and an ADR.

## The method

The procedure is a funnel from problem to recorded decision:

1. **Clarify requirements and constraints.** Functional scope answers "what must it
   do"; the constraints answer "inside what box" — scale numbers, budget, team size,
   deadline, compliance, and the stack already in production. A design without
   numbers is fiction, so an estimate of load and storage belongs on the page before
   any box is drawn.

2. **Identify the dominant quality attributes.** Two or three attributes decide the
   shape; the rest are satisfied, not optimized. A bank ranks consistency and
   security above latency; a social feed ranks the reverse. The ranking, with a
   target per attribute, is the spine the rest of the design hangs from.

3. **Sketch components and responsibilities.** Each component owns one
   responsibility and a slice of the data. The test of a good boundary: the things
   that change together live together, and the things that vary independently sit
   apart.

4. **Model the data.** Entities, keys, relationships, and access patterns come before
   the storage technology. The access patterns — the reads and writes the system
   actually issues — select the datastore, not the other way around.

5. **Define the interfaces and contracts.** Each boundary names a call style, a
   payload shape, and a failure behavior. A contract is the promise one component
   makes to another; an unstated contract is a future outage.

6. **Analyze trade-offs.** Each major choice names at least one alternative and what
   each option costs in the ranked attributes. A choice with no stated alternative is
   a preference wearing the costume of a decision.

7. **Choose, then record an ADR.** The decision, its context, its alternatives, and
   its consequences go into an [ADR](#the-adr). The record is the deliverable that
   survives the meeting.

## Quality attributes

The non-functional requirements (NFRs) that drive structure. Rank them; do not chase
all eight at once.

| Attribute | The question it answers | How it drives the design |
|---|---|---|
| **Scalability** | Does it hold as load grows 10x? | Stateless services behind a load balancer; partition (shard) data by key; favor horizontal scale over a bigger box. |
| **Availability** | What uptime, and what is the cost of downtime? | Redundancy, no single point of failure, health checks, graceful degradation; a target like 99.9% sets the redundancy budget. |
| **Latency** | How fast must the p99 response be? | Caching, read replicas, denormalization, work moved off the request path into a queue. |
| **Consistency** | Must every reader see the latest write? | Strong consistency forces coordination and costs latency and availability; eventual consistency buys scale at the price of stale reads. |
| **Security** | Who may do what, and where is the trust boundary? | Authn/authz at each entry point, encryption in transit and at rest, validation at the boundary, least privilege. |
| **Cost** | What does it cost to run at this scale? | Managed services versus self-hosted, storage tier, the price of redundancy and of idle headroom. |
| **Operability** | Can an on-call engineer diagnose it at 3am? | Logs, metrics, traces, dashboards, runbooks, and a clean rollback path on every deploy. |
| **Evolvability** | How cheaply does the next change land? | Clear module seams, versioned contracts, low coupling so one change does not ripple across the system. |

The tension is the point. Consistency fights availability and latency (CAP and
PACELC); cost fights everything; evolvability fights the speed of the first
release. Naming which attribute loses is the architecture.

## C4 levels

C4 keeps a diagram at one altitude so a reader knows what each box means. Three levels
carry most design work:

- **Context (level 1).** The system as one box, surrounded by its users and the
  external systems it talks to. Audience: anyone. The question: where does this system
  sit in the world?
- **Container (level 2).** The deployable and runnable units — web app, API service,
  worker, database, cache, queue — and the calls between them, each labeled with a
  protocol. Audience: engineers. **The container level is where most system-design
  work lives**, and the altitude the worked example below targets.
- **Component (level 3).** The major parts inside one container and their
  responsibilities. Audience: the engineers building that container. Reach for level 3
  only on the container whose internals are contested.

A box is not a container unless something deploys or runs it. A library is not a
container; a process, a database, or a managed service is.

## Patterns and trade-offs

No pattern is correct in the abstract. Each row states when the pattern earns its
complexity and what it costs.

### Monolith vs services

| | Choose when | Costs |
|---|---|---|
| **Modular monolith** | One team, early product, unproven scale, shared transactional data. | One deploy unit scales as a whole; a bad module can sink the process. |
| **Services** | Independent scaling or independent deploy cadence per domain; many teams. | Network calls, distributed failure, eventual consistency, and an operations burden most early teams cannot pay. |

Default to the modular monolith with clean internal seams. Split a service out when a
named force — a team boundary, a scaling hot spot, an isolation requirement — demands
it. Splitting on speculation buys the cost of distribution with none of the benefit.

### Synchronous vs event-driven

| | Choose when | Costs |
|---|---|---|
| **Synchronous (request/response)** | The caller needs the result now; the flow is a simple read or a transactional write. | Temporal coupling — the caller waits, and a slow callee becomes the caller's outage. |
| **Event-driven (async messaging)** | The work tolerates a delay; producer and consumer should scale and fail apart; one event fans out to many consumers. | Eventual consistency, harder debugging, message ordering and idempotency to design for. |

### SQL vs NoSQL

| | Choose when | Costs |
|---|---|---|
| **Relational (SQL)** | Rich queries, joins, multi-row transactions, strong consistency; the access patterns are not all known up front. | Vertical scaling first; horizontal sharding is real work. |
| **NoSQL (key-value, document, wide-column)** | The access patterns are known and few; the workload needs horizontal scale and predictable latency at huge volume. | Joins and ad-hoc queries are painful; consistency is often eventual; the schema is welded to the query. |

### Caching and queues

- **Cache** — a read in front of a slow store, traded for staleness and an
  invalidation problem. The two hard parts: choosing the eviction and TTL policy, and
  keeping the cache coherent with the source. Reach for a cache once a read is hot,
  repeated, and tolerant of mild staleness.
- **Queue** — a buffer that decouples a fast producer from a slow consumer and
  absorbs spikes, traded for latency on that path and the need for idempotent
  consumers. Reach for a queue once work can leave the request path without the user
  waiting on it.

## Capacity estimation

Back-of-the-envelope numbers separate a design from a daydream. Estimate before
choosing, so the structure matches the load.

The drill:

1. **Traffic.** From daily active users and actions per user, derive requests/day,
   then average requests/sec. Multiply the average by 2–10x for the peak.
2. **Read/write ratio.** Most consumer systems read far more than they write (often
   100:1). The ratio decides whether read replicas and caches dominate the design.
3. **Storage.** Bytes per record times records per day times the retention window
   gives total storage and growth/year.
4. **Bandwidth.** Request size times requests/sec gives ingress and egress per second.
5. **Memory.** To cache the hot set, estimate it (often ~20% of data serves ~80% of
   reads) and size the cache to it.

Round numbers ruthlessly. Useful constants: ~86,400 seconds/day (round to 100k), 1
million seconds ≈ 12 days. The goal is the right order of magnitude — does this need
one box or one thousand — not a decimal.

## Failure modes

Architecture fails in recognizable ways. Test the design against this list before
recording the decision.

- **Big design up front.** Months of diagrams modeling requirements that have not
  been validated, obsolete before the first deploy. Counter: design the first
  increment fully, sketch the rest, and leave seams to extend.
- **Resume-driven architecture.** Technology chosen for novelty or career value, not
  for the problem — Kubernetes for three services, microservices for one team, a
  trendy database with no matching access pattern. Counter: the choice must trace to a
  ranked attribute.
- **Ignoring NFRs.** A design that lists features and never names the target for
  latency, availability, or scale, then collapses under real load. Counter: step 2
  forces a number per dominant attribute.
- **No trade-off analysis.** A single option presented as inevitable, with no
  alternative and no stated cost. Counter: every major choice carries a rejected
  alternative in the ADR.
- **Accidental distributed monolith.** Services split on paper but coupled in
  practice — synchronous call chains, a shared database, one deploy that must ship
  them together. Worst of both worlds: distribution's cost without its independence.
  Counter: a service owns its data and deploys alone, or it is not a service.

### Red flags

- A datastore named before the access patterns are written.
- Microservices proposed by a single team for an unproven product.
- A diagram whose boxes mix altitudes (a class beside a service beside a cloud).
- "We'll need it later" justifying complexity with no current requirement.
- No number anywhere — no users, no requests/sec, no data volume.
- A shared database behind two or more "independent" services.
- Synchronous call chains three or more services deep on the request path.
- An NFR (security, availability, cost) that appears nowhere in the design.

## The ADR

An Architecture Decision Record captures one decision so the reasoning outlives the
author. One ADR per significant, hard-to-reverse choice. The structure:

- **Title** — a short noun phrase naming the decision.
- **Status** — proposed, accepted, deprecated, or superseded.
- **Context** — the forces in play: the requirement, the constraints, the ranked
  attributes that pressure the choice.
- **Decision** — the option chosen, stated as one active sentence.
- **Alternatives considered** — the other viable options and the reason each lost.
- **Consequences** — what becomes easier and what becomes harder, including the
  negative results accepted.

An ADR with no rejected alternative and no negative consequence is marketing, not a
decision record.

## Worked example: a URL shortener

A walk through the seven steps at the container level, ending in an ADR.

### 1. Requirements and constraints

- **Functional.** Shorten a long URL to a short code; redirect a short code to its
  long URL; report click counts per code.
- **Constraints.** Small team, cloud budget modest, public-facing.
- **Scale.** 100M new URLs/month; read-heavy at a 100:1 read/write ratio.

### 2. Ranked quality attributes

1. **Latency** — a redirect sits on the user's critical path; target p99 < 50ms.
2. **Availability** — a dead redirect breaks every link already shared; target 99.99%.
3. **Scalability** — billions of stored codes, with reads dominating.

Consistency ranks low: a newly created code may take a second to be globally
readable without harm.

### 3. Capacity estimate

- Writes: 100M/month ≈ 40 writes/sec average, ~400/sec at peak.
- Reads: 100:1 ratio ≈ 4,000 reads/sec average, ~40,000/sec at peak.
- Storage: ~500 bytes/record × 100M/month × 5 years ≈ ~30 TB. Growth dominates;
  plan for horizontal storage from day one.

The read volume and the 30 TB store rule out a single relational box serving reads
directly; a cache and a horizontally scalable store are required.

### 4. Containers and data

```
[Browser] --HTTPS--> [Edge / Load Balancer]
                          |
              +-----------+-----------+
              |                       |
        [Write API]              [Read API]
              |                       |
              v                       v
   [ID generator]   [Cache: code -> long URL] (read-through)
              |                       |
              +----------+-----------+
                         v
              [Key-value store: code -> long URL, clicks]
                         |
                         v
              [Async queue] -> [Analytics worker] -> [Counts store]
```

- **Write API** — validates the URL, obtains a unique code from the **ID generator**,
  persists the mapping to the **key-value store**. Owns code creation.
- **Read API** — resolves a code to a long URL via the cache, falling back to the
  store, then emits a click event to the queue and returns a redirect. Owns
  resolution.
- **Key-value store** — the system of record: `code -> {long_url, created_at}`,
  partitioned by code. Chosen for point-lookup latency and horizontal scale.
- **Cache** — read-through, `code -> long_url`, holding the hot set. Absorbs the
  redirect read volume.
- **Async queue + analytics worker** — click counting off the redirect's critical
  path, so analytics load never slows a redirect.

Data model: `code` (primary key, base62, ~7 chars), `long_url`, `created_at`,
`click_count` (kept in the counts store, updated asynchronously).

### 5. Contracts

- `POST /shorten {url}` → `{code}` — synchronous; rejects an invalid or unreachable
  URL at the boundary with a 4xx.
- `GET /{code}` → `301` to the long URL — synchronous; a cache miss falls through to
  the store; an unknown code returns 404.
- Click event → queue — fire-and-forget from the Read API; a queue outage degrades
  analytics, never the redirect.

### 6. Trade-off analysis

- **Key-value store over relational.** The dominant access pattern is a point lookup
  by code; joins and ad-hoc queries are absent. Relational would serve correctly but
  shards harder at 30 TB. Cost: ad-hoc reporting moves to the analytics path.
- **Counter codes vs hashing the URL.** A hash deduplicates identical URLs but risks
  collisions and leaks length information; a monotonic counter encoded as base62
  guarantees uniqueness and short codes. Cost: a hot ID generator to scale (mitigated
  by handing out ranges per write node).
- **Async click counting over synchronous increments.** A synchronous counter write
  on every redirect doubles the write path and the latency; the queue keeps the
  redirect fast. Cost: counts are eventually consistent — acceptable per the ranking.

### 7. ADR

> **ADR-001: Use a partitioned key-value store as the system of record**
>
> **Status:** Accepted
>
> **Context:** The redirect read path dominates (100:1 reads, ~40k reads/sec at peak)
> and sits on the user's critical path (p99 < 50ms, 99.99% availability). The store
> grows ~30 TB over five years. The only hot query is a point lookup by short code;
> no joins or ad-hoc queries are required online.
>
> **Decision:** Store the `code -> long_url` mapping in a partitioned key-value store,
> sharded by code, fronted by a read-through cache for the hot set.
>
> **Alternatives considered:**
> - *Relational database (single primary + read replicas).* Rejected: correct and
>   familiar, but sharding 30 TB is heavy operational work and the relational feature
>   set (joins, transactions, ad-hoc queries) buys nothing the online path uses.
> - *Hash the URL for the code instead of a counter.* Rejected: collision handling
>   adds read-path complexity and identical-URL deduplication is not a requirement.
>
> **Consequences:**
> - Positive: point lookups stay fast and the store scales horizontally by code;
>   the cache absorbs peak read volume.
> - Negative: ad-hoc reporting is impossible on the system of record and moves to a
>   separate analytics path; cross-key transactions are unavailable, accepted because
>   no flow needs them.

The deliverables that leave this exercise: the container sketch in step 4 and
ADR-001. Both are checkable — the sketch gives every container one responsibility,
and the ADR carries two rejected alternatives and one named negative consequence.
