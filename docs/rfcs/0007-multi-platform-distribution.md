# RFC-0007: Multi-Platform Distribution

- Status: Accepted
- Date: 2026-07-26
- Depends on: RFC-0002 (Prompt Architecture), RFC-0003 (Mechanism Design),
  ADR-0011, ADR-0012
- Supersedes: RFC-0001's deferral of multi-platform distribution, if
  accepted — not by disagreeing with the original reasoning, but because
  that reasoning ("until the Claude Skill itself is validated") was about
  sequencing, and this RFC is what "do it properly, in sequence" resolves
  to.

## Summary

Designs the adapter layer that would let Instinct's rules reach hosts other
than Claude Code — grounded directly in Ponytail's actual architecture
(confirmed by reading its repository, not just its README): a two-layer
split between a single skill layer holding real behavior and thin,
host-specific adapters, with sync verification as a first-class concern
rather than a maintenance afterthought.

## Why this is a real RFC and not a batch of files

Ponytail's robustness on this dimension isn't the adapter *files* — it's
that every adapter is provably in sync with one canonical source, checked
by a script, checked again by a real test suite (`tests/hooks-windows.test.js`
exists because someone hit a Windows-specific hook failure once and wrote a
test so it can't happen silently again). Ten adapter files with no sync
story would look like Ponytail from a directory listing and behave nothing
like it the first time someone edits the Gate and forgets one copy. The
design work here is the sync story, not the file count.

## The two-layer model, applied to what already exists

Ponytail's principle: "the skills in `skills/` hold the core behavior;
host-specific files are adapters that make that behavior easy to load."
Applied to Instinct's actual files rather than invented fresh:

- `SKILL.md`'s **body** (everything after the frontmatter close) is already
  host-agnostic — it never mentions triggering, matching, or loading, only
  the Gate and tier behavior. This was not deliberate at the time it was
  written, but it means the skill layer already exists and needs no
  rewrite: **`SKILL.md`'s body is the canonical source.**
- `SKILL.md`'s **frontmatter** (`name`, `description`) is Claude-Skill-
  specific — it exists to solve the description-matching problem RFC-0002
  designed around (ADR-0003). Hosts with no matching step don't need it and
  shouldn't get a translated version of it; they just get the body, always
  applied, the same way Ponytail's `AGENTS.md` states the ladder directly
  with no "when to load this" section.

## Host tiers (Ponytail's taxonomy, applied to what Instinct would target)

- **Plugin-tier** (native skill/hook support): Claude Code, where
  `SKILL.md` already is the native artifact. Whether Instinct's format
  maps cleanly onto other plugin-tier hosts Ponytail supports (Codex,
  others) is an open compatibility question this RFC does not resolve —
  scoped as follow-up, not assumed.
- **Instruction-tier** (always-on project instructions, no matching step):
  Cursor, GitHub Copilot, Windsurf, and a canonical `AGENTS.md` at the repo
  root — increasingly treated as a de facto standard several tools read
  directly, which is why Ponytail maintains one centrally rather than
  treating it as just another adapter.

## Consolidation, not pointers, for instruction-tier hosts

`SKILL.md`'s Critical tier says "Read `references/ladder.md`... and
`references/provenance-out.md`," which works because Claude Code can
actually execute that instruction. An always-on instruction file injected
as static context has no guaranteed equivalent action. Per Ponytail's own
language for this tier ("consolidated `AGENTS.md` rules," not pointers),
`AGENTS.md` and other instruction-tier adapters should **inline** the
Critical-tier detail and deposit mechanics rather than reference them —
one self-contained file, even though that means `AGENTS.md` is longer than
`SKILL.md`'s lazy-loaded core. This is a deliberate, host-driven exception
to keeping things thin, not a contradiction of it.

## Sync verification

A script (`scripts/check_adapters.py`, modeled on Ponytail's
`check-rule-copies.js`) that:

1. Reads `SKILL.md`'s body as the canonical text.
2. For each registered adapter, extracts its rule content and confirms it
   matches the canonical body — either byte-for-byte (instruction-tier
   adapters that just wrap it in host-specific frontmatter) or, for
   `AGENTS.md`'s consolidated form, confirms the inlined Critical-tier and
   deposit content matches `references/ladder.md` and
   `references/provenance-out.md`.
3. Exits non-zero on drift, with a diff — meant to run in CI the same way
   `eval/run.py` is meant to (RFC-0005), so an edit to `SKILL.md` that
   forgets to regenerate `AGENTS.md` fails the same way a code change that
   breaks a test fails.

This script is not written yet. Per the same reasoning as ADR-0009 (corpus
before implementation), it should be written once there are at least two
adapters to check — a sync checker with nothing to check is scaffolding,
not verification.

## Phased rollout, not a single batch

1. **Phase 1:** `AGENTS.md` (highest leverage — read by the most tools
   directly) plus one instruction-tier adapter as a template for the
   pattern (Cursor's `.mdc` frontmatter is well-documented:
   `description`, `globs`, `alwaysApply: true`) plus `check_adapters.py`
   covering just those two. Prove the sync story works before scaling it.
2. **Phase 2:** remaining instruction-tier adapters (Copilot, Windsurf,
   others) once Phase 1's sync tooling is proven, added as thin copies —
   genuinely mechanical once the pattern and the checker exist.
3. **Phase 3 (separate open question, not scoped here):** plugin-tier
   compatibility beyond Claude Code, and whether Instinct's single-ambient-
   skill choice (ADR-0004) still holds once other plugin-tier hosts are in
   scope, or needs revisiting alongside them.

## What this RFC does not do

Write any adapter file. That's implementation, gated on this RFC being
accepted, matching every other RFC in this project's process so far.

## Forward pointer

If accepted, Phase 1 is the next implementation task after the corpus
runner's `ApiBackend` (RFC-0005) — not before it. A canonical body worth
syncing to five hosts is worth less if the mechanism it encodes hasn't
been evaluated for real yet (ADR-0007, ADR-0008); multiplying an unproven
mechanism across hosts multiplies the cost of the correction when real
evaluation finds one, which is the exact risk RFC-0001 named originally.
