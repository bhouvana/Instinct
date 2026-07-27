# Evaluation corpus

Implements RFC-0005's Layer 1/2 suite. Three files:

- `corpus/trigger.yaml` — should the skill fire on this request.
- `corpus/gate_tier.yaml` — given it fired, what tier does the Gate assign,
  including adversarial cases that deliberately disguise one tier as
  another (see each entry's `note`).
- `corpus/worked_examples.yaml` — the three canonical RFC-0003 examples,
  checked for behavior shape, not just tier. This is the fastest signal
  that a wording edit collapsed the tiers into each other.

## Governance (RFC-0005)

- A regression is fixed by changing `SKILL.md` or a reference file, never
  by editing the corpus to match new behavior. Loosening a failing case is
  the same Goodhart failure RFC-0004 names, applied to this project's own
  test suite.
- New cases can be added freely. Removing or relabeling an existing one
  requires stating why in the commit that does it — RFC-0001's
  Provenance-out standard, applied here.
- Per RFC-0004's Goodhart guardrail, not every case that will eventually
  exist should be visible during day-to-day prompt iteration — a holdout
  split is expected once the corpus is large enough for one to be
  meaningful. Not done yet; noted so it isn't forgotten once it is.

See `docs/known-failure-modes.md` for the scenarios that have actually
fooled a real model in the past, as distinct from ones that merely look
tricky by design.

## Running it

```
pip install -r eval/requirements.txt
python eval/run.py                  # everything, stub backend
python eval/run.py --corpus trigger # one corpus
python eval/run.py --backend api --samples 3   # real judgment regression pass
                                                # needs ANTHROPIC_API_KEY
```

## Judgment regression suite: pass/fail policy

`.github/workflows/test.yml` runs `eval/run.py --backend api --samples 3`
on every push and PR, but only if an `ANTHROPIC_API_KEY` repository secret
is configured — it skips cleanly and exits 0 otherwise (deliberate: no key
has been added yet, so this is the expected state today, not a broken
check). The moment a key is added as a secret, this turns on with no
further engineering.

The policy once it's running for real:

- **N≥3 samples, majority vote, per RFC-0004's amendment.** A single
  zero-temperature call can't distinguish model noise from a real
  regression (RFC-0009 found a backend disagreeing with itself on
  identical calls) — `_sample`'s majority-vote + `k/n` agreement string is
  the only signal treated as a result.
- **A majority-vote disagreement fails the build.** No softer "warn only"
  mode. This follows directly from this file's own Governance section: a
  regression is fixed by changing `SKILL.md`, never by loosening what
  counts as a failure. A build that can be ignored isn't a regression
  suite, it's a suggestion.
- **A failure means investigate, not necessarily revert.** Per
  `docs/known-failure-modes.md`, two scenarios (`gt-03`, `gt-07`) have
  real histories of disagreeing before settling down after a wording fix —
  a first-time failure on either is a strong signal, a failure on a
  never-before-flagged case still needs the same "did the wording actually
  regress, or is this a new noise case" judgment call RFC-0009/0010 had to
  make by hand.

## Honest status: what this is and isn't, right now

The three corpus files are authored and locked per ADR-0009 — they exist
independently of any `SKILL.md` draft, which is the point. `run.py` runs
end to end against three backends now: `StubBackend` (keyword heuristic,
proves the harness plumbing works, its numbers are not a signal about
Instinct), `ApiBackend` (real Anthropic call, wired and CI-ready per
above, but never yet run in CI since no key has been added), and
`OpenAICompatBackend` (any OpenAI-chat-completions-shaped host, used for
the Ollama Cloud runs in RFC-0009–0011).

What's still missing, honestly: no properly-powered Claude-side full-corpus
pass exists — only the two scenarios sampled at RFC-0004's N≥3 standard
(`gt-03` in RFC-0011, informally `gt-07` across RFC-0008–0010) via manual
Agent-tool spot checks, not the automated path above. That path is now
ready; it just hasn't been triggered by a real key yet. The corpus itself
is also still small (21 scenarios total) — RFC-0005's own governance notes
a holdout split is only meaningful "once the corpus is large enough,"
which it isn't yet. Growing it needs the same real-model verification the
regression suite needs, so it isn't done speculatively here.

The dry run recorded in `docs/rfcs/0006-skill-v1-dry-run.md` is a manual
walkthrough of this corpus against the first `SKILL.md` draft, done by
reading the draft's rules and reasoning through each scenario by hand
(predates the `ApiBackend` interface above, and predates the hardening in
ADR-0011). It is useful for catching obvious authoring bugs before real
evaluation exists, and it is explicitly not RFC-0004 Layer 1/2 evaluation —
that requires an actual model call and a model that hasn't seen the corpus
while generating the draft, neither of which is true here. Treat the dry
run as "the author reread their own work carefully," not as passing tests,
and treat the stub backend's output as "the harness compiles," not as
passing them either.
