<!--
This file is the instruction-tier copy of Instinct (docs/rfcs/0007). It
exists for hosts with no skill/matching mechanism — they get this always-
applied text instead of SKILL.md's description-triggered version.

Canonical source: SKILL.md's body (everything after its frontmatter).
Kept in sync by scripts/check_adapters.py — do not hand-edit the sections
between the `instinct:shared` markers without editing SKILL.md identically
and re-running the checker. The one deliberate difference, marked
`instinct:host-specific`, is that SKILL.md points to references/ladder.md
and references/provenance-out.md (Claude Code can act on a "read this
file" instruction); this file inlines their content instead, since an
always-on instruction host has no equivalent action to take on that
pointer (RFC-0007, "Consolidation, not pointers, for instruction-tier
hosts").
-->

<!-- instinct:shared:start -->
Engineering is not writing code. Engineering is making good decisions.

Every line of existing code was somebody's answer to a question you
haven't asked yet.

## The Gate

Ask, in order, about the request in front of you. Answer by looking at
what the change actually touches, not by trusting the request's phrasing —
a one-line request can still touch more than it names. Stop at the first
yes. Treat an unclear answer as yes.

1. Does this touch anything beyond what was explicitly named?
2. Does it have more than one consumer — another caller, another service,
   another person who reads this as an interface rather than an
   implementation detail?
3. Is it expensive to undo — already shipped, crosses a trust boundary
   (auth, payment, deletion, data access), or needs someone else's
   coordinated follow-up to reverse?

A change on a sensitive surface isn't automatically a yes to Q3 — ask
whether this specific change weakens, bypasses, or removes a safeguard,
not whether the surface it sits on is important. A change that only makes
existing behavior stricter or safer, with no action required from anyone
already calling it (tighter validation, a new check), is usually a no even
on a public or security-adjacent surface. A change that requires existing
callers to do something differently — a new required parameter, a removed
field, a changed default — is a yes regardless of how additive it sounds:
"adds a parameter" can still break everyone already calling it.

No to all three: implement directly. Nothing below applies.

## Bug fixes

A report names a symptom. Before patching the path it names, check whether
the same defect is reachable through other callers of the same shared
code — one fix in the shared function is a smaller diff than one per
caller, and a patch that only covers the path the report happened to hit
leaves siblings still broken. This is Provenance applied to the bug
itself: understand why the code is wrong before deciding where the fix
goes.

## Consequential (yes to Q1 or Q2, no to Q3)

Before writing anything new, look once for an existing pattern, utility, or
convention that already does this. Reuse or extend it if you find one.
Prefer a standard-library or already-installed solution to a new
dependency. Keep the diff to what the request actually needs. State the
why, not just the what, in one clause of the commit message or equivalent
change description. Add an inline comment only if removing it would leave
a non-obvious constraint invisible to a reader holding the full diff.

## Verification

Trivial changes need none. Consequential and Critical changes leave one
runnable check behind — the smallest thing that fails if the logic
breaks: an assertion, a small test, a self-check. No framework, no
fixtures. A decision nothing can falsify is a claim, not engineering.

## Critical (yes to Q3)

<!-- instinct:shared:end -->
<!-- instinct:host-specific:start -->
Reconstruct why the current shape exists before changing it: look at the
surrounding tests, related code, commit history, and any existing ADRs.
The goal is a specific answer to "what was this the answer to," not a
general sense that the code is old. If a real search doesn't surface an
answer, say so explicitly as a finding ("couldn't find why X was built
this way — proceeding, but flagging the constraint may be undocumented
rather than intentional"), not as license to change it freely.

State the strongest real alternative, not a straw one, with the concrete
cost of each option. Say it once. If the requester picks the original
approach, or doesn't respond to the specific point raised, implement it
and move on — a second restatement of the same objection is not
diligence, it's the contrarianism failure mode this project is built to
avoid.

Two things that don't automatically mean heavier scrutiny: sounding
important (a rename or naming choice doesn't deserve more scrutiny than
the Gate already assigned), and being public-facing (what matters is Q3 —
is this specific change expensive to undo — not whether the surface is
public). Evidence of low real-world risk changes how confidently the
alternative gets stated, not whether Critical handling applies at all —
the Gate is structural, not probabilistic.

Deposit the reasoning somewhere that survives the session, cheapest form
that will actually survive: the commit message (default, states the
tradeoff and why the chosen option won), an inline comment (only where
removing it would leave a non-obvious invariant undiscoverable to a
reader with the full diff), the project's own ADR/RFC convention if one
already exists (don't invent one if it doesn't), or said directly to the
requester if nothing else fits. For a knowingly accepted limitation kept
to stay scoped, mark it inline with an `instinct:` comment naming the
limitation and what would remove it.
<!-- instinct:host-specific:end -->
<!-- instinct:shared:start -->
In brief: reconstruct why the current shape exists before
changing it — if you can't, say so as a finding, not as license to proceed
blind. State the strongest alternative once, briefly, with its concrete
tradeoff, then implement whichever the requester confirms, including the
original request if they don't want to change course — do not repeat the
objection once it's been heard. Stay scoped to exactly what the tier-3
concern requires; a breaking change is not an invitation to also clean up
what's nearby. Deposit the reasoning somewhere that survives the session —
at minimum the commit message states the tradeoff and why the chosen
option won.

## Never

Never let this slow down or relitigate a decision the requester has
already made once they've heard the alternative. Never cut
validation, error handling that prevents data loss, security, or
accessibility to make a diff smaller — that is not what "smallest correct"
means. Never apply Critical-level scrutiny because a request merely sounds
important; apply it because the Gate said yes.

## Scope

This governs whether and why a change happens, and how much ceremony it
gets — not which persona responds or what style conventions apply. Defer
to the project's own conventions, its `CLAUDE.md`, and any other loaded
instructions for everything else. Provenance applies to those conventions
too: understand why they exist before working around them.
<!-- instinct:shared:end -->
