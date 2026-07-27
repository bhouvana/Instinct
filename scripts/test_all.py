#!/usr/bin/env python3
"""Runs the exact sequence .github/workflows/test.yml runs, in one command.

Reverse-engineered from a gap Ponytail's root package.json closes for
itself: `npm test` there runs `node --test tests/*.test.js && npm test
--prefix pi-extension && npm test --prefix ponytail-mcp` in one shot, and
tests/package-scripts.test.js regression-tests that the aggregator string
never silently drops a subpackage. Instinct has no npm-primary root (it's
Python-first with two Node subpackages), so a root package.json would be
the wrong shape here — this script is the Instinct-native equivalent:
one command a contributor (or CI) can run to reproduce the whole suite
locally, instead of having to read the CI YAML to reconstruct the
sequence. tests/test_ci_workflow.py is this script's own
package-scripts.test.js: it verifies the workflow and this script don't
silently drift apart from each other.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# (label, command, cwd) — cwd is relative to ROOT, None means ROOT itself.
STEPS: list[tuple[str, list[str], str | None]] = [
    ("check_adapters.py", [sys.executable, "scripts/check_adapters.py"], None),
    ("check_versions.py", [sys.executable, "scripts/check_versions.py"], None),
    ("pytest", [sys.executable, "-m", "pytest", "tests/", "-v"], None),
]

NODE_SUBPACKAGES = ["instinct-mcp", "pi-extension"]


def run(label: str, cmd: list[str], cwd: str | None) -> bool:
    print(f"\n{'=' * 70}\n{label}\n{'=' * 70}")
    # On Windows, npm/node-based CLIs are .cmd wrappers — subprocess.run's
    # underlying CreateProcess call won't resolve those without going
    # through a shell, and fails with a bare FileNotFoundError that gives
    # no hint why. shutil.which() does the same PATHEXT-aware lookup a
    # shell would, so this runs identically on Windows, macOS, and Linux
    # without needing shell=True (which would need every arg re-quoted).
    resolved = shutil.which(cmd[0])
    if resolved is None:
        print(f"'{cmd[0]}' not found on PATH — skipping.")
        return False
    result = subprocess.run([resolved, *cmd[1:]], cwd=str(ROOT / cwd) if cwd else str(ROOT))
    return result.returncode == 0


def main() -> int:
    results: list[tuple[str, bool]] = []

    for label, cmd, cwd in STEPS:
        results.append((label, run(label, cmd, cwd)))

    if shutil.which("node") is None:
        print("\nnode not on PATH — skipping instinct-mcp/ and pi-extension/ test suites.")
    else:
        for pkg in NODE_SUBPACKAGES:
            ok = run(f"npm test ({pkg})", ["npm", "test"], pkg)
            results.append((pkg, ok))

    print(f"\n{'=' * 70}\nSummary\n{'=' * 70}")
    all_ok = True
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
        all_ok &= ok

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
