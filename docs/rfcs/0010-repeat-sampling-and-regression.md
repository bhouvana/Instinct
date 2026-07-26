# RFC-0010: Repeat Sampling, a Real Regression, and a Second Fix

- Status: Accepted (record of a completed check, not a proposal)
- Date: 2026-07-26
- Scope: adds `--samples N` (majority vote + agreement rate) to
  `eval/run.py`; a 3-sample full gate_tier run against Ollama Cloud; a
  6-sample Claude cross-check on the two live disagreements from RFC-0009
  (`gt-03`, `gt-07`) via the Agent tool (still no Anthropic API key); a
  real regression found and fixed as a result; a smaller re-verification
  pass on the fix.

## Why this exists

RFC-0009 left two things unresolved: whether `gt-03`/`gt-07`'s disagreements
were backend noise or a real Gate gap, and a named methodology hole (no
repeat-sampling in the harness, so a single pass can't tell the two apart).
Both get addressed here, using the Agent tool as a substitute for
`ApiBackend` since there is still no Anthropic key available.

## The harness change

`_sample()` in `eval/run.py` calls a backend N times per scenario, catching
per-call errors individually, and reports the majority value plus a `k/n`
agreement string (e.g. `2/3`). `--samples 1` (default) is unchanged
behavior. This is now the honest way to run this harness against any
backend with unknown reliability — RFC-0009's single-pass numbers should be
read as superseded by this, not as a separate data point to average in.

## Round 1: repeat sampling turns single-pass noise into real signal

Full gate_tier corpus, 3 samples each, against Ollama Cloud (`gpt-oss:120b`):

- **6 of 8 scenarios were internally consistent** (3/3 or a clear majority)
  — including all the ones RFC-0009 reported as one-off "parse errors."
  With repeat sampling, most of those are *stable* refusals/n/a answers,
  not random noise. This model reliably struggles with this task's output
  format, rather than randomly.
- **`gt-07` disagreed with its label 3/3 times** — Tier 2, not the expected
  Tier 1, every single call. That's a real, repeatable finding, not the
  single-sample fluke RFC-0009 couldn't rule out.
- **`gt-03` disagreed 2/3 times** — Tier 2, not the expected Tier 3, on the
  *canonical worked example*.

## Round 2: cross-checking against Claude via the Agent tool, on the
pre-existing SKILL.md

3 fresh, independent samples each on `gt-03` and `gt-07`, using the
`SKILL.md` wording as it stood after RFC-0008 (one prior fix, to `gt-07`
specifically):

- **`gt-07`: Tier 1, Tier 2, Tier 1** — 2/3 correct, not fully stable even
  on Claude. The Tier-2 outlier's reasoning: "the signup endpoint is a
  public interface with multiple consumers... so changing its validation
  behavior affects all callers" — routing through Q2 instead of Q3, arguing
  any public endpoint definitionally has multiple consumers regardless of
  whether the change itself affects them. RFC-0008's fix addressed Q3's
  "public surface" conflation; it never touched this Q2 reading.
- **`gt-03`: Tier 3, Tier 2, Tier 2** — 2/3 **wrong**, on Claude, on the
  project's own flagship Tier-3 example. Both Tier-2 samples explicitly
  reasoned that Q3 "doesn't clearly apply since it's an additive-required-
  field change" — **this is RFC-0008's own fix-language being read too
  broadly**. "An additive... change is usually a no" was written to stop
  public-surface changes from over-escalating, but a model applied the same
  logic to a required-parameter break, which is exactly the case the
  Critical tier's own worked example exists to catch. A fix for one false
  positive created a false negative on an unrelated case, because the two
  shared the word "additive" without the wording distinguishing them.

## The second fix

Replaced "An additive, strictly safety-improving change... is usually a
no" with a version that names the actual distinguishing test — does an
existing caller have to do anything differently — rather than leaning on
the word "additive," which turned out to be reusable in bad faith by a
model looking to justify not escalating:

> "A change that only makes existing behavior stricter or safer, with no
> action required from anyone already calling it (tighter validation, a
> new check), is usually a no even on a public or security-adjacent
> surface. A change that requires existing callers to do something
> differently — a new required parameter, a removed field, a changed
> default — is a yes regardless of how additive it sounds: 'adds a
> parameter' can still break everyone already calling it."

## Round 3: re-verifying the second fix

2 fresh Claude samples each, plus 2 Ollama samples each, against the new
wording:

- **`gt-07` (Claude): Tier 1, Tier 1** — unanimous, clean reasoning both
  times, no recurrence of the Q2 public-interface framing. Improvement over
  round 2's 2/3.
- **`gt-03` (Claude): Tier 3 (clean), Tier 1 (reasoning argues Q3-yes —
  "forces all 12 existing call sites to change... which is a yes on Q3" —
  but the final label contradicts its own reasoning and says Tier 1)** —
  one clean correct answer, one internally self-contradictory one. Better
  than round 2's consistent wrong answer, but the sample is too small and
  the second sample too strange to call this closed.
- **`gt-03` (Ollama): Tier 2 (still wrong), then a parse error.**
  **`gt-07` (Ollama): parse error, then Tier 1 (correct).** Ollama's
  reliability issues from round 1 are unchanged by a `SKILL.md` wording
  change, as expected — that problem was never about the Gate's wording.

## Honest conclusion

`gt-07` looks genuinely improved and close to stable on Claude after two
targeted fixes. `gt-03` is a live, still-open question — the fix helped
(it stopped being *consistently* wrong) but 5 total Claude samples across
two wordings, one of them self-contradictory, is not enough evidence to
call it resolved. This is not a case for a third ad hoc fix guessed from
five data points; it's exactly the gap RFC-0009 already named and this
RFC's forward pointer restates: a properly powered repeat-sampling pass
(the `--samples` flag now supports it) is what should resolve this next,
not more manual single-digit sampling in conversation.

## Forward pointer

RFC-0004 should be amended to require `--samples ≥ 3` (or a stated,
justified N) as the minimum for any reported Layer 1/2 result, given two
separate rounds in this project now showing single-pass numbers were
misleading. `gt-03` specifically should be the first scenario re-run once
that's standard practice, ideally at N=10 or more given how close the
signal is to the noise floor observed here.
