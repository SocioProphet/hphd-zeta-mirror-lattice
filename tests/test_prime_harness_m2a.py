"""Tests for Prime Harness v0.2 M2a ψ N-scan."""

from __future__ import annotations

from decimal import Decimal
import json

from prime_harness.intervals import Interval
from prime_harness.model1_psi_scan import run_model1_psi_scan, write_psi_scan_report
from prime_harness.zero_table_provenance import FIXTURE_GAMMAS


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

    assert all(v is not None for v in rows)
    return "\n".join(f"{i + 1} {rows[i]}" for i in range(200)) + "\n"


def test_model1_psi_scan_report_shape(tmp_path) -> None:
    primary = tmp_path / "odlyzko_fixture.txt"
    independent = tmp_path / "lmfdb_fixture.txt"
    fixture = _fixture_zero_lines()
    primary.write_text(fixture, encoding="utf-8")
    independent.write_text(fixture, encoding="utf-8")

    report = run_model1_psi_scan(
        interval=Interval("tiny", 100, 200),
        delta_u=0.1,
        primary_zero_table_path=primary,
        independent_zero_table_path=independent,
        n_values=(1, 2, 5),
    )

    assert report.schema_version == "prime-harness-v0.2-m2a-psi-scan"
    assert report.interval_name == "tiny"
    assert report.manifest_hash
    assert len(report.points) == 3
    assert [point.n for point in report.points] == [1, 2, 5]
    assert len(report.saturation_envelope) == 3
    envelope_values = [value for _, value in report.saturation_envelope]
    assert envelope_values == sorted(envelope_values)
    assert report.result_status == "measurement_only_no_novelty_claim"


def test_model1_psi_scan_report_json_roundtrip(tmp_path) -> None:
    primary = tmp_path / "odlyzko_fixture.txt"
    independent = tmp_path / "lmfdb_fixture.txt"
    fixture = _fixture_zero_lines()
    primary.write_text(fixture, encoding="utf-8")
    independent.write_text(fixture, encoding="utf-8")

    report = run_model1_psi_scan(
        interval=Interval("tiny", 100, 120),
        delta_u=0.05,
        primary_zero_table_path=primary,
        independent_zero_table_path=independent,
        n_values=(1,),
    )
    output = tmp_path / "report.json"
    write_psi_scan_report(report, output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "prime-harness-v0.2-m2a-psi-scan"
    assert payload["zero_table_provenance"]["status"] == "validated"
    assert payload["points"][0]["n"] == 1
    assert payload["result_status"] == "measurement_only_no_novelty_claim"
