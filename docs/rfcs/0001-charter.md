# RFC-0001: Project Charter

- Status: Accepted
- Date: 2026-07-26

## Summary

Instinct is a Claude Skill that changes what Claude optimizes for on the first
token of a response to an engineering request: not "how do I implement this"
but "is this the right thing to do, and what is the smallest correct version
of it." It does this by installing a decision procedure, not a persona.

## Problem Statement

Current coding assistants are locally agreeable and locally competent. Given a
request, they implement it. They know syntax, APIs, and frameworks well
enough that implementation is rarely the bottleneck. What they lack is the
thing that makes a senior engineer valuable, which has nothing to do with
knowing more syntax: the instinct to ask, before touching anything, why a
piece of code exists, whether the request is actually the right fix, and
whether the smallest change achieves the goal.

This is not a knowledge gap. It is a default-behavior gap. An assistant that
always implements exactly what was asked, as fast as possible, is optimizing
for compliance, not for engineering quality — and code is not neutral text
that can be judged in isolation. Every abstraction, interface, and workaround
in a real codebase is the fossil of a decision someone made under constraints
that are no longer visible. Treating code as text instead of as accumulated
decisions is the root failure mode this project addresses.

## Philosophy

### Tier 0 — Identity

> Engineering is not writing code. Engineering is making good decisions.
> Everything else is a consequence.

This is the sentence the rest of the project is downstream of. It reframes
Claude's self-concept for engineering tasks: from an implementation engine
that produces code, to a decision-maker that occasionally produces code as
the byproduct of a decision it can defend.

### Tier 1 — Operational Maxim

Tier 0 does not, by itself, change what happens at the moment a tool call is
about to be made — and a philosophy that only changes vibes and never changes
the next action is decoration, not design. Tier 1 is the sentence that fires
at that moment, specifically aimed at the failure mode that is easiest to
skip under time pressure: touching code before understanding it.

> Every line of existing code was somebody's answer to a question you
> haven't asked yet.

This converts "seek provenance" from an abstract virtue into a reflex: before
judging or modifying code, name the question it was answering. If that
question can't be reconstructed, that itself is a finding worth surfacing,
not a reason to proceed blind.

### The Mechanism: Provenance, Judgment, Efficiency

These three are not the philosophy. They are what the philosophy demands,
made mechanical:

- **Provenance** — good decisions require understanding the decisions
  already made. Consumed *and* produced: Instinct both seeks the reasoning
  behind existing code and leaves reasoning behind for the next reader, at a
  cost proportional to blast radius (see Guardrails). This bidirectionality
  is the one place this project departs materially from prior art (see
  RFC relationship to Ponytail, below, and ADR-0001).
- **Judgment** — good decisions require evaluating alternatives before
  committing to one. Evidence-driven, not argumentative: challenge the
  premise once, briefly, with a reason: then implement the decision that
  results, whether or not it was Claude's first suggestion.
- **Efficiency** — good decisions minimize unnecessary complexity. Deletion
  over addition, reuse over creation, extension over replacement, the
  smallest correct diff over the impressive one.

None of these three stand alone as a checklist to run every time. They are
lenses that a single underlying procedure (designed in RFC-0003) applies with
intensity proportional to what's at stake.

## Guardrails

A philosophy this is meant to change default behavior, which means it can
fail in two directions, not one. Both are treated as defects with equal
severity:

1. **Negligence** — skipping judgment and provenance-seeking to move fast.
   This is the failure mode of the assistants this project is a response to.
2. **Contrarianism** — applying full ceremony to every request regardless of
   stakes, turning "engineering judgment" into reflexive friction. An
   assistant that interrogates a one-line CSS fix with the same scrutiny as
   an auth-boundary change is not exercising judgment, it is performing
   caution, and it is exactly as untrustworthy as being a yes-man, just in
   the opposite direction.

To hold both, the following are non-negotiable:

- **Proportionality.** The depth of provenance-seeking and the intensity of
  judgment scale with blast radius and reversibility, not with the mere
  presence of a request. Low-stakes, easily-reversible changes get near-zero
  ceremony. Changes to public interfaces, shared abstractions, security
  boundaries, or anything hard to undo get real scrutiny. This single rule is
  the guardrail against contrarianism.
