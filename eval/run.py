#!/usr/bin/env python3
"""Runner for the RFC-0005 evaluation corpus.

Loads eval/corpus/*.yaml, sends each scenario to a Backend, and reports
pass/fail against the labeled expectation. This is the automated-runner
gap named in docs/ROADMAP.md and eval/README.md as not yet built.

Backends:
  stub           - a keyword heuristic, not a model. Proves the harness
                   plumbing works end to end. Its pass/fail numbers are
                   not evidence about Instinct. Default, zero setup.
  api            - real Anthropic API call. Needs `pip install anthropic`
                   and ANTHROPIC_API_KEY in the environment.
  openai-compat  - real call to any OpenAI-chat-completions-shaped host
                   (Groq, Together, Fireworks, DeepInfra, Ollama Cloud,
                   etc.). Needs INSTINCT_EVAL_BASE_URL, INSTINCT_EVAL_API_KEY,
                   INSTINCT_EVAL_MODEL in the environment — no extra
                   package required, stdlib urllib only.

Usage:
  python eval/run.py                          # stub backend, all corpora
  python eval/run.py --corpus trigger          # one corpus only
  python eval/run.py --backend api             # needs an Anthropic key
  INSTINCT_EVAL_BASE_URL=... INSTINCT_EVAL_API_KEY=... INSTINCT_EVAL_MODEL=... \\
    python eval/run.py --backend openai-compat # needs the three env vars above
  python eval/run.py --backend openai-compat --samples 3  # majority vote,
                                                            # see RFC-0009
"""

from __future__ import annotations

import argparse
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

CORPUS_DIR = Path(__file__).parent / "corpus"


class Backend(ABC):
    """What a runner needs from something that can answer the Gate."""

    @abstractmethod
    def should_trigger(self, request: str, context: Optional[str]) -> bool:
        ...

    @abstractmethod
    def classify_tier(self, request: str, context: Optional[str]) -> int:
        """Return 1, 2, or 3."""


class StubBackend(Backend):
    """Keyword heuristic. Exists to smoke-test the harness, not to grade
    Instinct. See module docstring — do not report these numbers as
    evaluation results.
    """

    _TIER3_HINTS = (
        "public", "breaking", "auth", "payment", "delet", "production",
        "trust", "deprecat", "signature", "call sites",
    )
    _TIER2_HINTS = ("refactor", "extract", "helper", "shared", "reuse")
    _INFO_HINTS = ("what does", "why do we", "why does")
    _EXECUTION_ONLY_HINTS = ("rename", "typo", "fix the typo")

    def should_trigger(self, request: str, context: Optional[str]) -> bool:
        low = request.lower()
        if any(h in low for h in self._INFO_HINTS):
            return False
        if any(h in low for h in self._EXECUTION_ONLY_HINTS) and "everywhere" not in low:
            return False
        return True

    def classify_tier(self, request: str, context: Optional[str]) -> int:
        text = f"{request} {context or ''}".lower()
        if any(h in text for h in self._TIER3_HINTS):
            return 3
        if any(h in text for h in self._TIER2_HINTS):
            return 2
        return 1


SKILL_PATH = Path(__file__).parent.parent / "SKILL.md"

_TIER_PROMPT = """You are evaluating a Claude Skill's rules, not writing code. Below is a
skill file (frontmatter + body) and a single user request it may apply to.

--- SKILL.md ---
{skill}
--- end SKILL.md ---

Request: {request}
Context: {context}

Answer two questions using only the skill text above:
1. Would the `description` in the frontmatter cause this skill to be loaded
   for this request? Answer yes or no.
2. If yes, walk "The Gate" section's three questions against the request
   (and context, if given) and state which tier it lands in: 1, 2, or 3.
   If the answer to (1) is no, answer "n/a".

Respond with exactly two lines, nothing else:
TRIGGER: yes|no
TIER: 1|2|3|n/a
"""


