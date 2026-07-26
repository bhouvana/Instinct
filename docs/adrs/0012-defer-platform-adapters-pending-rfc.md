# ADR-0012: Defer the multi-platform adapter layer pending its own RFC, rather than building it ad hoc

- Status: Accepted
- Date: 2026-07-26

## Context

A direct read of Ponytail's repository tree (not just its README) shows
what its robustness actually consists of: a two-layer architecture where
`skills/*/SKILL.md` hold the real behavior and thin, host-specific adapters
(`.cursor/rules/*.mdc`, `.windsurf/rules/*.md`, `.github/copilot-instructions.md`,
`AGENTS.md`, `.claude-plugin/*.json`, `hooks/*.js` for several runtimes,
platform-specific statusline scripts, `gemini-extension.json`,
`opencode.json`, and more) carry consolidated copies of the same rules into
25+ platforms, kept in sync by dedicated scripts (`check-rule-copies.js`,
`check-versions.js`) and verified by a real test suite (14 files under
`tests/`, covering behavior, correctness, and platform-specific hook
integration including a Windows-specific test file).

The request that prompted this research was to bring Instinct to that same
level of robustness. That is a real, legitimate goal — and it is also
exactly the expansion RFC-0001 named and explicitly deferred: "until the
Claude Skill itself is validated — porting an unvalidated mechanism to five
platforms multiplies the cost of any correction." Nothing has changed about
that reasoning; what's changed is that it's now grounded in a concrete
picture of what the expansion actually involves, rather than an abstract
deferral.

## Decision

Do not build platform adapters, sync tooling, or a multi-runtime hook
layer in this pass. Instead, write RFC-0007 to design the adapter layer
properly — same rigor as every other RFC in this project — grounded in
Ponytail's actual architecture (two-layer skill/adapter split, `AGENTS.md`
as the canonical instruction-tier source, sync verification as a first-class
concern, not an afterthought) rather than building files ad hoc in response
to this request. What does happen now, in this same pass: the cheap,
non-platform-expanding lessons from studying Ponytail's actual instruction
text get folded into `SKILL.md` directly (ADR-0011), and the automated
corpus runner already named as the next step in `docs/ROADMAP.md` gets
built — both strengthen robustness without taking on the platform-count
expansion RFC-0001 already reasoned about.

## Alternatives Considered

- **Build the adapter files now, matching the request directly.** This is
  what "just make it as robust as Ponytail" most literally asks for.
  Rejected as an unreviewed default, not rejected outright — RFC-0001's own
  reasoning for deferring this exact expansion hasn't been invalidated by
  anything found in this research, and reversing an accepted RFC's stance
  silently, without surfacing it, is precisely the failure this project's
  own Critical-tier rule exists to prevent: state the alternative once,
  then let the requester decide with the tradeoff in view. RFC-0007 is
  that statement, made properly instead of in passing.
- **Refuse the request pending re-litigating RFC-0001 from scratch.**
  Rejected — RFC-0001's guardrails are explicit that judgment never becomes
  a reason to withhold action once a decision is made, and this ADR isn't
  a refusal, it's a sequencing choice: design the expansion with the same
  process rigor the rest of the project got, in the very next step, not
  instead of doing it.

## Consequences

Makes easier: if RFC-0007 is accepted, the adapter layer gets built against
a real design (canonical source, sync verification, per-host format
catalog) instead of ten one-off files with no shared maintenance story —
exactly the gap that would make Instinct's version of this layer fragile
where Ponytail's is robust. Makes harder: the "robust like Ponytail" goal
isn't satisfied in this pass on the dimension the request most likely
meant (platform reach) — only on the dimensions that don't require it
(rule content, automated verification). That gap should read as sequencing,
not as declining the goal.
