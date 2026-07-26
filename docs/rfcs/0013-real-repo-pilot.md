# RFC-0013: Real-Repo Pilot (3 Tasks, tiangolo/full-stack-fastapi-template)

- Status: Accepted (record of a completed check, not a proposal)
- Date: 2026-07-26
- Scope: 3 tasks, each run twice (baseline / Instinct-loaded), in isolated
  git worktrees of `tiangolo/full-stack-fastapi-template` — the same real
  repository Ponytail's own agentic benchmark uses (confirmed by reading
  its actual benchmark docs, not guessing), cloned fresh into scratch and
  fully removed afterward. Methodology informed directly by that
  benchmark's structure (isolated workspace copies per run, a real
  production codebase, tasks chosen to expose a specific failure mode)
  scaled down to 3 tasks instead of 19, and scored by direct diff
  inspection rather than a judge.py-style automated pipeline, which
  doesn't exist yet.

## Why 3 tasks, not Ponytail's full suite

Ponytail's agentic benchmark runs 12 feature tasks + 6-7 safety tasks,
each 4-10 times, across multiple models. Replicating that scale here would
cost far more than this session's budget justifies for a first real-repo
pass, and it measures the wrong axis for this project anyway — Ponytail is
testing code-size/over-engineering; Instinct's claim is about decision
quality. Three tasks were chosen instead, one per pillar this project
actually claims to change, each grounded in real, verified code (not an
invented bug):

- **Task A** (Consequential / reuse): "Add an endpoint to export the
  current user's items as CSV."
- **Task B** (Critical / breaking change): "Make `title` required on
  item update" — a real field, verified optional in `ItemUpdate` before
  the task was written.
- **Task C** (root-cause bug fix): "Self-delete sometimes leaves orphaned
  items, unlike admin-delete — investigate and fix." Grounded in a real,
  verified asymmetry: `delete_user` explicitly bulk-deletes items first,
  `delete_user_me` relied solely on ORM relationship cascade.

## Results

**Task A.** Both added the same endpoint with the same reuse pattern
(existing auth dependency, existing query style, stdlib `csv`/`io`, no new
dependency) — baseline is competent on its own here. Difference: Instinct
added a `_csv_safe` helper guarding against formula/CSV-injection when the
export is opened in Excel, a real known risk baseline didn't mention at
all, plus two tests (scoping, injection-escaping). Baseline shipped no
tests for the new endpoint.

**Task B.** Both made the correct code change. Difference: Instinct
explicitly identified this as a breaking change on a public endpoint,
explained *why* the field was optional in the first place (partial-update
semantics via `exclude_unset=True` — real Provenance, not assumed),
checked both actual consumers (frontend component, backend tests) before
proceeding, and added a new test specifically asserting the required-field
behavior (`test_update_item_requires_title`). Baseline made the change and
noted the generated frontend client would go stale, but didn't reason
about it as a breaking change, didn't check real consumer impact
explicitly, and added no new test for the behavior itself.

**Task C.** Both correctly diagnosed the actual root cause — independently,
in near-identical language — and fixed it the same way (mirroring the
admin path's explicit delete). This is a good sign for baseline capability
on well-known repos, not a null result. Difference: Instinct extended the
existing `test_delete_user_me` to actually assert items are gone after
self-delete (previously untested behavior); baseline fixed the bug with no
corresponding test.

Both baseline and Instinct sessions independently found and fixed the same
two pre-existing, unrelated import-blocking bugs in the repo (a Python-2
exception syntax and an unquoted forward reference) — this is encouraging
about root-cause discipline in general, but it's a property of the task
setup (a broken repo state neither arm can avoid touching), not a
difference between the two arms.

## The pattern, stated plainly

Across all three tasks, independent of task type, **Instinct-loaded
sessions added a verification artifact (a test) that baseline sessions
did not.** This is exactly the "Verification" rule added to `SKILL.md` in
ADR-0011, showing up consistently in real, unprompted output rather than
just existing as a sentence in a prompt file. Task A additionally showed a
real security improvement (CSV-injection guard) that has nothing to do
with verification and everything to do with the Never-list's "never cut
security to make a diff smaller."

## Honest scope

3 tasks, 1 run each per condition (no repeat sampling — RFC-0004's amended
N≥3 standard applies to Layer 1/2 corpus scenarios, not yet extended to
Layer 3/4 task pilots, which is itself a gap this pilot doesn't close).
One repository, one task family per pillar. This is real signal, stronger
than RFC-0012's N=1, and still not the properly powered, multi-task,
human-reviewed program RFC-0004 actually specifies. Treat "Instinct adds
tests and catches security details baseline misses" as a hypothesis with
three consistent, real data points behind it, not a proven property.

## Housekeeping

Cloned into scratch, worked in six isolated worktrees (one per task ×
condition), verified the one transcript flagged by an availability notice
against its actual diff before trusting it. Everything (clone, worktrees,
branches, throwaway verification scripts one agent left in scratch) was
removed afterward; nothing besides this document is new in the actual
Instinct repo.
