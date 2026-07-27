#!/usr/bin/env node
/**
 * Qoder UserPromptSubmit hook. Why this exists: Qoder has no SessionStart
 * event at all, so there is no session-scoped injection point the way
 * instinct-activate.js uses for Claude Code and Codex. Ponytail's own
 * hooks/ponytail-mode-tracker.js documents this exact gap and works around
 * it by injecting on every UserPromptSubmit call instead. Instinct has no
 * mode to track, so this is that injection, without the mode-switching
 * logic that doesn't apply here.
 *
 * The cost is accepted deliberately, not overlooked: this re-emits the full
 * Gate on every single prompt, not once per session like instinct-activate.js
 * does for hosts with a real SessionStart event. There's no reliable
 * session-boundary signal available to inject only once instead — a
 * "first prompt" flag file would silently stop working the moment two
 * Qoder sessions share the same state path, which is a worse failure than
 * the repeated-injection cost. Revisit only if Qoder ships a real session
 * lifecycle event.
 *
 * Must never block the prompt: any failure here is caught and the hook
 * exits 0 with no output, same resilience principle the other hooks use.
 */

const { getSkillBody, emitAdditionalContext } = require("./lib");

try {
  emitAdditionalContext("UserPromptSubmit", getSkillBody());
} catch {
  // Silent, deliberate: a broken hook must never block the user's prompt.
}
