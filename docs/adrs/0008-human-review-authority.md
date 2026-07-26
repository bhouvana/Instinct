# ADR-0008: Human review is the scoring authority for decision-quality; LLM-as-judge is a pre-filter only

- Status: Accepted
- Date: 2026-07-26

## Context

RFC-0004's Layer 3 (decision-quality proxies) and Layer 4 (felt outcome)
aren't cleanly machine-checkable — "was this pushback warranted" is itself
a judgment call. LLM-as-judge scoring is the obvious way to make these
layers cheap and fast like Layers 1/2. It needs an explicit decision rather
than being adopted by default because it's convenient.

## Decision

Human review, blinded to condition where practical, is the scoring
authority for Layers 3 and 4. An LLM judge may be used only as a cheap
pre-filter to surface candidate sessions for human review faster (e.g.
flagging sessions where pushback occurred, for a human to then judge as
warranted or not) — never as the number that gets reported as the
project's evidence.

## Alternatives Considered

- **LLM-as-judge as the primary scorer for Layers 3/4.** Faster, cheaper,
  scales without needing human reviewer time. Rejected as primary because
  of a specific, non-generic risk to this project: a judge model can share
  the same blind spots as the system under test. Concretely, a judge asked
  "did this response show good engineering judgment" could reward
  hedging, alternative-listing, and stated caveats as evidence of judgment
  independent of whether they were warranted by the actual stakes of the
  request — which would score the contrarianism failure mode (RFC-0001,
  Guardrails) as a success. This isn't a generic "LLMs can be biased judges"
  objection; it's that the specific failure mode this project is designed
  to avoid is also the specific failure mode an unreflective judge is most
  likely to reward.
- **No automated layer at all; pure human review for everything, including
  Layers 1/2.** Rejected as needlessly slow — Layers 1/2 have real ground
  truth (a pre-labeled tier), so there's nothing for a human to adjudicate
  that a match/mismatch check doesn't already resolve.

## Consequences

Makes easier: the numbers reported for Layers 3/4 are trustworthy against
the specific failure mode this project cares most about avoiding. Makes
harder: Layer 3/4 evaluation has a hard floor on cost and turnaround set by
human reviewer availability, which is one more reason (alongside ADR-0007)
that these layers run at release-gate cadence, not per-edit, and one more
reason the project's own pace should be judged against that reality rather
than against how fast Layers 1/2 alone could iterate.
