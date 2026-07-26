How to deposit reasoning at Critical tier (ADR-0001), so a decision made
this session isn't fully lost the moment it ends. Cheapest form that will
actually survive — in order of preference:

1. **The commit message, or equivalent change description.** Default and
   minimum. State the tradeoff and why the chosen option won, not just
   what changed. This should almost always be possible and almost never
   skipped.
2. **An inline comment**, only where removing it would leave a non-obvious
   invariant, constraint, or workaround undiscoverable to a reader with the
   full diff and tests in front of them. This is the same bar the rest of
   this project's engineering norms already use — Critical tier doesn't
   get a looser standard, and it doesn't get a stricter one either. Most
   Critical changes don't need a comment; the commit message already
   carries the reasoning.
3. **The project's own ADR or RFC convention, if one already exists** —
   check for `docs/adrs/`, `docs/rfcs/`, or an equivalent before assuming
   one doesn't. A Critical-tier decision is exactly the kind of thing that
   convention exists for. Say explicitly that this decision is a candidate
   for it; don't silently skip mentioning it just because writing the
   actual document is more effort than a commit message.
4. **Do not invent an ADR/RFC convention that doesn't already exist in the
   target project.** If there's no such convention, the commit message is
   the deposit — introducing a new documentation ritual because this
   project has one is a scope decision that belongs to the user, not
   something to impose by default. This mirrors `SKILL.md`'s Scope
   section: defer to what's already there.

**A fifth case, narrower than 1–4: knowingly accepted limitations.** When a
Critical-tier change deliberately accepts a limitation to stay scoped — a
cache not invalidated for one edge case, a linear scan instead of an index,
a manual step instead of an automated one — mark it inline with an
`instinct:` comment naming the limitation and what would remove it, same as
the commit message names the tradeoff at the decision level. This is for
limits accepted on purpose, not a license to leave a bug and call it a
tradeoff — if it wasn't a real decision with a real alternative, it doesn't
get the marker, it gets fixed.

If none of the above has a natural home for the reasoning — a decision to
*not* do something, or an architectural rejection with no diff to attach a
message to — say it directly to the requester in conversation rather than
forcing it into an artifact that doesn't fit. A clearly stated sentence the
user actually reads beats a comment nobody will.
