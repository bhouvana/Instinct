# Roadmap

Sequencing rationale: philosophy has to exist before mechanism, mechanism
before prompt text, prompt text before it can be evaluated, evaluation
before benchmarks mean anything, and the core skill has to be validated
before it's worth multiplying across platforms. Each stage is a hard
dependency of the next; skipping ahead has been considered and rejected
more than once (RFC-0001's Forward Plan; ADR-0012).

## Design phase

- [x] **RFC-0001 — Charter.** Philosophy, problem statement, guardrails,
      relationship to prior art, success criteria.
- [x] **RFC-0002 — Prompt Architecture.** Broad trigger with an in-body fast
      exit (ADR-0003), single ambient skill for v1 (ADR-0004), draft
      `name`/`description` frontmatter, style law, composability rules.
- [x] **RFC-0003 — Mechanism Design.** The Gate (three yes/no questions),
      two tiers past it (ADR-0005), escalate-on-uncertainty (ADR-0006),
      tier-specific behavior for all three pillars, a resolved default for
      provenance-deposit, and three worked examples.
- [x] **RFC-0004 — Evaluation Methodology.** Four layers (trigger accuracy,
      Gate accuracy, decision-quality proxies, felt outcome), real-session
      substrate (ADR-0007), human review as scoring authority for the two
      layers that aren't machine-checkable (ADR-0008), a Goodhart guardrail.
- [x] **RFC-0005 — Testing Strategy.** Operationalizes RFC-0004's cheap
      Layers 1/2 into an automated suite. Corpus locked before the first
      implementation draft existed (ADR-0009).
- [x] **RFC-0007 — Multi-Platform Distribution.** Designs the adapter layer
      (`AGENTS.md` + instruction-tier copies) grounded in Ponytail's actual
      architecture: `SKILL.md`'s body as the one canonical source,
      consolidation instead of pointers for always-on hosts, sync
      verification, a three-phase rollout. Written *because* the obvious
      path (just build ten adapter files on request) was rejected — see
      ADR-0012. Its own Forward Plan sequences Phase 1 after real
      evaluation, not before.

## Implementation phase

- [x] Scenario corpus (`eval/corpus/*.yaml`) authored and locked before any
      `SKILL.md` draft existed, per ADR-0009.
- [x] `SKILL.md` — the Gate, Bug fixes, Verification, Consequential/Critical
      tiers, Never/Scope closers. Hardened twice past the v1 audited in
      RFC-0006: once from a direct read of Ponytail's instruction text
      (root-cause and verification-check rules, ADR-0011), once from a real
      bug an independent model found in the Gate itself (public-facing
      surfaces wrongly reading as automatically Critical, RFC-0008) —
      fixed and re-verified against a second fresh model, closed-loop.
- [x] Reference files — `references/ladder.md`,
      `references/provenance-out.md` (collapsed from three files to two
      during writing, ADR-0010; provenance-out gained the `instinct:`
      marker convention, ADR-0011).
- [x] Manual dry run of the pre-hardening v1 draft
      (`docs/rfcs/0006-skill-v1-dry-run.md`) — two gaps found and fixed,
      one ambiguity deliberately left for real evaluation rather than
      patched on the author's own say-so. **Superseded** by RFC-0008, which
      is what that deferred ambiguity turned into once actually tested.
- [x] **Corpus runner** (`eval/run.py`) — loads the corpus, runs it through
      a pluggable `Backend`, reports pass/fail, non-zero exit on failure.
      `StubBackend` (keyword heuristic, proves the harness not the skill)
      verified working. `ApiBackend` (real Anthropic SDK call) is
      implemented and fails loudly without a key rather than silently, but
      is **unexercised** — no `ANTHROPIC_API_KEY` in this environment.
- [x] **First independent evaluation** (`docs/rfcs/0008-first-independent-evaluation.md`)
      — 6 of 21 corpus scenarios, chosen for information density (the three
      adversarial Gate cases plus all three worked examples), run against
      fresh model instances via the Agent tool rather than `ApiBackend`
      (no API key available). Found and fixed one real bug, confirmed the
      fix against a second fresh model. The other 15 scenarios, and any
      trigger-corpus coverage at all, remain unexercised by real evaluation.
- [x] **`OpenAICompatBackend`** — generic backend (stdlib `urllib` only, no
      new dependency) for any OpenAI-chat-completions-shaped host, sharing
      its response-parsing logic with `ApiBackend` via a new `ModelBackend`
      base class instead of duplicating it.
- [x] **Full corpus run, for real** (`docs/rfcs/0009-ollama-cloud-corpus-run.md`)
      — all 18 trigger + gate_tier scenarios, against Ollama Cloud's
      `gpt-oss:120b`. Found and fixed two harness bugs along the way
      (reasoning-model token-budget truncation; one bad response crashing
      the whole run instead of failing just that scenario). Dominant
      finding was the *backend's* unreliability — confirmed non-determinism
      on identical zero-temperature calls — not a clean read on Instinct's
      Gate accuracy. One real signal survived the noise: `gt-07` has now
      disagreed with its label on 3 separate independent passes across two
      models; the RFC-0008 fix measurably helped (Tier 3 → Tier 2) but
      didn't fully close it.
- [x] **`--samples N` repeat sampling** added to `eval/run.py` (majority
      vote + `k/n` agreement string), directly motivated by RFC-0009's
      single-pass ambiguity. RFC-0004 amended to require N≥3 for any
      reported Layer 1/2 result going forward.
- [x] **Second real regression found and fixed**
      (`docs/rfcs/0010-repeat-sampling-and-regression.md`) — repeat
      sampling turned `gt-07`'s disagreement into a confirmed 3/3 on
      Ollama, and cross-checking against Claude (still via the Agent tool,
      no Anthropic key) found the RFC-0008 fix's own wording ("additive...
      is usually a no") was being misapplied to justify *not* escalating
      the project's own canonical Tier-3 example (`gt-03`, a required-
      parameter breaking change). Fixed by naming the actual test
      (does an existing caller have to change anything) instead of leaning
      on the word "additive." `gt-07` looks stable after the fix (2/2 clean
      on re-check); `gt-03` improved but is **not yet confirmed stable** —
      5 total samples across two wordings isn't enough, and one was
      internally self-contradictory.
