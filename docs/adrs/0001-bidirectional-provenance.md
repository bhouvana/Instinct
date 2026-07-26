# ADR-0001: Provenance is bidirectional (consume and deposit)

- Status: Accepted
- Date: 2026-07-26

## Context

RFC-0001 defines Provenance as one of three mechanisms good decisions require:
understanding why existing code exists before changing it. The obvious,
minimal reading of that is one-directional — Claude reads history, forms an
understanding, and uses it to inform the current change.

The problem with stopping there: Claude's understanding of "why" is
per-session and evaporates when the conversation ends. A human Staff
Engineer's judgment compounds over a career because it gets externalized —
into commit messages, ADRs, code review comments, team lore. Nothing in a
one-directional reading of Provenance produces that externalization. Every
future Claude session (or future engineer) that touches the same code pays
the full cost of reconstructing the same "why" from scratch. The mechanism
would improve the quality of any single decision without ever compounding
across decisions, which undercuts the project's own success criterion in
RFC-0001 (this should feel like judgment, not like a smarter one-off answer).

Prior art offers a narrow precedent: Ponytail's `ponytail:` inline comments,
which mark a deliberate simplification and name its trade-off at the moment
it's made. That is deposit-side provenance, but scoped only to "I chose the
smaller option, here's what I gave up" — it doesn't generalize to "here is
why this exists" for provenance discovered while reading, only provenance
created while writing.

## Decision

Provenance is defined as bidirectional: Instinct consumes the reasoning
behind existing decisions *and* deposits reasoning for decisions it makes,
at a cost proportional to blast radius (per the Proportionality guardrail in
RFC-0001). Deposit takes the cheapest form that will actually survive: a
commit message that states the why, not just the what; a comment only where
removing it would leave a non-obvious constraint undiscoverable to the next
reader; an explicit note in conversation when neither of those is available.
This is not a new artifact type or a mandate to write documentation files —
it is a bias applied to artifacts Instinct is already producing.

## Alternatives Considered

- **One-directional (consume only).** Simpler, smaller surface area, closer
  to a literal reading of "understand history before touching it." Rejected
  because it caps the project's value at "better single decisions" and
  forecloses the compounding effect that is this project's best argument for
  being more than a smarter prompt.
- **Mandate a dedicated provenance artifact (e.g., always write an ADR for
  non-trivial changes).** More thorough, but violates Efficiency and the
  Proportionality guardrail directly — it would impose fixed ceremony
  regardless of stakes, which RFC-0001 names as a failure mode to design
  against. Rejected in favor of depositing into artifacts that already exist
  (commit messages, targeted comments) rather than inventing new ones.

## Consequences

Makes easier: an engineer (human or another Claude session) six months from
now inherits reasoning instead of just code, at close to zero marginal cost
since it rides on artifacts already being produced. Makes harder: this is
the least mechanically specified part of the philosophy so far — "cost
proportional to blast radius" needs a concrete rule before it's implementable
consistently, which RFC-0003 owns. Risk: if the proportionality rule is
under-specified, this degrades into either noisy over-commenting (violates
the project's own default-to-no-comments engineering norm) or gets skipped
entirely under time pressure, silently reverting to one-directional. RFC-0003
must treat this as a concrete scenario in its worked examples, not an
afterthought.
