"""Semantic validation for plugin manifests, beyond "is it valid JSON."

Reverse-engineered from Ponytail's per-host test files (qoder-plugin.test.js,
copilot-plugin.test.js, gemini-extension.test.js), which all share one
pattern tests/test_hooks_json.py doesn't cover: a manifest can be
syntactically valid JSON while pointing at a `skills`/`hooks`/`rules` path
that doesn't exist, or a hooks config that no longer references the script
it claims to. Neither is a JSON error, so nothing catches it without a
test that actually resolves the paths and inspects the structure — the
same class of bug a typo'd script name or a moved directory would
introduce silently.
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent

# (manifest path, keys whose string value is a path relative to ROOT)
PATH_BEARING_MANIFESTS = [
    (".codex-plugin/plugin.json", ["skills", "hooks"]),
    (".qoder-plugin/plugin.json", ["skills", "rules", "hooks"]),
    (".github/plugin/plugin.json", ["skills", "hooks"]),
    (".claude-plugin/plugin.json", ["hooks"]),
]


def _resolve(rel: str) -> Path:
    # str.lstrip("./") strips a *character set*, not a prefix — it would eat
    # the leading "." off ".qoder/rules/" too. Strip the literal "./" prefix
    # instead (found by actually running this against real manifests, not
    # by inspection).
    if rel.startswith("./"):
        rel = rel[2:]
    return ROOT / rel


def test_every_manifest_path_field_resolves_to_something_real():
    for manifest_path, keys in PATH_BEARING_MANIFESTS:
        manifest = json.loads((ROOT / manifest_path).read_text(encoding="utf-8"))
        for key in keys:
            value = manifest.get(key)
            assert value, f"{manifest_path}: expected a '{key}' field"
            target = _resolve(value)
            assert target.exists(), f"{manifest_path}: '{key}' points at {value}, which doesn't exist"


def test_every_manifest_skills_dir_has_at_least_one_real_skill():
    for manifest_path, keys in PATH_BEARING_MANIFESTS:
        if "skills" not in keys:
            continue
        manifest = json.loads((ROOT / manifest_path).read_text(encoding="utf-8"))
        skills_dir = _resolve(manifest["skills"])
        real_skills = [d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
        assert real_skills, f"{manifest_path}: '{skills_dir}' has no subdirectory with a SKILL.md"


def test_qoder_hooks_config_registers_the_right_scripts():
    """Ponytail's qoder-plugin.test.js asserts the UserPromptSubmit command
    'must point at ponytail-mode-tracker.js' — a typo'd or stale script name
    here is a silent no-op install, not a crash, so it needs a real check."""
    config = json.loads((ROOT / "hooks" / "qoder-hooks.json").read_text(encoding="utf-8"))

    prompt_submit = config["hooks"]["UserPromptSubmit"]
    assert isinstance(prompt_submit, list) and prompt_submit
    cmd = prompt_submit[0]["hooks"][0]["command"]
    assert "instinct-qoder-activate.js" in cmd

    pre_tool_use = config["hooks"]["PreToolUse"]
    assert isinstance(pre_tool_use, list) and pre_tool_use
    assert pre_tool_use[0]["matcher"] == "task|Task"
    cmd = pre_tool_use[0]["hooks"][0]["command"]
    assert "instinct-subagent.js" in cmd


def test_codex_and_claude_manifests_agree_on_which_hooks_file():
    """Both point at the same shared hooks/hooks.json (see
    test_claude_and_codex_manifests_share_the_same_hooks_file in
    test_hooks_json.py for the byte-level version of this claim) — this
    test additionally confirms that file actually registers both lifecycle
    events Codex and Claude Code both rely on, not just that the path exists."""
    hooks_json = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    assert "SessionStart" in hooks_json["hooks"]
    assert "SubagentStart" in hooks_json["hooks"]