- [x] **`gt-03` resolved** (`docs/rfcs/0011-gt03-resolution.md`) — 10/10
      fresh Claude samples, unanimous Tier 3, clean reasoning, several
      quoting the RFC-0010 fix's own language. First evaluation pass in
      the project run at the N≥3 standard RFC-0004 itself now requires.
      Scoped honestly: closes this one scenario on this one model via
      Agent-tool spot checks — does not stand in for a full-corpus pass.
- [x] **Full-corpus pass at N=3, cheap path** (`docs/rfcs/0009` addendum) —
      one batch Bash call through `eval/run.py --samples 3` against Ollama,
      not per-scenario Agent-tool spawns (~65K tokens each, confirmed too
      expensive for blanket re-verification). 9/10 trigger, 2/8 clean
      gate_tier; new disagreements on `gt-02`/`gt-05`/`gt-08` deliberately
      *not* chased further — they don't show the repeatable, cross-model
      pattern that made `gt-03`/`gt-07` worth fixing, just this backend's
      known general unreliability. Still true: no Claude-side full-corpus
      pass exists, only the properly-sampled subset (`gt-03`, `gt-07`,
      RFC-0008's cases).
- [ ] **Run the corpus through `ApiBackend`** (Claude) the moment an
      Anthropic key is available — would replace ad hoc Agent-tool spot
      checks with the automated, repeatable path `eval/run.py` was built
      for.
- [x] **Judgment regression suite, wired and ready** — scoped and built in
      response to a direct question about whether Instinct's judgment
      mechanism itself (not the distribution plumbing) has real evidence
      behind it, comparable to Ponytail's issue history and benchmark
      suite. The honest answer was no: two real bugs found via ~20
      scenarios sampled a handful of times isn't in the same league. This
      closes the *readiness* gap, not the *evidence* gap, which still needs
      an actual key:
  - `.github/workflows/test.yml` now runs `eval/run.py --backend api
    --samples 3` on every push and PR, gated on an `ANTHROPIC_API_KEY`
    repository secret — skips cleanly with an explicit message if unset
    (true today), turns on with zero further engineering the moment one is
    added. Verified the skip branch actually behaves as written, and
    confirmed `ApiBackend`'s own missing-key/missing-package guard is a
    real fallback net if the CI conditional ever has a bug, not just
    reasoned about.
  - **Pass/fail policy written down**, not left implicit: N≥3 majority
    vote per RFC-0004's amendment, a disagreement hard-fails the build (no
    warn-only mode — a regression suite that can be ignored is a
    suggestion), and a failure means investigate using
    `docs/known-failure-modes.md`, not auto-revert. See `eval/README.md`.
  - **`docs/known-failure-modes.md`** — consolidates `gt-03`'s and
    `gt-07`'s actual regression history (dates, models, sample counts,
    resolution) out of the RFC-0008–0011 narrative and into one scannable
    file, distinct from the corpus's own `note` fields (which explain what
    a case targets, not what's actually happened when a real model saw
    it). Explicitly states what it doesn't cover: every other adversarial
    case has real reasoning but has only been sampled once or twice,
    mostly against the confirmed-noisy Ollama backend.
  - **Deliberately not done**: padding the 21-scenario corpus toward
    "hundreds." New labels need the same real-model verification the
    regression suite itself needs — authoring more scenarios without a way
    to verify them would be volume without evidence, the same trap flagged
    when this work was scoped.
  - Fixed `eval/README.md`'s stale claim that `ApiBackend` "raises
    NotImplementedError" — it's been a real implementation since RFC-0009;
    the doc had drifted from the code.
- [x] **A real Gate bug found and fixed the same day the suite was scoped** —
      before the CI path had a key to run through, two independent
      Agent-tool samples (fresh Claude, not stub or Ollama) covering the
      full 18-scenario trigger + gate_tier corpus found: 10/10 trigger
      correct in both samples (the strongest trigger evidence yet), 5/8
      gate_tier scenarios clean in both, and one real, consistent
      disagreement — `gt-07` landing on Tier 2 instead of 1 in both
      samples, via `Q2` ("more than one consumer") reading a public
      endpoint's end-user traffic as equivalent to a code-level interface
      dependency. Distinct from the Q3-based bug RFC-0008 already fixed for
      the same scenario ID. Fixed with a parallel Q2 carve-out in
      `SKILL.md` (public/heavily-used surface isn't automatically a yes to
      Q2 either), propagated to `AGENTS.md` and all 7 adapters, verified
      back in sync. Re-verified with two more fresh samples: `gt-07` now
      reads Tier 1 in both, and a paired non-regression check against
      `gt-02`/`gt-06` (genuinely Tier 2 via explicit stated reuse / two
      explicit callers) confirmed the tightened wording didn't overcorrect.
      Full writeup, plus two more real findings from the same run
      (`gt-01`/`gt-05`'s trigger-assumption methodology gap, and a watched-
      not-confirmed `trg-04` payment-proximity disagreement) in
      `docs/known-failure-modes.md`. ~306K tokens total across the four
      Agent calls this took (two 18-scenario batches, two 3-scenario
      re-verifications) — a real cost data point for whether Agent-tool
      spot-checks scale as the corpus grows, not just for CI-with-a-key.
- [x] **Layer 3/4 pilot, N=1** (`docs/rfcs/0012-layer34-pilot.md`) — one
      task, run twice (baseline vs. Instinct-loaded) in isolated worktrees
      against this repo's own now-real history. Clean contrast: baseline
      wrote a plausible file; Instinct-loaded found RFC-0007's specific
      prior design (consolidation not pointers), matched it, and flagged
      the Phase-1/2 sequencing gap once instead of ignoring it. One
      anecdote, not a validated pattern — real Layer 3/4 still needs many
      tasks and human review.
