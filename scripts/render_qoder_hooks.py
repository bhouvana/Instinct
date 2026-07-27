#!/usr/bin/env python3
"""Renders hooks/qoder-hooks.json with INSTINCT_DIR substituted for a real
path, ready to paste into .qoder/settings.json or ~/.qoder/settings.json.

Exists because docs/installation.md's Qoder section names a real,
currently-manual step: hooks/qoder-hooks.json is a template, not a
ready-to-use config (its own "_comment" field says so), and copying it by
hand means finding and correctly replacing every INSTINCT_DIR occurrence.
Removes the step instead of just documenting that it's manual.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TEMPLATE_PATH = ROOT / "hooks" / "qoder-hooks.json"


def render(instinct_dir: str, template_path: Path = TEMPLATE_PATH) -> dict:
    # A Windows path (e.g. from Path.resolve()) uses backslashes, which are
    # invalid JSON escapes once substituted into the template string before
    # parsing — confirmed by actually running this with the default arg on
    # Windows, not by inspection. Forward slashes work in Node path
    # arguments on both platforms, so normalize instead of trying to
    # JSON-escape backslashes correctly.
    safe_dir = instinct_dir.replace("\\", "/")
    text = template_path.read_text(encoding="utf-8")
    data = json.loads(text.replace("INSTINCT_DIR", safe_dir))
    data.pop("_comment", None)  # template-only metadata, not part of the real config
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "instinct_dir",
        nargs="?",
        default=str(ROOT.resolve()),
        help="Absolute path to this Instinct checkout (default: this repo's own root)",
    )
    args = parser.parse_args()

    print(json.dumps(render(args.instinct_dir), indent=2))
    print(
        '\nPaste the "hooks" key above into your .qoder/settings.json '
        "(or ~/.qoder/settings.json for a global install).",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
