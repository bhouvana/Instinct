"""Syntax checks for hooks/hooks.json's command strings.

Adapted from Ponytail's tests/hooks-windows.test.js, which exists because
these are real regressions it hit in production: cmd.exe %VAR% syntax
under PowerShell, POSIX-only guard syntax breaking on Windows, and the
bash-only `exec` builtin breaking under PowerShell entirely. None of these
need Node to check — they're string patterns in a JSON file — so unlike
tests/test_hooks.py this file doesn't skip when Node is missing.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
HOOKS_JSON = ROOT / "hooks" / "hooks.json"

# cmd.exe variable syntax (%FOO%); PowerShell leaves it literal, breaking the path.
CMD_VAR_SYNTAX = re.compile(r"%[A-Za-z_][A-Za-z0-9_]*%")
# PowerShell 5.1 rejects these POSIX shell guards when a host runs `command`.
POSIX_GUARD_SYNTAX = re.compile(r"\bcommand\s+-v\b|&&|\|\||>/dev/null|2>&1")
HOOK_SCRIPT = re.compile(r"hooks[\\/]([\w.-]+\.(?:js|mjs|cjs|ps1|sh))")


def _command_entries():
    config = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    entries = []
    for matchers in config["hooks"].values():
        for matcher in matchers:
            entries.extend(matcher["hooks"])
    return entries


def test_command_windows_uses_powershell_env_syntax_not_cmd_var():
    entries = [e["commandWindows"] for e in _command_entries() if "commandWindows" in e]
    assert entries, "expected at least one commandWindows entry"
    for cmd in entries:
        assert not CMD_VAR_SYNTAX.search(cmd), (
            f"commandWindows uses cmd.exe %VAR% syntax (breaks under PowerShell): {cmd}"
        )


def test_shared_command_avoids_posix_only_guard_syntax():
    entries = [e["command"] for e in _command_entries() if "command" in e]
    assert entries, "expected at least one command entry"
    for cmd in entries:
        assert not POSIX_GUARD_SYNTAX.search(cmd), (
            f"command uses POSIX-only guard syntax: {cmd}"
        )


def test_shared_command_is_shell_agnostic():
    entries = [e["command"] for e in _command_entries() if "command" in e]
    assert entries, "expected at least one command entry"
    for cmd in entries:
        assert not re.search(r"(^|\s)exec\s", cmd), (
            f"command must not use the bash-only 'exec' builtin (breaks under PowerShell): {cmd}"
        )
        assert re.match(r"^node\s+", cmd), (
            f"command must invoke node directly so it runs in both bash and PowerShell: {cmd}"
        )
        assert not cmd.rstrip().endswith("exit 0"), (
            f"command must not leave a shell wrapper waiting on node: {cmd}"
        )


def test_every_hook_command_points_at_a_script_that_ships_in_hooks():
    for entry in _command_entries():
        for cmd in (entry.get("command"), entry.get("commandWindows")):
            if not cmd:
                continue
            match = HOOK_SCRIPT.search(cmd)
            assert match, f"cannot find a hooks/ script in command: {cmd}"
            script = ROOT / "hooks" / match.group(1)
            assert script.exists(), f"command references a missing hook script: {match.group(1)}"
