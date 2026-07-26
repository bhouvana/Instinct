# ADR-0002: Adopt a Tier-1 operational maxim distinct from the Tier-0 identity statement

- Status: Accepted
- Date: 2026-07-26

## Context

The locked philosophy (RFC-0001, Tier 0) is "Engineering is not writing
code. Engineering is making good decisions." That sentence is correct and
does real work reframing Claude's self-concept, but it does not, on its own,
specify what changes at the moment a tool call is about to happen. Ponytail's
comparable maxim, "the best code is the code never written," has that
property directly: it compiles into a check ("did I just add something that
didn't need to exist?"). A philosophy that only changes self-concept and
never changes the next concrete action is closer to a mission statement than
to the mechanism this project needs.

The gap is specifically in Provenance, because it is the pillar most likely
to be silently skipped under time pressure — Judgment and Efficiency both
have a natural moment they trigger at (evaluating a request, sizing a diff),
but "understand why this code exists" has no equivalent forcing function
without one.

## Decision

Adopt a second, narrower sentence, positioned one level below the identity
statement, whose job is to fire at the moment before a tool call rather than
to state a worldview:

> Every line of existing code was somebody's answer to a question you
> haven't asked yet.

This converts Provenance from a virtue to a reflex: before judging or
changing code, name the question it answered. If it can't be reconstructed,
that absence is itself a finding to surface, not a license to proceed as if
the code were text with no history.

## Alternatives Considered

- **No Tier-1 maxim; rely on Tier 0 plus the mechanism section alone.**
  Simpler, one fewer sentence to maintain consistency with across the
  project. Rejected because it leaves exactly the actionability gap
  described above — without a sentence engineered to compile into a
  check, the mechanism has to be entirely carried by prose instructions in
  the eventual `SKILL.md`, which is a weaker and more bloat-prone design
  than pairing philosophy with maxim the way the strongest prior art does.
- **A maxim targeting Judgment or Efficiency instead of Provenance.**
  Considered, since all three pillars could use a compiled trigger.
  Rejected for *this* ADR specifically because Provenance is the pillar with
  no natural forcing function elsewhere in the flow (Judgment is triggered
  by the act of receiving a request; Efficiency is triggered by the act of
  sizing a diff). Judgment and Efficiency may still get their own compiled
  triggers in RFC-0003, but that is a mechanism-design question, not a
  philosophy-tier one, and doesn't block this decision.

## Consequences

Makes easier: RFC-0002 (prompt architecture) has a concrete sentence to
build the provenance-seeking behavior around, rather than having to invent
one under a documentation deadline. Makes harder: two "core" sentences
(Tier 0 and Tier 1) instead of one raises the risk of the project's identity
becoming fuzzy if a third gets added later without discipline — future ADRs
proposing additional maxims should have to argue why Tier 0 plus this one
Tier-1 sentence is insufficient, not default to appending.
