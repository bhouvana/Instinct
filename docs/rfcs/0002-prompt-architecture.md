# RFC-0002: Prompt Architecture

- Status: Accepted
- Date: 2026-07-26
- Depends on: RFC-0001 (Charter)
- Blocks: RFC-0003 (Mechanism Design)

## Summary

Defines how the philosophy locked in RFC-0001 becomes an actual `SKILL.md`
without becoming the prompt bloat this project is a reaction to: how the
skill gets invoked, how its body is structured, what register its text is
written in, and how it avoids fighting other instructions already loaded in
a user's session. Does not define the decision procedure itself — that's
RFC-0003. This RFC produces one concrete artifact: the skill's `name` and
`description` frontmatter, since that field is what the rest of this RFC is
actually about.

## Problem: the invocation gap

Ponytail's primary distribution mechanism is rule files (`AGENTS.md`,
`.cursor/rules/`, etc.) that most platforms auto-load at session start, plus
Claude Code hooks that inject rules on prompt submission. Either way, the
rules are *unconditionally* present once a session starts — the design
problem Ponytail solves is keeping that unconditional text small and
synchronized, not deciding whether it shows up at all.

A Claude Skill does not work that way. It is discovered from a one-line
`description` shown in a standing list, and its full body only enters
context when Claude matches the current task to that description and calls
it. This is a strictly harder invocation problem than Ponytail's: the
`description` has to correctly predict, from a short summary of a task,
whether that task is "engineering work" — and it has to do this via semantic
matching, not a deterministic rule. Get the description wrong and the whole
project stops working the moment it matters most, silently, with no error.

This is the central design problem of this RFC. Everything else here is
secondary to getting the trigger right.

## Decision: broad trigger, cheap fast-exit — not a narrow classifier

Two ways to handle the fact that most requests in a session are trivial and
shouldn't pay any ceremony cost (Efficiency, and the Proportionality
guardrail from RFC-0001):

1. Write a narrow `description` that only matches requests that already look
   consequential — new feature, refactor, architecture, dependency — and
   let everything else never trigger the skill at all.
2. Write a broad `description` that matches essentially all engineering
   work, and put the cheap exit for trivial cases *inside* the skill body
   as its first move, not in the trigger.

This project adopts (2). The reason is the same reason RFC-0001 rejected
judging blast radius from the surface phrasing of a request: whether a
change is actually trivial is not reliably knowable from how it's asked.
"Just add a quick console.log" and "just flip this config flag" are
surface-identical requests that can be genuinely trivial or a landmine
depending on what they touch — a `description` field, matched without the
surrounding codebase context, cannot make that call correctly. Pushing the
triviality check into the trigger asks the weakest available signal (a
one-line summary) to do the job of the strongest available signal (the
model, engaged, looking at the actual request). That is a category error,
and RFC-0001 already named the failure mode it produces: missing the
innocuous-looking request that was actually consequential.

Concretely: `description` matches broadly on "about to make an engineering
decision — write, change, delete, or choose between implementations." The
first move inside the body, once triggered, is the equivalent of Ponytail's
ladder rung one — a check cheap enough that resolving "this is genuinely
trivial, proceed" costs less attention than the Grep call the model would
have made anyway. The trigger's job is coverage; the body's job (RFC-0003)
is speed once triggered. See ADR-0003.

## Decision: one ambient skill for v1, not a family

Ponytail ships six skills — one passive core plus five explicit commands
(`ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`,
`ponytail-help`). Instinct defers that pattern. Shipping a family of
explicit, user-invoked commands (`instinct-why`, `instinct-challenge`,
`instinct-audit`, ...) before the single ambient mechanism is validated
would be speculative surface area — exactly the kind of addition RFC-0001's
own Efficiency pillar argues against, applied reflexively to this project's
own design. The core bet of this project is that the *ambient* behavior
change is the product; explicit commands are a second, separable bet that
should only be made after the first one is proven. See ADR-0004.

## Structure

```
SKILL.md              thin core: frontmatter, Tier 0 + Tier 1 sentences,
                       the fast-exit check, pointers to reference files
references/
  ladder.md            the full decision procedure (RFC-0003's output)
  proportionality.md   what determines blast radius, worked examples
  provenance-out.md    how/when to deposit reasoning (ADR-0001)
```

`SKILL.md` is written to be read in full on every trigger; `references/*`
are read only when the specific scenario in front of Claude calls for the
detail in that file, per the progressive-disclosure pattern this
environment's own skills already use (e.g. a design skill that only pulls a
palette reference file when a color decision is actually in front of it).
This is not a novel pattern to invent — it's the existing mechanism, applied
with discipline: nothing goes in `SKILL.md` that isn't needed on the
majority of triggers.

