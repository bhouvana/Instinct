"""Checks that file paths named in docs/installation.md actually exist.

Adapted from the same principle behind Ponytail's tests/package.test.js
("the README tells users to run scripts/uninstall.js, so guard that the
package actually ships it") — a doc making a claim about a file's
existence is itself a form of configuration that can drift silently, since
nothing else re-reads the doc against the filesystem. This is deliberately
narrow (one doc, a conservative path-like pattern) rather than a general
markdown-path scanner, to avoid false positives on prose that merely looks
path-shaped.
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DOC_PATH = ROOT / "docs" / "installation.md"

CODE_SPAN_RE = re.compile(r"`([^`]+)`")
# Conservative: no spaces or angle-bracket placeholders, ends in a known
# extension or a trailing slash (a directory reference).
PATH_LIKE_RE = re.compile(r"^[\w.\-]+(?:/[\w.\-]+)*(?:\.(?:json|md|js|mjs|py|ya?ml)|/)$")


def _referenced_paths() -> set[str]:
    text = DOC_PATH.read_text(encoding="utf-8")
    return {
        span for span in CODE_SPAN_RE.findall(text)
        if PATH_LIKE_RE.match(span) and "<" not in span
    }


def test_found_at_least_one_reference():
    """A sanity check on the regex itself — if this starts failing, the
    pattern has drifted from the doc's actual formatting and the real test
    below would be silently checking nothing."""
    assert len(_referenced_paths()) > 10


def test_every_referenced_path_exists():
    for rel in sorted(_referenced_paths()):
        assert (ROOT / rel).exists(), f"docs/installation.md references '{rel}', which doesn't exist"
