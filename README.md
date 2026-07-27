<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
  <img alt="Instinct" src="assets/logo.svg" width="420">
</picture>

Engineering judgment as a default instinct for AI coding agents — installed
as ambient behavior, not a persona, a checklist, or a slash command you have
to remember to invoke.

[![License: MIT](https://img.shields.io/badge/license-MIT-informational)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-91%20passing-success)](tests/)
[![Status](https://img.shields.io/badge/status-pre--alpha-yellow)](docs/ROADMAP.md)
[![Hosts](https://img.shields.io/badge/hosts-14-blue)](docs/installation.md)

> Engineering is not writing code. Engineering is making good decisions.
> Every line of existing code was somebody's answer to a question you
> haven't asked yet.

---

## What this is

Most coding assistants optimize for implementation: given a request, they
build it. Instinct changes the default so that, before any code is written,
Claude instinctively asks the questions a staff engineer asks without being
prompted to — why does this code exist, is this actually the right fix, does
an abstraction for this already exist, what's the smallest correct change.

Two compiled sentences carry the philosophy
(see [`docs/rfcs/0001-charter.md`](docs/rfcs/0001-charter.md)):

- **Identity** — Engineering is not writing code. Engineering is making good
  decisions.
- **Operational maxim** — Every line of existing code was somebody's answer
  to a question you haven't asked yet.

Underneath them sits a mechanical procedure, not a vibe: a three-question
Gate, followed by two tiers of behavior once you're past it. It turns
Provenance, Judgment, and Efficiency from named virtues into something
checkable — with explicit guardrails so "judgment" degrades toward neither
negligence (skipping it) nor contrarianism (applying it uniformly regardless
of stakes).

## The Gate

This is the entire mechanism. Everything else in this repository exists to
deliver it, verify it, or carry it to another host.

Ask, **in order**, about the request in front of you. Answer by looking at
what the change actually touches, not by trusting the request's phrasing.
**Stop at the first yes. Treat an unclear answer as yes.**

```
1. Does this touch anything beyond what was explicitly named?
2. Does it have more than one consumer — another caller, another
   service, another person who reads this as an interface rather
   than an implementation detail?
3. Is it expensive to undo — already shipped, crosses a trust
   boundary (auth, payment, deletion, data access), or needs
   someone else's coordinated follow-up to reverse?

   no · no · no  →  implement directly, nothing else applies
   yes to Q1/Q2  →  Consequential  (reuse-check, minimal diff, state why)
   yes to Q3     →  Critical       (reconstruct why, name the alternative,
                                     deposit the reasoning somewhere durable)
```

Two carve-outs exist specifically because real evaluation caught the Gate
over-escalating for the wrong reason, and both are load-bearing, not
decorative: a **public or heavily-used surface isn't automatically a yes to
Q2** (a signup form having many users isn't the same as another piece of
code depending on it as an interface), and a **sensitive-sounding surface
isn't automatically a yes to Q3** (tightening validation with no required
caller changes is usually a no, even on a security-adjacent surface — but a
new *required* parameter is a yes regardless of how additive it sounds). The
full text, with the rest of the tier obligations, `Bug fixes`, `Never`, and
`Scope` sections, lives in [`skills/instinct/SKILL.md`](skills/instinct/SKILL.md) —
that file is the actual artifact; everything above is a summary of it.

## The Gate in action

> "Add a required tenantId parameter to the public createUser API, used at 12 call sites."

Read as a request, this sounds additive — nothing removed, just one more
field. Read through the Gate:

- **Q1** (touches beyond what's named)? Yes — all 12 call sites now have to
  pass a value they didn't before.
- **Q2** (more than one consumer)? Yes.
- **Q3** (expensive to undo)? Yes — a *required* parameter breaks every
  existing caller simultaneously the moment it ships. "Adds a parameter"
  doesn't make that safe.

**Critical.** Reconstruct why `createUser` doesn't already scope by tenant,
state the alternative once (an optional parameter defaulting to the
caller's own tenant, say), then implement whichever the requester confirms.

This is this project's own canonical Critical-tier example
(`gt-03` in [`eval/corpus/gate_tier.yaml`](eval/corpus/gate_tier.yaml)) —
and also the one real bug this evaluation found and fixed *twice*: a fresh
model talked itself out of escalating it by leaning on the word "additive,"
before the Gate's own wording was corrected to name the actual test ("does
an existing caller have to change anything"). It now lands Critical on
**11/11** independent fresh-Claude samples, unanimous. Full history:
[`docs/known-failure-modes.md`](docs/known-failure-modes.md).

## What this is not

- A prompt pack of style instructions.
- A collection of workflow macros.
- A "senior engineer" persona or tone change.
- A code-size minimizer — see
  [Ponytail](https://github.com/DietrichGebert/ponytail) for that, which
  this project is designed to compose with, not replace. Ponytail asks
  "is this the smallest correct version"; Instinct asks "is this the right
  change and how much scrutiny does it deserve" — a layer earlier.
- A way to make Claude slower or more argumentative on every request.
  Proportional to stakes is a hard constraint, not a suggestion — the fast
  exit (no to all three questions) is deliberately as cheap as the Gate
  itself.

## The skill family

| Skill | Invocation | What it does |
|---|---|---|
| `instinct` | ambient | The Gate itself — applies before a change is made. |
| `instinct-review` | explicit | Audits one already-made diff against the Gate. |
| `instinct-audit` | explicit | The same question at repo/history scale: did recent Critical-tier-shaped commits actually leave the provenance the Gate obligates? |
| `instinct-debt` | explicit | Harvests `instinct:` accepted-limitation markers into a ledger, so a scoped-for-now tradeoff can't quietly become permanent. |
| `instinct-help` | explicit | One-screen quick reference — the Gate, the tiers, without re-reading `SKILL.md` or the RFCs. |

Deliberately missing two things a Ponytail-inspired reader might expect: no
user-selectable intensity modes (`/instinct lite|full|ultra`), and no
`instinct-gain` scoreboard — see [`docs/ROADMAP.md`](docs/ROADMAP.md) for
why both were considered and rejected rather than silently never brought up.

## Where it runs

Distributed to **14 hosts** across two delivery mechanisms, kept in sync
automatically rather than hand-maintained:

**7 file-based hosts** read `AGENTS.md` (the canonical consolidated body) or
a thin per-host copy of it — Claude Code, Cursor, Windsurf, Kiro, Cline,
GitHub Copilot, Qoder. `scripts/check_adapters.py` proves every copy stays
byte-identical to `skills/instinct/SKILL.md`, not just once but on every
change — and has itself been tested to actually catch injected drift, not
just pass when nothing's wrong.

**7 plugin-tier hosts** get real manifests and lifecycle hooks — Claude
Code (`.claude-plugin/`), Codex, GitHub Copilot CLI, Qoder, Gemini CLI,
OpenCode, the pi editor, and Hermes Agent — plus an MCP server
(`instinct-mcp/`) for any host with no file-based rule mechanism and no hook
lifecycle to piggyback on.

Every one of these has been verified by actually running it — not just
written and assumed correct. That includes installing the real Claude Code
plugin with the `claude` CLI, which caught a genuine load-failure bug
(`hooks/hooks.json` declared both explicitly and via auto-discovery, a hard
conflict) that had gone unnoticed because nobody had actually installed it
before. See [`docs/installation.md`](docs/installation.md) for exactly what's
**confirmed** (actually run, output inspected) versus **inferred** (follows
from a documented contract, not run against real host software from this
environment) for every host — that distinction is maintained deliberately,
not glossed over.

## Evidence

Instinct doesn't have Ponytail's kind of number — there's no LOC/cost/time
benchmark suite behind it, and building one just to have a chart would be
exactly the fabricated-looking-metrics theater this project argues
against elsewhere (see `docs/ROADMAP.md`'s call on why there's no
`instinct-gain` skill). What it has instead is real, individually-verified
evaluation evidence — every row below is something that was actually run,
not projected:

| What was tested | Result | Where |
|---|---|---|
| Trigger accuracy — does the skill correctly fire or skip | **10/10** on two independent fresh-Claude samples (20/20 total) | [`docs/known-failure-modes.md`](docs/known-failure-modes.md) |
| Canonical breaking-change example (`gt-03`, above) | **11/11** unanimous, Critical tier | [`docs/rfcs/0011`](docs/rfcs/0011-gt03-resolution.md) |
| Q2 wording fix (`gt-07`) | **3/3** clean after the fix — meets this project's own N≥3 confirmation standard | [`docs/known-failure-modes.md`](docs/known-failure-modes.md) |
| Real-repo pilot, 3 tasks, baseline vs. Instinct-loaded | Instinct-loaded added a verification step baseline skipped **in all 3**; caught a real CSV-injection vulnerability baseline missed entirely | [`docs/rfcs/0013`](docs/rfcs/0013-real-repo-pilot.md) |
| Claude Code plugin installability | Confirmed by actually installing it with the real `claude` CLI — found and fixed a load-breaking bug in the process that nobody had caught, because nobody had actually installed it before | [`docs/installation.md`](docs/installation.md) |
| Full test suite | **91/91** passing (85 Python + 6 Node), including tests that prove the checkers themselves catch injected drift, not just pass when nothing's wrong | [`tests/`](tests/) |

Three real bugs found and fixed via evaluation this way, not hypothesized
— each one confirmed on fresh model samples *after* the fix, not just
patched and assumed correct.

**The honest gap, stated here rather than only in `docs/ROADMAP.md`**:
this is real evidence, not a properly-powered evaluation program. The
corpus is 21 hand-labeled scenarios, not hundreds; the pilots are 1 and 3
tasks, not dozens. A judgment regression suite
([`eval/run.py`](eval/run.py)) is wired into CI and ready to run
automatically the moment a real `ANTHROPIC_API_KEY` is available — it
isn't yet, so it skips cleanly today rather than pretending to run.

## Installation

See [`docs/installation.md`](docs/installation.md) for exact steps per host,
each one marked confirmed or inferred. Quick version for Claude Code:

```bash
claude plugin marketplace add /path/to/this/checkout
claude plugin install instinct@instinct
```

Installs at user scope by default, applying the ambient Gate to every
project on the machine — pass `-s project` to scope it to one repo instead.

## Project structure

```
skills/
  instinct/            the Gate itself — SKILL.md, Claude Code-native
  instinct-review/      audit an already-made diff against the Gate
  instinct-audit/       the same question at repo/history scale
  instinct-debt/        harvest instinct: accepted-limitation markers
  instinct-help/        quick reference — explicit invocation, not ambient
AGENTS.md              canonical instruction-tier body — Critical-tier
                       detail consolidated (inlined), not pointed to,
                       for hosts with no matching step (RFC-0007)
.cursor/ .windsurf/ .kiro/ .clinerules/ .qoder/ .github/copilot-instructions.md
                       thin per-host copies of AGENTS.md, generated (not
                       hand-typed) by scripts/generate_adapters.py
.claude-plugin/ .codex-plugin/ .qoder-plugin/ .github/plugin/
                       plugin-tier manifests (RFC-0007 Phase 1/3)
gemini-extension.json  points Gemini CLI at AGENTS.md
opencode.json          points OpenCode at .opencode/plugins/instinct.mjs
plugin.yaml + __init__.py
                       Hermes Agent plugin (root-level, per Hermes convention)
hooks/                 SessionStart/SubagentStart (Claude Code, Codex),
                       Copilot- and Qoder-specific equivalents, shared
                       SKILL.md-reading logic (hooks/lib.js)
instinct-mcp/          MCP server (prompt + tool) for hosts with no
                       file-based rule mechanism — its own npm package
.opencode/plugins/     OpenCode server plugin
pi-extension/          pi editor extension
references/            detail SKILL.md defers to when a Critical-tier
                       request actually needs it
scripts/
  check_adapters.py    sync checker — all adapters vs. SKILL.md
  check_versions.py    every host manifest's version field must agree
  generate_adapters.py regenerates the plain-markdown adapters from AGENTS.md
  test_all.py          runs the entire suite in one local command
tests/                 pytest suite for the tooling itself (85 tests),
                       plus instinct-mcp/test/ and pi-extension/test/
                       (6 more, Node) — 91 total
eval/
  corpus/              labeled scenarios (RFC-0005) — what "correct" means,
                       locked before SKILL.md was written (ADR-0009)
  run.py               the corpus runner — stub, real Anthropic, and
                       OpenAI-compatible backends
docs/
  rfcs/                design proposals — the "what and why"
  adrs/                point-in-time decisions and the alternatives that lost
  installation.md      per-host setup, confirmed vs. inferred
  known-failure-modes.md  specific scenarios that have actually fooled
                       real models, with dates, models, and fixes
  ROADMAP.md           the live task list — what's done, open, and why
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
N=3) → `docs/rfcs/0007` (multi-platform distribution), preceded by
`docs/adrs/0012-defer-platform-adapters-pending-rfc.md`, which explains why
that RFC exists instead of a batch of adapter files. Each RFC's `Depends
on` / `Blocks` header lines say why that order, and each has one or more
ADRs immediately after it in `docs/adrs/` covering the sharpest calls
inside it — read the RFC first, the ADRs are the "why not the obvious
alternative" footnotes, not prerequisites.

If you just want the artifact itself rather than the reasoning behind it:
[`skills/instinct/SKILL.md`](skills/instinct/SKILL.md), then `references/`
only if a Critical-tier example doesn't make sense on its own.

## Contributing

This project holds itself to one standard throughout its own history: every
"sync," "verification," or "confirmed" claim has actually been run,
including proving the negative case (a checker is tested to confirm it
*catches* drift, not just that it passes when nothing's wrong). Read
[`CLAUDE.md`](CLAUDE.md) for the working norms this repo has accumulated
before assuming something is undecided — it's written for exactly that
purpose.

## License

MIT — see [`LICENSE`](LICENSE).
