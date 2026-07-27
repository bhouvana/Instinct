---
name: instinct-audit
description: >
  Use when the user asks for a whole-repo or whole-history audit of
  engineering judgment — "audit this repo", "did we leave reasoning
  behind", "find undocumented breaking changes", "provenance audit".
  Broader than instinct-review, which checks one diff; this looks across
  history. Explicit invocation only; one-shot report, changes nothing.
---

`instinct-review` checks whether one diff got the scrutiny it deserved.
This checks the same question at repo scale: across recent history, did
Critical-tier-shaped changes actually leave the reasoning `SKILL.md`
obligates, or did they just happen?

## What counts as Critical-tier-shaped, retroactively

Look at commits (default: recent history, or whatever range/timeframe the
user names) whose diff shows any of:
- a removed or renamed public function, export, endpoint, or config key
- a new required parameter, or a narrowed/changed default, on something
  with more than one caller
- a deleted file, module, or dependency that other code imported
- a changed trust-boundary surface (auth, payment, deletion, data access)
- **a change to a canonical rule/prompt/policy text that other files or
  hosts derive from** (this project's own `SKILL.md`; equally, a shared
  ESLint config, a schema other services validate against, an IaC module
  other stacks import) — easy to miss because the diff is "just words" or
  "just config," but the blast radius is every consumer of that text, not
  the file itself. Found by actually running this checklist against this
  project's own history: the commit tightening `SKILL.md`'s Q2 wording
  changes classification behavior across every host this project ships
  to, which is a bigger blast radius than most of the literal
  code-function bullets above, and none of them would have caught it.

## What to check for each one

1. **Does the commit message state a tradeoff**, not just describe the
   change? "Removed X" is a description. "Removed X because Y, chose Z
   over keeping X deprecated" is a tradeoff.
2. **Was an alternative named anywhere** — commit message, linked PR or
   issue, a code comment — or does history show only the path that got
   taken, with no evidence anything else was weighed?
3. **Is there a verification artifact** (test, assertion) added or updated
   in the same change, given the blast radius the bullet above implies?

## Reporting

One row per commit that qualifies as Critical-tier-shaped:

`<short-hash> <one-line summary> — provenance: present|missing. verification: present|missing.`

Lead with the ones missing both — highest-value findings first, not the
longest list. End with a one-line count, not a restated table. Zero
qualifying commits in range is a real, useful result: say
`No Critical-tier-shaped changes found in <range>.`, not a padded
non-answer.

## Boundaries

Reads git history and diffs only; changes nothing and proposes no fixes.
Rewriting old commit messages is out of scope — the point is visibility
into the pattern, not retroactively editing history. If the audit surfaces
a live, current problem (a breaking change with no test that's still
shipping), state it as a finding for a separate, explicit request through
the Gate — don't silently patch it as part of the audit.
