"""Hermes Agent plugin for Instinct.

Adapted from Ponytail's own root __init__.py: same register(ctx) contract
(register_skill for each skills/*/SKILL.md, register_hook for pre_llm_call),
with the mode state, mode-filtered skill body, and gateway slash-command
rewriting dropped, since Instinct has neither modes (ADR-0004) nor a
command family for v1 — there is nothing to filter or rewrite.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SKILLS_DIR = ROOT / "skills"
SKILL_MD = SKILLS_DIR / "instinct" / "SKILL.md"

_FRONTMATTER_RE = re.compile(r"^---\n[\s\S]*?\n---\n?")
# SKILL.md carries scripts/check_adapters.py's sync markers so the sync
# checker can find the host-specific block; strip them here the same way
# hooks/lib.js does for Claude Code, so they never leak into an LLM turn.
_SYNC_MARKER_RE = re.compile(r"<!-- instinct:(?:shared|host-specific):(?:start|end) -->\n?")


def build_injected_context() -> str:
    """Return the Gate, read fresh from SKILL.md on every call."""
    try:
        text = SKILL_MD.read_text(encoding="utf-8")
    except OSError:
        return ""
    text = _FRONTMATTER_RE.sub("", text, count=1)
    text = _SYNC_MARKER_RE.sub("", text)
    return text.strip()


def _pre_llm_call(**_: Any) -> dict[str, str] | None:
    context = build_injected_context()
    return {"context": context} if context else None


def register(ctx: Any) -> None:
    """Register Instinct's skill directories and its pre_llm_call hook with Hermes."""
    for child in sorted(SKILLS_DIR.iterdir() if SKILLS_DIR.exists() else []):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            ctx.register_skill(child.name, skill_md)

    ctx.register_hook("pre_llm_call", _pre_llm_call)
