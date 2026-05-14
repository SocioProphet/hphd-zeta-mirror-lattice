"""Tests for Prime Harness v0.2 M1 infrastructure."""

from __future__ import annotations

from decimal import Decimal
import math

import pytest

from prime_harness.explicit_formula import psi_model1_prediction, psi_zero_integral_closed
from prime_harness.intervals import deterministic_blocked_folds, make_log_boxes
from prime_harness.li_quadrature import li_box_expected, offset_li, zero_resolution_ok
from prime_harness.manifest import build_manifest
from prime_harness.metrics import saturation_envelope, standardized_residual, variance_explained
from prime_harness.psi_residual import psi_box_residual, psi_increment
from prime_harness.sieve_truth import is_prime_by_trial, prime_count, segmented_primes
from prime_harness.zero_table_provenance import FIXTURE_GAMMAS, validate_zero_table


def _fixture_zero_lines() -> str:
    """Build a monotone 200-row fixture table with hardcoded gamma fixtures."""

    rows: list[Decimal | None] = [None] * 200
    anchors = {idx - 1: value for idx, value in FIXTURE_GAMMAS.items()}
    for idx, value in anchors.items():
        rows[idx] = value

    anchor_positions = sorted(anchors)
    for left, right in zip(anchor_positions, anchor_positions[1:]):
        left_v = anchors[left]
        right_v = anchors[right]
        step = (right_v - left_v) / Decimal(right - left)
        for i in range(left + 1, right):
            rows[i] = left_v + step * Decimal(i - left)

    # No values before gamma_1 in this fixture. Ensure all rows exist.
    assert all(v is not None for v in rows)
    return "\n".join(f"{i + 1} {rows[i]}" for i in range(200)) + "\n"


def test_segmented_sieve_small_interval() -> None:
    assert segmented_primes(2, 30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert prime_count(100, 200) == 21
    assert is_prime_by_trial(101)
    assert not is_prime_by_trial(121)


def test_log_boxes_and_blocked_folds() -> None:
    boxes = make_log_boxes(100, 200, 0.1)
    assert boxes
    assert boxes[0].x_start == pytest.approx(100)
    assert boxes[-1].x_end == pytest.approx(200)
    folds = deterministic_blocked_folds(len(boxes), k=3)
    assert folds
    for train, eval_ in folds:
        assert set(train).isdisjoint(eval_)
        assert train
        assert eval_


def test_zero_table_provenance_accepts_two_matching_sources(tmp_path) -> None:
    table_a = tmp_path / "odlyzko.txt"
    table_b = tmp_path / "lmfdb.txt"
    fixture = _fixture_zero_lines()
    table_a.write_text(fixture, encoding="utf-8")
    table_b.write_text(fixture, encoding="utf-8")

    report = validate_zero_table(table_a, table_b)
    assert report.status == "validated"
    assert report.n_check == 200
    assert report.fixture_indices == (1, 50, 100, 200)
    assert report.max_cross_source_delta == "0"


def test_zero_table_provenance_rejects_single_source(tmp_path) -> None:
    table = tmp_path / "zeros.txt"
    table.write_text(_fixture_zero_lines(), encoding="utf-8")
    with pytest.raises(ValueError, match="two distinct"):
        validate_zero_table(table, table)


def test_li_quadrature_and_resolution() -> None:
    assert offset_li(10) > 0
    assert li_box_expected(100, 200) > 0
    assert zero_resolution_ok(0.0025, 396)
    assert not zero_resolution_ok(0.005, 396)


def test_psi_increment_includes_prime_powers() -> None:
    expected = 3 * math.log(2) + 2 * math.log(3) + math.log(5) + math.log(7)
    assert psi_increment(2, 11) == pytest.approx(expected)
    assert psi_box_residual(2, 11) == pytest.approx(expected - 9)


def test_explicit_formula_zero_integral_closed_gamma_zero() -> None:
    a = math.log(4)
    b = math.log(9)
    expected = 2 * (math.exp(b / 2) - math.exp(a / 2))
    assert psi_zero_integral_closed(0.0, a, b).real == pytest.approx(expected)
    assert psi_model1_prediction([14.134725141734695], a, b, 0) == 0.0


def test_metrics() -> None:
    result = variance_explained([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
    assert result.var_expl == pytest.approx(1.0)
    assert saturation_envelope([(1, 0.1), (2, 0.05), (5, 0.2)]) == [
        (1, 0.1),
        (2, 0.1),
        (5, 0.2),
    ]
    assert standardized_residual(4, 4) == pytest.approx(2.0)


def test_manifest_hash_is_deterministic() -> None:
    boxes = make_log_boxes(100, 110, 0.05)
    provenance = {"status": "validated", "fixture": True}
    m1 = build_manifest("tiny", boxes, 0.05, provenance)
    m2 = build_manifest("tiny", boxes, 0.05, provenance)
    assert m1.manifest_hash == m2.manifest_hash
    assert m1.boxes[0].prime_count >= 0
    assert m1.boxes[0].li_expected > 0
