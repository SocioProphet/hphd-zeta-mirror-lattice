"""Claim-boundary checks for the prime phase ranking harness specification.

These tests intentionally avoid third-party dependencies. They validate the v0.1
governance boundary before any executable benchmark harness is added.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "docs" / "04-prime-phase-ranking-harness.md"
SCHEMA_PATH = ROOT / "schemas" / "prime_phase_harness.schema.json"

REQUIRED_SPEC_PHRASES = [
    "computational experiment only",
    "pre-registered experimental constants",
    "G(n) is only an ordering score",
    "A gate that beats random order but fails to beat ascending order is not a successful next-prime search policy.",
    "No publication-grade language is allowed before the scale tiers are complete.",
]

REQUIRED_BASELINES = {
    "ascending_order",
    "random_order_fixed_seed",
    "wheel_channel_order",
    "distance_from_p",
    "local_density_prior",
    "phase_gate_order",
}

DISALLOWED_CLAIM_PATTERNS = [
    re.compile(r"\bprime formula\b", re.IGNORECASE),
    re.compile(r"\bproves RH\b", re.IGNORECASE),
    re.compile(r"\bproves BSD\b", re.IGNORECASE),
    re.compile(r"\bRH implies this gate\b", re.IGNORECASE),
    re.compile(r"\bcosine certifies primality\b", re.IGNORECASE),
    re.compile(r"\bcosine proves primality\b", re.IGNORECASE),
    re.compile(r"\bno free knobs\b", re.IGNORECASE),
    re.compile(r"\btuned composite\b", re.IGNORECASE),
]


class PrimePhaseSpecBoundaryTests(unittest.TestCase):
    def test_spec_exists(self) -> None:
        self.assertTrue(SPEC_PATH.exists(), f"missing spec: {SPEC_PATH}")

    def test_schema_exists(self) -> None:
        self.assertTrue(SCHEMA_PATH.exists(), f"missing schema: {SCHEMA_PATH}")

    def test_spec_contains_required_guardrails(self) -> None:
        text = SPEC_PATH.read_text(encoding="utf-8")
        for phrase in REQUIRED_SPEC_PHRASES:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_spec_does_not_promote_disallowed_claims(self) -> None:
        text = SPEC_PATH.read_text(encoding="utf-8")
        for pattern in DISALLOWED_CLAIM_PATTERNS:
            with self.subTest(pattern=pattern.pattern):
                self.assertIsNone(pattern.search(text))

    def test_schema_is_valid_json(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["title"], "Prime Phase Ranking Harness Receipt")
        self.assertEqual(schema["properties"]["schema_version"]["const"], "0.1.0")

    def test_schema_requires_claim_boundary(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertIn("claim_boundary", schema["required"])
        self.assertEqual(
            schema["properties"]["claim_boundary"]["const"],
            "computational_experiment_only_not_proof",
        )

    def test_schema_requires_pre_registration_block(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        required = set(schema["properties"]["pre_registration"]["required"])
        expected = {
            "input_policy",
            "magnitude_bands",
            "wheel_policy",
            "survivor_filters",
            "ranking_policies",
            "ranking_direction",
            "audit_method",
            "random_seed_ledger",
            "success_metrics",
        }
        self.assertEqual(required, expected)

    def test_schema_requires_mandatory_baselines(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        allowed = set(schema["properties"]["baselines"]["items"]["enum"])
        self.assertTrue(REQUIRED_BASELINES.issubset(allowed))
        self.assertGreaterEqual(schema["properties"]["baselines"]["minItems"], 6)

    def test_schema_tracks_ascending_order_comparison(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        window_required = set(schema["properties"]["windows"]["items"]["required"])
        for field in {
            "rank_gate",
            "rank_ascending",
            "rho_gate",
            "rho_ascending",
            "delta_rank_vs_ascending",
            "delta_rho_vs_ascending",
        }:
            with self.subTest(field=field):
                self.assertIn(field, window_required)

    def test_schema_aggregate_declares_ascending_verdict(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        aggregate_required = set(schema["properties"]["aggregates"]["required"])
        self.assertIn("beats_ascending_order", aggregate_required)
        self.assertEqual(
            schema["properties"]["aggregates"]["properties"]["beats_ascending_order"]["type"],
            "boolean",
        )


if __name__ == "__main__":
    unittest.main()
