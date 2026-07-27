# instinct-mcp

An MCP server that serves Instinct's Gate — the same content the SessionStart
and SubagentStart hooks inject for Claude Code, and the same body every other
adapter (`AGENTS.md`, `.cursor/rules/instinct.mdc`, etc.) carries.

It is not a replacement for the always-on adapters. Instinct normally lives in
context from session start, independent of any explicit invocation. MCP
prompts are user-invoked, and there is no portable MCP primitive for "inject
this into every turn" across hosts. So this server is the option for MCP
hosts whose only injection point is the prompt menu, or that pull context
through tools, with no file-based rule mechanism and no hook lifecycle to
piggyback on (RFC-0007 Phase 3).

## What it exposes

- Prompt `instinct`, returns the Gate as a user message. No arguments —
  Instinct has no modes to select between (ADR-0004).
- Tool `instinct_instructions`, same text, plus `structuredContent`
  (`{ instructions }`), for hosts that pull context via tools or code
  execution. Read-only.

Both read `SKILL.md` directly via `hooks/lib.js`'s `getSkillBody`, the same
function the Claude Code hooks use, so every host gets identical rules.

## Run it

```bash
cd instinct-mcp
npm install
node index.js        # speaks MCP over stdio
```

Point an MCP host at that command. Example client entry:

```json
{ "mcpServers": { "instinct": { "command": "node", "args": ["instinct-mcp/index.js"] } } }
```

## Test

```bash
npm test
```

Covers the instruction text (frontmatter and sync markers stripped, Gate
present). The MCP wiring in `index.js` is intentionally thin: it just maps
the prompt and tool onto `buildInstructions`, and has been verified
end-to-end with the real `@modelcontextprotocol/sdk` client, not just by
reading the code.