- **Disagreement is stated once.** If Claude pushes back on a request, it
  states the evidence-based objection briefly, a single time. Once the user
  has heard it and decided, Claude implements the decision without
  relitigating it. Judgment is not nagging.
- **Explicit user instructions are never a reason to withhold action.**
  Judgment changes *how* something is built, and can surface objections
  before building it, but it does not become an excuse to stall on a
  decision the user has already made.
- **Safety is never traded for efficiency.** Correctness, input validation,
  security, and data-loss prevention are outside the scope of "the smallest
  correct diff." They are part of correct, not a cost to be minimized away.

## Relationship to Prior Art

[Ponytail](https://github.com/DietrichGebert/ponytail) is the closest prior
art and the reason this project's philosophy was pressure-tested against a
working, benchmarked example rather than designed in a vacuum. Ponytail's
maxim, "the best code is the code never written," compiles directly into a
decision ladder (does this need building → already in the codebase → stdlib
→ platform feature → dependency → one line → minimal code) with explicit,
named carve-outs (security, validation, accessibility, explicit
requirements) so minimalism never becomes negligence. It is benchmarked
against a real baseline (46% fewer lines of code, safety held at 100% vs.
95%), which is what makes it trustworthy rather than aspirational.

Instinct borrows the structural lesson — a philosophy is only as strong as
the mechanical, falsifiable procedure it compiles into, and that procedure
needs explicit carve-outs — but addresses a different layer of the problem.
Ponytail governs the size and necessity of *what gets written*. Instinct
governs whether, why, and how a change should be made at all, before size is
even a question. The two are complementary, not competing: a codebase using
both would have an assistant that first decides a change is the right one
(Instinct) and then writes the smallest correct version of it (Ponytail).

The one genuine departure is bidirectional provenance (see ADR-0001):
Ponytail's `ponytail:` trade-off comments are a narrow, inline version of
depositing reasoning for the future; Instinct treats depositing provenance as
a first-class, proportional obligation, not an occasional annotation, because
it is the one mechanism that lets an ephemeral per-session judgment compound
into institutional memory across sessions.

## Non-Goals

Instinct is explicitly **not**:

- A prompt pack of stylistic instructions ("write clean code", "use SOLID").
- A collection of workflow macros for specific engineering tasks.
- A "senior engineer" persona or tone change.
- A code-size minimizer (that's Ponytail's job; Instinct composes with it).
- A mechanism for slowing down every request uniformly. Proportionality is
  load-bearing, not optional (see Guardrails).
- A replacement for the user's own architectural authority. Instinct informs
  decisions; it does not make them unilaterally or refuse to implement a
  decision once made.

## Success Criteria

The project is working if a developer, after using it for a week, describes
the change as "Claude has developed engineering judgment" rather than
"Claude follows better prompts" or "Claude asks more questions now." The
second framing is a specific failure mode to design against: if the visible
symptom is *more friction*, the guardrails have failed, regardless of
whether the underlying decisions improved. The visible symptom should be
*better decisions*, most of which are invisible because they happened before
any text was generated.

Falsifiable, benchmarkable proxies (fleshed out in RFC-0004):

- Rate of changes later reverted or amended because they solved the wrong
  problem, missed an existing abstraction, or duplicated functionality.
- Rate of unprompted, evidence-based pushback on requests that turn out
  (by the user's own judgment) to have been warranted.
- Ceremony cost on low-blast-radius requests, measured against a no-skill
  baseline (this should trend toward zero, per Proportionality).
- Diff size on accepted changes, relative to a no-skill baseline (expected
  to drop, though this is Ponytail's more direct metric — Instinct's
  contribution here is indirect, via fewer wrong-abstraction detours).

## Forward Plan

This charter is Tier 0/1 and the guardrails. It does not yet specify:

- How the Provenance/Judgment/Efficiency mechanism becomes a concrete,
  checkable procedure (RFC-0003).
- How any of this becomes actual `SKILL.md` prompt text without becoming
  the prompt bloat this project is a reaction to (RFC-0002).
- How success criteria above become a real evaluation harness (RFC-0004).
- How the harness gets exercised as regression tests (RFC-0005).

See `docs/ROADMAP.md` for sequencing.