class ModelBackend(Backend):
    """Shared plumbing for anything that answers by calling a real model:
    build the prompt, parse TRIGGER/TIER out of the reply. Subclasses only
    implement `_call_model(prompt) -> raw text response`. Extending this
    instead of duplicating ApiBackend's parsing logic in every new backend
    is the same "reuse before you add" rule SKILL.md itself states for
    Consequential-tier changes, applied to this file.
    """

    def _call_model(self, prompt: str) -> str:
        raise NotImplementedError

    def _ask(self, request: str, context: Optional[str]) -> tuple[bool, Optional[int]]:
        prompt = _TIER_PROMPT.format(skill=self._skill_text, request=request, context=context or "none")
        text = self._call_model(prompt)
        trigger = "TRIGGER: yes" in text
        tier = None
        for tok in ("1", "2", "3"):
            if f"TIER: {tok}" in text:
                tier = int(tok)
        return trigger, tier

    def should_trigger(self, request: str, context: Optional[str]) -> bool:
        trigger, _ = self._ask(request, context)
        return trigger

    def classify_tier(self, request: str, context: Optional[str]) -> int:
        _, tier = self._ask(request, context)
        if tier is None:
            raise ValueError("Model did not return a parseable TIER line")
        return tier


class ApiBackend(ModelBackend):
    """Real backend: calls the Anthropic Messages API with SKILL.md's
    actual contents as context and asks it to answer the Gate directly.
    Requires `pip install anthropic` and an ANTHROPIC_API_KEY in the
    environment — fails loudly and immediately if either is missing,
    rather than silently falling back to something else.
    """

    def __init__(self, model: str = "claude-sonnet-5"):
        try:
            import anthropic
        except ImportError as e:
            raise RuntimeError(
                "ApiBackend needs the anthropic package: pip install anthropic"
            ) from e
        import os
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ApiBackend needs ANTHROPIC_API_KEY set in the environment")
        self._client = anthropic.Anthropic()
        self._model = model
        self._skill_text = SKILL_PATH.read_text(encoding="utf-8")

    def _call_model(self, prompt: str) -> str:
        reply = self._client.messages.create(
            model=self._model,
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in reply.content if hasattr(block, "text"))


class OpenAICompatBackend(ModelBackend):
    """Real backend for any host that serves the OpenAI chat-completions
    API shape — which is most open-model hosts (Groq, Together, Fireworks,
    DeepInfra, Ollama Cloud, and others serving Llama and similar). Uses
    only the standard library (urllib) rather than adding a dependency for
    what is, from here, a single POST.

    Configured entirely through environment variables — the key is never
    written to a file in this repo, and this class never logs or returns
    it:

      INSTINCT_EVAL_BASE_URL   e.g. https://api.groq.com/openai/v1
      INSTINCT_EVAL_API_KEY    bearer token
      INSTINCT_EVAL_MODEL      e.g. llama-3.3-70b-versatile

    Run it as a one-shot env assignment on the same command line as the
    script invocation, not with a separate `export`/`$env:` step — shell
    state doesn't persist between tool calls in some harnesses, and a
    one-liner keeps the key out of anything that isn't this one process:

      INSTINCT_EVAL_BASE_URL=... INSTINCT_EVAL_API_KEY=... INSTINCT_EVAL_MODEL=... \\
        python eval/run.py --backend openai-compat
    """

    def __init__(self):
        import os
        self._base_url = os.environ.get("INSTINCT_EVAL_BASE_URL")
        self._api_key = os.environ.get("INSTINCT_EVAL_API_KEY")
        self._model = os.environ.get("INSTINCT_EVAL_MODEL")
        missing = [
            name for name, val in (
                ("INSTINCT_EVAL_BASE_URL", self._base_url),
                ("INSTINCT_EVAL_API_KEY", self._api_key),
                ("INSTINCT_EVAL_MODEL", self._model),
            ) if not val
        ]
        if missing:
            raise RuntimeError(
                "OpenAICompatBackend needs env vars: " + ", ".join(missing)
            )
        self._skill_text = SKILL_PATH.read_text(encoding="utf-8")

    def _call_model(self, prompt: str) -> str:
        import json
        import urllib.error
        import urllib.request

        body = json.dumps({
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            # Reasoning models (gpt-oss and similar) spend tokens on a
            # hidden chain-of-thought before the final `content` field —
            # confirmed empirically: 100 truncated before any content was
            # emitted at all, 800 left room for both, and even 1024 still
            # truncated on some scenarios in practice. Generous on purpose.
            "max_tokens": 2048,
            "temperature": 0,
        }).encode("utf-8")
        req = urllib.request.Request(
            self._base_url.rstrip("/") + "/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            # Read and surface the body — it's almost always a clearer
            # error than the bare status code (bad model name, bad key,
            # wrong base URL for this provider's actual endpoint shape).
            detail = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"{self._base_url} returned {e.code}: {detail}") from e
        return payload["choices"][0]["message"]["content"]


