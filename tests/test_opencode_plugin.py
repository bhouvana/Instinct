"""Tests for .opencode/plugins/instinct.mjs, the OpenCode server plugin
that injects the Gate into every chat's system prompt and registers the
skills/ directory. Adapted from Ponytail's .opencode/plugins/ponytail.mjs
with the mode-persistence layer dropped (ADR-0004: no modes).

Requires Node; skipped entirely if it isn't on PATH.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
PROBE = Path(__file__).parent / "fixtures" / "opencode_plugin_probe.mjs"

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node not on PATH")


def test_opencode_plugin_config_and_transform_behave_correctly():
    result = subprocess.run(
        ["node", str(PROBE)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout
