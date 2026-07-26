# RFC-0006: SKILL.md v1 — Dry Run Notes

- Status: Accepted (record of a completed check, not a proposal)
- Date: 2026-07-26
- Scope: manual walkthrough of `eval/corpus/*` against the first `SKILL.md`
  draft, done by reading the draft's rules and reasoning through each
  scenario by hand — not an automated run, not RFC-0004 Layer 1/2
  evaluation. See `eval/README.md` for why that distinction matters.

## Result

10/10 trigger corpus entries and 8/8 Gate/tier corpus entries reasoned to
their expected label against the draft as fixed below. Two real gaps were
found and fixed in the draft itself; one soft ambiguity was found and
deliberately left open rather than patched on the strength of a manual
walkthrough alone.

## Fixed

**Dependency-update wording gap (`trg-09`, lodash patch bump).** The
original description text said "adding a dependency," which doesn't
cleanly cover updating an existing one's version — a genuinely ambiguous
match. Changed to "adding or updating a dependency."

**Gate answered from phrasing instead of investigation (`gt-04`, the
`ENABLE_LEGACY_AUTH` flag flip; also relevant to `gt-05`/`gt-07`).** The
original Gate text asked the three questions without instructing that they
be answered by looking at what the change actually touches. A one-line
request naming only `config.js` could get Q1 answered "no" reflexively,
missing that the flag gates a production auth path — which is exactly the
disguised-Critical case `gt-04` exists to catch, and exactly the failure
ADR-0003's whole argument depends on not happening. Added: "Answer by
looking at what the change actually touches, not by trusting the request's
phrasing — a one-line request can still touch more than it names."

## Deliberately not fixed

**`gt-07` (validation added to the public `signup` endpoint) turns on a
subtle reading of Q2.** "More than one consumer" is meant to ask whether
the interface's *contract* changes for callers, not whether the endpoint
has real traffic — a public endpoint with many users but an unchanged,
backward-compatible contract should stay low-tier, and `gt-07` is written
to test exactly that distinction. The current wording ("another caller,
another service, another person who reads this as an interface rather than
an implementation detail") is aimed at that distinction but isn't airtight
against a reading that fixates on "public-facing" instead. This was left
unpatched rather than reworded speculatively, on purpose: RFC-0004 already
named the risk of over-trusting a single author's own reasoning as a stand-
in for real evaluation, and a manual walkthrough by the same author who
wrote the rule is the weakest possible evidence that a wording tweak would
actually help rather than just move the ambiguity somewhere else. This is
flagged as a specific thing to watch once a real runner (RFC-0005) exists,
not treated as resolved.

## What this dry run is not evidence of

Not trigger precision/recall in the RFC-0004 sense (no real model calls
were made against unseen requests), not Gate accuracy under real
adversarial pressure (the same author wrote both the rules and the test
cases, which is exactly the fit-to-the-suite risk RFC-0004's holdout
guardrail exists to catch), and not any signal at all about Layers 3/4
(decision-quality, felt outcome). It is a bug-catching pass on the prompt
text before spending real evaluation budget on it, nothing more.
