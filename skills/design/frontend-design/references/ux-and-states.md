# UX, usability, and system states

A product interface is a conversation the user holds with a machine that cannot explain
itself. Usability is how little the user must already know to hold that conversation: the
interface shows what is possible, signals what is happening, names things in the user's
language, and recovers gracefully when the user errs. A screen can look polished and
still fail every user, because visibility, feedback, error recovery, and accessibility
are judgment calls no component library makes.

The work below is ordered the way leverage runs. A screen can have flawless pixels and
still fail, because the state was invisible, the affordance was a guess, or the error
discarded the user's work. Visual polish (the [visual rules](visual-rules.md)) is the
floor; the leverage is here.

## 1. Nielsen's 10 usability heuristics

Jakob Nielsen's heuristics are the canonical lens for evaluating an interface. Each
heuristic below pairs the principle with one concrete UI application.

| # | Heuristic | Concrete UI application |
|---|-----------|-------------------------|
| 1 | **Visibility of system status** | A file upload shows a determinate progress bar and a percentage, never a frozen button. The user knows the system received the action and how far along the work is. |
| 2 | **Match between system and the real world** | A trash icon for delete, "Archive" rather than "Soft-delete record," dates as "3 days ago" near "Jun 19, 2026." The label speaks the user's language, not the schema's. |
| 3 | **User control and freedom** | An "Undo" toast after a destructive action, a visible back path out of every modal, a cancel button on a multi-step wizard. The user holds a marked exit from a mistaken state. |
| 4 | **Consistency and standards** | The primary action sits bottom-right in every dialog, the same verb ("Save") means the same thing on every screen, and a checkbox always toggles. Platform conventions are honored, not reinvented. |
| 5 | **Error prevention** | Disable "Submit" until the form validates, confirm a destructive action with a typed object name, and constrain a date picker so the past cannot be chosen for a future event. The design removes the chance to err before recovery is needed. |
| 6 | **Recognition rather than recall** | A search box shows recent queries, a form pre-fills the saved address, and a command palette lists actions by name. The user recognizes an option on screen instead of remembering it from a prior screen. |
| 7 | **Flexibility and efficiency of use** | Keyboard shortcuts for power users layered over clickable controls for novices, plus bulk actions on a multi-select list. The interface serves the expert without abandoning the beginner. |
| 8 | **Aesthetic and minimalist design** | One primary action per view, secondary actions visually quieter, and no field on a form the task does not require. Every extra element competes with the signal and dilutes it. |
| 9 | **Help users recognize, diagnose, and recover from errors** | An error in plain language ("That email is already registered — sign in instead?") next to the offending field, with a route to the fix. The message names the cause and offers the next step, never a raw stack trace or code. |
| 10 | **Help and documentation** | Inline hints, a contextual tooltip on an unusual control, and searchable docs reachable without leaving the task. Help is findable at the point of confusion, not buried in a separate manual. |

Score each heuristic against the screen under review, mark a pass or a violation with a
severity, and tie every violation to the user task it endangers. A violation the designer
cannot act on is noise, not a finding.

## 2. Affordances and interaction patterns

An affordance is a visible signal of what a control can do. A button looks pressable, a
link looks clickable, a slider looks draggable — the appearance promises the behavior,
and a broken promise is a usability defect.

- **Signifiers carry the affordance.** A control communicates its function through shape,
  color, elevation, and a cursor change on hover. A clickable element styled as plain text
  is "mystery meat" — the user cannot tell action from decoration.
- **State is visible across the interaction.** Every interactive control shows its states:
  default, hover, focus, active, disabled, and loading. A disabled control reads as
  disabled (lower contrast, no hover), so the user is not left clicking a dead button.
- **The target is large enough to hit.** Touch targets meet the platform minimum (about
  44×44 pt on iOS, 48×48 dp on Android), with spacing so adjacent targets do not collide.
  A target too small is a miss the user blames on themselves.
