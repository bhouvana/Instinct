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

## Running it

```
pip install -r eval/requirements.txt
python eval/run.py                  # everything, stub backend
python eval/run.py --corpus trigger # one corpus
```

## Honest status: what this is and isn't, right now

The three corpus files are authored and locked per ADR-0009 — they exist
independently of any `SKILL.md` draft, which is the point. `run.py` exists
and the harness runs end to end: it loads the corpus, calls a `Backend`,
compares against the label, reports pass/fail, exits non-zero on any
failure. What it does *not* have is a real backend — `StubBackend` is a
keyword heuristic that exists only to prove the plumbing works, and its
pass/fail numbers are not a signal about Instinct. `ApiBackend` is the real
integration point (wire a Claude API call using `SKILL.md` as the system
prompt) and currently raises `NotImplementedError` rather than pretending
to work. Wiring it is the concrete next engineering task — see
`docs/ROADMAP.md`.

The dry run recorded in `docs/rfcs/0006-skill-v1-dry-run.md` is a manual
walkthrough of this corpus against the first `SKILL.md` draft, done by
reading the draft's rules and reasoning through each scenario by hand
(predates the `ApiBackend` interface above, and predates the hardening in
ADR-0011 — a fresh pass is due once `ApiBackend` is real). It is useful for
catching obvious authoring bugs before real evaluation exists, and it is
explicitly not RFC-0004 Layer 1/2 evaluation — that requires an actual
model call and a model that hasn't seen the corpus while generating the
draft, neither of which is true here. Treat the dry run as "the author
reread their own work carefully," not as passing tests, and treat the stub
backend's output as "the harness compiles," not as passing them either.
