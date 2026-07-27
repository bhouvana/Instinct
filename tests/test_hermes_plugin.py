"""Tests for the root __init__.py / plugin.yaml Hermes Agent plugin.

Adapted from Ponytail's own root __init__.py, which register()s each
skills/*/SKILL.md and a pre_llm_call hook that injects its ruleset before
every LLM turn. This version drops the mode state and slash-command
rewriting Ponytail's has, since Instinct has neither (ADR-0004).
"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import yaml

ROOT = Path(__file__).parent.parent


def _load_plugin_module():
    spec = importlib.util.spec_from_file_location("instinct_hermes_plugin", ROOT / "__init__.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_plugin_yaml_is_valid_and_lists_the_actual_skill_dirs():
    manifest = yaml.safe_load((ROOT / "plugin.yaml").read_text(encoding="utf-8"))
    assert manifest["name"] == "instinct"
    assert "pre_llm_call" in manifest["provides_hooks"]
    for skill in manifest["provides_skills"]:
        assert (ROOT / "skills" / skill / "SKILL.md").exists(), f"listed skill {skill} has no SKILL.md"


def test_plugin_yaml_lists_every_real_skill_directory():
    """The reverse of the check above: every skills/*/SKILL.md on disk must
    be listed in plugin.yaml's provides_skills, not just the other way
    round. Adapted from Ponytail's tests/hermes-plugin.test.js, which reads
    the actual skills/ directory listing and cross-checks it against the
    manifest — this is the direction that catches a new skill directory
    getting added to the repo but forgotten in the manifest, which the
    "every listed skill exists" check above can't see at all."""
    manifest = yaml.safe_load((ROOT / "plugin.yaml").read_text(encoding="utf-8"))
    real_skill_dirs = {
        d.name for d in (ROOT / "skills").iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    }
    assert real_skill_dirs, "expected at least one real skill directory"
    assert set(manifest["provides_skills"]) == real_skill_dirs


def test_build_injected_context_returns_the_gate():
    plugin = _load_plugin_module()
    context = plugin.build_injected_context()
    assert "## The Gate" in context
    assert "Engineering is not writing code" in context


def test_build_injected_context_strips_frontmatter_and_sync_markers():
    plugin = _load_plugin_module()
    context = plugin.build_injected_context()
    assert not context.startswith("---")
    assert "instinct:host-specific" not in context
    assert "instinct:shared" not in context


def test_pre_llm_call_returns_context_dict():
    plugin = _load_plugin_module()
    result = plugin._pre_llm_call(session_id="abc")
    assert "## The Gate" in result["context"]


def test_register_wires_skills_and_hook_onto_ctx():
    plugin = _load_plugin_module()
    ctx = MagicMock()
    plugin.register(ctx)

    registered_skill_names = {call.args[0] for call in ctx.register_skill.call_args_list}
    assert registered_skill_names == {"instinct-review", "instinct-help"}

    hook_names = {call.args[0] for call in ctx.register_hook.call_args_list}
    assert hook_names == {"pre_llm_call"}
