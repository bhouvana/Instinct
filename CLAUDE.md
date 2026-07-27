# Working notes for Claude sessions in this repo

Named `CLAUDE.md`, not `HANDOFF.md`, on purpose: Claude Code auto-loads
this file for every session opened here, so it's read automatically
instead of needing to be discovered — the strongest version of "same
knowledge, new conversation" available. If you're picking this project up
cold, read this file, then `docs/ROADMAP.md` (the live task list), then
whichever `docs/rfcs/*` the roadmap points you to for detail. Don't
re-derive decisions already made below — check here and in the RFCs
before concluding something is undecided.

## What this is, in 30 seconds

A Claude Skill that installs engineering judgment as a default instinct
rather than a persona or a checklist. Two compiled sentences carry the
philosophy: **"Engineering is not writing code. Engineering is making good
decisions"** (identity) and **"Every line of existing code was somebody's
answer to a question you haven't asked yet"** (operational maxim). The
mechanism is a three-question Gate (touches beyond what's named? more than
one consumer? expensive to undo?) plus two tiers past it (Consequential,
Critical). Full reasoning: `docs/rfcs/0001` through `0003`.

## Current state (check `git log --oneline` for the real up-to-date list)

Design (RFC-0001–0007) locked. `SKILL.md` implemented, dry-run audited,
then hardened twice more by real repeat-sampled evaluation — two real bugs
found and fixed (not hypothesized): public-facing surfaces misreading as
automatically Critical (RFC-0008), and the fix for that bug's own wording
("additive... is usually a no") getting misapplied to justify *not*
escalating a genuine breaking change (RFC-0010). Both confirmed via
independent fresh-model evaluation, the second one at N=10 unanimous
(RFC-0011). Two real-repo pilots (RFC-0012 N=1 on this repo, RFC-0013
3-task on `tiangolo/full-stack-fastapi-template`, the same repo Ponytail's
own benchmark uses) show a consistent pattern: Instinct-loaded sessions
add a verification artifact baseline skips, plus caught a real
CSV-injection issue baseline missed entirely.

Distributed to 7 file-based hosts (Claude Code, Cursor, Windsurf, Kiro,
Cline, Copilot, Qoder) via `AGENTS.md` as canonical body, kept in sync by
`scripts/check_adapters.py` (proven to actually catch drift, not just
pass once — see its own test in `tests/`). Real, installable Claude Code
plugin (`.claude-plugin/`). Hooks: `SessionStart`
(`hooks/instinct-activate.js`, guarantees the Gate loads every session
independent of skill-matching), `SubagentStart`
(`hooks/instinct-subagent.js`, closes the gap where subagents otherwise
run Instinct-unaware), and Qoder's `UserPromptSubmit`/`PreToolUse`
equivalents (Qoder has no `SessionStart` event). Two companion skills
(`skills/instinct-review`, `skills/instinct-help`), explicit-invocation
only.

RFC-0007 Phase 3 (plugin-tier hosts beyond Claude Code) is built, not
deferred anymore — done on direct instruction overriding this project's
own "RFC before code" sequencing rule. Covers Gemini CLI
(`gemini-extension.json`), Codex (`.codex-plugin/`, reuses
`hooks/hooks.json` unchanged), GitHub Copilot CLI (`.github/plugin/`,
`hooks/copilot-hooks.json`, a real new `isCopilot` branch in
`hooks/lib.js`'s `emitAdditionalContext` since its output contract
differs), Qoder's plugin-tier manifest, `instinct-mcp/` (a real MCP server,
this project's first runtime dependency — `@modelcontextprotocol/sdk` +
`zod`, verified end-to-end with the real SDK client over stdio, not just
unit-tested), an OpenCode server plugin (`.opencode/plugins/instinct.mjs`),
a pi editor extension (`pi-extension/`), and a Hermes Agent plugin (root
`plugin.yaml` + `__init__.py`). Every one of these was verified by actually
running it (spawning the process, invoking the exported hooks with a mock
host object, or a real SDK client), not just written and assumed correct.
40 tests total now, including `instinct-mcp/test/` and `pi-extension/test/`
alongside the main pytest suite (`tests/`, run via
`.github/workflows/test.yml`).

## Non-obvious things that will save you time

