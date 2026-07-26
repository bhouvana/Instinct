#!/usr/bin/env node
/**
 * SubagentStart hook. Why this exists: a SessionStart hook's context is
 * parent-thread only and never reaches subagents — every Task-spawned
 * agent runs Instinct-unaware without this, which is exactly the gap this
 * project has been manually working around all session by pasting
 * SKILL.md's text into every Agent-tool prompt (see docs/rfcs/0008
 * onward). This closes it at the source instead.
 *
 * Modeled on Ponytail's hooks/ponytail-subagent.js — its own code (not a
 * doc describing it) confirmed SubagentStart uses the same
 * hookSpecificOutput.additionalContext contract as SessionStart, which
 * directly overturned an earlier, more conservative answer from
 * claude-code-guide before this was written. Real, shipped, tested code
 * from a mature project outweighed an uncertain documentation summary —
 * but this still hasn't been observed firing in an actual live
 * SubagentStart event from inside this development environment, only
 * run standalone via `node`. Flagging that residual gap rather than
 * overclaiming it's fully verified.
 *
 * Optional scoping via INSTINCT_SUBAGENT_MATCHER (a regex tested against
 * the spawned agent's `agent_type` from stdin) — unset by default, so
 * Instinct injects into every subagent unless someone deliberately narrows
 * it. Fail-safe direction matches ADR-0006 (escalate on uncertainty): if
 * agent_type can't be read or parsed, inject anyway rather than silently
 * dropping context — the same principle Ponytail's own version uses,
 * arrived at independently.
 */

const { getSkillBody, emitAdditionalContext } = require("./lib");

function readStdinWithTimeout(timeoutMs) {
  return new Promise((resolve) => {
    if (process.stdin.isTTY) {
      resolve(null);
      return;
    }
    let data = "";
    let settled = false;
    const finish = (result) => {
      if (settled) return;
      settled = true;
      resolve(result);
    };
    // Windows PowerShell stdin can hang with nothing to read; never let
    // that block subagent spawning — same detail Ponytail's version
    // calls out explicitly.
    const timer = setTimeout(() => finish(null), timeoutMs);
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => {
      data += chunk;
    });
    process.stdin.on("end", () => {
      clearTimeout(timer);
      finish(data);
    });
    process.stdin.on("error", () => {
      clearTimeout(timer);
      finish(null);
    });
  });
}

async function main() {
  const matcher = process.env.INSTINCT_SUBAGENT_MATCHER;
  if (matcher) {
    const raw = await readStdinWithTimeout(1000);
    let agentType = null;
    if (raw) {
      try {
        agentType = JSON.parse(raw).agent_type ?? null;
      } catch {
        agentType = null;
      }
    }
    if (agentType !== null && !new RegExp(matcher).test(agentType)) {
      return;
    }
    // agentType === null (missing/unparseable): fall through and inject.
  }
  emitAdditionalContext("SubagentStart", getSkillBody());
}

main().catch(() => {
  // Silent, deliberate: a broken hook must never block subagent spawning.
});
