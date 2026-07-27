---
name: instinct-debt
description: >
  Use when the user asks to see accepted engineering debt, "what did
  instinct defer", "list the instinct: markers", "instinct debt ledger",
  or wants a report of deliberately-accepted limitations across the
  codebase. Explicit invocation only; one-shot report, changes nothing.
---

Every knowingly-accepted limitation from a Critical-tier decision is
marked with an `instinct:` comment naming the limitation and what would
remove it (`references/provenance-out.md`, case 5). This collects them
into one ledger so a deliberate, scoped-for-now tradeoff can't quietly
become a permanent, unexamined one.

## Scan

Grep the repo for the marker, anchored to a comment prefix so it matches
actual inline comments and not prose that merely mentions the convention
(a plain `grep -rn "instinct:"` was tried while writing this skill and
returned two dozen false positives — docs, ADRs, this file itself, and the
sync-marker's own regex source in `hooks/lib.js` — none of them real debt):

`grep -rnE '(#|//) ?instinct:' --include=*.py --include=*.js --include=*.ts .`

(extend the pattern with other comment prefixes — `--`, `;`, `<!--` — for
the target stack). This also naturally excludes the sync-marker convention
(`instinct:shared`, `instinct:host-specific`), which appears inside HTML
comments and regex source, not as a `#`/`//`-prefixed inline marker.

## Output

One row per marker, grouped by file:

`<file>:<line> — <what was limited>. removes when: <the trigger named in the comment>.`

Flag any marker with no named removal trigger — those are the ones most
likely to rot into permanent, unexamined debt, exactly the failure mode
the convention exists to prevent.

End with `<N> markers, <M> with no removal trigger.` Nothing found:
`No instinct: debt. Clean ledger.` — an expected, normal result for a
codebase that hasn't needed the escape hatch yet, not a sign the
convention is broken or unused.

## Boundaries

Reads and reports only, changes nothing. If a finding warrants action —
a marker whose trigger condition has actually arrived — that's a new
request through the Gate, not something this report resolves itself.