**Token budget.** No number is asserted as correct here — RFC-0004 owns
measuring whether this works — but the design target for `SKILL.md` is
that reading it costs meaningfully less than the tool call that follows it.
If the file gets long enough to notice, that is itself a signal the file is
explaining instead of compiling, and a reason to move content to a
reference file or cut it.

## Draft artifact: frontmatter

```yaml
name: instinct
description: >
  Load before any non-trivial engineering action: writing new code,
  changing existing code or its behavior, choosing between designs,
  adding a dependency, or deleting/replacing an abstraction. Establishes
  whether this is the right change and the smallest correct version of it
  before implementation starts. Skip for pure information questions with
  no code change, and for requests where the user has already specified
  the exact change and is asking only for its execution.
```

This is a first draft for RFC-0003 and implementation to react to, not a
final artifact — it will need real trigger-precision testing (RFC-0004)
before it ships.

## Style law

Skill text is a compiled instruction, not documentation of one. This RFC is
allowed to explain; `SKILL.md` is not. Concretely:

- Imperative sentences, not descriptive ones. "Name the question this code
  answered before changing it," not "Instinct helps Claude understand the
  provenance of code before modification."
- No tables of trigger keywords, confidence percentages, or persona
  hierarchies. If a rule needs a probability attached to feel authoritative,
  it isn't a rule yet, it's a guess dressed as one.
- The two locked maxims (RFC-0001, Tier 0 and Tier 1) appear verbatim,
  exactly once, and are not restated or paraphrased elsewhere in the file.
  Everything else in the body has to earn its place as an instruction, not
  as support for the maxims — the maxims don't need the support, and text
  that exists to justify a rule rather than state one is documentation
  register leaking into instruction register.

This law has a concrete negative example already present in this
environment: the loaded global framework (`COMMANDS.md`, `ORCHESTRATOR.md`,
`PERSONAS.md`, and siblings) that ships alongside this session is built from
YAML frontmatter blocks, percentage-weighted activation scoring, and
priority-hierarchy tables spanning hundreds of lines per persona. It is
comprehensive and clearly took real effort, and it is the shape this project
is defining itself against: it reads as a specification for how an
orchestration system *should* behave, not as the thing that makes a model
behave that way by default. Whether it succeeds on its own terms isn't this
RFC's call to make — but it's a live, present example of the failure mode
"detailed instructions" and "compiled instinct" are not the same artifact,
and Instinct fails on its own terms if `SKILL.md` ends up structurally
closer to that than to Ponytail's `AGENTS.md`.

## Composability

Instinct operates one layer below persona/orchestration systems, not
alongside them as a competing framework:

- It does not define personas, priority hierarchies, or its own routing
  logic. It does not ask to be the thing deciding *which* specialist voice
  responds; it shapes what happens before any voice starts implementing.
- It defers to a project's existing conventions by construction — Provenance
  (RFC-0001) already requires understanding existing decisions before
  changing them, and that requirement applies to other loaded frameworks and
  a project's own `CLAUDE.md` exactly as it applies to code. Instinct does
  not get a carve-out from its own first mechanism.
- It composes with Ponytail rather than overlapping it: Ponytail governs the
  size and necessity of what gets written once a change is already decided;
  Instinct governs whether and why the change happens at all. A body
  instruction should make this boundary explicit so the two don't both try
  to own "should I write this" from different angles and produce
  contradictory advice.

## Non-goals for v1

- A skill family with explicit invocable commands (deferred, ADR-0004).
- Multi-platform rule-file distribution (deferred, RFC-0001).
- Any mechanism for detecting or negotiating with other installed
  frameworks beyond "don't contradict, don't duplicate, defer to what's
  already there."

## Open questions handed to RFC-0003

- The actual content of the fast-exit check and the full ladder-equivalent
  procedure.
- The concrete rule for what determines blast radius (Proportionality,
  RFC-0001) — this RFC only established that the *trigger* shouldn't try to
  compute it; RFC-0003 has to define what does.
- A concrete, low-ceremony default for provenance-deposit (ADR-0001) that
  the `provenance-out.md` reference file can encode.

## Forward pointer

RFC-0004 (Evaluation Methodology) should treat trigger precision and recall
— did the skill fire when the request was actually consequential, did it
stay quiet when the request was actually trivial — as a metric distinct
from and prior to decision-quality metrics. A perfect decision procedure
behind a trigger that doesn't fire is invisible; a trigger that fires
constantly regardless of stakes is the contrarianism failure mode
(RFC-0001, Guardrails) by construction, independent of what the procedure
inside it says.
