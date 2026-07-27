"""Tests for scripts/render_qoder_hooks.py — closes the manual
INSTINCT_DIR substitution step docs/installation.md's Qoder section
names as a real, currently-manual step.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import render_qoder_hooks as rqh  # noqa: E402

ROOT = Path(__file__).parent.parent


def test_renders_a_unix_style_path():
    data = rqh.render("/home/someuser/instinct")
    cmd = data["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
    assert cmd == "node /home/someuser/instinct/hooks/instinct-qoder-activate.js"


def test_renders_a_windows_style_path_without_breaking_json():
    """Regression test for a real bug found by actually running this
    script with its own default argument on Windows: Path.resolve()
    returns backslashes, which are invalid JSON escapes once substituted
    into the template before parsing. Confirmed crashing with
    json.decoder.JSONDecodeError before the fix, confirmed clean after."""
    data = rqh.render(r"C:\Users\someuser\instinct")
    cmd = data["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
    assert cmd == "node C:/Users/someuser/instinct/hooks/instinct-qoder-activate.js"


def test_strips_the_template_only_comment_field():
    data = rqh.render("/anywhere")
    assert "_comment" not in data


def test_registers_both_hooks_pointing_at_current_script_names():
    data = rqh.render("/anywhere")
    assert "instinct-qoder-activate.js" in data["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
    assert "instinct-subagent.js" in data["hooks"]["PreToolUse"][0]["hooks"][0]["command"]


def test_default_arg_does_not_crash():
    """The exact scenario that surfaced the backslash bug: running with no
    argument at all, so it falls back to this repo's own resolved path."""
    data = rqh.render(str(ROOT.resolve()))
    assert "hooks" in data
