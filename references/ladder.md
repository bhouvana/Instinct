Full detail for a Critical-tier request (Gate said yes to Q3). Read this
before acting once the Gate has already told you to; it is not the
classification step itself — `SKILL.md` already ran that.

## Reconstructing why

Look at the surrounding tests, related code, commit history, and any
existing ADRs before changing what's there. The goal is a specific answer
to "what was this the answer to" — not a general sense that the code is
old or that someone must have had a reason. If a real search doesn't
surface an answer, say so explicitly to the requester as a finding
("couldn't find why X was built this way — proceeding, but flagging the
constraint may be undocumented rather than intentional"), rather than
treating the absence as permission to change it freely. An undocumented
constraint might still be load-bearing; not finding the reason isn't
evidence there isn't one.

## Stating the alternative

State the strongest real alternative, not a straw one, with the concrete
cost of each option — not "there are tradeoffs" but the specific thing that
gets worse under each choice. Say it once. If the requester picks the
original approach, or doesn't respond to the specific point raised,
implement it and move on — a second restatement of the same objection is
not diligence, it's the contrarianism failure mode this project is built
to avoid.

## Two things that don't automatically mean Critical scrutiny gets heavier

- **Sounding important.** A rename, a naming choice, or anything that
  reads as a "design decision" on its face doesn't deserve more scrutiny
  than the Gate already assigned. If the Gate said Consequential or
  lower because the actual consumers and undo-cost are limited, a change
  that merely sounds significant stays at that tier.
- **Being public-facing.** An endpoint, exported function, or public
  interface isn't automatically Critical by virtue of being public. What
  matters is Q3: is this specific change to it expensive to undo. Additive,
  strictly safety-improving changes to a public surface are often still
  Consequential or lower.

Evidence of low real-world risk (a deprecated function with zero recent
call volume, a flag that's already default-off elsewhere) belongs in how
confidently the alternative gets stated, not in whether the tier applies.
The Gate is structural — is this the kind of change that's expensive to
undo if wrong — not probabilistic — how likely is it to actually go wrong.
Good evidence changes the tone of the pushback, not whether Critical
handling happens at all.

## Worked examples

**Trivial (Gate: no, no, no).** "Add `*.log` to `.gitignore`." Touches only
the named file, no other consumer, trivially reversible. Implement
directly — no provenance check, no alternatives, no deposit beyond the
commit the change gets anyway.

**Consequential (Gate: no, yes, no).** "Add a `formatCurrency` helper for
the invoice component." One lookup for an existing money-formatting
utility or convention. Suppose nothing turns up: writing a new one is
warranted. Reach for `Intl.NumberFormat` before a hand-rolled formatter or
a new dependency. Commit message: "add formatCurrency: no existing
money-formatting utility, wraps Intl.NumberFormat so invoice call sites
stay consistent." No inline comment — nothing here is non-obvious to a
reader of the diff.

**Critical (Gate: yes, yes, yes).** "Add a required `tenantId` parameter
to the public `createUser` API, used at 12 call sites." Check why
`createUser` currently has no tenant concept — deliberately deferred, or
never came up — and whether other public functions already have an
established scoping pattern to match. State once: "This breaks all 12
call sites immediately. An alternative is an optional `tenantId` with a
default-tenant fallback, which avoids touching every call site now but
risks silently mis-scoping data if a caller forgets to pass it. Given
[whatever the history search surfaced], I'd lean required — flagging the
alternative since the blast radius is real either way." Implement whichever
the requester confirms, without repeating the point. Touch exactly the 12
call sites and the signature — resist folding in unrelated cleanup while
already in the file. Commit message states the tradeoff and why required
won; if the repo has `docs/adrs/`, say this decision is a candidate for one
rather than letting it live only in the commit log.
