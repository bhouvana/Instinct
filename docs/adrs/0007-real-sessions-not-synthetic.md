# ADR-0007: Evaluate on real agentic sessions against real repositories, not synthetic single-shot prompts

- Status: Accepted
- Date: 2026-07-26

## Context

The cheapest way to build an evaluation set is to write synthetic prompts
("implement X") against small scaffolded fixture repos built to exercise a
specific rule. RFC-0004 needs to decide whether that's an adequate
substrate for measuring whether Instinct actually improves decisions, or
whether it only measures whether Instinct follows instructions in a
vacuum.

## Decision

The primary evaluation substrate is multi-turn agentic sessions against
real repositories with genuine, unmodified commit history — not
single-shot generation, not fixtures built to order.

## Alternatives Considered

- **Synthetic single-shot prompts against scaffolded fixtures.** Cheaper,
  faster, fully reproducible, easy to scale up in volume. Rejected as the
  *primary* substrate (it remains fine for the cheap Layer 1/2 checks in
  RFC-0005, which test classification, not decision quality) because two
  of the three pillars this project exists for have no real material to
  act on in a scaffolded fixture: Provenance has nothing genuine to
  reconstruct if the "history" was written yesterday to make a point, and
  Judgment has no real neighboring abstraction to notice or miss if the
  fixture was built minimally around the one scenario it's testing. A
  benchmark built this way would only ever be able to detect whether
  Instinct implements correctly, which was never the identified gap
  (RFC-0001's problem statement is explicit that implementation is not
  where current assistants fail).
- **Wholly automated, no real session cost.** Rejected for the same reason
  — real sessions cost real time and compute, but the alternative is
  measuring something adjacent to the actual claim instead of the claim.

## Consequences

Makes easier: results that actually speak to RFC-0001's problem statement,
and a benchmark methodology consistent with the one piece of prior art this
project already leaned on (Ponytail's own published methodology explicitly
uses real agentic sessions on real repos rather than isolated generations,
specifically to avoid metrics inflation — this project adopts the same
discipline rather than a cheaper one). Makes harder: Layer 3/4 evaluation
(RFC-0004) is expensive and slow by construction, which is exactly why
RFC-0004 gates it to release cadence rather than per-edit, and why RFC-0005
exists at all — to give day-to-day prompt iteration a fast, cheap loop that
doesn't require this substrate for every change.
