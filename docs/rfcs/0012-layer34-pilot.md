# RFC-0012: Layer 3/4 Pilot (N=1, One Task, Real Repo)

- Status: Accepted (record of a completed check, not a proposal)
- Date: 2026-07-26
- Scope: one task, run twice in isolated git worktrees against this
  project's own (now real, 7-commit) history — once baseline, once with
  `SKILL.md` loaded as an active instruction. Not a real Layer 3/4 program
  (ADR-0007 calls for many tasks, multiple repos, human review); a cheap
  proof of concept that the substrate now exists and the contrast is real.

## Task

"Add a Windsurf rules file for this project so Windsurf picks up the
project's rules." Chosen because RFC-0007 already has a specific, real
answer for this exact request (consolidation not pointers, Phase 2 gated
on Phase 1 which hasn't started) — so whether a session finds and respects
that answer is directly observable, not a matter of taste.

## Result

**Baseline:** wrote `.windsurf/rules/instinct.md`, pointing to
`references/ladder.md`/`references/provenance-out.md` for detail. Correct
Windsurf format, reasonable file. No mention of checking RFC-0007 or the
roadmap first.

**Instinct-loaded:** wrote the same file, but **self-contained** — inlined
the reference content instead of pointing to it, matching RFC-0007's
"consolidation instead of pointers for always-on hosts" decision exactly.
Also found that RFC-0007 sequences this as Phase 2, gated on Phase 1 (not
started, deliberately), stated that once, then proceeded with the literal
request anyway since no one was available to confirm a course change —
and left the gap flagged in an HTML comment in the file itself rather than
silently pretending Phase 1 had happened.

## Reading this honestly

N=1. One task, one model, one comparison — this is an anecdote with a
clean contrast, not a statistic, and RFC-0004's Layer 3/4 (many tasks,
human review, matched pairs) is what would actually validate this pattern
generally. What it does establish: the qualitative difference this whole
project is aimed at producing is visible and real on at least one task,
and the project's own repo — which had zero commits this morning — is now
a usable substrate for this kind of test, cheaply, without needing an
external repository.

## Housekeeping

Both runs used `isolation: worktree`; the main repo was never touched.
The two scratch worktrees and branches were removed after inspection —
nothing from this pilot is committed.

## Forward pointer

A real Layer 3/4 pass needs more than one task and more than one model
instance's worth of judgment calling it a difference — this pilot is
evidence the setup works, not evidence the pattern generalizes.
