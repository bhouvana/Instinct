#!/usr/bin/env python3
"""Sync checker for RFC-0007's adapter layer.

SKILL.md's body is the canonical source. Every adapter (AGENTS.md, plus
any future instruction-tier copy) must match it exactly outside the
`instinct:host-specific` block — that block is where SKILL.md points at
reference files (Claude Code can act on that) and consolidated adapters
inline the same content instead (an always-on instruction host can't act
on a "read this file" pointer, per RFC-0007's consolidation decision).

Registered adapters that use the consolidated (inlined) form must also
match *each other* inside the host-specific block, since they're solving
the same problem the same way. SKILL.md's host-specific block is expected
to differ from theirs (it's the pointer form) and isn't compared.

Exit 0: everything registered is in sync. Exit 1: drift found, printed as
a unified diff. This is meant to run wherever `eval/run.py` runs — on
every change to SKILL.md or a registered adapter, not just when someone
remembers to check by hand.
"""

from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILL_PATH = ROOT / "SKILL.md"

# (path, is_consolidated) — is_consolidated=True means this adapter inlines
# reference content instead of pointing to it, and its host-specific block
# is compared against other consolidated adapters, not against SKILL.md's.
ADAPTERS = [
    (ROOT / "AGENTS.md", True),
    (ROOT / ".cursor" / "rules" / "instinct.mdc", True),
]

HOST_SPECIFIC_RE = re.compile(
    r"<!-- instinct:host-specific:start -->\n(.*?)<!-- instinct:host-specific:end -->\n?",
    re.DOTALL,
)
SHARED_MARKER_RE = re.compile(r"<!-- instinct:shared:(start|end) -->\n?")


LEADING_EXPLANATORY_COMMENT_RE = re.compile(r"\A\s*<!--(?!\s*instinct:).*?-->\s*", re.DOTALL)


def strip_frontmatter(text: str) -> str:
    """Drop a leading `---\\n...\\n---\\n` YAML frontmatter block, if present,
    and a leading explanatory HTML comment (adapters may have one describing
    the file; it's not part of the canonical content being compared)."""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            text = text[end + 5 :]
    return LEADING_EXPLANATORY_COMMENT_RE.sub("", text, count=1)


def split_shared_and_host_specific(text: str) -> tuple[str, str | None]:
    """Return (shared_text_with_placeholder, host_specific_text_or_None)."""
    match = HOST_SPECIFIC_RE.search(text)
    host_specific = match.group(1) if match else None
    shared = HOST_SPECIFIC_RE.sub("\0HOST_SPECIFIC\0\n", text)
    shared = SHARED_MARKER_RE.sub("", shared)
    return shared.strip(), (host_specific.strip() if host_specific else None)


def diff(label_a: str, a: str, label_b: str, b: str) -> str:
    return "".join(
        difflib.unified_diff(
            a.splitlines(keepends=True),
            b.splitlines(keepends=True),
            fromfile=label_a,
            tofile=label_b,
        )
    )


def main() -> int:
    skill_body = strip_frontmatter(SKILL_PATH.read_text(encoding="utf-8"))
    skill_shared, skill_host_specific = split_shared_and_host_specific(skill_body)

    problems: list[str] = []
    consolidated_host_specific: list[tuple[str, str]] = []

    for path, is_consolidated in ADAPTERS:
        if not path.exists():
            problems.append(f"{path.relative_to(ROOT)}: registered but missing")
            continue
        text = strip_frontmatter(path.read_text(encoding="utf-8"))
        shared, host_specific = split_shared_and_host_specific(text)

        if shared != skill_shared:
            d = diff("SKILL.md (shared)", skill_shared, str(path.relative_to(ROOT)), shared)
            problems.append(f"{path.relative_to(ROOT)}: shared content drifted from SKILL.md\n{d}")

        if is_consolidated and host_specific:
            consolidated_host_specific.append((str(path.relative_to(ROOT)), host_specific))

    # Consolidated adapters must agree with each other on the inlined
    # Critical-tier content, even though they're expected to differ from
    # SKILL.md's pointer-based version.
    if len(consolidated_host_specific) > 1:
        base_label, base_text = consolidated_host_specific[0]
        for label, text in consolidated_host_specific[1:]:
            if text != base_text:
                d = diff(base_label, base_text, label, text)
                problems.append(f"{label}: consolidated content drifted from {base_label}\n{d}")

    if problems:
        print("DRIFT FOUND:\n")
        for p in problems:
            print(p)
            print()
        return 1

    print(f"OK — {len(ADAPTERS)} adapter(s) in sync with SKILL.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
