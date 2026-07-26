# ADR-0010: Merge references/proportionality.md into references/ladder.md

- Status: Accepted
- Date: 2026-07-26

## Context

RFC-0002's structure sketch listed three reference files: `ladder.md` (the
full decision procedure), `proportionality.md` (what determines blast
radius, worked examples), and `provenance-out.md`. Writing the actual files
during implementation, the split didn't hold up: "what determines blast
radius" is the Gate, which lives in `SKILL.md` itself (it has to, per
ADR-0003 — it runs on every Critical/Consequential trigger, not just some),
and "worked examples" apply across all three tiers, not to proportionality
alone. A separate `proportionality.md` would have ended up holding either a
near-duplicate of the Gate already in `SKILL.md`, or a thin file that
existed only to satisfy the original three-file sketch.

## Decision

Two reference files, not three: `references/ladder.md` (full Critical-tier
detail, the two "doesn't automatically mean heavier scrutiny" clarifications,
and all three worked examples) and `references/provenance-out.md` (deposit
mechanics, unchanged from the original sketch).

## Alternatives Considered

- **Keep three files as RFC-0002 sketched them.** Rejected once actually
  writing the content made clear the split would produce either duplication
  between `SKILL.md` and `proportionality.md`, or a file too thin to justify
  a separate `Read`. RFC-0002's own structure section was explicit that
  nothing should go in a reference file that doesn't earn its place, which
  argues against keeping a file that fails that test just to match an
  earlier sketch exactly.

## Consequences

Makes easier: one less file to keep in sync, and the worked examples live
next to the tier definitions they illustrate instead of split across two
files by an artificial boundary. Makes harder: none identified — this is a
same-session correction of a sketch to what the content actually needed,
not a tradeoff. Noted as its own ADR anyway because RFC-0002's file list
was a specific, named decision, and silently diverging from a named
decision without recording why is exactly the kind of undeposited
provenance ADR-0001 exists to prevent — applied here to this project's own
design documents, not to a codebase.