BACKENDS = {"stub": StubBackend, "api": ApiBackend, "openai-compat": OpenAICompatBackend}


@dataclass
class Result:
    corpus: str
    id: str
    passed: bool
    expected: object
    actual: object
    note: str = ""
    agreement: str = ""  # e.g. "3/3", "2/3" — empty when samples=1


def load_corpus(name: str) -> list[dict]:
    path = CORPUS_DIR / f"{name}.yaml"
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _sample(call, samples: int):
    """Call `call()` `samples` times, catching per-call errors so one bad
    response doesn't lose the rest of the samples, and return (majority
    value, "k/n" agreement string). Ties broken by first-seen order — for
    small N that's a real limitation, not a hidden one: the agreement
    string itself exposes a tie (e.g. "1/2") for anyone reading the report.
    Added after RFC-0009 found a backend disagreeing with itself on
    identical zero-temperature calls; a single sample can't tell noise from
    a real miss, and pretending it can is worse than admitting samples=1
    is a weak read.
    """
    from collections import Counter
    values = []
    for _ in range(samples):
        try:
            values.append(call())
        except Exception as e:  # noqa: BLE001 - see module-level rationale
            values.append(f"ERROR: {e}")
    counts = Counter(values)
    value, count = counts.most_common(1)[0]
    return value, f"{count}/{samples}"


def run_trigger(backend: Backend, samples: int = 1) -> list[Result]:
    results = []
    for entry in load_corpus("trigger"):
        actual, agreement = _sample(
            lambda e=entry: backend.should_trigger(e["request"], e.get("context")), samples
        )
        # PyYAML parses bare yes/no as bool already (YAML 1.1); accept both
        # that and a literal "yes"/"no" string in case the corpus is hand-
        # edited into the string form later.
        raw = entry["expected_trigger"]
        expected = raw if isinstance(raw, bool) else raw == "yes"
        results.append(Result("trigger", entry["id"], actual == expected, expected, actual, entry.get("note", ""), agreement))
    return results


def run_gate_tier(backend: Backend, samples: int = 1) -> list[Result]:
    results = []
    for entry in load_corpus("gate_tier"):
        adversarial = " [adversarial]" if entry.get("adversarial") else ""
        actual, agreement = _sample(
            lambda e=entry: backend.classify_tier(e["request"], e.get("context")), samples
        )
        expected = entry["expected_tier"]
        results.append(Result("gate_tier", entry["id"] + adversarial, actual == expected, expected, actual, entry.get("note", ""), agreement))
    return results


def run_worked_examples() -> None:
    print("worked_examples: shape checks require reading the response, not")
    print("just a label - this runner can't grade them. See")
    print("docs/rfcs/0006-skill-v1-dry-run.md for the last manual pass.")


def report(results: list[Result]) -> bool:
    all_ok = True
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        if not r.passed:
            all_ok = False
        agreement = f"  agreement={r.agreement}" if r.agreement else ""
        print(f"  [{status}] {r.corpus}:{r.id}  expected={r.expected!r} actual={r.actual!r}{agreement}")
    return all_ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--backend", choices=BACKENDS, default="stub")
    parser.add_argument("--corpus", choices=["trigger", "gate_tier", "worked_examples", "all"], default="all")
    parser.add_argument("--samples", type=int, default=1, help="repeat each scenario N times, report majority vote + agreement (RFC-0009)")
    args = parser.parse_args()

    try:
        backend = BACKENDS[args.backend]()
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if args.backend == "stub":
        print("=" * 70)
        print("STUB BACKEND: keyword heuristic, not a model.")
        print("Proves the harness runs end to end. NOT an evaluation result.")
        print("See eval/README.md before citing these numbers as anything.")
        print("=" * 70)

    all_ok = True
    try:
        if args.corpus in ("trigger", "all"):
            print("\ntrigger corpus:")
            all_ok &= report(run_trigger(backend, args.samples))
        if args.corpus in ("gate_tier", "all"):
            print("\ngate_tier corpus:")
            all_ok &= report(run_gate_tier(backend, args.samples))
        if args.corpus in ("worked_examples", "all"):
            print("\nworked_examples:")
            run_worked_examples()
    except NotImplementedError as e:
        print(f"\n{e}", file=sys.stderr)
        return 2

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
