// Instinct — OpenCode plugin.
//
// Injects the Gate into every chat's system prompt and registers the
// skills/ directory so instinct-review and instinct-help are discoverable.
// Reuses hooks/lib.js's getSkillBody so every host reads one source of
// truth — the same file the Claude Code hooks and instinct-mcp already use.
//
// OpenCode loads this as a server plugin — add it to your opencode.json:
//   { "plugin": ["<path-to-this-repo>/.opencode/plugins/instinct.mjs"] }
// (this repo's own root opencode.json already does this for itself).
//
// Adapted from Ponytail's .opencode/plugins/ponytail.mjs: same
// experimental.chat.system.transform injection point and skills
// registration, with the mode-persistence layer dropped since Instinct has
// no modes to track (ADR-0004) — the Gate is the same text every turn,
// matching how the SessionStart hook behaves for Claude Code.

import { createRequire } from 'module';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// hooks/lib.js is CommonJS; bridge to it from this ES module.
const require = createRequire(import.meta.url);
const { getSkillBody } = require('../../hooks/lib.js');

export default async () => {
  const instinctSkillsDir = path.resolve(__dirname, '../../skills');

  return {
    // Register the skills directory so OpenCode can discover
    // skills/instinct-review and skills/instinct-help.
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(instinctSkillsDir)) {
        config.skills.paths.push(instinctSkillsDir);
      }
    },

    // Append the Gate to the system prompt every turn. There's no confirmed
    // session-boundary signal in OpenCode's plugin API to inject only once
    // instead — Ponytail's own equivalent plugin injects every turn too,
    // for the same reason its SessionStart hook can't be assumed to persist
    // OpenCode's system prompt array across turns on its own.
    'experimental.chat.system.transform': async (_input, output) => {
      const instructions = getSkillBody();
      if (output.system.length > 0) {
        output.system[output.system.length - 1] += '\n\n' + instructions;
      } else {
        output.system.push(instructions);
      }
    },
  };
};