- **No Anthropic API key is available in this environment.** Don't try
  `eval/run.py --backend api` expecting it to work. The Agent tool
  (spawning fresh subagents with `SKILL.md` pasted in, or now via the
  `SubagentStart` hook once it's confirmed firing live) has been the
  working substitute for real Claude-side evaluation throughout.
- **A user-provided Ollama Cloud key was used for real backend testing**
  (RFC-0009–0011, `--backend openai-compat`). It was pasted directly in
  chat, which is why it's never been written into any file here — treat
  it as possibly rotated/invalid; don't assume it still works, ask before
  relying on it again.
- **`hooks/instinct-subagent.js`'s output contract was confirmed by
  reading Ponytail's actual shipped source code**, which directly
  overturned a more conservative answer from the `claude-code-guide`
  subagent claiming `SubagentStart` doesn't support context injection.
  Real, tested code from a mature project outweighed an uncertain doc
  summary. It's still only been run standalone via `node`, never observed
  firing in a real live `SubagentStart` event inside this environment —
  that's a residual gap, not fully closed.
- **Root `SKILL.md` is deliberately still at repo root**, not moved to
  `skills/instinct/SKILL.md` to match the layout the two companion skills
  and Ponytail itself use. Open question, not resolved — moving
  already-validated infrastructure on a guess about plugin-loading
  conventions was judged not worth the risk. See `docs/ROADMAP.md`.
- **Every "sync" or "verification" claim in this repo has actually been
  run, including proving the negative case** (e.g. `check_adapters.py`
  was tested to confirm it *catches* deliberately introduced drift, not
  just that it passes when nothing's wrong). Keep that standard — don't
  report something as working without having actually run it.

## How this user likes to work (learned this session, not guessed)

- Wants incremental loops — research one thing just enough to act, build
  it, test it, commit it, move on. Not big upfront analysis documents.
  Said explicitly: "if you spend more than one iteration only reading,
  you have spent too long researching."
- Cares about token efficiency concretely, not abstractly — e.g. shifted
  from ~65K-token-per-call Agent-tool spot checks to a single cheap batch
  script call once the cost became visible. Watch for cheaper paths to the
  same evidence.
- Wants real verification, not claimed verification — this repo's whole
  testing culture (proving checkers catch drift, proving hooks fail safe,
  manually inspecting a flagged transcript before trusting it) is the
  expected standard, not extra effort.
- Comfortable with autonomous ADOPT/ADAPT/REJECT/NEW calls on engineering
  mechanisms without being asked each time — wants the reasoning recorded
  briefly (commit message, ROADMAP line), not a full ADR for every one.
- Explicitly framed Ponytail as "a mature engineering system to reverse-
  engineer," not a project to copy — study why a mechanism exists, decide
  if Instinct needs an equivalent, adapt rather than clone.
- Pushes back on contradictions in their own instructions when there are
  any — pointing them out briefly and then resolving them is the right
  move, not silently picking one interpretation or stopping to ask.

## Where to actually look next

`docs/ROADMAP.md`'s open items are the real todo list — don't duplicate it
here, it changes too fast for this file to track. As of this commit, the
honest gaps are: no properly-powered Claude-side Layer 1/2 corpus pass, and
no properly-powered Layer 3/4 program (two pilots, not the real thing).

A full reverse-engineering pass over Ponytail happened before the Phase 3
build: statusline (reject, no mode concept), the mode-tracking hook family
(reject, its output-contract nugget later adopted for real in Copilot's
branch), `check-rule-copies.js` (already covered, more strongly),
OpenClaw/ClawHub (reject, no presence there). One real find came out of
that pass: reproducing Ponytail's own `hooks-windows.test.js`
stdin-never-closes scenario against `hooks/instinct-subagent.js` found a
genuine hang bug (an open stdin pipe kept Node's event loop alive even
after the internal timeout resolved) — fixed with `process.stdin.destroy()`,
regression-tested. Its command-syntax checks were also ported wholesale
into `tests/test_hooks_json.py`.

Everything that pass had deferred pending an RFC (the MCP server, Gemini,
Codex, Copilot CLI, Qoder, OpenCode, pi, Hermes) was then built anyway on
direct instruction — see `docs/ROADMAP.md`'s "RFC-0007 Phase 3" entry for
what shipped and how each piece was actually verified, not just written.
What's left of Ponytail's own surface: its benchmark/eval tooling, which
is out of scope here. What's left overall: the two big properly-powered
evaluation programs (Claude-side Layer 1/2 corpus, Layer 3/4) noted above,
untouched by this pass, and the still-open question of whether ADR-0004's
single-ambient-skill choice holds now that several plugin-tier hosts
actually exist (no real user feedback yet either way).
