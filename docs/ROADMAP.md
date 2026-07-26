# Roadmap

Sequencing rationale: philosophy has to exist before mechanism, mechanism
before prompt text, prompt text before it can be evaluated, evaluation
before benchmarks mean anything, and the core skill has to be validated
before it's worth multiplying across platforms. Each stage is a hard
dependency of the next; skipping ahead has been considered and rejected
more than once (RFC-0001's Forward Plan; ADR-0012).

## Design phase

- [x] **RFC-0001 — Charter.** Philosophy, problem statement, guardrails,
      relationship to prior art, success criteria.
- [x] **RFC-0002 — Prompt Architecture.** Broad trigger with an in-body fast
      exit (ADR-0003), single ambient skill for v1 (ADR-0004), draft
      `name`/`description` frontmatter, style law, composability rules.
- [x] **RFC-0003 — Mechanism Design.** The Gate (three yes/no questions),
      two tiers past it (ADR-0005), escalate-on-uncertainty (ADR-0006),
      tier-specific behavior for all three pillars, a resolved default for
      provenance-deposit, and three worked examples.
- [x] **RFC-0004 — Evaluation Methodology.** Four layers (trigger accuracy,
      Gate accuracy, decision-quality proxies, felt outcome), real-session
      substrate (ADR-0007), human review as scoring authority for the two
      layers that aren't machine-checkable (ADR-0008), a Goodhart guardrail.
- [x] **RFC-0005 — Testing Strategy.** Operationalizes RFC-0004's cheap
      Layers 1/2 into an automated suite. Corpus locked before the first
      implementation draft existed (ADR-0009).
- [x] **RFC-0007 — Multi-Platform Distribution.** Designs the adapter layer
      (`AGENTS.md` + instruction-tier copies) grounded in Ponytail's actual
      architecture: `SKILL.md`'s body as the one canonical source,
      consolidation instead of pointers for always-on hosts, sync
      verification, a three-phase rollout. Written *because* the obvious
      path (just build ten adapter files on request) was rejected — see
      ADR-0012. Its own Forward Plan sequences Phase 1 after real
      evaluation, not before.

## Implementation phase

- [x] Scenario corpus (`eval/corpus/*.yaml`) authored and locked before any
      `SKILL.md` draft existed, per ADR-0009.
- [x] `SKILL.md` — the Gate, Bug fixes, Verification, Consequential/Critical
      tiers, Never/Scope closers. Hardened twice past the v1 audited in
      RFC-0006: once from a direct read of Ponytail's instruction text
      (root-cause and verification-check rules, ADR-0011), once from a real
      bug an independent model found in the Gate itself (public-facing
      surfaces wrongly reading as automatically Critical, RFC-0008) —
      fixed and re-verified against a second fresh model, closed-loop.
- [x] Reference files — `references/ladder.md`,
      `references/provenance-out.md` (collapsed from three files to two
      during writing, ADR-0010; provenance-out gained the `instinct:`
      marker convention, ADR-0011).
- [x] Manual dry run of the pre-hardening v1 draft
      (`docs/rfcs/0006-skill-v1-dry-run.md`) — two gaps found and fixed,
      one ambiguity deliberately left for real evaluation rather than
      patched on the author's own say-so. **Superseded** by RFC-0008, which
      is what that deferred ambiguity turned into once actually tested.
- [x] **Corpus runner** (`eval/run.py`) — loads the corpus, runs it through
      a pluggable `Backend`, reports pass/fail, non-zero exit on failure.
      `StubBackend` (keyword heuristic, proves the harness not the skill)
      verified working. `ApiBackend` (real Anthropic SDK call) is
      implemented and fails loudly without a key rather than silently, but
      is **unexercised** — no `ANTHROPIC_API_KEY` in this environment.
- [x] **First independent evaluation** (`docs/rfcs/0008-first-independent-evaluation.md`)
      — 6 of 21 corpus scenarios, chosen for information density (the three
      adversarial Gate cases plus all three worked examples), run against
      fresh model instances via the Agent tool rather than `ApiBackend`
      (no API key available). Found and fixed one real bug, confirmed the
      fix against a second fresh model. The other 15 scenarios, and any
      trigger-corpus coverage at all, remain unexercised by real evaluation.
- [x] **`OpenAICompatBackend`** — generic backend (stdlib `urllib` only, no
      new dependency) for any OpenAI-chat-completions-shaped host, sharing
      its response-parsing logic with `ApiBackend` via a new `ModelBackend`
      base class instead of duplicating it.
- [x] **Full corpus run, for real** (`docs/rfcs/0009-ollama-cloud-corpus-run.md`)
      — all 18 trigger + gate_tier scenarios, against Ollama Cloud's
      `gpt-oss:120b`. Found and fixed two harness bugs along the way
      (reasoning-model token-budget truncation; one bad response crashing
      the whole run instead of failing just that scenario). Dominant
      finding was the *backend's* unreliability — confirmed non-determinism
      on identical zero-temperature calls — not a clean read on Instinct's
      Gate accuracy. One real signal survived the noise: `gt-07` has now
      disagreed with its label on 3 separate independent passes across two
      models; the RFC-0008 fix measurably helped (Tier 3 → Tier 2) but
      didn't fully close it.
- [x] **`--samples N` repeat sampling** added to `eval/run.py` (majority
      vote + `k/n` agreement string), directly motivated by RFC-0009's
      single-pass ambiguity. RFC-0004 amended to require N≥3 for any
      reported Layer 1/2 result going forward.
- [x] **Second real regression found and fixed**
      (`docs/rfcs/0010-repeat-sampling-and-regression.md`) — repeat
      sampling turned `gt-07`'s disagreement into a confirmed 3/3 on
      Ollama, and cross-checking against Claude (still via the Agent tool,
      no Anthropic key) found the RFC-0008 fix's own wording ("additive...
      is usually a no") was being misapplied to justify *not* escalating
      the project's own canonical Tier-3 example (`gt-03`, a required-
      parameter breaking change). Fixed by naming the actual test
      (does an existing caller have to change anything) instead of leaning
      on the word "additive." `gt-07` looks stable after the fix (2/2 clean
      on re-check); `gt-03` improved but is **not yet confirmed stable** —
      5 total samples across two wordings isn't enough, and one was
      internally self-contradictory.
