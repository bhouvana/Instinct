# ADR-0011: Adopt root-cause-fix and verification-check as core rules, informed by Ponytail's actual instruction text

- Status: Accepted
- Date: 2026-07-26

## Context

Earlier research on Ponytail (informing RFC-0001 through RFC-0006) worked
from its README and `AGENTS.md` at summary level. A closer read of its
actual canonical instruction file (`.github/copilot-instructions.md`) and
its `.cursor/rules/ponytail.mdc` surfaced two concrete rules with no
equivalent anywhere in Instinct:

1. **Root cause over symptom.** "A report names a symptom... grep every
   caller of the function you touch and fix the shared function once."
   Nothing in `SKILL.md` addressed bug fixes specifically, and this is a
   real, common request shape the Gate/tier system doesn't otherwise call
   out.
2. **A verification requirement tied to non-trivial changes.** "Non-trivial
   logic leaves ONE runnable check behind... Trivial one-liners need no
   test." Instinct's mechanism (RFC-0003) governs whether and how a
   decision gets made, but says nothing about leaving evidence that the
   resulting code actually works — a real gap given RFC-0001's own
   evidence-based-reasoning stance.

## Decision

Add both to `SKILL.md`: a "Bug fixes" section stating the root-cause rule,
and a "Verification" section requiring one runnable check on Consequential
and Critical changes (Trivial changes are exempt, matching the Gate's own
proportionality logic rather than inventing a separate threshold). Add a
narrower, Instinct-specific `instinct:` marker convention to
`references/provenance-out.md` for Critical-tier changes that knowingly
accept a scoped limitation — adapted from Ponytail's `ponytail:` comment
convention, not copied verbatim (Ponytail's marks a corner deliberately
cut for size; Instinct's marks a tradeoff accepted at Critical tier
specifically, consistent with Instinct governing decisions rather than
diff size).

## Alternatives Considered

- **Leave both as future scope, revisit after real evaluation exists.**
  Rejected — unlike the multi-platform question (ADR-0012), neither rule
  requires new infrastructure, contradicts an existing ADR, or expands the
  project's platform surface. They're additions to the same file, in the
  same register the style law already established, filling a gap that
  became visible by reading real prior-art text instead of a summary of
  it. Deferring a cheap, in-scope, immediately-integrable fix for no
  reason other than "it wasn't already planned" would be its own small
  failure of the project's own Efficiency pillar.
- **Copy Ponytail's `ponytail:` marker convention verbatim as `instinct:`
  with the same scope (any deliberately-cut corner).** Rejected — that
  scope is defined in terms of diff-size/complexity corners, which is
  Ponytail's domain (RFC-0001's non-goals explicitly excludes Instinct
  from being a code-size minimizer). Narrowed to Critical-tier tradeoffs
  specifically so the marker means something derived from Instinct's own
  mechanism, not an import that doesn't quite fit.

## Consequences

Makes easier: `SKILL.md` now covers two common, concrete request shapes
(bug fixes, anything non-trivial enough to need proof it works) that the
Gate/tier system alone didn't address, closing gaps a real user would hit
quickly. Makes harder: `SKILL.md` is now longer than the v1 draft audited
in RFC-0006 — the corpus and dry-run notes there predate these additions
and should be re-checked (informally, until the real runner exists) rather
than assumed to still hold unchanged.
