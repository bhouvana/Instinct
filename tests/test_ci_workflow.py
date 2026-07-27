"""Structural invariants for .github/workflows/test.yml and its local
counterpart, scripts/test_all.py.

Reverse-engineered from Ponytail's tests/package-scripts.test.js, which
exists to catch two failure modes that only otherwise show up as a broken
CI run: a subpackage's test command silently missing from the aggregate
"run everything" command, and a test step running before the install step
it depends on. Ponytail encodes both as literal substring/position checks
against one root package.json's test script. Instinct has no npm-primary
root — this is the same failure mode, checked against its actual shape:
a YAML workflow with per-directory steps, and scripts/test_all.py as the
local equivalent of that one aggregate npm script.

Written generically (scanning for package.json files with a test script,
not a hardcoded list of two names) so a future third subpackage that gets
added to the repo but forgotten in CI or in test_all.py fails loudly here,
rather than silently passing everything except the part nobody wired up.
"""

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "test.yml"
TEST_ALL_PATH = ROOT / "scripts" / "test_all.py"

# Directories that are their own installable Node package with a `test`
# script — discovered from disk, not hardcoded, so a new one added later is
# picked up automatically instead of needing this file edited too.
_EXCLUDE_DIRS = {"node_modules", ".git"}


def _node_subpackages() -> list[str]:
    subpackages = []
    for pkg_json in ROOT.glob("*/package.json"):
        rel_dir = pkg_json.parent.relative_to(ROOT)
        if str(rel_dir) in _EXCLUDE_DIRS:
            continue
        data = json.loads(pkg_json.read_text(encoding="utf-8"))
        if data.get("scripts", {}).get("test"):
            subpackages.append(str(rel_dir))
    return sorted(subpackages)


def _workflow_steps() -> list[dict]:
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    return workflow["jobs"]["test"]["steps"]


def test_every_node_subpackage_has_a_ci_step_that_tests_it():
    subpackages = _node_subpackages()
    assert subpackages, "expected at least one Node subpackage with a test script"
    steps = _workflow_steps()

    for pkg in subpackages:
        matching = [
            s for s in steps
            if s.get("working-directory") == pkg and "npm test" in s.get("run", "")
        ]
        assert matching, (
            f"{pkg}/package.json declares a test script, but no CI step in "
            f"{WORKFLOW_PATH.relative_to(ROOT)} runs `npm test` with "
            f"working-directory: {pkg}"
        )


def test_npm_install_precedes_npm_test_within_each_ci_step():
    steps = _workflow_steps()
    for step in steps:
        run = step.get("run", "")
        if "npm test" in run and "npm install" in run:
            assert run.index("npm install") < run.index("npm test"), (
                f"step {step.get('name')!r} runs npm install after npm test "
                f"in the same run block — dependencies won't be there yet"
            )


def test_subpackage_with_dependencies_has_install_somewhere_before_its_test_step():
    steps = _workflow_steps()
    for pkg in _node_subpackages():
        pkg_json = json.loads((ROOT / pkg / "package.json").read_text(encoding="utf-8"))
        if not pkg_json.get("dependencies"):
            continue  # nothing to install — pi-extension has no deps today

        test_step_index = next(
            (i for i, s in enumerate(steps)
             if s.get("working-directory") == pkg and "npm test" in s.get("run", "")),
            None,
        )
        assert test_step_index is not None, f"no test step found for {pkg}"

        installs_before = any(
            "npm install" in steps[i].get("run", "") and steps[i].get("working-directory") == pkg
            for i in range(test_step_index + 1)
        )
        assert installs_before, (
            f"{pkg} declares dependencies but no step at or before its test "
            f"step (working-directory: {pkg}) runs npm install there"
        )


def test_local_test_all_script_covers_every_node_subpackage():
    """scripts/test_all.py is the local, no-CI equivalent of the workflow
    above — it must not drift from the same set of subpackages, or a
    contributor running it locally gets a false "everything passed"."""
    subpackages = _node_subpackages()
    script_text = TEST_ALL_PATH.read_text(encoding="utf-8")
    for pkg in subpackages:
        assert f'"{pkg}"' in script_text or f"'{pkg}'" in script_text, (
            f"{pkg} has a test script but scripts/test_all.py doesn't "
            f"reference it — local runs would silently skip it"
        )
