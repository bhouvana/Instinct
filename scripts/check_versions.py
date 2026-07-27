#!/usr/bin/env python3
"""Version-consistency guard for every host manifest that carries its own
version field.

Adapted from Ponytail's scripts/check-versions.js. Rejected earlier in this
project's history (see docs/ROADMAP.md) because only one file — plugin.json —
carried a version number, so there was nothing to drift against. RFC-0007
Phase 3 changed that: building Codex, Qoder, Copilot CLI, Gemini, and
instinct-mcp support added six more version-bearing files, each bumped by
hand on release. This closes the gap the same way Ponytail's version does:
every version-bearing file must share one pinned X.Y.Z version.

pi-extension/package.json is deliberately excluded, matching Ponytail's own
check-versions.js: it's a private, unpublished dev package with no version
field to begin with, not an oversight.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
PINNED_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")

# Every file that declares the project version. Add new host manifests here
# so a future ecosystem can't drift unnoticed.
VERSION_FILES = [
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".qoder-plugin/plugin.json",
    ".github/plugin/plugin.json",
    "gemini-extension.json",
    "instinct-mcp/package.json",
    "plugin.yaml",
]


def read_version(rel_path: str) -> str | None:
    path = ROOT / rel_path
    text = path.read_text(encoding="utf-8-sig")  # tolerate a stray BOM
    if rel_path.endswith(".yaml"):
        return yaml.safe_load(text).get("version")
    return json.loads(text).get("version")


def main() -> int:
    failed = False
    versions: list[tuple[str, str | None]] = []

    for rel_path in VERSION_FILES:
        try:
            version = read_version(rel_path)
        except (OSError, json.JSONDecodeError, yaml.YAMLError) as e:
            print(f"{rel_path}: {e}")
            failed = True
            continue
        if not isinstance(version, str) or not PINNED_SEMVER.match(version):
            print(f"{rel_path}: version must be a pinned X.Y.Z semver, got {version!r}")
            failed = True
        versions.append((rel_path, version))

    distinct = sorted({v for _, v in versions if v is not None})
    if len(distinct) > 1:
        print("Version mismatch — every manifest must share one version:")
        for rel_path, version in versions:
            print(f"  {version}\t{rel_path}")
        failed = True

    if failed:
        print("Align the version fields so every manifest shares one version.")
        return 1

    print(f"OK — all {len(VERSION_FILES)} version files pinned at {distinct[0]}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
