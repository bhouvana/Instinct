# RFC-0003: Mechanism Design

- Status: Accepted
- Date: 2026-07-26
- Depends on: RFC-0001 (Charter), RFC-0002 (Prompt Architecture)
- Blocks: RFC-0004 (Evaluation Methodology), RFC-0005 (Testing Strategy),
  implementation

## Summary

Turns Provenance, Judgment, and Efficiency from named pillars into a
procedure Claude actually runs: a cheap classification step (the Gate)
followed by a small number of concrete, tier-specific moves. This is
Instinct's equivalent of Ponytail's decision ladder — the artifact that
makes the philosophy checkable instead of aspirational.

## Design constraints inherited, not reopened

Two things are already decided and this RFC has to fit inside them, not
relitigate them:

- **The Gate has to be genuinely cheap** (ADR-0003). If classifying blast
  radius costs more than the fast-exit it's supposed to enable, RFC-0002's
  broad-trigger decision stops paying for itself.
- **No numeric scoring, no weighted formulas** (RFC-0002 style law). It
  would be easy to reach for "complexity × 0.4 + surface_area × 0.3 + ..."
  — the very framework this project already used itself as a cautionary
  example in RFC-0002 does exactly that. A rule that needs a fake-precision
  number attached to feel authoritative isn't a rule yet. Every check below
  is a plain yes/no question answerable by looking, not a score.

## The Gate

One pass, three yes/no questions, asked in this order, stop at the first
"yes":

1. **Does this touch anything besides what was explicitly named?** — a
   file, function, or config not directly referenced in the request.
2. **Does it have more than one consumer** — another caller, another
   service, another person who reads this output as an interface rather
   than an implementation detail?
3. **Is it expensive to undo** — already shipped/deployed, crosses a trust
   boundary (auth, payment, deletion, data access), or would require someone
   else's coordinated follow-up to reverse?

**No to all three → exit the Gate. Implement directly.** This is the
majority case and must stay that cheap — three short questions against a
request that's usually already unambiguous, not an investigation.

**Yes to any → continue to tiering below.** Per ADR-0006, ties and
uncertainty count as yes. A "does this touch anything besides what was
named" that isn't obviously no gets treated as a yes — the cost of a
wasted tier-2 check is small and bounded; the cost of a missed tier-3
change is not.

## Tiering

Two tiers past the Gate, not a fourth "everything else" bucket — see
ADR-0005 for why two and not more:

- **Tier 2 (Consequential):** answered yes to Q1 or Q2 above, no to Q3.
  Ordinary feature work, most refactors, most new abstractions.
- **Tier 3 (Critical):** answered yes to Q3, regardless of the others.
  Public interfaces, trust boundaries, anything expensive to undo.

## What each pillar does at each tier

**Tier 1 (Gate exit — trivial):** none of the below. Implement.

**Tier 2 (Consequential):**
- *Provenance:* one lookup, not an investigation — check whether the thing
  being touched already has a pattern elsewhere (existing util, existing
  convention, an obvious neighbor to be consistent with). If a five-second
  look doesn't surface an answer, proceed; this tier doesn't license
  spelunking.
- *Judgment:* before writing something new, check once for an existing
  abstraction that already does it. If one exists, extend or reuse it
  instead of adding a parallel one.
- *Efficiency:* smallest diff that solves the stated problem. No new
  dependency without checking stdlib/an already-installed one first.
- *Provenance-out:* the commit message (or equivalent change description)
  states the *why* in addition to the *what* — one clause is usually
  enough. No inline comment unless removing it would hide a non-obvious
  constraint from a reader with the full diff in front of them (this is
  the existing, already-in-force bar for when a comment earns its place —
  Instinct doesn't get a looser standard than the rest of the project's own
  engineering norms).

