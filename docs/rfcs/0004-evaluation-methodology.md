# RFC-0004: Evaluation Methodology

- Status: Accepted
- Date: 2026-07-26
- Depends on: RFC-0001 (Charter), RFC-0002 (Prompt Architecture), RFC-0003
  (Mechanism Design)
- Blocks: RFC-0005 (Testing Strategy), implementation sign-off

## Summary

Turns RFC-0001's success criteria, RFC-0002's trigger-precision pointer, and
RFC-0003's Gate-accuracy pointer into an actual measurement program: what
gets measured, on what substrate, scored by what authority, and guarded
against what gaming risk. This RFC is science, not engineering — it defines
what "working" means and how we'd know. RFC-0005 takes the cheap, fast
subset of this and turns it into an automated suite.

## The honest problem this RFC has to admit up front

RFC-0001's actual success criterion is a felt one: a developer says "Claude
has developed engineering judgment," not "Claude follows better prompts."
That is not a number. Most of what's valuable about this project resists
the kind of clean automated scoring a compiler or a test suite gives you,
because the thing being measured — was this the right call — is itself a
judgment, subject to the same disagreement engineering judgment always is.
Pretending otherwise and reaching for a single dashboard metric would be
its own failure of Provenance and Judgment, applied to the project's own
evaluation of itself. This RFC treats that as a constraint to design around,
not a problem to paper over with a score that looks rigorous and measures
the wrong thing.

## What gets measured, and by what

Four layers, each with a different evidentiary standard:

**1. Trigger accuracy** (validates RFC-0002). Precision and recall of the
skill firing on a labeled corpus of requests: does it fire on requests that
are actually Tier 2/3, does it stay quiet on requests that are actually
Tier 1. Machine-checkable against pre-labeled ground truth. Cheap, fast,
belongs in RFC-0005's automated suite.

**2. Gate/tier accuracy** (validates RFC-0003). Same shape as above, one
level in: given a request that already triggered the skill, does the Gate
classify it into the tier a human labeler agrees with, including the
adversarial near-miss cases RFC-0003 already calls for (a Tier 3 request
disguised to look Tier 1, and the reverse). Machine-checkable against
pre-labeled ground truth. Also belongs in RFC-0005.

**3. Decision-quality proxies** (validates RFC-0001's success criteria
directly): rate of changes later reverted or amended because they solved
the wrong problem, missed an existing abstraction, or duplicated
functionality; rate of unprompted pushback that the user, after the fact,
agrees was warranted; diff size relative to a no-skill baseline on matched
tasks; ceremony cost (extra turns, extra questions) on Tier 1 requests
relative to baseline, which per the Proportionality guardrail should trend
toward zero. These require *real sessions*, not single-shot generation —
see the substrate section below — and a mix of log-derived counts
(reverts, diff size — machine-checkable) and human judgment (was this
pushback warranted — not machine-checkable without the LLM-as-judge risk
discussed below).

**4. The felt outcome** (RFC-0001's actual bar). Structured qualitative
review: give evaluators transcripts of matched Instinct-enabled and
baseline sessions, blinded to which is which, and ask which one reads like
working with a better engineer, and why, in their own words. This is the
slowest, most expensive layer, and the one this project ultimately answers
to — layers 1 through 3 are proxies for this, not replacements for it.

## Repeat sampling (amended after RFC-0009 / RFC-0010)

A single pass per scenario is not sufficient evidence for Layers 1/2,
full stop. This was assumed rather than stated when this RFC was first
written; RFC-0009 found a backend that disagreed with itself on
identical, zero-temperature calls, and RFC-0010 showed that repeat
sampling turned what looked like scattered single-pass noise into a
stable, real 3/3 disagreement on one scenario and a 2/3 one on another —
signal a single pass could not have distinguished from noise in either
direction. Any reported Layer 1/2 result must state its sample count and
use majority vote (`eval/run.py --samples N`, N ≥ 3 minimum, more for a
scenario close to the noise floor) rather than a single call. A result
reported at N=1 is not evidence, it's an anecdote with a pass/fail label
on it.

## Substrate: real agentic sessions on real repositories, not synthetic
single-shot prompts

See ADR-0007. In short: Provenance can't be meaningfully tested against a
repository with no real history to reconstruct, and Judgment can't be
meaningfully tested against a task with no real alternative abstractions
sitting nearby to notice or miss. A single-shot "here's a prompt, generate
a diff" benchmark exercises implementation quality, which was never the
gap this project targets. The substrate has to be multi-turn sessions
against repositories with genuine accumulated decisions — real open-source
projects with real git history, not scaffolded fixtures built to order.

## Scoring authority: human review, with cheap automated proxies feeding
it, not replacing it

See ADR-0008. Layers 1 and 2 are legitimately machine-checkable — there is
a ground-truth tier label, and the model's classification either matches it
or doesn't. Layers 3 and 4 are not, and the temptation to close that gap
with an LLM-as-judge automated scorer has a specific, named risk here: a
judge model can share the same blind spots as the system it's judging (for
instance, rewarding hedged, alternative-listing responses as "showing
judgment" independent of whether the hedging was warranted, which is
exactly the contrarianism failure mode RFC-0001 warns against, scored as a
success by a judge with the same bias). Human review, ideally blinded to
condition, is the scoring authority for layers 3 and 4. LLM-as-judge is
permitted only as a cheap pre-filter that flags candidates for human review
faster — never as the number that gets reported.

## Goodhart guardrail

Every metric above is a proxy, and proxies get gamed, especially by a
system whose entire design is aimed at satisfying evaluators. Two concrete
countermeasures, not just an acknowledgment:

- **Track override/rejection rate as a standing counter-metric.** If a
  user explicitly rejects or overrides an Instinct-driven suggestion (a
  Tier 3 pushback, a "reuse this instead" redirect), that's logged
  independent of whether the primary metrics look good. A system that hits
  its revert-rate and diff-size targets by becoming falsely conservative —
  padding Tier 2 into Tier 3, hedging on requests that didn't need it —
  should show up here even if it's invisible to layers 1 through 3.
- **Holdout scenarios.** A portion of the Layer 1/2 labeled corpus and the
  Layer 3/4 task set is never shown during any tuning or prompt-iteration
  work, evaluated only at release-gate time. Without this, "the suite
  passes" measures fit to the suite, not the mechanism.

## Cadence

Layers 1 and 2 are cheap enough to run on every `SKILL.md`/reference-file
change — this is RFC-0005's job. Layers 3 and 4 are expensive (real
sessions, human review) and run at release-gate cadence, not per-edit:
before any version bump that changes the Gate, the tiers, or the maxims
themselves. A prompt-wording tweak that layers 1/2 pass does not
automatically justify skipping 3/4 before a release — those layers exist
specifically because 1/2 passing is necessary and not sufficient.

## What this RFC does not specify

The literal scenario corpus, its file format, and the CI mechanics that run
it on every change — that's RFC-0005, which inherits layers 1 and 2 from
here as its actual content.
