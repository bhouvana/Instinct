# ADR-0009: The test corpus is authored and locked before the first SKILL.md draft exists

- Status: Accepted
- Date: 2026-07-26

## Context

RFC-0005's suite needs to come from somewhere. The natural, path-of-least-
resistance order is: write a first draft of `SKILL.md`, see how it behaves,
then write scenarios that capture that behavior as the expected baseline.
The alternative is to write the scenario corpus first, from RFC-0003's
worked examples and its own reasoning alone, before any implementation
exists to look at.

## Decision

The scenario corpus (trigger set, Gate/tier set, worked-example smoke test)
is authored and locked as its own artifact before the first `SKILL.md`
draft is written. The first draft is then checked against a bar that
existed independently of it.

## Alternatives Considered

- **Write the corpus by observing the first implementation's actual
  behavior.** Faster to produce, and guarantees the suite starts green.
  Rejected because that's precisely the property that makes it worthless as
  a check: a corpus derived from watching the implementation can only ever
  encode what the implementation already does, including its mistakes. If
  the first draft's Gate silently conflates Tier 2 and Tier 3 on some class
  of request, a corpus written after the fact would learn to expect that
  conflation rather than catch it. This is the same failure this ADR's
  sibling in RFC-0005 already names for the "loosen a failing test" case,
  just occurring at authoring time instead of at fix time — writing the
  corpus after the implementation is the same mistake made earlier, not a
  different one.

## Consequences

Makes easier: the first `SKILL.md` draft has an honest, independent pass/fail
signal from the moment it exists, instead of a suite that can only detect
drift from itself. Makes harder: corpus authoring now has to happen from
RFC-0003's reasoning alone, with no real model behavior to sanity-check
scenario difficulty against — some scenarios in the first version of the
corpus will likely be miscalibrated (too easy, ambiguously labeled, or
testing something that turns out not to be the right boundary), and that's
an accepted cost, correctable through the same governance RFC-0005 already
sets (add and relabel with stated reasons), not a reason to have skipped
writing it first.
