---
name: instinct-help
description: >
  Use when the user asks what Instinct is, how it works, or wants a quick
  reference to the Gate/tiers without re-reading SKILL.md or the RFCs.
  Explicit invocation only.
---

Instinct in one screen:

**Identity:** Engineering is not writing code. Engineering is making good
decisions.

**The Gate** (three questions, stop at first yes, unclear counts as yes):
1. Touches anything beyond what was named?
2. More than one consumer?
3. Expensive to undo (shipped, trust boundary, needs coordinated follow-up)?

No to all three → implement directly.

**Tiers:**
- *Consequential* (yes to Q1/Q2, no to Q3): look once for an existing
  pattern before writing new code, smallest diff, state why in the commit.
- *Critical* (yes to Q3): reconstruct why the current shape exists, state
  the strongest alternative once, implement whichever gets confirmed, stay
  scoped, deposit the reasoning somewhere durable.

**Always:** non-trivial logic leaves one runnable check behind. Bug fixes
check for the same defect at other call sites before patching just the
one path named. Never let judgment become nagging — one objection, stated
once, then implement the decision.

**Full detail:** `SKILL.md` (the actual behavior), `references/ladder.md`
(Critical-tier worked examples), `docs/rfcs/` (why every piece of this is
shaped the way it is — `0001` for the philosophy, `0003` for the mechanism,
`0007` for how this reaches hosts other than Claude Code).

**Related:** `instinct-review` audits an already-made change against this
same Gate; the core `instinct` skill is ambient and applies before a
change is made, not after.
