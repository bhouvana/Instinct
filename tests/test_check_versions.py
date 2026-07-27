"""Tests for scripts/check_versions.py — the version-consistency guard for
RFC-0007 Phase 3's host manifests. Adapted from Ponytail's own
scripts/check-versions.js (see docs/ROADMAP.md for why this was rejected
earlier in this project's history and why Phase 3 reopened the question).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import check_versions as cv  # noqa: E402

ROOT = Path(__file__).parent.parent


def test_real_repo_versions_are_pinned_and_agree():
    """Integration check: the actual files in this repo, not fixtures."""
    assert cv.main() == 0


def test_detects_real_mismatch(tmp_path, monkeypatch):
    """Doesn't just trust that main() returns 0 — proves it returns 1 when
    a manifest actually disagrees, using throwaway copies so the real repo
    files are never touched."""
    (tmp_path / "a.json").write_text('{"version": "0.1.0"}', encoding="utf-8")
    (tmp_path / "b.json").write_text('{"version": "0.2.0"}', encoding="utf-8")

    monkeypatch.setattr(cv, "ROOT", tmp_path)
    monkeypatch.setattr(cv, "VERSION_FILES", ["a.json", "b.json"])

    assert cv.main() == 1


def test_detects_unpinned_version(tmp_path, monkeypatch):
    """A non-semver or missing version must fail, not just a mismatch."""
    (tmp_path / "a.json").write_text('{"version": "latest"}', encoding="utf-8")

    monkeypatch.setattr(cv, "ROOT", tmp_path)
    monkeypatch.setattr(cv, "VERSION_FILES", ["a.json"])

    assert cv.main() == 1


def test_reads_yaml_version(tmp_path, monkeypatch):
    (tmp_path / "plugin.yaml").write_text("name: x\nversion: 1.2.3\n", encoding="utf-8")
    monkeypatch.setattr(cv, "ROOT", tmp_path)
    assert cv.read_version("plugin.yaml") == "1.2.3"


@pytest.mark.parametrize("rel_path", cv.VERSION_FILES)
def test_every_registered_version_file_exists(rel_path):
    assert (ROOT / rel_path).exists(), f"registered version file is missing: {rel_path}"