- **Feedback follows every action within budget.** A tap produces an immediate visible
  response (ripple, color shift, spinner) inside about 100 ms, so the action registers as
  received. Silence after a tap reads as a broken control.
- **Direct manipulation beats indirect where it fits.** Drag-to-reorder, swipe-to-delete,
  and inline editing let the user act on the object itself rather than through a distant
  form. Proximity of action to object lowers the cognitive load.

Red flags: a clickable element styled as static text; a control with no hover or focus
state; touch targets packed below the platform minimum; a tap that produces no visible
response; a hover-only action with no keyboard or touch equivalent.

## 3. Form design

A form is where the user does the most work and loses the most patience. Labels,
validation, and error recovery decide whether the form completes or gets abandoned.

- **Labels stay visible.** Every field carries a persistent label above or beside the
  input — never a placeholder masquerading as a label. A placeholder vanishes on focus, so
  a placeholder-as-label leaves the user guessing what a half-filled field holds.
- **One column, logical grouping.** Fields stack in a single column in the order the user
  thinks (name, then email, then password), grouped under headings when the form is long.
  A multi-column form scatters the eye and inflates completion time.
- **Ask only what the task needs.** Every field on the form earns its place, and an
  optional field is marked optional rather than leaving "required" as the silent default.
  A shorter form converts higher because each field is a small tax on completion.
- **Validation is inline and timed right.** A field validates on blur (after the user
  leaves it), not on every keystroke, and the success or error state shows beside the
  field. Validation deferred to a final submit forces the user to hunt for what broke.
- **Errors name the cause and the fix.** An invalid field shows a specific message
  ("Password needs 8+ characters") in red beside the input, with the field marked, focus
  moved to the first error, and the rest of the form preserved. A generic "Invalid input"
  banner at the top leaves the user scanning.
- **The form never loses entered data.** A validation failure, a back navigation, or a
  session timeout returns the user to a form that still holds what they typed. Discarded
  input on error is the fastest path to abandonment.
- **Input types match the data.** A numeric field raises a numeric keypad, an email field
  raises the email keyboard, and autocomplete tokens fill known values. The right input
  type lowers the typing burden on mobile.

Red flags: a placeholder used as the only label; validation only at submit; a top-only
error banner with no per-field marker; a form that clears on a validation error or a back
press; "required" assumed silently with no "optional" markers; a free-text field where a
constrained picker fits.

## 4. The system states

Every data-bearing view holds five states, not one. Designing only the success state
ships a screen that breaks the first time data is slow, absent, or wrong. Name and design
each state before the view is "done."

| State | What it shows | Why it matters |
|-------|---------------|----------------|
| **Loading** | A skeleton screen or a determinate progress indicator that mirrors the coming layout. | The user knows work is underway and roughly how long. A skeleton beats a spinner because it previews structure and lowers perceived wait. |
| **Empty** | A first-run or zero-results state with a one-line explanation and a primary action ("No projects yet — create your first"). | An empty list with no guidance reads as a bug. The empty state is an onboarding opportunity, not dead space. |
| **Error** | A plain-language message naming the cause, a retry control, and a path to support. | A failed fetch must explain and offer recovery, never a blank screen or a raw error code. The error state protects trust. |
| **Partial** | Loaded content beside placeholders for the rest, or a "load more" boundary on a paged list. | A view that pages or streams must show what arrived without blocking on what has not. Partial keeps the interface responsive under slow data. |
| **Success** | The fully loaded content, plus a confirmation after a completed action. | The default designers reach for first. Success without a confirmation after a write leaves the user unsure the action took. |

A view missing its empty, error, or partial state is incomplete, regardless of how good
the success state looks.

## 5. Feedback and perceived performance

Perceived speed matters more than measured speed. The interface manages the user's sense
of time through well-placed feedback against three response-time thresholds (Nielsen,
Card):

- **Under ~100 ms** reads as instant — direct manipulation and button presses must land
  here, so the action feels like cause and effect.