**Tier 3 (Critical):**
- *Provenance:* actually reconstruct why the current shape exists — read
  the surrounding tests, related code, commit history, or prior ADRs if the
  target repo has that convention. If the "why" genuinely can't be
  reconstructed, that absence is itself surfaced to the user as a finding
  ("couldn't find why X was built this way — proceeding, but flagging that
  the constraint may be undocumented rather than intentional"), not silently
  treated as license to change it freely.
- *Judgment:* state the alternative once, briefly, with the concrete
  tradeoff, before implementing — per RFC-0001's guardrail, exactly once.
  Then implement whichever the user confirms, including the original
  request if they don't want to change course. This is where "disagreement
  is stated once" (RFC-0001, Guardrails) actually fires; at Tier 1 or 2 it
  essentially never should.
- *Efficiency:* the change stays scoped to exactly what the tier-3 concern
  requires. A breaking change to a public signature is not an invitation to
  also clean up unrelated parts of the same function.
- *Provenance-out:* reasoning gets deposited somewhere that survives the
  session — at minimum a commit message that states the tradeoff and why
  the chosen option won, not just what changed. If the repo already has an
  ADR/RFC convention (per RFC-0002's composability rule — use what's
  already there, don't invent a new convention uninvited), a decision at
  this tier is exactly the kind that convention exists for, and Instinct
  should say so rather than let it live only in a commit message.

## Worked examples

**Tier 1 — "Add `*.log` to `.gitignore`."**
Gate: touches only the named file, no other consumer, trivially reversible.
Exit immediately. No provenance check, no alternatives, no deposit beyond
whatever commit message the change already gets.

**Tier 2 — "Add a `formatCurrency` helper for the invoice component."**
Gate: Q1 no (does exactly what's named), Q2 borderline-yes (a formatting
helper is likely to get reused) → continue.
Provenance: one grep for "currency" / "format" / an existing `utils/`
convention. Suppose nothing turns up.
Judgment: no existing abstraction found, so writing a new one is warranted.
Efficiency: reach for `Intl.NumberFormat` (platform feature) before a
hand-rolled formatter or a new dependency.
Provenance-out: commit message — "add formatCurrency: no existing
money-formatting utility, wraps Intl.NumberFormat so invoice call sites stay
consistent." No inline comment needed; nothing here is non-obvious to a
reader of the diff.

**Tier 3 — "Add a required `tenantId` parameter to the public `createUser`
API, used at 12 call sites."**
Gate: Q2 yes (12 consumers), Q3 yes (breaking, requires coordinated
follow-up at every call site) → Tier 3, no ambiguity.
Provenance: check why `createUser` currently has no tenant concept —
deliberately deferred, or never came up. Check whether other public
functions in the codebase already have an established tenant-scoping
pattern this should match.
Judgment, stated once: "This breaks all 12 call sites immediately. An
alternative is an optional `tenantId` with a default-tenant fallback, which
avoids touching every call site now but risks silently mis-scoping data if
a caller forgets to pass it. Given [whatever Provenance surfaced — e.g. an
existing required-parameter convention for other scoping fields], I'd lean
required. Flagging the alternative since the blast radius is real either
way." Then implement whichever the user confirms — without repeating the
objection once they've decided.
Efficiency: touch exactly the 12 call sites and the signature. Resist
folding in unrelated cleanup of `createUser` even if it's tempting while
already in the file.
Provenance-out: commit message states the tradeoff and the reason required
was chosen over optional-with-fallback. If the repo has `docs/adrs/`, this
decision is a direct candidate for one — say so explicitly rather than
letting it live only in the commit log.

## Interaction with the Guardrails (RFC-0001)

- "Disagreement stated once" is now mechanically located: it only fires
  inside Tier 3's Judgment step, exactly once, and Tier 3 itself is gated
  by concrete yes/no questions, not vibes — so it can't creep into Tier 1
  or 2 and become the contrarianism failure mode RFC-0001 warned against.
- "Safety never traded for efficiency" is not a fourth tier or a separate
  check — it's a constraint on the Efficiency pillar's output at every
  tier: "smallest diff that solves the problem" never includes cutting
  validation, error handling that prevents data loss, or security, because
  those are part of what "solves the problem" means, not a cost line item
  Efficiency is allowed to minimize.
- "Explicit user instructions are never a reason to withhold action" means
  the Gate and tiers change *how much is said before implementing*, never
  *whether* implementation happens once the user has heard the Tier-3
  objection (if any) and responded.

## What this RFC does not specify

The exact prose that goes in `SKILL.md` and `references/*.md` — that's
implementation, gated on this RFC being accepted, per RFC-0002's structure
decision. This RFC is the procedure the prose has to compile; it is
deliberately still written in explanatory register because it's a design
document, not the skill text itself (RFC-0002's style law applies to
`SKILL.md`, not to RFCs).

## Forward pointers

- RFC-0004 should treat the three worked examples above as the seed of its
  benchmark scenario set, not write a disconnected new one.
- RFC-0005's regression suite should include at least one adversarial case
  per Gate question — a request engineered to look like a "no" on Q1/Q2/Q3
  while actually being a "yes" — to test whether the Gate's cheapness
  compromises its accuracy in practice, not just in this RFC's reasoning.
