# Installing Instinct

Every host's setup step currently lives as a comment inside the file that
needs it (`hooks/qoder-hooks.json`'s `_comment`, the header of
`.opencode/plugins/instinct.mjs`, `instinct-mcp/README.md`) — reasonable
for whoever wrote that file, but there was nowhere a new user could see
all of them at once. This page collects them. Reverse-engineered from the
same problem Ponytail's own after-install.md solves for Hermes
specifically: an install that requires a manual activation step and
documents that step nowhere general-purpose is indistinguishable, from
the user's side, from a broken install.

Confidence varies by host, and this page says which is which:
**confirmed** means the mechanism has actually been run and its output
inspected (see the relevant `docs/ROADMAP.md`/`docs/rfcs` entry).
**Inferred** means it follows directly from a host's documented plugin
contract or from Ponytail's own working install path for the same host,
but hasn't been run against real host software from inside this
environment — say so rather than assert it confidently, per this
project's own verification standard.

## File-based hosts (read `AGENTS.md`-derived content automatically)

These need no install step beyond having the file present at the path the
host already scans by convention. If you're vendoring Instinct into a
different project (not developing this repo itself), copy the one file
your host needs into that project:

| Host | File to copy | Confidence |
|---|---|---|
| Cursor | `.cursor/rules/instinct.mdc` | confirmed present, untested against real Cursor |
| Windsurf | `.windsurf/rules/instinct.md` | confirmed present, untested against real Windsurf |
| Kiro | `.kiro/steering/instinct.md` | confirmed present, untested against real Kiro |
| Cline | `.clinerules/instinct.md` | confirmed present, untested against real Cline |
| GitHub Copilot (in-editor) | `.github/copilot-instructions.md` | confirmed present, untested against real Copilot |
| Qoder (instruction-tier) | `.qoder/rules/instinct.md` | confirmed present, untested against real Qoder |
| Antigravity, CodeWhale, Swival, Amp, Jules, Zed, VS Code Codex ext., JetBrains Junie, generic agents | `AGENTS.md` at repo root | inferred from each host's own docs, via Ponytail's docs/agent-portability.md (its own host matrix — see the "RFC-0007 Phase 3" entry in `docs/ROADMAP.md` for what was reverse-engineered from it) — likely works with zero extra file, unverified |

All of these are kept byte-identical to `skills/instinct/SKILL.md` by `scripts/check_adapters.py` — if you hand-edit one, it will fail CI, not silently drift.

## Claude Code

Two options:
1. **As a plugin**: `claude plugin marketplace add <path-or-repo>` then `claude plugin install instinct@instinct`. This wires up `hooks/hooks.json` automatically — `SessionStart` and `SubagentStart` fire without further setup. **Confirmed working with the real `claude` CLI**, not just inferred: `claude plugin install` from a local marketplace add, `claude plugin list --json` showing `"enabled": true`, and the installed cache directory
   (`~/.claude/plugins/cache/instinct/instinct/<version>/`) physically containing all 5 `skills/*/SKILL.md` directories and `hooks/` intact. This replaces an earlier, overclaimed status here — "confirmed working, this is how it's been developed and tested throughout" previously meant the hooks were run standalone via `node` and `skills/instinct/SKILL.md`'s text was pasted into Agent-tool prompts, which is not the same as the plugin actually installing. It didn't: the plugin failed to load the first time this was actually tried (see the `hooks/hooks.json` note below). Installing at `--scope user` (the default) applies the ambient Gate to *every* Claude Code session on the machine, not just this repo — pass `-s project` or `-s local` to scope it instead.
2. **As a skill only**: `skills/instinct/SKILL.md`'s own frontmatter `description` is broad enough to self-trigger without the plugin, but without the hooks it's subject to Claude Code's own matching (can silently not fire) — the plugin path is the one actually exercised and now actually confirmed.

**Real bug found and fixed by actually installing it**: `.claude-plugin/plugin.json` used to declare `"hooks": "./hooks/hooks.json"` explicitly. Claude Code auto-discovers `hooks/hooks.json` by convention already — an explicit field pointing at that exact same default path isn't redundant-but-harmless, it's a hard load failure ("Duplicate hooks file detected"). Ponytail's own manifest avoids this by naming its hooks file something else (Ponytail's hooks/claude-codex-hooks.json); fixed here by dropping the field and relying on auto-discovery, the same way `skills/` already does.

## Codex

