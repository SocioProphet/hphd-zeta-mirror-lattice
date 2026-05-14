"""Paired ψ/π scan orchestration for Prime Harness v0.2."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

from .intervals import Interval
from .model1_pi_scan import run_model1_pi_scan, write_pi_scan_report
from .model1_psi_scan import DEFAULT_N_VALUES, run_model1_psi_scan, write_psi_scan_report


@dataclass(frozen=True)
class PairScanIndex:
    """Index tying together paired ψ and π scan artifacts."""

    schema_version: str
    interval: str
    delta_u: float
    n_values: tuple[int, ...]
    psi_report: str
    pi_report: str
    psi_manifest_hash: str
    pi_manifest_hash: str
    result_status: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


def run_pair_scans(
    interval: Interval,
    delta_u: float,
    primary_zero_table_path: str | Path,
    independent_zero_table_path: str | Path,
    output_dir: str | Path,
    *,
    n_values: tuple[int, ...] = DEFAULT_N_VALUES,
) -> PairScanIndex:
    """Run paired Model 1 ψ and π scans and write all reports.

    The individual scan reports retain `measurement_only_no_novelty_claim`.
    The returned index is an artifact locator, not a benchmark claim.
    """

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    psi_report = run_model1_psi_scan(
        interval=interval,
        delta_u=delta_u,
        primary_zero_table_path=primary_zero_table_path,
        independent_zero_table_path=independent_zero_table_path,
        n_values=n_values,
    )
    pi_report = run_model1_pi_scan(
        interval=interval,
        delta_u=delta_u,
        primary_zero_table_path=primary_zero_table_path,
        independent_zero_table_path=independent_zero_table_path,
        n_values=n_values,
    )

    psi_path = output / f"model1_psi_scan_{interval.name}.json"
    pi_path = output / f"model1_pi_scan_{interval.name}.json"
    index_path = output / f"model1_pair_scan_{interval.name}_index.json"

    write_psi_scan_report(psi_report, psi_path)
    write_pi_scan_report(pi_report, pi_path)

    index = PairScanIndex(
        schema_version="prime-harness-v0.2-m2-pair-scan-index",
        interval=interval.name,
        delta_u=delta_u,
        n_values=tuple(n_values),
        psi_report=str(psi_path),
        pi_report=str(pi_path),
        psi_manifest_hash=psi_report.manifest_hash,
        pi_manifest_hash=pi_report.manifest_hash,
        result_status="measurement_only_no_novelty_claim",
    )
    index_path.write_text(index.to_json(), encoding="utf-8")
    return index