- **Under ~1 s** keeps the user's flow of thought intact — show an immediate state change
  even while the result still loads, so the gap is acknowledged.
- **Over ~1 s** breaks attention — show a determinate progress indicator past this
  threshold, so the user knows the system is working and how long remains.

Tactics that buy perceived performance:

- **Optimistic UI.** Reflect the user's action immediately (a "liked" heart fills at
  once) and reconcile with the server in the background, rolling back visibly on failure.
- **Skeleton screens.** Render the page structure with placeholder blocks during load, so
  the wait feels shorter than a blank screen or a centered spinner.
- **Confirm every consequential action.** A save shows a toast, a delete shows an undo, a
  submit transitions to a result. Silence after a write is the most common feedback gap.
- **Surface progress for long work.** A multi-second job shows steps or a percentage,
  never a frozen UI that looks crashed.

Red flags: a button that does nothing visible for a full second after a click; a write
that completes with no confirmation; a spinner used where a skeleton would preview
structure; an irreversible action with no undo and no progress signal.

## 6. Information hierarchy and progressive disclosure

Information hierarchy is the visual order that tells the eye what to read first. A flat
screen where every element shouts equally has no hierarchy, so the user reads nothing in
particular. The visual mechanics live in [visual-rules.md](visual-rules.md) section 4;
the usability discipline is here.

- **Establish hierarchy with size, weight, color, and space.** A clear type scale (one
  H1, fewer H2s, body text), spacing that groups related items, and contrast reserved for
  the primary action route the eye from most to least important.
- **One primary action per view.** The main action carries the strongest visual weight,
  secondary actions read quieter, and tertiary actions hide behind a menu. Two co-equal
  "primary" buttons give the user no main path.
- **Group by proximity and the law of common region.** Related controls sit close and
  share a container; unrelated controls separate. Proximity does the grouping work a
  border would otherwise carry.
- **Progressive disclosure defers complexity.** Show the common path first and reveal
  advanced options on demand — an "Advanced settings" accordion, a "Show more" link, a
  wizard that asks one thing per step. Disclosure trades a complete view for a learnable
  one, and the trade favors the novice without blocking the expert.
- **Defaults carry most users.** A sensible default on every optional control means the
  user changes only what matters to them. A good default is a decision the user does not
  have to make.

Red flags: a screen with no clear primary action; uniform type and weight across all
text; every advanced option exposed at once; controls scattered with no grouping; a
required choice where a sensible default belongs.

## 7. Navigation patterns

Navigation answers three questions the user holds at all times: where am I, where can I
go, and how do I get back. A navigation system that leaves any of the three unanswered
strands the user.

- **The current location is always marked.** The active nav item is highlighted, the
  breadcrumb shows the path, and the page title matches the destination the user chose. An
  unmarked location forces the user to reconstruct where they are.
- **Pick the pattern to fit the breadth.** A top nav bar suits five to seven primary
  destinations; a sidebar suits a deep app with many sections; a bottom tab bar suits
  three to five top-level areas on mobile; a hamburger menu hides navigation and suits
  only secondary destinations. Structure follows the count and the platform.
- **Depth stays shallow.** Most destinations sit within two or three taps of the entry
  point, and a breadcrumb marks the trail on a deep hierarchy. Deep nesting buries content
  the user then cannot find.
- **Back always works.** The browser back button, a swipe-back gesture, and an in-app back
  control all return the user to the prior state without losing context. A back path that
  dead-ends or reloads from scratch breaks the user's mental map.
- **Search complements navigation.** A global search lets the user jump straight to a
  known target instead of clicking through the tree. Search is the escape hatch when the
  hierarchy does not match how the user thinks.

Red flags: no active-state marker on the current nav item; primary destinations hidden
behind a hamburger on desktop; a hierarchy more than three levels deep with no breadcrumb;
a back action that loses the user's place; no search on a content-heavy app.