- [x] **Real-repo pilot, 3 tasks** (`docs/rfcs/0013-real-repo-pilot.md`) —
      against `tiangolo/full-stack-fastapi-template` (same repo Ponytail's
      own agentic benchmark uses), one task per pillar (reuse, breaking-
      change judgment, root-cause fix), verified against real code, not
      invented bugs. Consistent pattern across all three: Instinct-loaded
      added a test baseline didn't, plus a real security catch (CSV-
      injection guard) baseline missed entirely. 3 data points, not a
      proven property — repeat sampling for Layer 3/4 tasks is still an
      open methodology gap, same as RFC-0004 Layer 1/2 was before RFC-0009.
- [ ] RFC-0004 Layers 3/4, properly powered (many tasks, multiple repos,
      blinded human review, repeat-sampled, per ADR-0007/0008) — two
      pilots now (RFC-0012 N=1, RFC-0013 N=3) prove the setup and show a
      consistent early pattern; neither is the real program. Not started.
- [x] **RFC-0007 Phase 1** — `AGENTS.md` (canonical body consolidated with
      inlined Critical-tier detail instead of pointers), `.cursor/rules/instinct.mdc`
      as the one adapter template (real Cursor `.mdc` frontmatter,
      `alwaysApply: true`), and `scripts/check_adapters.py` verifying
      both against `SKILL.md`. The checker was proven both ways, not just
      run once green: confirmed it catches deliberately introduced drift
      (a one-word change), then confirmed clean again after reverting.
      Four rounds of real evaluation (RFC-0008 through 0011) plus two real
      pilots (RFC-0012, 0013) preceded this, per RFC-0007's own sequencing
      — this wasn't started until there was real evidence behind it.
- [x] **RFC-0007 Phase 2** — Windsurf, Kiro, Cline, GitHub Copilot added as
      thin, generated (not hand-typed) copies via `scripts/generate_adapters.py`,
      verified in sync by `check_adapters.py` (6 adapters total now).
      `.claude-plugin/plugin.json` + `marketplace.json` make this a real,
      installable Claude Code plugin, not just a loose `SKILL.md`.
- [x] **Real test suite** (`tests/`, pytest, 16 tests) for the tooling
      itself — `check_adapters.py` and `eval/run.py`. Found and fixed a
      real bug while writing it: the checker crashed instead of reporting
      cleanly when a path wasn't under repo root.
- [x] **Companion skills** — `skills/instinct-review` (audit an
      already-made diff against the Gate) and `skills/instinct-help`
      (quick reference), explicit-invocation only, matching Ponytail's
      review/help pattern. Root `SKILL.md` deliberately left where it was
      at the time rather than moved under `skills/instinct/` to match
      convention — that structural question is now resolved, see below.
