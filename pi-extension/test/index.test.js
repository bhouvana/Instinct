import assert from "node:assert/strict";
import test from "node:test";

import instinctExtension from "../index.js";

// Minimal mock of pi's extension host: records handlers registered via
// .on() so the test can invoke them directly, the same way the real host
// would when the corresponding event fires.
function makePi() {
  const handlers = {};
  return {
    on: (event, handler) => {
      handlers[event] = handler;
    },
    handlers,
  };
}

test("registers a before_agent_start handler", () => {
  const pi = makePi();
  instinctExtension(pi);
  assert.equal(typeof pi.handlers.before_agent_start, "function");
});

test("injects the Gate when there is no existing system prompt", async () => {
  const pi = makePi();
  instinctExtension(pi);
  const result = await pi.handlers.before_agent_start({});
  assert.match(result.systemPrompt, /## The Gate/);
});

test("appends to, rather than replaces, an existing system prompt", async () => {
  const pi = makePi();
  instinctExtension(pi);
  const result = await pi.handlers.before_agent_start({ systemPrompt: "existing prompt" });
  assert.ok(result.systemPrompt.startsWith("existing prompt"));
  assert.match(result.systemPrompt, /## The Gate/);
});

test("does not crash and does not prepend 'undefined' on a null event", async () => {
  const pi = makePi();
  instinctExtension(pi);
  const result = await pi.handlers.before_agent_start(null);
  assert.ok(!result.systemPrompt.startsWith("undefined"));
  assert.match(result.systemPrompt, /## The Gate/);
});