## 8. Accessibility — the interaction layer

An interface usable by people with disabilities is more usable for everyone. Keyboard
support, focus management, ARIA semantics, and contrast are structural, not a layer added
at the end. The bar is WCAG 2.1 AA. The contrast thresholds (4.5:1 body, 3:1 large) live
in [visual-rules.md](visual-rules.md) section 3; the interaction-level requirements are
here.

- **Everything works from the keyboard.** Every interactive control reaches focus and
  activates with Tab, Enter, and Space, in a logical order that matches the visual flow. A
  control reachable only by mouse excludes keyboard and screen-reader users entirely.
- **Focus is visible and managed.** A clear focus ring marks the focused element, opening
  a modal moves focus into it and traps focus there, and closing the modal returns focus
  to the trigger. A lost focus point leaves a keyboard user stranded.
- **Semantics come from native elements first.** A real `<button>`, a real `<nav>`, and a
  real `<label>` tied to its input carry meaning to assistive technology for free. ARIA
  patches what native HTML cannot express — an `aria-label` on an icon button, `aria-live`
  on a status region, a `role` only where no native element fits. The first rule of ARIA
  is to prefer a native element over an ARIA role.
- **Contrast clears the threshold.** Body text holds at least a 4.5:1 contrast ratio
  against its background, large text and UI components at least 3:1. Low-contrast text is
  unreadable for low-vision users and in bright light for everyone.
- **Meaning never rests on color alone.** An error pairs a color with an icon and text, a
  required field carries a marker beyond red, and a chart labels series rather than relying
  on hue. Color-blind users miss a signal carried by color alone.
- **Content is reachable by screen reader.** Images carry alt text, form fields carry
  programmatic labels, and dynamic updates announce through a live region. A screen-reader
  user builds the same model a sighted user does only when the structure is exposed.

Red flags: a custom control with no keyboard handler; no visible focus ring; a modal that
does not trap or restore focus; an icon-only button with no accessible name; body text
under 4.5:1 contrast; an error signaled by red alone; an image with no alt text.

## 9. Failure modes

- **Mystery-meat navigation.** Icons or labels that hide their destination until clicked,
  or clickable elements indistinguishable from static content. The user cannot predict
  where a control leads, so navigation becomes trial and error. Fix: visible, labeled,
  conventionally styled controls.
- **Missing empty and error states.** A list that renders blank when empty and white when
  the fetch fails. The user reads absence as a bug and a failure as a crash. Fix: design
  the empty and error states as first-class views with guidance and recovery.
- **Destructive actions without confirmation.** A delete that fires on a single click with
  no undo and no confirm. One slip costs the user real data. Fix: a confirmation for the
  irreversible, an undo window for the reversible, and "Cancel" as the safe default in the
  dialog.
- **Forms that lose data.** A validation error, a back press, or a timeout that wipes every
  field the user filled. Lost work is the fastest route to abandonment. Fix: preserve
  entered values across validation, navigation, and recoverable session loss.
- **Invisible system status.** A button that gives no feedback after a click, a save with
  no confirmation, a long job behind a frozen screen. The user cannot tell working from
  broken. Fix: immediate feedback on action and a confirmation on completion.
- **Placeholder-as-label forms.** Labels that live only in the placeholder and vanish on
  focus. A half-filled form becomes unreadable, and error recovery becomes a guessing game.
  Fix: persistent visible labels.
- **Inaccessible custom controls.** A bespoke dropdown or toggle built from `<div>`s with
  no keyboard support, no focus, and no role. Keyboard and screen-reader users are locked
  out. Fix: native elements first, ARIA only to fill the gaps.
- **No clear primary action.** Several buttons of equal visual weight, so the eye finds no
  main path. The user hesitates over which control advances the task. Fix: one primary
  action per view, secondary actions visually subordinate.

## Red flags

- A heuristic violation (status, error recovery, control freedom) endangers a core user
  task.