- [x] **Reverse-engineered Ponytail's CI + hooks, adopted what transfers**
      (incremental, not a big upfront doc — see commit history):
  - **ADOPT (adapted): `hooks/instinct-activate.js`, a `SessionStart` hook.**
    Why it exists in Ponytail: description-matching alone can silently
    fail to load a skill for a given session — a false negative with no
    error. A `SessionStart` hook sidesteps that non-deterministically-
    matched path entirely by guaranteeing injection every session. This
    doesn't replace Gate accuracy (still RFC-0008–0011's job) — it only
    guarantees the Gate is present to run at all, closing a real gap
    RFC-0002/ADR-0003 reasoned about but never fully closed. Adapted, not
    copied: dropped Ponytail's intensity-mode/statusline-nudge layer,
    since Instinct has no modes to track yet. Verified against
    `claude-code-guide` for the actual hook I/O contract before writing
    it, not guessed — and found a real bug in the first version (sync
    markers leaking into the injected context) via manual testing before
    it was ever committed. `SubagentStart` was investigated and is
    **not** used for the equivalent purpose: confirmed it doesn't support
    context injection (observability/gate use only), so the "paste
    SKILL.md into every Agent prompt" pattern from RFC-0008 onward remains
    the correct approach for subagents, not a gap to close.
  - **ADOPT (adapted): CI workflow** (`.github/workflows/test.yml`) —
    Python + Node setup, `check_adapters.py`, plugin-manifest JSON
    validation, `pytest`. Every step verified to actually pass locally
    before committing, not assumed from the YAML alone.
  - **ADOPT: `.env.example`** — documents `eval/run.py`'s real env vars.
    Found and fixed a real gap while adding it: `.env` itself wasn't in
    `.gitignore` yet.
  - **REJECT (for now): `scripts/uninstall.js` equivalent.** Ponytail
    needs one because it installs itself across 25+ heterogeneous hosts
    with no uniform mechanism. Instinct doesn't have an equivalent
    "install into an arbitrary target project" flow to begin with — for
    Claude Code specifically, install/uninstall is already Claude Code's
    own plugin-manager job now that a real manifest exists. Building
    uninstall before install is solving half a problem backwards.
  - **REJECT (for now) — reopened and resolved below: `scripts/check-versions.js`
    equivalent.** Only one file carries a version number right now
    (`plugin.json`) — there's nothing to drift against yet. A version-sync
    checker with nothing to check is scaffolding, not verification, the
    same call already made for `AGENTS.md` before it existed (RFC-0007).
    **Update, after RFC-0007 Phase 3:** the premise changed. Phase 3 added
    six more version-bearing files (`.codex-plugin/`, `.qoder-plugin/`,
    `.github/plugin/`, `gemini-extension.json`, `instinct-mcp/package.json`,
    `plugin.yaml`) — there is now something real to drift against, the
    exact condition this reject said would justify building it.
    `scripts/check_versions.py` adopts Ponytail's `check-versions.js`
    directly: every version-bearing file must share one pinned `X.Y.Z`.
    `pi-extension/package.json` stays excluded, matching Ponytail's own
    checker exactly — it's a private, unpublished dev package with no
    version field to begin with, not an oversight. Confirmed the checker
    actually catches a mismatch (bumped one file to `0.2.0`, watched it
    fail, reverted, confirmed clean again), not just that it passes once.
    Wired into CI alongside `check_adapters.py`.
  - **ADOPT (adapted): `hooks/instinct-subagent.js`, a `SubagentStart`
    hook.** Closes a gap this project had been manually working around
    all session — a `SessionStart` hook's context is parent-thread only
    and never reaches Task-spawned subagents, so every evaluation agent
    since RFC-0008 needed `SKILL.md` pasted into its prompt by hand.
    Modeled on Ponytail's real `hooks/ponytail-subagent.js` /
    `ponytail-runtime.js` — reading their actual `writeHookOutput` source
    directly overturned an earlier, more conservative answer from
    `claude-code-guide` claiming `SubagentStart` doesn't support context
    injection. Real, shipped, tested code from a mature project outweighed
    an uncertain documentation summary. Still honestly flagged: this has
    only been run standalone via `node`, never observed firing inside an
    actual live `SubagentStart` event in this environment — residual gap,
    not claimed as fully verified. Optional `INSTINCT_SUBAGENT_MATCHER`
    env var scopes injection by agent type; unset by default (injects
    into every subagent). Fails safe toward injection on unparseable
    stdin, matching ADR-0006's escalate-on-uncertainty direction —
    arrived at independently, same as Ponytail's own stated fail-safe
    logic. `hooks/lib.js` factored out once two hook scripts needed the
    same SKILL.md-reading logic (dogfooding the project's own
    "reuse before you add" rule on itself). 9 new/updated tests, all
    passing.
  - **REJECT: `hooks/ponytail-statusline.sh`/`.ps1` equivalent.** Read
    both scripts directly: they render `[PONYTAIL]` or `[PONYTAIL:MODE]`
    in the terminal statusline by reading a flag file that tracks which
    *intensity mode* (`lite`/`full`/`ultra`) the user has switched the
    session into via `/ponytail`. That flag file, and the mode concept it
    displays, doesn't exist in Instinct and isn't a gap to fill — ADR-0004
    already chose one ambient skill with no user-selected intensity levels
    for v1, the same reason `instinct-activate.js`'s docstring gave for
    dropping this layer when the SessionStart hook was adapted. There is
    no state for a statusline to show. Revisit only if/when Instinct grows
    actual modes, not before.
  - **DEFER (not reject) — superseded, see "RFC-0007 Phase 3" below: `ponytail-mcp/` equivalent.** Read `index.js`
    and its README: it's a real, generalizable answer to a problem
    Ponytail's docs name directly — MCP hosts whose *only* injection point
    is the prompt/tool menu, with no file-based rule mechanism and no
    hook lifecycle to piggyback on. That problem is real for Instinct too,
    but it's specifically the problem RFC-0007 Phase 3 (plugin-tier
    compatibility beyond Claude Code — Codex and others) already named and
    explicitly left unresolved, not a new discovery. Building the server
    now, ahead of deciding *which* hosts actually need it, would invert
    this project's own sequencing rule (mechanism after the RFC that
    justifies it, not before — see ADR-0012). It would also be this
    project's first real runtime dependency (`@modelcontextprotocol/sdk`,
    `zod`) — a cost worth taking only once a concrete host needs it, not
    speculatively. Left for Phase 3 to pick up.
  - **REJECT (already covered, more strongly): `scripts/check-rule-copies.js`
    equivalent.** Read it directly: it byte-compares AGENTS.md against each
    compact rule copy (same idea as `check_adapters.py`), then falls back to
    a list of hand-picked load-bearing phrase invariants to check that
    `skills/ponytail/SKILL.md` and `AGENTS.md` haven't silently diverged on
    wording — a workaround needed because Ponytail's `SKILL.md` and
    `AGENTS.md` aren't structurally tied together, so they can't be
    byte-diffed. `check_adapters.py` doesn't have that problem: RFC-0007's
    `instinct:shared`/`instinct:host-specific` markers make `SKILL.md`'s
    shared block and every adapter's shared block literally the same text,
    byte-compared already (`split_shared_and_host_specific` +
    `shared != skill_shared`). Byte equality is strictly stronger than a
    hand-picked phrase canary — anything an invariant list could catch, full
    equality catches too, with no list to keep in sync by hand. Nothing to
    adopt; confirmed by re-running `check_adapters.py` clean, not just by
    reading the code.
  - **REJECT (mode-tracking hook family): `hooks/ponytail-config.js`,
    `ponytail-instructions.js`, `ponytail-mode-tracker.js`,
    `ponytail-runtime.js`.** Read all four directly. Together they resolve
    a default mode (env var → config file → `full`), track which
    `off`/`lite`/`full`/`ultra`/`review` mode a session is in via a flag
    file, and filter `SKILL.md`'s body down to the active mode's rows
    before injecting it. Same ADR-0004 reasoning as the statusline reject:
    there is no mode state in Instinct for any of this to track or filter.
    One piece was flagged here, not adopted at the time, and has since
    been adopted for real (see "RFC-0007 Phase 3" below):
    `ponytail-runtime.js`'s `writeHookOutput` sniffs
    `COPILOT_PLUGIN_DATA`/`PLUGIN_DATA`/`QODER_SESSION_ID` env vars
    and shapes its JSON differently per host (Copilot wants
    `additionalContext` only on `SessionStart`; Codex wants a
    `systemMessage` plus `hookSpecificOutput`; Qoder wants
    `hookSpecificOutput` without `systemMessage`). `hooks/lib.js`'s
    `emitAdditionalContext` only knew the native-Claude-Code shape, which
    is correct today since Instinct's hooks only target Claude Code — this
    is real reference material for the day a Phase-3 host needs it, not a
    gap to close now.
  - **ADOPT (found and fixed a real bug): `tests/hooks-windows.test.js`'s
    stdin-never-closes regression test (issue #443 in Ponytail).** Read the
    test, then reproduced its exact scenario against
    `hooks/instinct-subagent.js` (spawn with a stdin pipe never written to
    or closed, with `INSTINCT_SUBAGENT_MATCHER` set so the hook's stdin-read
    path actually runs) before assuming it applied — it hung indefinitely.
    Root cause: `readStdinWithTimeout`'s fallback only resolved the
    internal promise on timeout; it never touched the still-open stdin
    pipe, and a pipe with active listeners keeps Node's event loop alive
    on its own regardless of what the application logic thinks is "done."
    Fixed by calling `process.stdin.destroy()` in the timeout branch
    alongside resolving the promise. Reproduced hanging before the fix,
    confirmed exiting at ~1s with correct, untruncated output after it
    (`hooks/instinct-subagent.js`, `tests/test_hooks.py`
    `test_subagent_hook_self_exits_when_stdin_never_closes`). This is the
    kind of bug that only shows up on hosts that don't close stdin
    promptly — plausible on Windows, per Ponytail's own account of the
    failure — and would otherwise have shipped silently, since every
    existing test closed stdin normally and none of them hit this path.
  - **ADOPT: `tests/hooks-windows.test.js`'s command-syntax checks
    (`tests/test_hooks_json.py`).** Ported the four static checks that
    aren't about the stdin bug — no cmd.exe `%VAR%` in `commandWindows`, no
    POSIX-only guard syntax in the shared `command`, no bash-only `exec`
    prefix and no dangling shell wrapper, every referenced script actually
    exists under `hooks/` — as pure-Python checks against
    `hooks/hooks.json`, since they're string patterns in JSON and need no
    Node. Confirmed they pass against the current file, then confirmed
    they actually catch injected drift (rewrote `commandWindows` to use
    `%CLAUDE_PLUGIN_ROOT%` and watched the `%VAR%` check fail), not just
    that they pass once. Kept in a separate file from `test_hooks.py`
    rather than added to it, since that file's Node-availability skip
    marker doesn't apply here — these checks have nothing to do with Node
    being on `PATH`.
  - **REJECT: `scripts/build-openclaw-skills.js` /
    `publish-openclaw-skills.js` equivalent.** Read both: they package
    Ponytail's skills for ClawHub, a third-party OpenClaw skill registry,
    and push them there with a dedicated CLI. Instinct has no ClawHub
    presence and no evidence of demand for one — unlike the AGENTS.md-only
    hosts noted above, this isn't "already covered for free," it's a
    distribution channel this project isn't on. Building publishing
    tooling for a registry with no consumer would be scaffolding, not
    verification.
  - **Spot-checked, nothing new: `.opencode/plugins/ponytail.mjs` (OpenCode
    server plugin), `commands/*.toml` (Codex custom-prompt format).** Both
    read directly. The OpenCode plugin injects the ruleset every turn via
    `experimental.chat.system.transform` and persists mode to a flag file
    beside OpenCode's own config — same mode-tracking pattern already
    rejected above, applied to yet another host. The Codex `.toml` commands
    are the same content Ponytail already ships elsewhere, reformatted for
    Codex's command format — the same "thin generated per-host copy"
    pattern `generate_adapters.py` already implements for Instinct's
    Markdown-based hosts, just a different file format. Neither reveals a
    mechanism not already captured by the Phase 3 scope note above or the
    mode-tracking-family reject; not spending further reads on `pi-extension/`,
    the Hermes `plugin.yaml`, or `gemini-extension.json` on the same basis —
    each is a plugin manifest for one specific host in that same narrowed
    Phase 3 list, not a new category of thing to decide on. This closes out
    the reverse-engineering pass at reasonable depth: everything in
    Ponytail that isn't a Phase-3-gated host plugin or its own benchmark/eval
    tooling (out of scope here) has now been read and given an explicit
    ADOPT/ADAPT/REJECT/DEFER call.
- [x] **RFC-0007 Phase 3 — built without waiting for an RFC.** This project's
      own sequencing rule (mechanism after the RFC that justifies it — the
      basis for every DEFER call recorded above) was explicitly overridden by
      direct instruction: told to build the deferred hosts and the MCP server
      now rather than wait. Reasoning recorded here in place of a dedicated
      RFC, per the same "brief record, not a full ADR for every one" standard
      already used throughout this log:
  - `gemini-extension.json` — zero new code, points `contextFileName` at the
    `AGENTS.md` Instinct already ships.
  - `.codex-plugin/plugin.json` — reuses `hooks/hooks.json` unchanged.
    Confirmed from Ponytail's own manifests that Claude Code and Codex share
    one hook contract; no new script or output branch needed.
  - GitHub Copilot CLI (`.github/plugin/`, `hooks/copilot-hooks.json`) — the
    one host needing a real code change: its contract wants
    `additionalContext` unwrapped and only on `SessionStart`, confirmed from
    Ponytail's `ponytail-runtime.js`. Added an `isCopilot` branch to
    `hooks/lib.js`'s `emitAdditionalContext` (env var `COPILOT_PLUGIN_DATA`),
    the nugget flagged and left unbuilt in the mode-tracking-family reject
    above, now actually adopted.
  - Qoder (`.qoder-plugin/`, `hooks/qoder-hooks.json`,
    `hooks/instinct-qoder-activate.js`, `.qoder/rules/instinct.md`) — the one
    host with no `SessionStart` event at all. Added a `UserPromptSubmit`
    hook that re-injects the Gate every prompt (no reliable session-boundary
    signal exists to do it only once — same tradeoff Ponytail's own
    mode-tracker accepts for this host) and reused `instinct-subagent.js`
    unchanged for the `PreToolUse`-matched subagent-equivalent path,
    confirmed safe from Ponytail's actual `ponytail-subagent.js` (it
    hardcodes `'SubagentStart'` as the output label regardless of the real
    triggering event). Also generated `.qoder/rules/instinct.md` as a proper
    adapter via `generate_adapters.py`/`check_adapters.py`, since the plugin
    manifest referenced a rules directory that didn't exist yet — now 7
    adapters in sync, not 6.
  - `instinct-mcp/` — the MCP server itself, the mechanism this project had
    called its "first real runtime dependency" as a reason to wait
    (`@modelcontextprotocol/sdk`, `zod`). Adapted from `ponytail-mcp/`: one
    prompt (`instinct`) and one tool (`instinct_instructions`), no mode
    argument since there's nothing to select between. `npm audit` flags a
    moderate transitive advisory in the SDK's optional HTTP transport
    (`@hono/node-server` path traversal on Windows) — not reachable here,
    since this server only ever uses `StdioServerTransport`. Verified
    end-to-end with the real `@modelcontextprotocol/sdk` client (not a
    hand-rolled JSON-RPC harness), spawning the actual server over stdio and
    calling both the prompt and the tool.
  - `.opencode/plugins/instinct.mjs` + root `opencode.json` — injects the
    Gate every turn via `experimental.chat.system.transform` and registers
    `skills/`. Verified by invoking the plugin's exported hooks directly
    with a mock host object: no duplicate skill-path registration across
    repeated `config()` calls, and the system-prompt transform correctly
    appends to (not replaces) an existing prompt.
  - `pi-extension/` — the smallest of the bunch once mode state, the
    status-bar indicator, and `/ponytail-*` command aliases were dropped
    (none apply here — pi already reads `skills/` directly per Ponytail's
    own `docs/agent-portability.md`). Verified the same way as the OpenCode
    plugin, with a mock `pi` host object, including the null-event edge
    case Ponytail's own extension guards against.
  - Root `plugin.yaml` + `__init__.py` — the Hermes Agent plugin. Same
    `register(ctx)` contract as Ponytail's, with mode state and gateway
    slash-command rewriting dropped. `provides_skills` originally listed
    only `instinct-review`/`instinct-help`, since at the time the Gate
    lived at root `SKILL.md` rather than `skills/instinct/` — now that the
    move below has happened, `register()`'s generic directory walk picks
    up `instinct` too, and `provides_skills` was updated to match.
    Verified with real Python execution via
    `importlib`, including that `register()` wires exactly the right skill
    names and hook onto a mock `ctx`.

  40 tests pass across the whole suite (`tests/`, `instinct-mcp/test/`,
  `pi-extension/test/`) after this phase, all added or extended in this
  pass, not carried over unchanged.
