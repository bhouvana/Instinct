# ADR-0003: Broad ambient trigger with an in-body fast exit, not a narrow pre-filtering trigger

- Status: Accepted
- Date: 2026-07-26

## Context

A Claude Skill only enters context when its `description` is matched against
the current task. Most requests in a real session are trivial and, per the
Proportionality guardrail (RFC-0001), should cost near-zero ceremony. Two
places exist to enforce that: filter at the trigger (narrow description, most
requests never load the skill), or filter inside the skill body after a
broad trigger (most requests load a few lines, then exit immediately).

## Decision

Filter inside the body. The `description` matches broadly on "an engineering
decision is about to be made"; the first move once triggered is a cheap
check that lets genuinely trivial requests exit without engaging the rest of
the procedure.

## Alternatives Considered

- **Narrow description, filter at the trigger.** Would keep the skill out of
  context entirely on most turns, which is the more efficient outcome when
  it works. Rejected because the input available to a trigger match — a
  short summary of the request — is exactly the surface-level signal
  RFC-0001 already identified as unreliable for judging blast radius. A
  narrow trigger asks the cheapest, least-informed point in the pipeline to
  make the call that most needs context to make correctly. The failure mode
  is silent and asymmetric: a missed trigger on a consequential request that
  looked trivial produces no error, just a skipped decision, whereas a false
  trigger on a genuinely trivial request costs a few wasted lines and is
  caught by the fast exit either way.

## Consequences

Makes easier: coverage. The skill sees every engineering request at least
once, so "it looked trivial but wasn't" can't slip past a mismatched
one-line description. Makes harder: `SKILL.md`'s opening section now has a
hard latency/token requirement — the fast-exit check has to be cheaper than
the tool call it precedes, on every trivial request, which is most requests.
If RFC-0003 can't deliver a fast-exit that actually is cheap, this decision
should be revisited rather than shipped with a slow "fast" exit, since a slow
fast-exit is strictly worse than a narrow trigger that skips the cost
entirely.
