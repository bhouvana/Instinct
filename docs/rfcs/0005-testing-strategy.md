# RFC-0005: Testing Strategy

- Status: Accepted
- Date: 2026-07-26
- Depends on: RFC-0003 (Mechanism Design), RFC-0004 (Evaluation Methodology)
- Blocks: implementation sign-off

## Summary

Operationalizes RFC-0004's Layer 1 and Layer 2 — the cheap, machine-checkable
subset — into an actual regression suite that runs on every change to
`SKILL.md` or a reference file, the same way a unit test suite runs on every
code change. RFC-0004's Layer 3/4 stay human-reviewed, release-gated, and
outside this RFC's scope; this is deliberately the fast loop, not the
authoritative one.

## Why this exists as a separate artifact from RFC-0004

A prompt file is a decision, same as any code change, and this project's
own philosophy (RFC-0001) says decisions need evidence before they ship —
that applies reflexively to editing `SKILL.md` itself, or the project
fails its own standard the first time someone tweaks a sentence. Without an
automated suite, "does this wording change break the Gate" can only be
answered by re-running expensive Layer 3/4 evaluation (ADR-0007, ADR-0008)
or by eyeballing it, and eyeballing a prompt change for regressions is
exactly the kind of unverified confidence this project exists to replace.

## What's in the suite

**1. Trigger corpus** (RFC-0004 Layer 1). A set of requests labeled
"should trigger" / "should not trigger," covering: obvious Tier 2/3 work,
obvious pure-information questions, and specifically the boundary cases —
requests that read as informational but imply a change, and requests that
read as a change but are fully specified with no room for a different
approach (RFC-0002's stated skip condition). Pass criterion: precision and
recall against this corpus stay at or above whatever bar the first accepted
version establishes as baseline — this RFC does not invent a number, RFC-0004
Layer 1's first real run does, and the suite fails on regression against
that baseline, not against an assumed target.

**2. Gate/tier corpus** (RFC-0004 Layer 2). A set of requests labeled with
their correct Gate answers and resulting tier, seeded directly from
RFC-0003's three worked examples and expanded to include, per RFC-0003's
own forward pointer, at least one adversarial case per Gate question: a
request engineered to read as "no" on a question while the underlying
change is actually "yes" (e.g. a request phrased as touching one file that
actually has a second, non-obvious consumer), and the reverse. Pass
criterion: exact tier match against the label.

**3. Worked-example smoke test.** The three canonical examples from
RFC-0003 (the `.gitignore` add, the `formatCurrency` helper, the
`createUser` signature break) run against the current `SKILL.md` on every
change, checked not just for correct tier but for the *shape* of the
tier-specific behavior — Tier 3 actually states an alternative once, Tier 1
actually proceeds without ceremony. This is the fastest possible check that
a wording edit hasn't silently collapsed the tiers into each other.

## What's explicitly not in this suite

Anything requiring a judgment call about whether a decision was *correct*
rather than *classified consistently* — "was the Tier 3 pushback actually
the right call" is Layer 3/4 territory (RFC-0004), stays human-reviewed,
and does not get an automated proxy here. A suite that tried to automate
this would need exactly the LLM-as-judge shortcut ADR-0008 already rejected
as an authority, for the same reason.

## Corpus governance

See ADR-0009 for the sharpest call: the corpus is authored and locked
*before* the first real `SKILL.md` draft exists, not written to match
whatever the draft happens to do. Beyond that:

- A regression caught by this suite is fixed by changing the prompt, not by
  editing the corpus to match the new behavior — loosening a failing test
  to make it pass is the same Goodhart failure RFC-0004 already names, and
  the suite has no authority left the moment editing the corpus becomes the
  easier fix.
- New scenarios can be added (coverage should grow), but removing or
  relabeling an existing one requires stating why in the commit — this is
  RFC-0001's own Provenance-out standard, applied to the project's test
  corpus instead of to a codebase, which is the correct place for it to
  apply.
- A portion of the corpus is held out per ADR-suite discipline already
  established in RFC-0004 (the Goodhart guardrail's holdout scenarios) —
  not every case the suite checks should be visible during day-to-day
  prompt iteration, or the fast loop optimizes for the visible cases only.

## Relationship to implementation

This suite is written and locked before the first `SKILL.md` draft, and the
first draft is checked against it immediately, not audited for regressions
after the fact. Test-first here isn't a stylistic preference — an
independently authored bar that implementation has to clear is a materially
different, stronger check than a suite assembled by watching what the
implementation already does and writing down its behavior.

## What this RFC does not specify

The literal file format of the corpus and how it's run (a script, a hook,
CI) — that's an implementation detail resolved when the corpus is actually
authored, not a design question this RFC needs to settle in the abstract.
