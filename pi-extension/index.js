// Instinct — pi editor extension.
//
// Injects the Gate into the system prompt via pi's before_agent_start
// event, the same injection point Ponytail's own pi-extension/index.js
// uses. Reuses hooks/lib.js's getSkillBody so every host reads one source
// of truth — the same file the Claude Code hooks, instinct-mcp, and the
// OpenCode plugin already use.
//
// Adapted, not cloned: Ponytail's version is ~180 lines because most of it
// is mode state, a status-bar indicator, and /ponytail-* command aliases
// forwarding to its skill family. Instinct has none of that (ADR-0004: no
// modes, no command family for v1) — pi already reads skills/ directly per
// Ponytail's own docs/agent-portability.md, so instinct-review and
// instinct-help need no alias commands here either.

import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { getSkillBody } = require("../hooks/lib.js");

export default function instinctExtension(pi) {
  pi.on("before_agent_start", async (event) => {
    // Guard a null/undefined event or a missing systemPrompt: don't crash,
    // and don't prepend the literal string "undefined" to the prompt —
    // the same edge case Ponytail's own extension guards against.
    const base = event?.systemPrompt ? `${event.systemPrompt}\n\n` : "";
    return { systemPrompt: `${base}${getSkillBody()}` };
  });
}
