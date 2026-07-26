"""Tests for hooks/instinct-activate.js — the SessionStart hook that
guarantees SKILL.md's body is present in context every session,
independent of the skill's own description-matching. Adapted from
Ponytail's hooks/ponytail-activate.js (RFC/ROADMAP note on the reverse
engineering behind this).

Requires Node; skipped entirely if it isn't on PATH rather than failing
the whole suite over an optional runtime.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
HOOK = ROOT / "hooks" / "instinct-activate.js"

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node not on PATH")


def run_hook(plugin_root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", str(HOOK)],
        env={"CLAUDE_PLUGIN_ROOT": str(plugin_root)},
        capture_output=True,
        text=True,
    )


def test_hook_emits_valid_session_start_json():
    result = run_hook(ROOT)
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["hookSpecificOutput"]["hookEventName"] == "SessionStart"


def test_hook_context_contains_the_gate():
    result = run_hook(ROOT)
    ctx = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "## The Gate" in ctx
    assert "Engineering is not writing code" in ctx


def test_hook_strips_sync_markers():
    """A regression test for a real bug found during manual testing: the
    check_adapters.py sync markers were leaking verbatim into the injected
    context before this was fixed."""
    result = run_hook(ROOT)
    ctx = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "instinct:host-specific" not in ctx
    assert "instinct:shared" not in ctx


def test_hook_strips_frontmatter():
    result = run_hook(ROOT)
    ctx = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert not ctx.startswith("---")
    assert "name: instinct" not in ctx


def test_hook_fails_silently_when_skill_md_missing(tmp_path):
    """Must never block session startup — confirmed by exit code 0 and
    empty output, not by inspecting an error message (there shouldn't be
    one)."""
    result = run_hook(tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""