- [x] **`gt-03` resolved** (`docs/rfcs/0011-gt03-resolution.md`) — 10/10
      fresh Claude samples, unanimous Tier 3, clean reasoning, several
      quoting the RFC-0010 fix's own language. First evaluation pass in
      the project run at the N≥3 standard RFC-0004 itself now requires.
      Scoped honestly: closes this one scenario on this one model via
      Agent-tool spot checks — does not stand in for a full-corpus pass.
- [x] **Full-corpus pass at N=3, cheap path** (`docs/rfcs/0009` addendum) —
      one batch Bash call through `eval/run.py --samples 3` against Ollama,
      not per-scenario Agent-tool spawns (~65K tokens each, confirmed too
      expensive for blanket re-verification). 9/10 trigger, 2/8 clean
      gate_tier; new disagreements on `gt-02`/`gt-05`/`gt-08` deliberately
      *not* chased further — they don't show the repeatable, cross-model
      pattern that made `gt-03`/`gt-07` worth fixing, just this backend's
      known general unreliability. Still true: no Claude-side full-corpus
      pass exists, only the properly-sampled subset (`gt-03`, `gt-07`,
      RFC-0008's cases).
- [ ] **Run the corpus through `ApiBackend`** (Claude) the moment an
      Anthropic key is available — would replace ad hoc Agent-tool spot
      checks with the automated, repeatable path `eval/run.py` was built
      for.
- [x] **Layer 3/4 pilot, N=1** (`docs/rfcs/0012-layer34-pilot.md`) — one
      task, run twice (baseline vs. Instinct-loaded) in isolated worktrees
      against this repo's own now-real history. Clean contrast: baseline
      wrote a plausible file; Instinct-loaded found RFC-0007's specific
      prior design (consolidation not pointers), matched it, and flagged
      the Phase-1/2 sequencing gap once instead of ignoring it. One
      anecdote, not a validated pattern — real Layer 3/4 still needs many
      tasks and human review.
- [x] **Real-repo pilot, 3 tasks** (`docs/rfcs/0013-real-repo-pilot.md`) —
      against `tiangolo/full-stack-fastapi-template` (same repo Ponytail's
      own agentic benchmark uses), one task per pillar (reuse, breaking-
      change judgment, root-cause fix), verified against real code, not
      invented bugs. Consistent pattern across all three: Instinct-loaded
      added a test baseline didn't, plus a real security catch (CSV-
      injection guard) baseline missed entirely. 3 data points, not a
      proven property — repeat sampling for Layer 3/4 tasks is still an
      open methodology gap, same as RFC-0004 Layer 1/2 was before RFC-0009.
- [ ] RFC-0004 Layers 3/4, properly powered (many tasks, multiple repos,
      blinded human review, repeat-sampled, per ADR-0007/0008) — two
      pilots now (RFC-0012 N=1, RFC-0013 N=3) prove the setup and show a
      consistent early pattern; neither is the real program. Not started.
- [ ] RFC-0007 Phase 1 (`AGENTS.md` + one adapter template + sync checker)
      — still sequenced *after* a trustworthy evaluation pass. Three
      rounds of real testing (RFC-0009, RFC-0010, RFC-0011) have found and
      fixed two real bugs in `SKILL.md` that didn't exist in anyone's
      imagination beforehand — exactly the cost-of-correction argument
      RFC-0007's own Forward Plan made for waiting. `gt-03`/`gt-07` being
      resolved is encouraging, not sufficient — the full-corpus gap above
      is still open, and this item waits on it, not on vibes.
- [ ] Public release checklist — deferred until the above are stable.

## Explicitly deferred, not forgotten

- RFC-0007 Phase 3: plugin-tier compatibility beyond Claude Code (Codex and
  others, per Ponytail's own host taxonomy), and whether the single-
  ambient-skill choice (ADR-0004) still holds once other plugin-tier hosts
  are in scope. Not resolved by RFC-0007 itself.
- A dedicated Tier-1 maxim for Judgment or Efficiency (considered and
  deferred in ADR-0002 as a mechanism-design question, not a philosophy one).
