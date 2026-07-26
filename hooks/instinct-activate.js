#!/usr/bin/env node
/**
 * SessionStart hook. Why this exists: relying only on SKILL.md's
 * description-matching for Claude Code means the Gate can silently never
 * load for a session if the match doesn't fire — a false negative with no
 * error, which is exactly the failure mode RFC-0002/ADR-0003 spent real
 * effort reasoning about without fully closing. This hook closes the
 * separate half of that problem deterministically: it guarantees SKILL.md's
 * body is present in context from session start, every session, regardless
 * of matching. It does not replace Gate accuracy (RFC-0008 through 0011
 * still own whether the Gate classifies correctly once loaded) — it only
 * guarantees the Gate is there to run at all.
 *
 * Adapted from Ponytail's hooks/ponytail-activate.js: same SessionStart
 * mechanism, deliberately without its intensity-mode / statusline-nudge
 * layer, since Instinct has no equivalent modes yet — that's real scope
 * this project doesn't need until it has more than one mode to track.
 *
 * Must never block session start: any failure here is caught and the hook
 * exits 0 with no output, same resilience principle Ponytail's version
 * uses, for the same reason (a broken hook is a worse failure than a
 * missing one).
 */

const { getSkillBody, emitAdditionalContext } = require("./lib");

try {
  emitAdditionalContext("SessionStart", getSkillBody());
} catch {
  // Silent, deliberate: a broken hook must never block session startup.
}
