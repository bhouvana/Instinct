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

The pure `_missing_*`/`_installs_before_test` functions exist separately
from the `test_*` functions that call them against the real repo so a
second set of tests can call the same logic against synthetic data and
prove it actually detects a problem — the same discipline
tests/test_check_adapters.py's test_detects_real_drift and
tests/test_check_versions.py's test_detects_real_mismatch already hold
their own checkers to. Without this split, a bug that silently turned any
of the checks below into a no-op (e.g. an accidentally-inverted condition)
would have nothing here to catch it.
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


def _node_subpackages(root: Path = ROOT) -> list[str]:
    subpackages = []
    for pkg_json in root.glob("*/package.json"):
        rel_dir = pkg_json.parent.relative_to(root)
        if str(rel_dir) in _EXCLUDE_DIRS:
            continue
        data = json.loads(pkg_json.read_text(encoding="utf-8"))
        if data.get("scripts", {}).get("test"):
            subpackages.append(str(rel_dir))
    return sorted(subpackages)


def _workflow_steps(workflow_path: Path = WORKFLOW_PATH) -> list[dict]:
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    return workflow["jobs"]["test"]["steps"]


def _subpackages_missing_ci_step(subpackages: list[str], steps: list[dict]) -> list[str]:
    return [
        pkg for pkg in subpackages
        if not any(s.get("working-directory") == pkg and "npm test" in s.get("run", "") for s in steps)
    ]


def _steps_with_install_after_test(steps: list[dict]) -> list[str]:
    bad = []
    for step in steps:
        run = step.get("run", "")
        if "npm test" in run and "npm install" in run and run.index("npm install") > run.index("npm test"):
            bad.append(step.get("name", "<unnamed step>"))
    return bad


def _subpackages_missing_install_before_test(root: Path, subpackages: list[str], steps: list[dict]) -> list[str]:
    missing = []
    for pkg in subpackages:
        pkg_json = json.loads((root / pkg / "package.json").read_text(encoding="utf-8"))
        if not pkg_json.get("dependencies"):
            continue  # nothing to install — pi-extension has no deps today

        test_step_index = next(
            (i for i, s in enumerate(steps)
             if s.get("working-directory") == pkg and "npm test" in s.get("run", "")),
            None,
        )
        if test_step_index is None:
            missing.append(pkg)  # no test step at all is also "not preceded by install"
            continue

        installs_before = any(
            "npm install" in steps[i].get("run", "") and steps[i].get("working-directory") == pkg
            for i in range(test_step_index + 1)
        )
        if not installs_before:
            missing.append(pkg)
    return missing


def _subpackages_missing_from_test_all(subpackages: list[str], script_text: str) -> list[str]:
    return [
        pkg for pkg in subpackages
        if f'"{pkg}"' not in script_text and f"'{pkg}'" not in script_text
    ]


# --- checks against the real repo ---

def test_every_node_subpackage_has_a_ci_step_that_tests_it():
    subpackages = _node_subpackages()
    assert subpackages, "expected at least one Node subpackage with a test script"
    missing = _subpackages_missing_ci_step(subpackages, _workflow_steps())
    assert not missing, (
        f"{missing} declare a test script but no CI step in "
        f"{WORKFLOW_PATH.relative_to(ROOT)} runs npm test for them"
    )


def test_npm_install_precedes_npm_test_within_each_ci_step():
    bad = _steps_with_install_after_test(_workflow_steps())
    assert not bad, f"steps run npm install after npm test in the same block: {bad}"


def test_subpackage_with_dependencies_has_install_somewhere_before_its_test_step():
    missing = _subpackages_missing_install_before_test(ROOT, _node_subpackages(), _workflow_steps())
    assert not missing, f"{missing} declare dependencies with no install step before their test step"


def test_local_test_all_script_covers_every_node_subpackage():
    """scripts/test_all.py is the local, no-CI equivalent of the workflow
    above — it must not drift from the same set of subpackages, or a
    contributor running it locally gets a false "everything passed"."""
    missing = _subpackages_missing_from_test_all(_node_subpackages(), TEST_ALL_PATH.read_text(encoding="utf-8"))
    assert not missing, f"{missing} have a test script but scripts/test_all.py doesn't reference them"


# --- proof the checks above actually detect a problem, not just pass by luck ---

def test_detects_a_subpackage_missing_from_ci():
    steps = [{"name": "other", "run": "npm test", "working-directory": "other-pkg"}]
    assert _subpackages_missing_ci_step(["some-pkg"], steps) == ["some-pkg"]
    assert _subpackages_missing_ci_step(["other-pkg"], steps) == []


def test_detects_install_running_after_test():
    bad_step = {"name": "backwards", "run": "npm test\nnpm install"}
    good_step = {"name": "forwards", "run": "npm install\nnpm test"}
    assert _steps_with_install_after_test([bad_step]) == ["backwards"]
    assert _steps_with_install_after_test([good_step]) == []


def test_detects_missing_install_before_test_step(tmp_path):
    pkg_dir = tmp_path / "needs-install"
    pkg_dir.mkdir()
    (pkg_dir / "package.json").write_text(json.dumps({"dependencies": {"left-pad": "^1.0.0"}}))
    steps_without_install = [{"working-directory": "needs-install", "run": "npm test"}]
    steps_with_install = [{"working-directory": "needs-install", "run": "npm install\nnpm test"}]

    assert _subpackages_missing_install_before_test(tmp_path, ["needs-install"], steps_without_install) == ["needs-install"]
    assert _subpackages_missing_install_before_test(tmp_path, ["needs-install"], steps_with_install) == []


def test_detects_a_subpackage_missing_from_test_all_script():
    assert _subpackages_missing_from_test_all(["some-pkg"], "NODE_SUBPACKAGES = []") == ["some-pkg"]
    assert _subpackages_missing_from_test_all(["some-pkg"], 'NODE_SUBPACKAGES = ["some-pkg"]') == []
