# ADR-0005: Two qualitative tiers past the Gate, not a numeric blast-radius score

- Status: Accepted
- Date: 2026-07-26

## Context

RFC-0003 needs some way to decide how much ceremony a request past the Gate
gets. The obvious "rigorous-looking" option is a weighted score — surface
area, reversibility, consumer count, each weighted and summed against a
threshold. RFC-0002's style law already rejected this shape for `SKILL.md`
prose, using the loaded SuperClaude framework's percentage-weighted
persona-activation tables as the concrete negative example. The same
question resurfaces here at the mechanism-design level, not just the prose
level, so it's worth deciding explicitly rather than assuming the earlier
call already covers it.

## Decision

Two tiers, reached by three plain yes/no questions (the Gate), not a score.
Tier 2 (Consequential) if any Gate question is yes and the undo-cost
question specifically is no; Tier 3 (Critical) if the undo-cost question is
yes, full stop.

## Alternatives Considered

- **Numeric weighted score with a threshold.** Rejected for the same reason
  RFC-0002 rejected it in prose form, applied one level deeper: a formula
  like `0.3*surface + 0.4*reversibility + ...` produces a number that looks
  authoritative and is not — the weights are asserted, not measured, and
  asserting them wouldn't survive its own Provenance/Judgment standard
  applied reflexively (where did 0.4 come from? what decision does it
  encode?). A yes/no question is falsifiable by looking at the code; a
  weight is not.
- **More than two tiers (e.g. four or five gradations).** Considered for
  finer control. Rejected because RFC-0003 needs each tier to map to a
  concretely different *action* (Tier 1: nothing, Tier 2: one lookup, Tier
  3: reconstruct + state alternative once). More tiers than there are
  distinct actions just re-fragments Tier 2 into shades that don't change
  what Claude actually does differently, which is complexity with no
  corresponding behavior payoff — the exact thing Efficiency argues against.
- **One tier (binary trivial/non-trivial).** Rejected because it collapses
  "extend a component's props" and "break a public API used at 12 call
  sites" into the same response, and RFC-0001's guardrail against
  contrarianism specifically requires *not* giving every non-trivial request
  full Tier-3 ceremony — a binary split can't express that distinction.

## Consequences

Makes easier: every tiering decision is auditable by re-checking three
concrete questions against the actual request, which is what RFC-0005's
regression suite needs to test against. Makes harder: real requests will
sometimes sit awkwardly between Tier 2 and Tier 3 in a way three yes/no
questions flatten — ADR-0006's escalate-on-uncertainty rule is the release
valve for that, not a fourth tier.