- [x] **Engineering-parity sweep** — on direct instruction to treat Ponytail
      as a production-engineering reference rather than an inspiration:
      read every remaining unexamined mechanism (root `package.json`,
      `.github/workflows/publish.yml`, `after-install.md`, and the test
      files for every host adapter Instinct now has an equivalent of —
      `qoder-plugin.test.js`, `gemini-extension.test.js`,
      `opencode-plugin.test.js`, `hermes-plugin.test.js`,
      `copilot-plugin.test.js`, `package.test.js`,
      `package-scripts.test.js`, `commands.test.js`,
      `behavior.test.js`/`correctness.test.js`, `ponytail-debt/SKILL.md`),
      decided ADOPT/REJECT/DEFER on each with the underlying failure mode
      named, and implemented+tested the real gaps immediately rather than
      batching the research:
  - **ADOPT: `scripts/test_all.py`.** Ponytail's root `package.json` runs
    its whole test suite (JS + two subpackages) with one `npm test`;
    Instinct had no equivalent single command, so reproducing CI locally
    meant reading the workflow YAML. Found a real bug writing it:
    `subprocess.run(["npm", ...])` fails on Windows with a bare
    `FileNotFoundError` (npm is a `.cmd` wrapper `CreateProcess` won't
    resolve without a shell) — fixed with `shutil.which()` resolution.
  - **ADOPT: `tests/test_ci_workflow.py`.** From
    `tests/package-scripts.test.js`, which exists because Ponytail's own
    aggregate test script and CI once silently stopped covering a
    subpackage. Scans the filesystem for `package.json` files with a test
    script (not a hardcoded list) and asserts each has a matching,
    correctly-ordered CI step and a reference in `test_all.py` — so a
    third subpackage added later fails loudly instead of silently passing
    around the part nobody wired up. Confirmed it actually catches drift
    (deleted a CI step in a throwaway mutation, watched it fail, restored
    via `git checkout`) — and hit a real PyYAML gotcha doing so: re-dumping
    parsed YAML turned the bare `on:` key into `true:`, restored from git
    rather than the round-tripped copy.
  - **ADOPT: `tests/test_manifest_completeness.py`.** From
    `qoder-plugin.test.js`/`copilot-plugin.test.js`/`gemini-extension.test.js`:
    a manifest can be valid JSON while its `skills`/`hooks`/`rules` field
    points at something that no longer exists, or a hooks config
    references a stale script name — neither is a JSON parse error.
    Found a real bug in the test itself while writing it:
    `str.lstrip("./")` strips a character set, not a prefix, so it silently
    ate the leading `.` off `.qoder/rules/` too. Caught by running it, not
    by inspection.
  - **ADOPT (fixed a real gap): Hermes plugin completeness.**
    `hermes-plugin.test.js` reads the actual `skills/` directory listing
    and cross-checks it against `plugin.yaml`, catching a new skill
    directory added but never registered. `test_hermes_plugin.py` only
    checked the other direction (every *listed* skill exists) — added the
    missing direction, confirmed it catches an unregistered skill dir via
    a throwaway mutation.
  - **ADOPT: `docs/installation.md`.** From `after-install.md` — an install
    needing a manual activation step, documented nowhere general-purpose,
    is indistinguishable from broken. Consolidates what was scattered
    across `hooks/qoder-hooks.json`'s `_comment`, a plugin file's header
    comment, and `instinct-mcp/README.md`, marking each host's confidence
    level (confirmed vs. inferred — most plugin-tier hosts have never
    actually been run from this environment) rather than presenting
    guesses with the same confidence as tested facts. Names the real
    unsolved problem: no plugin-tier host can be installed by a third
    party without cloning this repo, since nothing is published anywhere.
    `tests/test_doc_file_references.py` regression-tests its own path
    claims — caught two real mistakes while writing it (referencing
    Ponytail's own files as if they were this repo's) before they shipped.
  - **REJECT (precondition doesn't exist): `commands.test.js` equivalent.**
    Exists because a pi-registered command with no matching
    `commands/*.toml`/`.opencode/command/*.md` file drifted silently in
    Ponytail. Instinct's `pi-extension/` registers zero commands by design
    (ADR-0004: no command family for v1) — the failure mode needs a
    command-registration surface to drift from, and there isn't one.
  - **REJECT (already covered, differently): `behavior.test.js` /
    `correctness.test.js` equivalent.** These test whether Ponytail's own
    benchmark auto-grader can tell good code from bad for its curated
    tasks — infrastructure for its separate marketing/benchmark suite, out
    of scope per this project's own earlier decision to not chase
    Ponytail's benchmark tooling. The equivalent concern for Instinct's
    actual judgment corpus ("does the grading logic work") is already
    covered by `tests/test_eval_run.py` against `eval/run.py`.
  - **REJECT (nothing to harvest yet), later reopened and built:
    `ponytail-debt`/`instinct:` marker ledger.** Read
    `skills/ponytail-debt/SKILL.md`: it harvests every `ponytail:`
    shortcut-marker comment into a ledger so a deferral can't quietly
    become permanent. Instinct has the same underlying convention,
    narrower in scope (`references/provenance-out.md`'s `instinct:` marker,
    Critical-tier accepted-limitations only) — at the time, a repo-wide
    grep confirmed zero markers existed anywhere, so a harvester had
    nothing to check, the same scaffolding-not-verification call already
    made for `check-versions.js` before Phase 3. **Update**: on direct
    instruction to expand the skill family regardless (the "nothing to
    harvest yet" reasoning was about a *script* run automatically, not a
    reusable *skill* invoked on demand — `instinct-review` exists the same
    way for diffs that may not need it), built `skills/instinct-debt/`.
    Found a real bug in its own first draft by actually running the grep
    it instructs: a plain `grep -rn "instinct:"` returned two dozen false
    positives (docs, ADRs, the sync-marker's own regex source) because it
    wasn't anchored to a comment prefix — Ponytail's own
    `grep -rnE '(#|//) ?ponytail:'` already solved this correctly and
    hadn't been re-checked before adapting it. Fixed to anchor the same
    way, re-verified it returns zero matches against the real repo (still
    true — no debt yet, and now the skill would report that correctly
    instead of drowning it in noise).
  - **DEFER (no consumer yet): `.github/workflows/publish.yml` (npm
    trusted publishing via OIDC).** A genuinely good pattern — no stored
    npm token, provenance attached automatically, tag-triggered — but
    `instinct-mcp/` is `"private": true` and published nowhere. Building a
    secretless publish pipeline for a package nobody can install via a
    registry yet would be building a capability, not fixing a failure
    mode Instinct currently has. Tied to the same open question
    `docs/installation.md` names: real third-party installability needs
    actual npm publishing first, which is a product decision, not a
    hygiene one.
  - 63 tests pass after this sweep, all newly added or extended, not
    carried over.
- [x] **Turned the "10,000 users, 100 contributors" lens on this session's
      own new tooling, not just on Ponytail.** Auditing the sweep above
      immediately after finishing it (per the same directive: don't wait
      until done studying) found it had reproduced the exact gap it was
      supposed to close:
  - **Found: none of `test_ci_workflow.py`, `test_manifest_completeness.py`,
    or `test_doc_file_references.py` had a permanent failure-injection
    test** — each was proven to catch drift by hand, once, during
    development, then left with nothing guaranteeing the detection logic
    itself couldn't silently regress into a no-op (an inverted condition,
    a refactor that breaks the glob). `test_check_adapters.py` and
    `test_check_versions.py` already held themselves to this standard
    (`test_detects_real_drift`, `test_detects_real_mismatch`); the three
    new files didn't. Fixed by refactoring each into pure "find the
    problem" functions the pytest assertions call against the real repo,
    so a second set of tests could feed them synthetic bad data directly —
    including a test that pins the exact `lstrip("./")` bug found earlier
    as a permanent regression, not just an explanatory comment.
  - **Found: `hooks/instinct-qoder-activate.js` had no direct test at
    all** — only its script *name* being spelled correctly inside
    `qoder-hooks.json` was checked, never that running the script actually
    works, unlike `instinct-activate.js` and `instinct-subagent.js`, which
    both have dedicated tests. Added the same pair (emits valid JSON /
    fails silently when `SKILL.md` is missing).
  - **Found: `SKILL.md`'s "Read `references/ladder.md`... and
    `references/provenance-out.md`" instruction had nothing checking
    either file still exists.** A live instruction pointing at a path, one
    rename away from silently breaking Critical-tier behavior. Added to
    `test_check_adapters.py`.
  - **Found and fixed: real, unnecessary manual work.**
    `docs/installation.md`'s Qoder section named a real, currently-manual
    step (substituting `INSTINCT_DIR` by hand into a JSON template) as
    unautomated friction rather than closing it. Built
    `scripts/render_qoder_hooks.py` to remove it — and found a real bug
    running it with its own default argument on Windows:
    `Path.resolve()`'s backslashes are invalid JSON escapes once
    substituted into the template, a genuine crash, not a hypothetical
    one. Fixed by normalizing to forward slashes before substitution,
    pinned as a permanent test.
  - 81 tests pass after this pass — 18 added closing gaps in tooling that
    was itself less than a day old.
- [x] **`SKILL.md` moved to `skills/instinct/SKILL.md`, resolving the
      structural question deferred since RFC-0007 Phase 1/2.** Confirmed
      from Ponytail's own reference implementation, not guessed: its
      `.claude-plugin/plugin.json` has no `"skills"` field at all and no
      root `SKILL.md` anywhere — Claude Code auto-discovers
      `skills/*/SKILL.md` by convention alone, which is strong evidence
      the root location was never required, just where the file happened
      to start. Updated every path reference
      (`hooks/lib.js`'s `getSkillBody`, `scripts/check_adapters.py`,
      `eval/run.py`, the Hermes `__init__.py`) and the tests that hardcoded
      the old location. One real cascading effect, not just a rename:
      the Hermes plugin's `register()` already walked `skills/*` generically,
      so moving `SKILL.md` there makes it a registered, explicitly-invocable
      skill too (`instinct`, alongside `instinct-review`/`instinct-help`) —
      `plugin.yaml`'s `provides_skills` and its completeness test were
      updated to match, not left inconsistent. 81 tests still pass.
      Honestly flagged, not claimed: whether real Claude Code still loads
      the skill correctly from the new path is **inferred** from Ponytail's
      working example, not run against real Claude Code from this
      environment — same category as every other unverified host in
      `docs/installation.md`.
- [x] **Skill family expanded, on direct instruction, ahead of ADR-0004's
      original "prove the ambient mechanism first" precondition being
      fully met.** That precondition hasn't changed — still no
      properly-powered evaluation, still no real usage — but the call was
      made anyway, so the reasoning is recorded rather than silently
      overridden:
  - `skills/instinct-debt/` — see the reopened entry above.
  - `skills/instinct-audit/` — new, not a straight port. Ponytail's
    `ponytail-audit` is a whole-repo *over-engineering* sweep (find code to
    delete/simplify), which is Ponytail's own core mission scaled up and
    doesn't map onto what Instinct actually checks for. Designed instead
    as `instinct-review`'s question ("was this diff handled with the right
    scrutiny") asked at repo/history scale instead of one diff: scan
    recent commits for Critical-tier-shaped changes (removed public
    surface, new required parameter, deleted file others imported, a
    changed trust boundary) and check whether each one actually left the
    provenance `SKILL.md`'s Critical tier obligates — a tradeoff stated, an
    alternative named, a verification artifact — rather than just having
    happened.
  - **No `instinct-gain` equivalent, and none is planned.** Ponytail's
    version is a scoreboard pulled from its own real benchmark suite (LOC
    reduction, cost, speed across real runs). Instinct has deliberately
    not built benchmark tooling (see the earlier `behavior.test.js`/
    `correctness.test.js` reject) and "made a better decision" isn't
    obviously quantifiable the way "fewer lines of code" is — a skill that
    prints fabricated-looking numbers with no real measurement behind them
    would be exactly the "looks tested" theater this project argues
    against, not a fourth skill worth having.
- [x] **Real judgment evidence, not more plumbing** — on direct instruction
      to stop hardening infrastructure and grow the actual unproven part.
      Two concrete results, both from real fresh-Claude sampling, not
      authored guesses:
  - **Found and fixed a real bug in `eval/run.py` itself**, not just in
    `SKILL.md`. `classify_tier()` shared one prompt with `should_trigger()`
    that asked about triggering regardless of which one was being tested.
    `gate_tier.yaml` is Layer 2 by design (RFC-0005: "given it fired, what
    tier"), so when a fresh model reasonably answered "this wouldn't
    trigger" for `gt-01`/`gt-05` (both fully-specified single-step edits),
    there was no `TIER` line to parse — a bare `ValueError`, not a tier
    judgment, misrepresenting a measurement bug as a Gate failure. Fixed
    with a dedicated `_GATE_TIER_ONLY_PROMPT` that presupposes the skill
    is active and asks only for the tier, removing the confound instead of
    coercing an answer to a question `gate_tier.yaml` was never designed
    to ask. Added real unit test coverage for `ModelBackend` that didn't
    exist before (only `StubBackend` had any). Re-verified with two fresh
    samples using the new prompt: both `gt-01` and `gt-05` now cleanly
    resolve to Tier 1, matching their labels — see
    `docs/known-failure-modes.md`.
  - **Investigated and closed `trg-04`'s payment-proximity disagreement**
    rather than leaving it as a "watch this" item. Two more samples, same
    request but with the blast radius made explicit (no signature change,
    the payment-submission call itself unchanged), both cleanly agreed on
    Tier 1 — the opposite of a keyword-association bug. Conclusion: the
    original split traced to the request itself being genuinely
    underspecified, which is ADR-0006's escalate-on-uncertainty rule
    working as intended, not a defect. No `SKILL.md` change made — the
    honest finding here is "this wasn't actually a bug," which is real
    evidence too, not a null result.
  - Three more Agent-tool calls this pass (~208K tokens total), all with
    real, recorded outcomes in `docs/known-failure-modes.md` — the
    ongoing cost/evidence tradeoff this project has tracked since RFC-0009.
- [ ] Public release checklist — deferred until the above are stable.

## Explicitly deferred, not forgotten

- Whether the single-ambient-skill choice (ADR-0004) still holds once other
  plugin-tier hosts are in scope, now that RFC-0007 Phase 3 (below) has
  actually shipped several of them without any host needing more than one
  ambient skill. Real signal, not proof — no host-specific feedback exists
  yet since none of these adapters have a real user base.
- A dedicated Tier-1 maxim for Judgment or Efficiency (considered and
  deferred in ADR-0002 as a mechanism-design question, not a philosophy one).