`.codex-plugin/plugin.json` reuses `hooks/hooks.json` unchanged (confirmed: Codex and Claude Code share one hook contract, see `docs/ROADMAP.md`'s RFC-0007 Phase 3 entry). Install mechanism (how a `.codex-plugin/` manifest actually gets registered with a running Codex instance) is **inferred from the manifest format, not run against real Codex** — this environment has no Codex install to test against.

## GitHub Copilot CLI

`.github/plugin/plugin.json` + `.github/plugin/marketplace.json` + `hooks/copilot-hooks.json`. Ponytail's own documented install command for the same plugin shape is:
```
copilot plugin marketplace add <owner>/<repo>
copilot plugin install instinct@instinct
```
**Inferred, not run** — this repo has no configured git remote yet, so there's no real `<owner>/<repo>` to substitute or test against. The `isCopilot` output-shape branch in `hooks/lib.js` (unwrapped `additionalContext`, only on `SessionStart`) is confirmed correct by direct testing (`tests/test_hooks.py`); the marketplace-install mechanism itself is not.

## Qoder (plugin-tier)

`.qoder-plugin/plugin.json` points at `hooks/qoder-hooks.json`, which is a **template, not a ready-to-use config** — its own `_comment` field says so. Run:
```bash
python scripts/render_qoder_hooks.py /absolute/path/to/this/checkout
```
and paste the printed `"hooks"` object into your `.qoder/settings.json` (or `~/.qoder/settings.json` for a global install). Omit the argument to use this checkout's own path. Handles both Unix- and Windows-style paths correctly — the naive version (string-substitute and hope) breaks on Windows, since `Path.resolve()`'s backslashes are invalid JSON escapes once substituted into the template; confirmed by actually hitting that crash while building this script, not by inspection.

## Gemini CLI

`gemini-extension.json` at repo root, pointing `contextFileName` at `AGENTS.md`. **Inferred** that Gemini CLI auto-loads this from a project root or an extensions directory (per Ponytail's docs/agent-portability.md's row for this host, reverse-engineered into `docs/ROADMAP.md`) — not run against real Gemini CLI.

## OpenCode

Add to your project's `opencode.json`:
```json
{ "plugin": ["<path-to-this-checkout>/.opencode/plugins/instinct.mjs"] }
```
This repo's own root `opencode.json` already does this for itself. The plugin's `config()`/`experimental.chat.system.transform` hooks are confirmed correct by directly invoking them with a mock host object (`tests/test_opencode_plugin.py`); OpenCode actually loading the manifest and calling those hooks the same way is inferred, not run.

## pi editor

`pi-extension/index.js`, structured to match pi's `before_agent_start` hook contract. **Inferred** install path (pi's own package.json `pi.extensions` convention, seen in Ponytail's real root `package.json` — Instinct's `pi-extension/package.json` doesn't declare this field yet since it isn't published anywhere pi could discover it that way; see "What's still missing" below). The extension's own hook logic is confirmed correct via `pi-extension/test/` with a mock `pi` host object.

## Hermes Agent

Root `plugin.yaml` + `__init__.py`. Per Ponytail's own after-install.md for this exact host:
```bash
hermes plugins install <owner>/<repo>
hermes plugins enable instinct   # only if not installed with --enable
```
Then **restart Hermes or the gateway**. This enable step is easy to miss and looks identical to "nothing happened" if skipped — flagging it here explicitly rather than leaving it as an assumption. Unlike Ponytail's Hermes plugin, Instinct's has no mode state at all, so the "shared-gateway, process-local state" hazard Ponytail's after-install.md warns about doesn't apply here — there's nothing for one user's session to affect another's.

## MCP hosts (no file-based rules, no hook lifecycle)

Point an MCP client config at `instinct-mcp/index.js`:
```json
{ "mcpServers": { "instinct": { "command": "node", "args": ["instinct-mcp/index.js"] } } }
```
Requires `cd instinct-mcp && npm install` first. Confirmed working end-to-end against the real `@modelcontextprotocol/sdk` client (see `docs/ROADMAP.md`'s RFC-0007 Phase 3 entry) — this is the most rigorously tested install path of any host that isn't Claude Code itself, precisely because it was the easiest to test without needing the real external host installed.

## What's still missing

None of the plugin-tier hosts can currently be installed by a third party without cloning this whole repository and hand-editing an absolute path into their own config. Ponytail solves this by being a real, published npm package — its root `package.json` has `main`/`exports` fields and a `pi` field that let hosts auto-discover it once installed via `npm install ponytail`, and a `files` field controlling exactly what ships. Instinct's `instinct-mcp/` and `pi-extension/` are both `"private": true` and published nowhere, so every install path above requires a local checkout. Fixing this for real means publishing at least `instinct-mcp` (and possibly a root package for `pi`/`opencode` auto-discovery) to npm — deliberately not done speculatively here; see `docs/ROADMAP.md` for why, and what would need to be true before it's worth doing.
