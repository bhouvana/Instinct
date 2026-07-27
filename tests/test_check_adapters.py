"""Tests for scripts/check_adapters.py — the sync verification tool for
RFC-0007's adapter layer. Covers the parsing logic in isolation (so a
regression here is caught by pytest, not by hand-inspecting a diff) and
runs the real checker against the actual repo files as an integration
check.
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import check_adapters as ca  # noqa: E402

ROOT = Path(__file__).parent.parent


def test_strip_frontmatter_removes_yaml_block():
    text = "---\nname: x\n---\nbody here\n"
    assert ca.strip_frontmatter(text) == "body here\n"


def test_strip_frontmatter_no_frontmatter_passthrough():
    text = "just a body, no frontmatter\n"
    assert ca.strip_frontmatter(text) == text


def test_strip_frontmatter_removes_leading_explanatory_comment():
    text = "<!-- some explanation -->\n\nreal content\n"
    assert ca.strip_frontmatter(text) == "real content\n"


def test_strip_frontmatter_keeps_instinct_markers():
    text = "<!-- instinct:host-specific:start -->\nkeep me\n"
    assert ca.strip_frontmatter(text) == text


def test_split_shared_and_host_specific_extracts_block():
    text = (
        "before\n"
        "<!-- instinct:host-specific:start -->\n"
        "unique content\n"
        "<!-- instinct:host-specific:end -->\n"
        "after\n"
    )
    shared, host_specific = ca.split_shared_and_host_specific(text)
    assert host_specific == "unique content"
    assert "unique content" not in shared
    assert "before" in shared and "after" in shared


def test_split_with_no_host_specific_block():
    text = "just shared content\n"
    shared, host_specific = ca.split_shared_and_host_specific(text)
    assert host_specific is None
    assert shared == "just shared content"


def test_real_repo_adapters_are_in_sync():
    """Integration check: the actual files in this repo, not fixtures."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_adapters.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_skill_md_references_real_files():
    """SKILL.md's Critical tier instructs 'Read references/ladder.md...
    and references/provenance-out.md' — a live instruction pointing at a
    path, with nothing anywhere checking either file still exists. A
    rename or deletion of either would silently break Critical-tier
    behavior with no test catching it."""
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for ref in ("references/ladder.md", "references/provenance-out.md"):
        assert ref in skill_text, f"SKILL.md no longer mentions {ref} — is this reference stale?"
        assert (ROOT / ref).exists(), f"SKILL.md references {ref}, which doesn't exist"


def test_detects_real_drift(tmp_path, monkeypatch):
    """Doesn't just trust that main() returns 0 — proves it returns 1 when
    an adapter actually disagrees with SKILL.md, using throwaway copies so
    the real repo files are never touched."""
    skill = tmp_path / "SKILL.md"
    skill.write_text("---\nname: x\n---\nshared text\n", encoding="utf-8")
    good_adapter = tmp_path / "AGENTS.md"
    good_adapter.write_text("shared text\n", encoding="utf-8")
    bad_adapter = tmp_path / "DRIFTED.md"
    bad_adapter.write_text("drifted text\n", encoding="utf-8")

    monkeypatch.setattr(ca, "SKILL_PATH", skill)
    monkeypatch.setattr(ca, "ADAPTERS", [(good_adapter, True), (bad_adapter, True)])

    assert ca.main() == 1
