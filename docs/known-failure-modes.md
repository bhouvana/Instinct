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

**Status**: improved and currently stable on re-check, but never
confirmed at RFC-0004's N≥3 standard on Claude specifically the way
`gt-03` was in RFC-0011. Treat as "probably fixed," not "closed" — the
next real Claude-side pass should sample this one specifically.

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
