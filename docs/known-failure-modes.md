# Known failure modes

A scannable catalog of judgment regressions this project has actually
found and fixed, as distinct from the corpus entries that target them.
`eval/corpus/gate_tier.yaml`'s `note` field on each adversarial case
explains *what the case is designed to catch*; this file records *what
has actually happened* when real models were asked to classify it —
dates, models, sample counts, outcome. Read this before assuming a case
is "just another adversarial scenario" — two of them have a real history
of fooling real models, which is a different (and stronger) kind of
evidence than "this seems like it could be tricky."

Governance note (from `eval/README.md`): a regression here is fixed by
changing `SKILL.md` or a reference file, never by editing the corpus to
match new behavior. This file exists to make that discipline easier to
apply consistently, not to replace it.

## `gt-07` — public-facing surfaces wrongly reading as automatically Critical

**Case**: "Add input validation to the public signup form endpoint to
reject emails without an @ symbol." Expected tier: 1 (additive,
safety-improving, trivially reversible — "public-facing" alone isn't a
Gate "yes").

**History**:
- First found in `docs/rfcs/0008-first-independent-evaluation.md`: an
  independent fresh-model run misclassified a case in this shape as
  Tier 3, purely on "public-facing" association. Fixed by adding the
  explicit carve-out now in `SKILL.md`'s Gate section ("a change that
  only makes existing behavior stricter or safer... is usually a no even
  on a public or security-adjacent surface").
- `docs/rfcs/0009-ollama-cloud-corpus-run.md`: after that fix, `gt-07` had
  disagreed with its label on 3 separate independent passes across two
  models. The RFC-0008 fix measurably helped (moved the wrong answer from
  Tier 3 to Tier 2) but didn't fully close it.
- `docs/rfcs/0010-repeat-sampling-and-regression.md`: repeat sampling
  turned the disagreement into a confirmed 3/3 on Ollama, then a
  follow-up wording pass looked stable — 2/2 clean on re-check.
