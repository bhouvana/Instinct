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

Checks against the real repo are kept separate from the pure functions
they call, so a second set of tests can feed those functions synthetic
data and prove they actually detect a problem — the same "prove the
checker isn't a no-op" discipline as tests/test_check_adapters.py and
tests/test_ci_workflow.py.
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


def _resolve(root: Path, rel: str) -> Path:
    # str.lstrip("./") strips a *character set*, not a prefix — it would eat
    # the leading "." off ".qoder/rules/" too. Strip the literal "./" prefix
    # instead (found by actually running this against real manifests, not
    # by inspection — see test_resolve_does_not_eat_a_leading_dot below,
    # which pins that specific regression).
    if rel.startswith("./"):
        rel = rel[2:]
    return root / rel


def _missing_manifest_paths(root: Path, manifests: list[tuple[str, list[str]]]) -> list[str]:
    problems = []
    for manifest_path, keys in manifests:
        manifest = json.loads((root / manifest_path).read_text(encoding="utf-8"))
        for key in keys:
            value = manifest.get(key)
            if not value or not _resolve(root, value).exists():
                problems.append(f"{manifest_path}:{key}")
    return problems


def _skills_dirs_without_a_real_skill(root: Path, manifests: list[tuple[str, list[str]]]) -> list[str]:
    problems = []
    for manifest_path, keys in manifests:
        if "skills" not in keys:
            continue
        manifest = json.loads((root / manifest_path).read_text(encoding="utf-8"))
        skills_dir = _resolve(root, manifest["skills"])
        if not skills_dir.is_dir():
            problems.append(manifest_path)
            continue
        real_skills = [d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
        if not real_skills:
            problems.append(manifest_path)
    return problems


def _qoder_hook_script_mismatches(config: dict) -> list[str]:
    problems = []
    try:
        cmd = config["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
        if "instinct-qoder-activate.js" not in cmd:
            problems.append("UserPromptSubmit")
    except (KeyError, IndexError):
        problems.append("UserPromptSubmit")

    try:
        entry = config["hooks"]["PreToolUse"][0]
        cmd = entry["hooks"][0]["command"]
        if entry.get("matcher") != "task|Task" or "instinct-subagent.js" not in cmd:
            problems.append("PreToolUse")
    except (KeyError, IndexError):
        problems.append("PreToolUse")
    return problems


# --- checks against the real repo ---

def test_every_manifest_path_field_resolves_to_something_real():
    missing = _missing_manifest_paths(ROOT, PATH_BEARING_MANIFESTS)
    assert not missing, f"manifest fields point at paths that don't exist: {missing}"


def test_every_manifest_skills_dir_has_at_least_one_real_skill():
    bad = _skills_dirs_without_a_real_skill(ROOT, PATH_BEARING_MANIFESTS)
    assert not bad, f"manifests whose 'skills' dir has no real skill: {bad}"


def test_qoder_hooks_config_registers_the_right_scripts():
    """Ponytail's qoder-plugin.test.js asserts the UserPromptSubmit command
    'must point at ponytail-mode-tracker.js' — a typo'd or stale script name
    here is a silent no-op install, not a crash, so it needs a real check."""
    config = json.loads((ROOT / "hooks" / "qoder-hooks.json").read_text(encoding="utf-8"))
    problems = _qoder_hook_script_mismatches(config)
    assert not problems, f"qoder-hooks.json entries don't reference the current scripts: {problems}"


def test_codex_and_claude_manifests_agree_on_which_hooks_file():
    """Both point at the same shared hooks/hooks.json (see
    test_claude_and_codex_manifests_share_the_same_hooks_file in
    test_hooks_json.py for the byte-level version of this claim) — this
    test additionally confirms that file actually registers both lifecycle
    events Codex and Claude Code both rely on, not just that the path exists."""
    hooks_json = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    assert "SessionStart" in hooks_json["hooks"]
    assert "SubagentStart" in hooks_json["hooks"]


# --- proof the checks above actually detect a problem ---

def test_resolve_does_not_eat_a_leading_dot():
    """Pins the exact bug found while writing this file: str.lstrip('./')
    strips a character set, so '.qoder/rules/' loses its leading '.' and
    silently resolves to the wrong directory. This must never regress."""
    assert _resolve(Path("/repo"), "./.qoder/rules/") == Path("/repo/.qoder/rules/")
    assert _resolve(Path("/repo"), "skills/") == Path("/repo/skills/")


def test_detects_a_manifest_path_field_that_does_not_exist(tmp_path):
    (tmp_path / "plugin.json").write_text(json.dumps({"skills": "./nonexistent/"}))
    problems = _missing_manifest_paths(tmp_path, [("plugin.json", ["skills"])])
    assert problems == ["plugin.json:skills"]


def test_detects_a_skills_dir_with_no_real_skill(tmp_path):
    (tmp_path / "empty-skills").mkdir()
    (tmp_path / "plugin.json").write_text(json.dumps({"skills": "empty-skills/"}))
    bad = _skills_dirs_without_a_real_skill(tmp_path, [("plugin.json", ["skills"])])
    assert bad == ["plugin.json"]


def test_detects_a_stale_qoder_hook_script_name():
    config = {
        "hooks": {
            "UserPromptSubmit": [{"hooks": [{"command": "node hooks/instinct-qoder-activatee.js"}]}],
            "PreToolUse": [{"matcher": "task|Task", "hooks": [{"command": "node hooks/instinct-subagent.js"}]}],
        }
    }
    assert _qoder_hook_script_mismatches(config) == ["UserPromptSubmit"]
