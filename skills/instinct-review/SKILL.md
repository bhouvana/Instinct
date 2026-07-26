---
name: instinct-review
description: >
  Use when the user asks to review a diff, PR, or set of already-made
  changes for engineering judgment — not code style, the decision quality
  behind the change. Explicit invocation only; does not fire ambiently
  the way the core `instinct` skill does.
---

Retrospective, not ambient: the change already happened. The question is
whether it was the right one, made the right way.

## What to check, in order

1. **What tier should this have been?** Re-run the Gate against the actual
   diff, not the request that produced it — a diff can reveal a bigger
   blast radius than the request implied. If the diff touches more than
   one file, has a consumer the request didn't mention, or breaks
   something, it should read as Consequential or Critical regardless of
   how it was framed going in.
2. **Does the commit message or PR description carry the why?** Not just
   what changed — the why, per Provenance-out. Its absence on a
   Consequential+ change is a finding, not a style nitpick.
3. **Is there a verification artifact?** A test, an assertion, a runnable
   check for anything beyond Trivial. Its absence on real logic is a
   finding.
4. **For anything Critical-shaped:** was an alternative considered and
   stated anywhere (commit message, PR description, review comments), or
   does the diff read like the first idea got implemented with no
   evidence anything else was weighed?
5. **Root cause or symptom?** For a bug fix specifically: does the diff
   patch one call site when the same defect is reachable from others?

## Reporting

State findings as specific, evidenced claims tied to a file/line — "no
test added for the new required-parameter behavior in `models.py`," not
"could use more testing." If everything checks out, say so plainly and
briefly; a clean review report is one sentence, not a padded list of
non-findings. This mirrors the core skill's own guardrail: judgment isn't
friction, and a review that manufactures findings to look thorough is the
same failure mode as ambient over-scrutiny.
