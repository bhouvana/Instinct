# RFC-0009: First Full-Corpus Automated Run (Ollama Cloud / gpt-oss:120b)

- Status: Accepted (record of a completed check, not a proposal)
- Date: 2026-07-26
- Scope: the full trigger + gate_tier corpus (18 scenarios), run for real
  through `eval/run.py --backend openai-compat` against Ollama Cloud's
  `gpt-oss:120b`, using a key the user provided directly in conversation.

## Infrastructure notes (not about Instinct)

Two real bugs in the harness itself, found and fixed before results here
are meaningful:

1. **Token-budget truncation.** `gpt-oss:120b` is a reasoning model that
   emits a `reasoning` field before `content`. At `max_tokens: 100`
   (copied from `ApiBackend`'s working value against Claude), `content`
   came back empty every time — confirmed by inspecting the raw response.
   Raised to 2048. This is specific to reasoning-style open models; the
   Anthropic backend's original value was never wrong for what it was
   built against.
2. **A single bad response crashed the whole run.** `run_trigger` and
   `run_gate_tier` now catch per-scenario exceptions and record them as a
   failed `Result` with the error visible, instead of taking down the rest
   of the corpus. Real robustness gap, fixed once, applies to every future
   backend.

## Results

**Trigger corpus: 9/10.** Single failure (`trg-10`, "Should I use Redux or
Zustand for state management here?" — expected trigger, got none) on a
re-run; a different single item (`trg-08`/`trg-09`) failed on an earlier
pass with the same configuration. Not the same failure twice — see
Non-determinism below.

**Gate/tier corpus: 2/8 clean passes** (`gt-02`, `gt-06`). Of the 6
failures, 4 were `ERROR: Model did not return a parseable TIER line`
(`gt-01`, `gt-04`, `gt-05`, `gt-08`) and 2 were real tier mismatches
(`gt-03`: expected 3, got 2; `gt-07`: expected 1, got 2).

## Non-determinism: the dominant finding, and it isn't about Instinct

Identical prompts, same `temperature: 0`, produced different answers
across separate calls. `gt-01` (the simplest possible case — `.gitignore`,
canonical Tier 1) returned `TRIGGER: yes / TIER: 2` on one call and
`TRIGGER: no / TIER: n/a` on another, for byte-identical input. Most of the
"parseable TIER line" errors are this, not a formatting problem: the model
answered `TRIGGER: no`, which per its own instructions correctly produces
`TIER: n/a` — the harness has nothing to classify because the model
disagreed about triggering on that particular call, not because it
malformed its answer.

This means most of this run's poor gate_tier numbers are not a clean
signal about the Gate's design — they're a property of this specific
model/backend combination's reliability on structured, repeated,
zero-temperature calls, which is itself useful information (this backend
is a poor instrument for RFC-0004 Layer 1/2 evaluation as currently
configured) but shouldn't be read as "Instinct's mechanism scored 2/8."

## The one signal that isn't noise: `gt-07` again

`gt-07` (additive email validation on a public signup endpoint, expected
Tier 1) has now disagreed with the label in **three separate independent
evaluations**, across two different models and two different harnesses:

1. Agent-tool fresh model, pre-fix (RFC-0008): Tier 3.
2. Agent-tool fresh model, post-fix, same session (RFC-0008): Tier 1 —
   the fix from RFC-0008 held under that specific re-test.
3. `gpt-oss:120b` via Ollama Cloud, this run, with the RFC-0008 fix already
   in `SKILL.md`: Tier 2.

The RFC-0008 fix ("a change on a sensitive surface isn't automatically a
yes to Q3...") measurably helped — it moved this case from a clean Tier-3
miss to a Tier-2 near-miss even on a model that wasn't involved in
producing the fix — but didn't fully close it on this model. `gt-03`
(the canonical, unambiguous Tier-3 worked example) also missed low, to
Tier 2, on this run, which is a second data point in the same direction:
this model may be generally biased toward under-escalating relative to
Claude, not specifically confused by `gt-07`'s public-facing framing. Not
enough data here to tell those two explanations apart — that needs more
than one model and more than one pass per model, which is exactly what
`ApiBackend` running the same corpus would provide for comparison, once a
key exists.

## What this does and doesn't establish

Real evidence that the harness works end-to-end against a live, external,
OpenAI-compatible backend — that's new and wasn't true before this pass.
Weak evidence about Instinct's actual Gate accuracy, because the dominant
failure mode (model non-determinism) drowns out whatever clean signal
exists underneath it. `gt-07` is the one finding worth carrying forward
with real weight; everything else here is closer to "this backend needs a
higher sample count per scenario (majority vote across N calls) before its
numbers mean anything," which is a methodology gap for RFC-0004 to close,
not a finding about `SKILL.md`.

## Forward pointer

RFC-0004 doesn't currently say anything about per-scenario repeat sampling
or how to handle a backend with observed non-determinism — this run is the
first evidence that gap is real, not hypothetical, and RFC-0004 should be
revisited to specify a minimum sample count (majority vote, or explicit
variance reporting) rather than trusting a single pass per scenario, at
least for backends that show this behavior. Not fixed in this pass — noted
as a finding, not resolved on the spot.

## Addendum: full corpus at N=3 (after RFC-0010/0011's fixes)

Same backend, `--samples 3`, one Bash call, full 18-scenario corpus —
deliberately the cheap path (one batch call through the real harness)
rather than more expensive per-scenario Agent-tool spawns, once those
turned out to cost ~65K tokens each for a task this small.

Trigger: 9/10, only `trg-10` (Redux vs. Zustand) failing, 2/3 toward
no-trigger. Gate/tier: 2/8 clean (`gt-06` 3/3, and see below), the rest a
mix of parse errors and wrong tiers — `gt-01`/`gt-04` still consistently
error, `gt-02`/`gt-05`/`gt-08` newly show 2/3-majority wrong answers that
didn't appear this clearly in the original run.

None of this is being chased further with additional Claude spot-checks
right now, and that's a deliberate call, not an oversight: every new
disagreement here is on a scenario whose wording hasn't changed since the
last check, which points to this model's general unreliability on
structured output for this task (already the dominant finding of this
whole RFC) rather than a new Gate defect worth burning more evaluation
budget to isolate. The two disagreements that *did* turn out to be real,
cross-model Gate bugs (`gt-07`, `gt-03`) were both caught because they
recurred in a pattern distinct from random noise, and were confirmed
independently on Claude before any fix was trusted (RFC-0010, RFC-0011).
Nothing in this batch clears that bar yet. If any of these specific cases
(`gt-02`, `gt-05`, `gt-08`) shows the same kind of stable, repeatable
disagreement on a reliable backend later, it gets the same treatment
`gt-03`/`gt-07` got — not before.
