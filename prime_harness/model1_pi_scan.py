"""Model 1 π explicit-formula N-scan for Prime Harness v0.2.

This module performs the M2b measurement path using the normative real-u
integral form declared in SPEC v0.2. It consumes validated zero tables,
box manifests, and reports VarExpl(1,N) plus the saturation envelope.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

from .explicit_formula import decimal_gammas_as_float, pi_model1_prediction
from .intervals import Interval, make_log_boxes
from .manifest import build_manifest
from .metrics import saturation_envelope, variance_explained
from .model1_psi_scan import DEFAULT_N_VALUES
from .zero_table_provenance import ZeroTableProvenance, validate_zero_table
from .zeta_zeros import load_zero_table


@dataclass(frozen=True)
class PiScanPoint:
    """One N value in a Model 1 π N-scan."""

    n: int
    var_expl: float
    sse: float
    sst: float


@dataclass(frozen=True)
class PiScanReport:
    """Serializable M2b π N-scan report."""

    schema_version: str
    interval_name: str
    interval_start: int
    interval_end: int
    delta_u: float
    n_values: tuple[int, ...]
    zero_table_provenance: dict[str, object]
    manifest_hash: str
    points: tuple[PiScanPoint, ...]
    saturation_envelope: tuple[tuple[int, float], ...]
    branch_convention: str
    result_status: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


def run_model1_pi_scan(
    interval: Interval,
    delta_u: float,
    primary_zero_table_path: str | Path,
    independent_zero_table_path: str | Path,
    *,
    n_values: tuple[int, ...] = DEFAULT_N_VALUES,
    n_check: int | None = None,
) -> PiScanReport:
    """Run Model 1 π explicit-formula N-scan on one interval.

    This function validates G0 before loading zeros for the scan. It writes no
    files and claims no novelty; callers may serialize the returned report.
    """

    interval.validate()
    if not n_values:
        raise ValueError("at least one N value is required")
    if any(n < 0 for n in n_values):
        raise ValueError("N values must be non-negative")

    max_n = max(n_values)
    provenance: ZeroTableProvenance = validate_zero_table(
        primary_zero_table_path,
        independent_zero_table_path,
        n_check=n_check or max(max_n, 200),
    )
    zero_table = load_zero_table(primary_zero_table_path)
    gammas = decimal_gammas_as_float(zero_table.values, max_n)

    boxes = make_log_boxes(interval.start, interval.end, delta_u)
    manifest = build_manifest(
        interval_name=interval.name,
        boxes=boxes,
        delta_u=delta_u,
        zero_table_provenance=provenance.to_dict(),
    )

    observed = [box.pi_residual for box in manifest.boxes]
    points: list[PiScanPoint] = []
    for n in n_values:
        predicted = [
            pi_model1_prediction(gammas, box.u_start, box.u_end, n)
            for box in manifest.boxes
        ]
        metric = variance_explained(observed, predicted)
        points.append(
            PiScanPoint(
                n=n,
                var_expl=metric.var_expl,
                sse=metric.sse,
                sst=metric.sst,
            )
        )

    envelope = tuple(saturation_envelope([(p.n, p.var_expl) for p in points]))
    return PiScanReport(
        schema_version="prime-harness-v0.2-m2b-pi-scan",
        interval_name=interval.name,
        interval_start=interval.start,
        interval_end=interval.end,
        delta_u=delta_u,
        n_values=tuple(n_values),
        zero_table_provenance=provenance.to_dict(),
        manifest_hash=manifest.manifest_hash or "",
        points=tuple(points),
        saturation_envelope=envelope,
        branch_convention="N1: real-u integral primary; complex-Ei not used",
        result_status="measurement_only_no_novelty_claim",
    )


def write_pi_scan_report(report: PiScanReport, path: str | Path) -> None:
    """Write a deterministic JSON report."""

    Path(path).write_text(report.to_json(), encoding="utf-8")
