import assert from "node:assert/strict";
import test from "node:test";

import { buildInstructions } from "../instructions.js";

test("buildInstructions returns the Gate", () => {
  const text = buildInstructions();
  assert.match(text, /## The Gate/);
  assert.match(text, /Engineering is not writing code/);
});

test("buildInstructions strips frontmatter and sync markers", () => {
  const text = buildInstructions();
  assert.doesNotMatch(text, /^---/);
  assert.doesNotMatch(text, /instinct:host-specific/);
  assert.doesNotMatch(text, /instinct:shared/);
});
