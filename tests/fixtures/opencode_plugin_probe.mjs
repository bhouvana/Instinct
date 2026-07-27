// Exercises .opencode/plugins/instinct.mjs the way OpenCode itself would
// call it: config() to collect skill paths, then
// experimental.chat.system.transform() to inject the Gate into a turn.
// Node has no ESM import for hooks that take a plain plugin object like
// this, so this is a small standalone script instead of a node:test file —
// invoked by tests/test_opencode_plugin.py, which only checks exit code 0.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const pluginPath = path.join(root, ".opencode", "plugins", "instinct.mjs");
const plugin = (await import(pathToFileURL(pluginPath).href)).default;

const hooks = await plugin({});

const config = {};
await hooks.config(config);
assert.equal(config.skills.paths.length, 1);
assert.ok(fs.existsSync(config.skills.paths[0]), "registered skills dir must exist");

// Calling config() again (a second chat session, same process) must not
// duplicate the path.
await hooks.config(config);
assert.equal(config.skills.paths.length, 1);

const emptySystem = { system: [] };
await hooks["experimental.chat.system.transform"]({}, emptySystem);
assert.match(emptySystem.system[0], /## The Gate/);

const populatedSystem = { system: ["existing system prompt"] };
await hooks["experimental.chat.system.transform"]({}, populatedSystem);
assert.equal(populatedSystem.system.length, 1);
assert.ok(populatedSystem.system[0].startsWith("existing system prompt"));
assert.match(populatedSystem.system[0], /## The Gate/);

console.log("ok");
