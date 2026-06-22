# Subtraction

The reference behind the ladder. Code is the most expensive asset a project owns: a line of it is read more than it is written, tested, ported across refactors, and carried until someone deletes it. Subtraction is the practice of paying that cost only when a requirement forces it. The leading idea is YAGNI — *you aren't gonna need it* — turned into a procedure you can run on any change.

Climb the ladder rung by rung. Stop at the first rung whose condition holds; the lower rungs are the answer. The sections below expand each rung with a before/after, then cover the carve-outs that never leave, the comment convention for a deliberate shortcut, the failure modes, and a full worked example.

## Why subtraction beats addition

- **Liability scales with volume.** A bug lives in code that exists. Less code is less surface for defects, less to hold in working memory, and less to migrate when the framework version turns over.
- **Deletion is the cheapest feature.** Removing a speculative branch removes its tests, its docs, and the questions every future reader asks about it.
- **Cleverness has a half-life.** A dense one-liner that reads as a puzzle is a future incident — someone decodes it at 3am under pressure. Brevity is a means to clarity, never a substitute for it.
- **Abstraction is a debt taken against a future that may not arrive.** A seam built for callers who never appear is pure cost with no return.

## Rung 1 — does this need to exist?

The highest-leverage rung. Code that should not exist cannot be made small enough; the only correct size is zero. A need is real when a current user or a committed contract demands it. A speculative need ("we might want pluggable backends someday") is dropped, and the one-line reason is recorded in the commit or the ticket so the decision is visible later.

Before — a config knob and a strategy interface for a single in-memory store nobody asked to swap:

```python
class StorageBackend(ABC):
    @abstractmethod
    def get(self, key): ...
    @abstractmethod
    def put(self, key, value): ...

class InMemoryBackend(StorageBackend):
    def __init__(self):
        self._d = {}
    def get(self, key):
        return self._d.get(key)
    def put(self, key, value):
        self._d[key] = value

backend = load_backend(config.get("storage", "memory"))
```

After — the requirement names one store, so the abstraction is dropped:

```python
cache = {}
```

The check: confirm a current caller or a committed contract exercises the thing. With neither, delete it and record why.

## Rung 2 — does the standard library cover it?

A stdlib call ships with the runtime, is documented, and is already trusted by every reader. Reach for it before any third-party name and long before hand-rolled logic.

Before — a hand-written unique-counter that re-implements `collections.Counter`:

```python
counts = {}
for word in words:
    if word in counts:
        counts[word] = counts[word] + 1
    else:
        counts[word] = 1
```

After:

```python
from collections import Counter
counts = Counter(words)
```

The check: search the standard library for the operation by its name (counting, grouping, date math, path handling, JSON) and confirm no stdlib primitive already does it.

## Rung 3 — does a native platform feature cover it?

A platform primitive — a database constraint, an HTTP-framework guard, a built-in language operator — beats a dependency or app code that re-implements the same guarantee. The platform enforces it closer to the metal and keeps it correct under concurrency.

Before — app-level uniqueness that races two concurrent inserts:

```python
if db.query(User).filter_by(email=email).first():
    raise DuplicateEmail()
db.add(User(email=email))
db.commit()
```

After — a database `UNIQUE` constraint, with the app catching the violation:

```python
# schema: UNIQUE(email)
try:
    db.add(User(email=email))
    db.commit()
except IntegrityError:
    raise DuplicateEmail()
```

The check: confirm the platform layer (schema, framework, language) enforces the rule, so two racing callers cannot both pass.

## Rung 4 — does an installed dependency solve it?

A package already in the lockfile is a paid cost; using more of it is free. Adding a *new* dependency is a fresh supply-chain edge, a new audit target, and another version to track — pay that only when nothing installed suffices.

Before — a bespoke retry-with-backoff loop in a project that already depends on `tenacity`:

```python
for attempt in range(5):
    try:
        return call()
    except TransientError:
        time.sleep(2 ** attempt)
raise
```

After:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential())
def call_with_retry():
    return call()
```

The check: grep the lockfile for a package that covers the need before introducing a new name.

## Rung 5 — can it be one expression?

A single readable expression beats a helper function, a class, or a config layer for logic used once. Write the one line when the one line is clear at a glance. Stop short when density turns into a puzzle — clarity outranks character count, so a two-line version that reads plainly wins over a nested one-liner.

Before — a six-line accumulator:

```python
result = []
for n in numbers:
    if n > 0:
        result.append(n * 2)