- **A second, distinct failure mode**, found via a fresh two-sample
  Agent-tool evaluation of the full trigger + gate_tier corpus (not tied
  to a numbered RFC): both independent Claude samples landed on Tier 2,
  not Tier 1, with matching reasoning — "a public endpoint has multiple
  callers (Q2 yes), but stricter validation with no required caller
  changes is a no on Q3." This is not the original Q3-based bug (both
  samples correctly avoided that one); it's Q2's "consumer" wording
  reading "many end users hit this" as equivalent to "another piece of
  code depends on this as an interface." Fixed by adding a parallel
  carve-out to Q2 in `SKILL.md` ("a public or heavily-used surface isn't
  automatically a yes to Q2... Logic that only the one handler which owns
  it ever calls stays a no even when that handler itself is
  public-facing"), propagated to `AGENTS.md` and every adapter. Re-verified
  with two more fresh samples after the fix: both now read Tier 1 for
  `gt-07`, citing the new Q2 language directly, and a paired check against
  `gt-02`/`gt-06` (which need Q2 "yes" for real reasons — explicit stated
  reuse, two explicit callers) confirmed the tightened wording didn't
  overcorrect those into Tier 1.

**Status**: the Q3-based failure mode is stable (per RFC-0010's re-check);
the Q2-based failure mode found this session is fixed and now confirmed
3/3 on fresh Claude samples, meeting RFC-0004's N≥3 standard — the third
sample (added specifically to close this out, not incidentally) again
landed Tier 1 citing the Q2 carve-out directly. The companion
non-regression check on `gt-02`/`gt-06` remains at 2/2, not yet pushed to
N≥3 itself, but those weren't newly-fixed cases, just a check that the
fix didn't break something already working.

## `gt-03` — the RFC-0008 fix's own wording getting misapplied

**Case**: "Add a required tenantId parameter to the public createUser
API, used at 12 call sites." Expected tier: 3 (this project's own
canonical breaking-change example, RFC-0003).

**History**:
- `docs/rfcs/0010-repeat-sampling-and-regression.md`: cross-checking
  against Claude found the RFC-0008 fix's own language ("additive... is
  usually a no") was being misapplied to justify *not* escalating this
  case — a required parameter is textually "additive" (nothing removed)
  but breaks every existing caller. Fixed by naming the actual test
  ("does an existing caller have to change anything") instead of leaning
  on the word "additive." 5 total samples across two wordings wasn't
  enough to call it stable, and one sample was internally
  self-contradictory.
- `docs/rfcs/0011-gt03-resolution.md`: 10/10 fresh Claude samples,
  unanimous Tier 3, clean reasoning, several samples quoting the fix's
  own corrected language back.
- One additional fresh sample this session (unprompted by any new
  wording change — just an incidental re-check while confirming `gt-07`
  above): 11/11, still unanimous Tier 3.

**Status**: resolved and confirmed at the N≥3 standard, on Claude,
specifically. The strongest-evidence case in the corpus.

## Resolved methodology bug: `gt-01`/`gt-05` assumed they already triggered

Found by a two-sample evaluation that asked both the trigger question and
the tier question for every `gate_tier.yaml` entry (the same combined
prompt `eval/run.py`'s `classify_tier()` used at the time) — which the
corpus itself doesn't intend, per RFC-0005: `gate_tier.yaml` is Layer 2,
"given it fired, what tier," with no `expected_trigger` field at all.
Asked cold, both fresh samples said `gt-01` ("Add *.log to .gitignore")
and `gt-05` (a fully-specified single-file rename) wouldn't trigger at
all — a defensible reading given `trigger.yaml`'s own execution-only skip
cases (`trg-03`, `trg-05`) look the same shape — which left no `TIER` line
to parse and surfaced as a bare `ValueError`, not a tier judgment.

This was a real bug in `eval/run.py`, not just a corpus-design footnote:
`classify_tier()` shared one prompt with `should_trigger()` that asked
about triggering regardless of which one was being tested, so any
gate_tier scenario a model reasonably read as "wouldn't trigger" could
turn into a spurious failure with no tier signal at all. Fixed by giving
`classify_tier()` its own prompt (`_GATE_TIER_ONLY_PROMPT`) that tells the
model to assume the skill is already active and asks only for the tier —
removing the confound instead of coercing an answer to a question this
corpus was never designed to ask. Re-verified with two fresh samples using
the new prompt: both `gt-01` and `gt-05` now cleanly resolve to Tier 1,
matching their labels, with no trigger-related noise at all.

## Investigated and closed: `trg-04` was ambiguity, not a keyword-association bug

`trg-04` is a `trigger.yaml`-only case (no `expected_tier` — it was never
claiming a tier label), but an earlier two-sample tier probe on it
disagreed with itself: one sample said Tier 2, the other Tier 3, on
"Refactor the payment retry logic to use exponential backoff instead of
fixed delay." That looked like the same shape as the already-fixed
"public" association bug — a trust-boundary word (`payment`) pulling
escalation by proximity rather than actual exposure — so it was worth
checking rather than assuming.

Follow-up with two more samples, holding the request's ambiguity fixed
instead of leaving it open: given the *exact same request* but with the
blast radius made explicit (no signature change, the actual
payment-submission call is unchanged, only the retry-delay math moves),
both samples cleanly agreed on Tier 1, explicitly reasoning that Q3 is no
because "this is code merely adjacent to payment logic, not a change to
the trust boundary itself." That's the opposite of a keyword-association
bug — it shows the Gate correctly separates "near payment" from "crosses
the payment boundary" once given enough information to do so.

**Conclusion**: the original disagreement traces to the request itself
being genuinely underspecified (does the refactor touch the payment call
or not? the one-line request doesn't say), not to the Gate over-weighting
the word "payment." Splitting under real ambiguity is arguably
ADR-0006's escalate-on-uncertainty rule working as intended, not a defect
to fix. No `SKILL.md` change made. If `trg-04` is ever promoted into
`gate_tier.yaml` with a real `expected_tier`, its `context` field should
state the blast radius explicitly, the same way `gt-04`'s already does —
an ambiguous one-liner isn't a fair tier-accuracy test either way.

## What this catalog is not

Not a claim that these are the only two fragile cases — they're the only
two that have actually been stress-tested enough times to know. The other
adversarial cases (`gt-04`, `gt-05`, `gt-08`, and the full `trigger.yaml`
corpus) have real reasoning behind why they might be hard, but have only
been sampled once or twice each, mostly against Ollama's confirmed-noisy
backend (`docs/rfcs/0009` addendum: 9/10 trigger, 2/8 clean gate_tier at
N=3, with `gt-02`/`gt-05`/`gt-08` disagreements deliberately not chased
further since they don't show the repeatable, cross-model pattern that
made `gt-03`/`gt-07` worth fixing). Absence from this file means
"not enough evidence yet," not "confirmed fine."
