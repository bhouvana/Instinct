#!/usr/bin/env node
// Instinct MCP server: serves the Gate over stdio as a prompt (user-invoked)
// and a tool (for hosts that pull context via tools). It does not replace
// the always-on adapters RFC-0007 already ships — it's the option for hosts
// whose only injection point is the prompt/tool menu, with no file-based
// rule mechanism and no hook lifecycle to piggyback on. Adapted from
// Ponytail's ponytail-mcp/index.js: same prompt+tool shape over the same
// SDK, with the mode argument dropped since Instinct has no modes (ADR-0004).
import { createRequire } from "node:module";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { buildInstructions } from "./instructions.js";

const require = createRequire(import.meta.url);
const { version } = require("./package.json");
const server = new McpServer({ name: "instinct", version });

server.registerPrompt(
  "instinct",
  {
    title: "Instinct",
    description:
      "The Gate and its tiers: whether a change is the right one and how much scrutiny it needs before implementation.",
  },
  () => ({
    messages: [{ role: "user", content: { type: "text", text: buildInstructions() } }],
  }),
);

server.registerTool(
  "instinct_instructions",
  {
    title: "Instinct instructions",
    description: "Return the Gate and its tiers.",
    outputSchema: { instructions: z.string() },
    annotations: { readOnlyHint: true, openWorldHint: false },
  },
  () => {
    const instructions = buildInstructions();
    return { content: [{ type: "text", text: instructions }], structuredContent: { instructions } };
  },
);

await server.connect(new StdioServerTransport());
