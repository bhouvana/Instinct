#!/usr/bin/env python3
"""Generates the plain-markdown consolidated adapters — no frontmatter,
confirmed from Ponytail's actual files for each host — from AGENTS.md's
canonical consolidated body. Run after editing AGENTS.md, then
scripts/check_adapters.py verifies everything stayed in sync.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from check_adapters import ROOT, LEADING_EXPLANATORY_COMMENT_RE  # noqa: E402

HEADER = """<!-- {host}'s copy of Instinct (docs/rfcs/0007), consolidated for
this always-on host. Canonical source: AGENTS.md. Regenerate with
scripts/generate_adapters.py after editing AGENTS.md — don't hand-edit. -->

"""

TARGETS = {
    ".windsurf/rules/instinct.md": "Windsurf",
    ".kiro/steering/instinct.md": "Kiro",
    ".clinerules/instinct.md": "Cline",
    ".github/copilot-instructions.md": "GitHub Copilot",
}


def main() -> int:
    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    body = LEADING_EXPLANATORY_COMMENT_RE.sub("", agents_text, count=1)
    for rel, host in TARGETS.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(HEADER.format(host=host) + body, encoding="utf-8")
        print(f"wrote {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