```

After:

```python
result = [n * 2 for n in numbers if n > 0]
```

The check: confirm the one-liner reads in a single pass. With a second reader squinting at it, expand back to two plain lines.

## Rung 6 — the minimum code that works

The last rung, reached when the rungs above do not cover the need. Write the smallest implementation that satisfies the requirement in full — carve-outs included — and not one branch more. "In full" is the load-bearing phrase: minimum means minimum-that-works, never minimum-that-demos.

The check: confirm the implementation passes the requirement's real inputs and carries every carve-out below, with no speculative branch added for inputs the requirement does not name.

## The carve-outs — what subtraction never removes

Four concerns stay in at every rung. Each one is silent on omission and expensive on failure, so brevity is never a license to cut them.

- **Input validation at trust boundaries.** External data — a request body, a CLI argument, file contents, an upstream API response — is validated before any logic runs on it. The failure mode of skipping this is corrupted state or an injection, surfacing far from the cut that caused it.
- **Error handling that prevents data loss.** A multi-step write is wrapped so a partial failure cannot leave half-written state; a destructive path checks its result. A swallowed exception on a save is data loss waiting to happen.
- **Security controls.** Authorization on every new action, parameterized queries, and output encoding are load-bearing logic, not boilerplate to trim. A removed authz check is a breach, not a simplification.
- **Accessibility basics.** A role, an accessible name, and keyboard operation per interactive element are part of "works" for a UI. Dropping them excludes real users and breaks assistive technology.

The reason these resist subtraction: their cost is paid by someone other than the author, later, and invisibly at write time. The ladder cuts code whose cost the author pays now and sees now. A carve-out fails the opposite way, so the rule is explicit rather than left to judgment.

## Marking a deliberate simplification

A shortcut taken on purpose carries a comment so the next reader inherits the decision instead of re-deriving it or "fixing" a thing that was intentional. The comment names two things: the **ceiling** the shortcut stops at, and the **upgrade path** past it.

```python
# SIMPLIFIED: linear scan, fine up to ~1k items (current max ~50).
# Upgrade path: index by id into a dict when the list grows.
match = next((x for x in items if x.id == target), None)
```

```python
# KNOWN-CEILING: single-region only; multi-region needs a shared cache.
# Tracked in TICKET-481. Revisit before the EU launch.
cache = {}
```

The convention has three parts:

1. **A stable tag** (`SIMPLIFIED:` or `KNOWN-CEILING:`) so the shortcuts are greppable across the codebase.
2. **The ceiling** — the condition under which the shortcut stops being correct (a scale, a region, a load).
3. **The upgrade path** — the concrete next step, with a ticket reference when one exists.

A shortcut with no comment is indistinguishable from a bug. The comment is what separates a deliberate, bounded simplification from an accident.

## Failure modes

Subtraction has its own ways to go wrong. Watch for these:

- **Cleverness someone decodes at 3am.** A nested ternary, a chained comprehension, or a bit-twiddling trick that saves three lines but costs the reader ten minutes. Brevity that hurts comprehension is a net loss — the goal is least code that is *clear*, not least characters.
- **Premature abstraction (the inverted failure).** A factory, a plugin system, or a generic base class built for a second caller who never arrives. Over-abstraction is the opposite sin to over-coding, and the ladder catches it at rung 1: an abstraction for one caller does not need to exist.
- **Deleting a needed safety check in the name of brevity.** A removed validation, a dropped transaction, a stripped authz guard — sold as "simplification," paid as an incident. The carve-outs exist to block exactly this move.
- **False reuse.** Forcing two superficially similar call sites through one shared function couples things that vary independently, and the shared function grows flags to serve both. Two clear copies beat one tangled abstraction until the duplication is proven and stable.
- **Minimum-that-demos, not minimum-that-works.** Cutting the requirement down to the happy path and calling it small. Minimum means the full requirement with carve-outs, expressed as little as possible — never a subset dressed as the whole.

## Worked example — taking a snippet down to size

The task: read a JSON config file and return the list of enabled feature names.

Before — over-engineered: a class, a speculative format switch, a swallowed error, and a manual loop.

```python
class ConfigLoader:
    def __init__(self, path, fmt="json"):
        self.path = path
        self.fmt = fmt

    def load(self):
        try:
            with open(self.path) as f:
                if self.fmt == "json":
                    data = json.load(f)
                else:
                    data = None  # other formats "later"
        except Exception:
            return []
        enabled = []
        for feature in data.get("features", []):
            if feature.get("enabled") == True:
                enabled.append(feature.get("name"))
        return enabled

loader = ConfigLoader("config.json")
names = loader.load()
```

The walk down the ladder:

- **Rung 1 — does the class need to exist?** No caller swaps formats and none reuses the loader as an object; the `fmt` switch serves a future that is not committed. Drop the class and the format branch.
- **Rung 2 — stdlib?** `json` already parses the file. No third-party parser is warranted.
- **Rung 5 — one expression?** The accumulator loop is a comprehension.
- **Carve-out — error handling.** The bare `except ... : return []` hides a missing or malformed file as an empty result, which is data loss disguised as success. Narrow the catch to the expected failure and let an unexpected one surface. A genuinely optional file gets a documented default, marked as a deliberate choice.

After:

```python
def enabled_features(path):
    with open(path) as f:
        config = json.load(f)
    return [feat["name"] for feat in config["features"] if feat["enabled"]]
```

With a missing config file being a real, expected case, the single bounded carve-out is marked rather than swallowed:

```python
def enabled_features(path):
    # SIMPLIFIED: a missing config means no features on; malformed JSON still raises.
    # Upgrade path: validate against a schema once the config grows nested sections.
    if not os.path.exists(path):
        return []
    with open(path) as f:
        config = json.load(f)
    return [feat["name"] for feat in config["features"] if feat["enabled"]]
```

The result: eight lines down from twenty-five, the speculative format switch gone, the error narrowed from "hide everything" to "default only on the one expected absence," and the single shortcut documented with its ceiling and upgrade path. Smaller, clearer, and safer at once — the ladder delivered all three because it cut speculation while the carve-out kept the safety.
