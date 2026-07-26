"""Tests for eval/run.py — the RFC-0005 corpus runner. Covers the parts
that don't need a live model: corpus loading/schema, the StubBackend
heuristic, and the repeat-sampling majority-vote logic added in RFC-0010.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "eval"))
import run as eval_run  # noqa: E402

ROOT = Path(__file__).parent.parent


def test_load_corpus_trigger_has_required_fields():
    entries = eval_run.load_corpus("trigger")
    assert len(entries) > 0
    for e in entries:
        assert "id" in e and "request" in e and "expected_trigger" in e


def test_load_corpus_gate_tier_has_required_fields():
    entries = eval_run.load_corpus("gate_tier")
    assert len(entries) > 0
    for e in entries:
        assert "id" in e and "request" in e and "expected_tier" in e
        assert e["expected_tier"] in (1, 2, 3)


def test_stub_backend_skips_pure_info_questions():
    backend = eval_run.StubBackend()
    assert backend.should_trigger("What does this function do?", None) is False


def test_stub_backend_triggers_on_new_code():
    backend = eval_run.StubBackend()
    assert backend.should_trigger("Add a new REST endpoint for X", None) is True


def test_stub_backend_tiers_trust_boundary_as_3():
    backend = eval_run.StubBackend()
    assert backend.classify_tier("Change the auth flow", None) == 3


def test_sample_majority_vote():
    calls = iter([1, 2, 1])
    value, agreement = eval_run._sample(lambda: next(calls), samples=3)
    assert value == 1
    assert agreement == "2/3"


def test_sample_catches_per_call_errors_without_crashing():
    def flaky():
        raise ValueError("boom")

    value, agreement = eval_run._sample(flaky, samples=2)
    assert "ERROR" in value
    assert agreement == "2/2"


def test_skill_md_referenced_by_eval_exists():
    """SKILL_PATH is a module-level constant other tests rely on implicitly
    (ApiBackend/OpenAICompatBackend read it) — catch it silently pointing
    nowhere before a real backend run does."""
    assert eval_run.SKILL_PATH.exists()
