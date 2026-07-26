# ADR-0004: Ship one ambient skill for v1; defer an explicit-command family

- Status: Accepted
- Date: 2026-07-26

## Context

Ponytail ships a passive core plus five explicit, user-invoked commands
(review, audit, debt, gain, help). Instinct could follow the same pattern —
e.g. an on-demand command to surface the provenance of a file, or to run a
retrospective judgment pass over a diff before it ships.

## Decision

v1 ships exactly one skill: the ambient core described in RFC-0002. No
explicit sub-commands.

## Alternatives Considered

- **Ship a command family alongside the ambient core, matching Ponytail's
  structure.** Rejected for v1, not permanently. This project's central and
  untested bet is that ambient, invisible behavior change is possible and is
  the actual product (RFC-0001's success criterion is explicitly that
  developers feel a shift, not that they gain a new command to run). Explicit
  commands are a different, separable bet — they're useful regardless of
  whether the ambient mechanism works, which is exactly why building them
  first would tell us nothing about whether the harder, riskier bet paid
  off. Building them now would also be scope growth ahead of any evidence
  the core mechanism works, which is the failure mode RFC-0001's Efficiency
  pillar exists to catch — applied here to this project's own roadmap
  instead of to a codebase.

## Consequences

Makes easier: RFC-0003 and the evaluation harness (RFC-0004) both get a
single, unambiguous surface to design and measure against, instead of
splitting effort across a core mechanism and a set of commands that have
never been requested. Makes harder: no explicit escape hatch exists yet for
a user who wants to force a provenance/judgment pass on demand outside the
ambient trigger. That's an accepted gap for v1, not an oversight — if
real usage shows the ambient trigger under- or over-fires often enough that
users want manual control, that's evidence for revisiting this ADR, not a
reason to have built the family speculatively now.