- A clickable element is indistinguishable from static text (mystery meat).
- A data view ships without an empty, error, or partial state.
- A destructive action carries no confirmation and no undo.
- A form loses entered data on a validation error, a back press, or a timeout.
- An action produces no visible feedback, or a write completes with no confirmation.
- A screen presents no clear primary action, or every element carries equal weight.
- A control is unreachable by keyboard, or the focus ring is invisible or unmanaged.
- Body text falls under a 4.5:1 contrast ratio, or a signal rests on color alone.
- An icon-only button or an image carries no accessible name or alt text.

## Worked example — improving a settings page's UX

**The before.** A SaaS app ships an account settings page as one long form. Symptoms,
mapped to the principles above:

- Twenty fields in two columns under no headings — broken hierarchy (§6) and a scattered
  layout (§3).
- Field labels live in placeholders that vanish on focus — a placeholder-as-label failure
  (§3, §9).
- A single "Save" at the bottom commits the whole page, and validation surfaces only on
  that click — late validation with a top-only error banner (§3).
- "Delete account" sits as a plain red button beside "Save," firing on one click — a
  destructive action with no confirm (§2, §9).
- A save shows no confirmation; the page just reloads — invisible status (§1, §5).
- The custom toggle switches are `<div>`s with no keyboard support and no focus ring —
  inaccessible controls (§8).

**The after, change by change:**

1. **Group and sequence (§6).** Split the twenty fields into three labeled sections —
   Profile, Notifications, Security — each in a single column in the order the user
   thinks. The eye now reads top to bottom with a clear path. *Check:* every field sits
   under a section heading in one column.
2. **Persistent labels (§3).** Move every label above its input and reserve placeholders
   for format hints ("e.g. jane@acme.com"). A half-filled field stays readable. *Check:*
   no field relies on a placeholder for its label.
3. **Inline, timed validation (§3).** Validate each field on blur, show the error beside
   the field in plain language, mark the field, and move focus to the first error on a
   failed save. The user fixes errors in place. *Check:* a deliberately invalid entry
   shows a per-field message on blur, not only at submit.
4. **Section-level save with confirmation (§1, §5).** Give each section its own "Save,"
   disable it while that section is pristine or invalid, and show a success toast on
   completion. The user knows the write took. *Check:* a successful save raises a visible
   confirmation; the save control is disabled while the section is pristine or invalid.
5. **Guard the destructive action (§2, §9).** Move "Delete account" into a "Danger zone"
   section, require the user to type the account name in a confirm dialog, and make
   "Cancel" the default focus. One slip no longer destroys the account. *Check:* deleting
   requires a typed confirmation in a separate dialog.
6. **Accessible controls (§8).** Replace the `<div>` toggles with native checkbox inputs
   styled as switches, each tied to a `<label>`, reachable by Tab, toggled by Space, with
   a visible focus ring and an `aria-checked` state. Keyboard and screen-reader users can
   now operate every control. *Check:* every toggle reaches focus and activates from the
   keyboard with a visible ring.

**The result.** The page reads as three scannable sections, never loses the user's input,
confirms every save, cannot delete the account by accident, and works end to end from the
keyboard. Every change traces to a heuristic and a state, and each ends on a condition a
reviewer can verify.

## UX checklist

- [ ] **Heuristics** — all 10 carry a verdict; every violation names the task it
  endangers.
- [ ] **States** — every data view has loading, empty, error, partial, and success
  designed.
- [ ] **Forms** — persistent labels, inline validation on blur, per-field errors,
  preserved input.
- [ ] **Feedback** — every write confirms; long work shows determinate progress.
- [ ] **Primary action** — exactly one per view; secondary actions subordinate.
- [ ] **Navigation** — current location marked; back always works; depth ≤ three with
  breadcrumbs.
- [ ] **Keyboard** — every control reachable and operable; focus visible, trapped in
  modals, restored on close.
- [ ] **Destructive actions** — confirmation or undo on every irreversible action.
