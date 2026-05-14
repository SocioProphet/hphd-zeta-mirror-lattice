"""Tests for paired ψ/π scan execution support."""

from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path

from prime_harness.intervals import Interval
from prime_harness.pair_scans import run_pair_scans
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

    assert all(v is not None for v in rows)
    return "\n".join(f"{i + 1} {rows[i]}" for i in range(200)) + "\n"


def _write_fixture_tables(tmp_path: Path) -> tuple[Path, Path]:
    primary = tmp_path / "odlyzko_fixture.txt"
    independent = tmp_path / "lmfdb_fixture.txt"
    fixture = _fixture_zero_lines()
    primary.write_text(fixture, encoding="utf-8")
    independent.write_text(fixture, encoding="utf-8")
    return primary, independent


def test_validate_zero_table_report_payload(tmp_path) -> None:
    primary, independent = _write_fixture_tables(tmp_path)
    report = validate_zero_table(primary, independent)
    payload = report.to_dict()

    assert payload["status"] == "validated"
    assert payload["n_check"] == 200
    assert payload["primary_sha256"]
    assert payload["independent_sha256"]
    assert payload["fixture_indices"] == (1, 50, 100, 200)


def test_run_pair_scans_writes_index_and_reports(tmp_path) -> None:
    primary, independent = _write_fixture_tables(tmp_path)
    output_dir = tmp_path / "reports"

    index = run_pair_scans(
        interval=Interval("tiny", 100, 110),
        delta_u=0.1,
        primary_zero_table_path=primary,
        independent_zero_table_path=independent,
        output_dir=output_dir,
        n_values=(1,),
    )

    assert index.schema_version == "prime-harness-v0.2-m2-pair-scan-index"
    assert index.interval == "tiny"
    assert index.result_status == "measurement_only_no_novelty_claim"
    assert index.psi_manifest_hash
    assert index.pi_manifest_hash

    psi_path = Path(index.psi_report)
    pi_path = Path(index.pi_report)
    index_path = output_dir / "model1_pair_scan_tiny_index.json"

    assert psi_path.exists()
    assert pi_path.exists()
    assert index_path.exists()

    psi_payload = json.loads(psi_path.read_text(encoding="utf-8"))
    pi_payload = json.loads(pi_path.read_text(encoding="utf-8"))
    index_payload = json.loads(index_path.read_text(encoding="utf-8"))

    assert psi_payload["schema_version"] == "prime-harness-v0.2-m2a-psi-scan"
    assert pi_payload["schema_version"] == "prime-harness-v0.2-m2b-pi-scan"
    assert pi_payload["branch_convention"] == "N1: real-u integral primary; complex-Ei not used"
    assert index_payload["result_status"] == "measurement_only_no_novelty_claim"
    assert index_payload["psi_manifest_hash"] == index.psi_manifest_hash
    assert index_payload["pi_manifest_hash"] == index.pi_manifest_hash
