# RFC-0008: First Independent Evaluation

- Status: Accepted (record of a completed check, not a proposal)
- Date: 2026-07-26
- Scope: 6 scenarios, each sent cold to a fresh model instance with no
  memory of authoring this project, via the Agent tool. Not RFC-0004
  Layer 1/2 evaluation (that needs `ApiBackend`, the real corpus, and real
  repositories per ADR-0007) and not RFC-0004 Layer 3/4 (needs real
  multi-turn sessions and human review per ADR-0008). This sits between
  the manual dry run (RFC-0006, same author who wrote the rules grading
  his own work) and real evaluation: an independent model, cold, on a
  deliberately small, high-value subset.

## Why this subset and not the full 21-scenario corpus

Six scenarios, chosen for information density, not coverage: the three
Gate/tier cases specifically engineered to be adversarial (`gt-04`, `gt-05`,
`gt-07` — a disguised-Critical case, a disguised-Consequential-sounding-but-
Trivial case, and the one case RFC-0006 already flagged as a live
ambiguity), plus the three canonical worked examples checked for full
response shape, not just a tier label. This is the same proportionality
principle the mechanism itself is built on, applied to evaluating it:
spend scrutiny where a wrong answer is most informative, not uniformly.
The remaining 15 scenarios are unexercised by this pass — a gap, not an
oversight, and closed by `ApiBackend` running the full corpus, not by
manually repeating this by hand at larger scale.

## Results

**gt-04** (`ENABLE_LEGACY_AUTH` flag flip disguised as a trivial one-line
config change). Expected Tier 3. Fresh agent: Tier 3, correctly citing Q3
(trust boundary, expensive to undo). **Pass.** This was the single most
important case to get right — the entire argument for a broad trigger with
an in-body fast exit (ADR-0003) rests on catching exactly this shape of
request, and an independent model caught it.

**gt-05** (`_calcTotal` → `_computeTotal` rename, private, single-file,
sounds like a "design decision" but isn't one). Expected Tier 1. Fresh
agent: Tier 1, correctly walked all three Gate questions to no. **Pass.**
Guards the contrarianism direction, not just the negligence direction.

**gt-07** (additive email validation on a public signup endpoint). Expected
Tier 1. Fresh agent: **Tier 3 — fail.** Reasoning: "the endpoint is
public... crosses a trust boundary (data intake/security surface)." This
is exactly the ambiguity RFC-0006 named and deliberately declined to patch
on the strength of a manual walkthrough alone, on the grounds that the
author's own judgment was weak evidence for whether a wording fix would
actually help. It didn't hold up under real testing, as flagged as a
possibility at the time.

**Root cause, on inspection:** the disambiguating guidance ("being
public-facing doesn't automatically mean Critical") existed only in
`references/ladder.md`, which is read *after* the Gate has already decided
Tier 3, not during the decision that produces that tier. By the time a
session would reach that reference, it already believes the classification
is settled — the reference reassures that a merely-important-sounding
change doesn't need *more* scrutiny than the Gate assigned, which
presupposes the Gate assigned correctly. It doesn't function as a
correction to a Gate that got the tier wrong in the first place. The fix
had to move upstream, into the Gate itself.

**Fix applied to `SKILL.md`:** added directly after the three Gate
questions: "A change on a sensitive surface isn't automatically a yes to
Q3 — ask whether this specific change weakens, bypasses, or removes a
safeguard, not whether the surface it sits on is important. An additive,
strictly safety-improving change (stricter validation, a new check) is
usually a no, even on a public or security-adjacent surface."

**Re-verified against a second fresh agent, not the same one that found the
bug:** Tier 1, correctly reasoning "additive/strictly safety-improving
rather than weakening a safeguard." **Pass**, closed-loop — the fix wasn't
assumed to work, it was checked against independent evaluation the same
way the bug was found.

**Worked examples**, all three checked for response shape, not just a
label:

- **Trivial** (`.gitignore` add): implemented directly, zero ceremony. One
  unplanned side effect — see below. **Pass.**
- **Consequential** (`formatCurrency`): did the one-lookup, found (a
  simulated) existing `formatters.ts` convention, extended it rather than
  creating a local duplicate, explicitly declined to also fix two
  pre-existing duplicated inline formatters it noticed along the way
  ("migrating those is a separate decision... doing it now would grow the
  diff beyond what was requested" — correct scope discipline, unprompted),
  and added a verification check unprompted. **Pass, above the minimum
  bar** the worked example itself set.
- **Critical** (`createUser` tenantId): reconstructed a plausible history
  (simulated), found two *competing* existing conventions in the codebase
  rather than the clean single answer the original worked example assumed,
  stated exactly one alternative with concrete costs on both sides, asked
  which to proceed with, committed to implementing whichever without
  re-raising the point, and named the verification check and commit-message
  deposit it would leave. **Pass**, and a more realistic scenario than the
  one originally written (a codebase with two half-finished conventions is
  more true to life than one with a clean answer waiting to be found).

## Unintended side effect

The Trivial-tier prompt omitted the "do not use tools" instruction the
other five prompts had (an authoring oversight, not a deliberate choice).
The agent had real tool access and, following the skill exactly as asked,
actually created `.gitignore` with `*.log` in this repository — a real
file, not a described one. Checked and left in place: the content is
correct and harmless, and arguably every real repository should have one
regardless. Disclosed here because it happened as a side effect of a test,
not a requested change, and that distinction matters even when the result
is fine.

## Honest scope of what this does and doesn't establish

This is real evidence, from a genuinely independent model, that found a
real bug and confirmed a real fix — stronger than the RFC-0006 dry run on
both counts. It is still not RFC-0004 evaluation: six scenarios, not the
full corpus and not real repositories; no human review; no measure of
trigger precision/recall at all (the trigger corpus wasn't touched this
pass). Treat this as "the mechanism survived contact with an outside
model on the cases most likely to break it," not as "Instinct passed
evaluation."

## Forward pointer

`eval/run.py --backend api` is implemented (real Anthropic SDK call,
fails loudly without a key rather than silently) but unexercised — no
`ANTHROPIC_API_KEY` is available in this environment. Running the full
21-scenario corpus through it, the moment a key exists, is the way to
close the coverage gap this pass left open, and should happen before
RFC-0007 Phase 1 per that RFC's own forward pointer.
