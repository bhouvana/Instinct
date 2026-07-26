# ADR-0006: Ties and uncertainty escalate; they never resolve toward less scrutiny

- Status: Accepted
- Date: 2026-07-26

## Context

The Gate's three questions (RFC-0003) are written to be answerable by
looking, but real requests won't always give a clean yes or no — "does this
have more than one consumer" can be genuinely unclear without a deeper
search than the Gate is supposed to cost. Some default behavior is needed
for the ambiguous case, and it needs to be decided once, centrally, rather
than left to be improvised differently at the Gate, at Tier 2, and again at
Tier 3.

## Decision

Uncertainty always resolves toward more scrutiny, never less: an unclear
Gate answer counts as yes; an unclear Tier 2/3 boundary counts as Tier 3.
This is the same rule ADR-0003 already used to justify a broad trigger over
a narrow one, applied consistently one layer down instead of invented fresh
here.

## Alternatives Considered

- **Default to less scrutiny on uncertainty (favor speed).** Would keep the
  common case faster and matches a naive reading of "proportionality means
  staying out of the way." Rejected because the cost asymmetry is real and
  already established: a wasted Tier 2 check on something that turns out
  trivial costs a few seconds; a Tier 3 change nodded through as Tier 2
  because a consumer count was unclear is exactly the failure mode RFC-0001
  opens with. Optimizing the ambiguous middle for speed trades a small,
  bounded cost for an unbounded one.
- **Ask the user to resolve ambiguity before proceeding.** Considered for
  the Tier 2/3 boundary specifically. Rejected as a default because it
  reintroduces the ceremony-on-every-request cost this whole mechanism
  exists to avoid — RFC-0001's guardrail is that judgment shouldn't read as
  friction, and stopping to ask "is this Tier 2 or 3?" on an ambiguous case
  is friction with no corresponding decision-quality gain, since escalating
  silently to Tier 3 already produces the more careful behavior without
  needing the user to referee it.

## Consequences

Makes easier: one rule, applied at every layer of the mechanism (trigger,
Gate, tiering), instead of three independent judgment calls that could drift
out of consistency with each other over time. Makes harder: this
deliberately biases the whole mechanism toward over-scrutiny under
uncertainty, which means RFC-0004's ceremony-cost metric (measuring
low-stakes requests against a no-skill baseline) has to watch specifically
for uncertainty being triggered too easily and inflating Tier 2/3 rates on
requests that are actually fine at Tier 1 — this rule is only justified if
the Gate's questions are precise enough that "uncertain" stays rare, not a
license to make the questions vague and let this ADR paper over it.
