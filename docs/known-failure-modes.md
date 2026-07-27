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
the Q2-based failure mode found this session is fixed and confirmed 2/2 on
fresh Claude samples, with a companion 2/2 non-regression check on the
adjacent legitimately-Tier-2 cases. Neither confirmed at RFC-0004's full
N≥3 standard yet (2 samples each, not 3) — the next real pass should push
both to N≥3.

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

**Status**: resolved and confirmed at the N≥3 standard, on Claude,
specifically. The strongest-evidence case in the corpus.

## Methodology gap, not a Gate bug: `gt-01`/`gt-05` assume they already triggered

The same two-sample evaluation that found the `gt-07` Q2 issue asked both
the trigger question and the tier question for every `gate_tier.yaml`
entry, which the corpus itself doesn't do — `gate_tier.yaml` has no
`expected_trigger` field; it assumes each scenario already triggered and
only grades the tier. Asked cold, both fresh samples said `gt-01` ("Add
*.log to .gitignore") and `gt-05` (a fully-specified single-file rename)
wouldn't trigger at all, which is a defensible reading given `trigger.yaml`'s
own execution-only skip cases (`trg-03`, `trg-05`) look the same shape.
Not a Gate defect — the Gate was never actually asked to classify these
under `eval/run.py`'s real methodology, since `classify_tier()` doesn't
call `should_trigger()` first. Worth a decision at some point: either add
`expected_trigger` to every `gate_tier.yaml` entry, or accept that these
two are informative but ungraded until it does.

## Watching, not confirmed: `trg-04` and payment-adjacent code

Not in `gate_tier.yaml` (no `expected_tier` to grade against), but the
same two-sample run disagreed with itself on "Refactor the payment retry
logic to use exponential backoff instead of fixed delay" — one sample said
Tier 2, the other Tier 3, over whether touching code adjacent to payment
without changing its interface "crosses" the trust boundary Q3 names
explicitly (`auth, payment, deletion, data access`). N=1 disagreement is
noise until it repeats, per this file's own governance, but it's the same
shape as the already-fixed "public" association bug — a named trust-
boundary word possibly pulling escalation by proximity rather than actual
exposure. Not chased further now; sample this one again before touching
anything.

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
