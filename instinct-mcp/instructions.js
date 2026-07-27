// Pure instruction accessor for the Instinct MCP server. No MCP/SDK imports,
// so this stays unit-testable on its own. Reuses hooks/lib.js's SKILL.md
// reader so every host gets identical rules, the same reuse-before-you-add
// rule the hooks already followed for each other.
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { getSkillBody } = require("../hooks/lib.js");

export function buildInstructions() {
  return getSkillBody();
}
