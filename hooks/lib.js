/**
 * Shared logic for Instinct's hooks. Factored out once a second hook
 * (instinct-subagent.js) needed the exact same "read SKILL.md, strip
 * frontmatter and sync markers" logic instinct-activate.js already had —
 * the Consequential-tier rule this project's own SKILL.md states ("look
 * once for an existing pattern... reuse or extend it") applied to its own
 * hook scripts instead of a target codebase.
 */

const fs = require("fs");
const path = require("path");

function stripFrontmatter(text) {
  if (text.startsWith("---\n")) {
    const end = text.indexOf("\n---\n", 4);
    if (end !== -1) return text.slice(end + 5);
  }
  return text;
}

// SKILL.md carries scripts/check_adapters.py's sync markers so the sync
// checker can find the host-specific block. Those markers are maintenance
// metadata for that tool, not part of the rules — strip them so they
// never leak into what the model actually sees.
function stripSyncMarkers(text) {
  return text.replace(/<!-- instinct:(?:shared|host-specific):(?:start|end) -->\n?/g, "");
}

function getSkillBody(pluginRoot) {
  const root = pluginRoot || process.env.CLAUDE_PLUGIN_ROOT || path.join(__dirname, "..");
  const skillPath = path.join(root, "skills", "instinct", "SKILL.md");
  const raw = stripFrontmatter(fs.readFileSync(skillPath, "utf8"));
  return stripSyncMarkers(raw).trim();
}

// GitHub Copilot CLI sets this env var for its own plugins; confirmed from
// Ponytail's hooks/ponytail-runtime.js (isCopilot check), not guessed. Its
// hook contract differs from Claude Code/Codex/Qoder's, which all accept the
// same hookSpecificOutput-wrapped JSON (confirmed working for Claude Code by
// this project's own tests): Copilot wants additionalContext unwrapped, and
// only reads it on SessionStart — other events get an empty object, same as
// Ponytail's own contract for it.
const isCopilot = Boolean(process.env.COPILOT_PLUGIN_DATA);

function emitAdditionalContext(hookEventName, context) {
  if (isCopilot) {
    process.stdout.write(
      JSON.stringify(hookEventName === "SessionStart" && context ? { additionalContext: context } : {})
    );
    return;
  }
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: { hookEventName, additionalContext: context },
    })
  );
}

module.exports = { stripFrontmatter, stripSyncMarkers, getSkillBody, emitAdditionalContext, isCopilot };
