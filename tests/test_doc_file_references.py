"""Checks that file paths named in README.md and docs/installation.md
actually exist.

Adapted from the same principle behind Ponytail's tests/package.test.js
("the README tells users to run scripts/uninstall.js, so guard that the
package actually ships it") — a doc making a claim about a file's
existence is itself a form of configuration that can drift silently, since
nothing else re-reads the doc against the filesystem. Covers two
reference styles docs in this repo actually use: bare backtick code spans
(`` `docs/ROADMAP.md` ``) and markdown link targets
(`[text](docs/ROADMAP.md)`) — deliberately not a general prose scanner,
to avoid false positives on text that merely looks path-shaped.
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DOC_PATHS = [ROOT / "README.md", ROOT / "docs" / "installation.md"]

CODE_SPAN_RE = re.compile(r"`([^`]+)`")
LINK_TARGET_RE = re.compile(r"\]\(([^)]+)\)")
# Conservative: no spaces or angle-bracket placeholders, MUST end in a
# known extension or a trailing slash (a directory reference) — making
# this suffix optional was tried and reverted: it made bare words like
# "claude" or "node" match as "paths" with no file-like shape at all,
# confirmed by actually running it and seeing false positives, not by
# inspection.
PATH_LIKE_RE = re.compile(r"^[\w.\-]+(?:/[\w.\-]+)*(?:\.(?:json|md|js|mjs|py|ya?ml|svg)|/)$")


def _referenced_paths(text: str) -> set[str]:
    candidates = set(CODE_SPAN_RE.findall(text))
    # Link targets are unambiguous references (not prose), so accept them
    # directly rather than re-applying the code-span heuristic — just
    # exclude external URLs, anchors, and mailto links.
    for target in LINK_TARGET_RE.findall(text):
        if not target.startswith(("http://", "https://", "#", "mailto:")):
            candidates.add(target)
    return {
        span for span in candidates
        if PATH_LIKE_RE.match(span) and "<" not in span and "://" not in span
    }


def _missing_paths(root: Path, text: str) -> list[str]:
    return sorted(rel for rel in _referenced_paths(text) if not (root / rel).exists())


def test_found_at_least_one_reference_per_doc():
    """A sanity check on the regexes themselves, not a precise count — if
    this starts failing, the pattern has drifted from a doc's actual
    formatting and the real test below would be silently checking nothing
    for that file. Confirmed real counts before picking this threshold
    (7 for README.md, 21 for installation.md), rather than guessing a
    round number and hoping both docs clear it."""
    for doc in DOC_PATHS:
        found = _referenced_paths(doc.read_text(encoding="utf-8"))
        assert len(found) >= 5, f"{doc.relative_to(ROOT)}: expected >=5 path references, found {len(found)}"


def test_every_referenced_path_exists():
    for doc in DOC_PATHS:
        missing = _missing_paths(ROOT, doc.read_text(encoding="utf-8"))
        assert not missing, f"{doc.relative_to(ROOT)} references paths that don't exist: {missing}"


def test_detects_a_reference_to_a_missing_file(tmp_path):
    """Proof the check above isn't a no-op: a path-shaped code span or
    link target that doesn't resolve must be reported."""
    assert _missing_paths(tmp_path, "See `some/missing/file.md` for details.") == ["some/missing/file.md"]
    assert _missing_paths(tmp_path, "See [it](some/missing/file.md) for details.") == ["some/missing/file.md"]


def test_does_not_flag_a_real_file_or_an_external_link(tmp_path):
    (tmp_path / "real.md").write_text("hi")
    assert _missing_paths(tmp_path, "See `real.md` for details.") == []
    assert _missing_paths(tmp_path, "See [real](real.md) or [Ponytail](https://github.com/DietrichGebert/ponytail).") == []
