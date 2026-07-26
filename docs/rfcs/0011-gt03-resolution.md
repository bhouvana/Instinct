# RFC-0011: gt-03 Resolution (Properly Powered Re-Test)

- Status: Accepted (record of a completed check, not a proposal)
- Date: 2026-07-26
- Scope: 10 independent, fresh Claude samples (via the Agent tool — still no
  Anthropic API key) on `gt-03` against the current `SKILL.md`, following
  RFC-0010's amendment to RFC-0004 requiring N≥3 for any reported result.
  This is the first evaluation pass in the project run at the standard it
  itself just set, rather than at whatever sample count was convenient.

## Result

**10/10 — Tier 3, unanimous.** Every sample cited Q3 as the deciding
question; several quoted the fix's own language ("regardless of how
additive it sounds") directly in their reasoning. No self-contradictory
responses this round, unlike one sample in RFC-0010's smaller check.

## Reading this against RFC-0010's open question

RFC-0010 left `gt-03` genuinely unresolved on 5 total samples across two
wordings, one of which was internally inconsistent (reasoning argued Q3-yes,
label said Tier 1). 10/10 clean agreement here is a materially different
strength of evidence, not just a bigger version of the same weak signal —
it's the kind of result the amended RFC-0004 was written to require before
anyone gets to call something resolved. On the evidence available:

- **The second fix (RFC-0010) worked.** The `gt-03` regression that fix was
  meant to address is closed, on Claude, with high confidence.
- **This does not re-litigate Ollama's `gt-03` miss** (`docs/rfcs/0009`,
  `0010`). That backend's issue was substantially about its own reliability
  (high parse-error rate, self-disagreement on identical calls), not
  necessarily the same failure this fix addressed. No claim is made here
  about Ollama's current behavior on `gt-03` — that would need its own
  properly-powered re-test, not an inference from Claude's result.
- **This is still one scenario, on one model, via one evaluation path**
  (Agent-tool spot checks, not `ApiBackend`'s automated corpus run). It
  closes the specific open question RFC-0010 left hanging; it does not
  stand in for a full corpus pass at N≥3 across every scenario, which
  remains undone.

## What this closes, and what it doesn't

Closes: the specific "is `gt-03` actually fixed" question, with real
confidence for the first time in this project's evaluation history.

Does not close: RFC-0004 Layer 1/2 coverage generally (only `gt-03`,
`gt-07`, and the earlier RFC-0008 cases have been properly sampled; the
rest of the 21-scenario corpus has only ever seen N=1); RFC-0004 Layers
3/4 (real sessions, real repos, human review — not attempted); or RFC-0007
Phase 1's gate, which per its own Forward Plan was waiting on a trustworthy
evaluation pass in general, not on this one scenario specifically.
