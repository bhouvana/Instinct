# Instinct

A Claude Skill that installs engineering judgment as a default instinct,
not a checklist you have to invoke.

> Engineering is not writing code. Engineering is making good decisions.
> Everything else is a consequence.

## Status

Pre-alpha. Design (RFC-0001 through RFC-0005, RFC-0007) is locked.
`SKILL.md` has been hardened four times past the version RFC-0006
originally audited, the last two from real repeat-sampled evaluation, not
single-pass checks: reading Ponytail's own instruction text (ADR-0011); an
independent model finding a real Gate bug (public surfaces misreading as
automatically Critical — RFC-0008); a full 18-scenario corpus run against a
live external backend, Ollama Cloud's `gpt-oss:120b`, that mostly exposed
*that backend's* non-determinism rather than the skill (RFC-0009); and,
after adding proper `--samples N` majority-vote support to the harness,
finding that the RFC-0008 fix's own wording had created a second, opposite
bug — a model using "additive... is usually a no" to justify *not*
escalating the project's own canonical Tier-3 breaking-change example
(RFC-0010), then confirmed fixed at N=10, unanimous, on a proper re-test
(RFC-0011). A full-corpus N=3 pass against Ollama (cheap: one batch call,
not per-scenario agent spawns) is also done — see `docs/ROADMAP.md` for
what it did and didn't settle, and what's still open.

## What this is

Most coding assistants optimize for implementation: given a request, they
build it. Instinct changes the default so that, before any code is written,
Claude instinctively asks the questions a Staff Engineer asks without being
prompted to — why does this code exist, is this actually the right fix, does
an abstraction for this already exist, what's the smallest correct change.

Two compiled sentences carry the philosophy (`docs/rfcs/0001-charter.md`):

- **Identity:** Engineering is not writing code. Engineering is making good
  decisions.
- **Operational maxim:** Every line of existing code was somebody's answer
  to a question you haven't asked yet.

Underneath them, a mechanical procedure — a three-question Gate followed by
two tiers of behavior — turns Provenance, Judgment, and Efficiency from
named virtues into something checkable, with explicit guardrails so
"judgment" degrades toward neither negligence (skipping it) nor
contrarianism (applying it uniformly regardless of stakes). See
`docs/rfcs/0003-mechanism-design.md`, and `SKILL.md` for where it actually
landed.

## What this is not

- A prompt pack of style instructions.
- A collection of workflow macros.
- A "senior engineer" persona or tone change.
- A code-size minimizer — see
  [Ponytail](https://github.com/DietrichGebert/ponytail) for that, which
  this project is designed to compose with, not replace.
- A way to make Claude slower or more argumentative on every request.
  Proportional to stakes is a hard constraint, not a suggestion.

## Project structure

```
SKILL.md              the skill itself — read this first if you just want
                       to know what it does
references/            detail SKILL.md defers to when a Critical-tier
                       request actually needs it
eval/
  corpus/              labeled scenarios (RFC-0005) — what "correct" means,
                       locked before SKILL.md was written (ADR-0009)
  run.py               the corpus runner — stub backend proven, real API
                       backend implemented but not yet run (no key here)
docs/
  rfcs/                design proposals — the "what and why"
  adrs/                point-in-time decisions and the alternatives that lost
```

## Reading order

Design, in dependency order: `docs/rfcs/0001` (charter) →
`docs/rfcs/0002` (prompt architecture) → `docs/rfcs/0003` (mechanism
design) → `docs/rfcs/0004` (evaluation methodology) → `docs/rfcs/0005`
(testing strategy) → `docs/rfcs/0006` (v1 dry-run notes, superseded — read
`docs/adrs/0011-ponytail-informed-hardening.md` right after it) →
`docs/rfcs/0008` (first independent evaluation — a real bug, found and
fixed) → `docs/rfcs/0009` (first full-corpus run against a live external
model — mostly a lesson about that backend's reliability, but one
unresolved real signal survived it) → `docs/rfcs/0010` (repeat sampling
turns that signal into a confirmed bug, and finds a second bug hiding in
the first fix's own wording — read this one for the sharpest example in
the whole project of why a single test pass isn't evidence) →
`docs/rfcs/0011` (the fix confirmed, this time at N=10 instead of N=1 or
N=3) → `docs/rfcs/0007` (multi-platform distribution) preceded by
`docs/adrs/0012-defer-platform-adapters-pending-rfc.md`, which explains why
that RFC exists instead of a batch of adapter files. Each RFC's `Depends
on` / `Blocks` header lines say why that order, and each has one or more
ADRs immediately after it in `docs/adrs/` covering the sharpest calls
inside it — read the RFC first, the ADRs are the "why not the obvious
alternative" footnotes, not prerequisites.

If you just want the artifact itself rather than the reasoning behind it:
`SKILL.md`, then `references/` only if a Critical-tier example doesn't
make sense on its own.

## License

MIT — see `LICENSE`.
