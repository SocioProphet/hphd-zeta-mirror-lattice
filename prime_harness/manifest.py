"""Deterministic manifest writer for Prime Harness v0.2."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any

from .intervals import LogBox
from .li_quadrature import li_box_expected
from .psi_residual import psi_box_residual, psi_increment
from .sieve_truth import segmented_primes


@dataclass(frozen=True)
class BoxObservation:
    index: int
    u_start: float
    u_end: float
    x_start: float
    x_end: float
    prime_count: int
    li_expected: float
    pi_residual: float
    psi_increment: float
    psi_residual: float


@dataclass(frozen=True)
class BenchmarkManifest:
    schema_version: str
    interval_name: str
    delta_u: float
    zero_table_provenance: dict[str, Any]
    boxes: list[BoxObservation]
    manifest_hash: str | None = None

    def without_hash(self) -> dict[str, Any]:
        data = asdict(self)
        data["manifest_hash"] = None
        return data

    def canonical_json_without_hash(self) -> str:
        return json.dumps(self.without_hash(), sort_keys=True, separators=(",", ":"))

    def with_computed_hash(self) -> "BenchmarkManifest":
        digest = sha256(self.canonical_json_without_hash().encode("utf-8")).hexdigest()
        return BenchmarkManifest(
            schema_version=self.schema_version,
            interval_name=self.interval_name,
            delta_u=self.delta_u,
            zero_table_provenance=self.zero_table_provenance,
            boxes=self.boxes,
            manifest_hash=digest,
        )


def _int_interval_for_box(box: LogBox) -> tuple[int, int]:
    """Convert floating ordinary-scale endpoints to a half-open integer interval."""

    return max(2, math.ceil(box.x_start)), max(2, math.ceil(box.x_end))


def observe_box(box: LogBox) -> BoxObservation:
    """Construct a box observation using the sieve oracle exactly once."""

    start_i, end_i = _int_interval_for_box(box)
    primes = segmented_primes(start_i, end_i)
    li_expected = li_box_expected(box.x_start, box.x_end)
    prime_count = len(primes)
    psi_inc = psi_increment(box.x_start, box.x_end)
    return BoxObservation(
        index=box.index,
        u_start=box.u_start,
        u_end=box.u_end,
        x_start=box.x_start,
        x_end=box.x_end,
        prime_count=prime_count,
        li_expected=li_expected,
        pi_residual=prime_count - li_expected,
        psi_increment=psi_inc,
        psi_residual=psi_box_residual(box.x_start, box.x_end),
    )


def build_manifest(
    interval_name: str,
    boxes: list[LogBox],
    delta_u: float,
    zero_table_provenance: dict[str, Any],
) -> BenchmarkManifest:
    """Build a deterministic benchmark manifest from already-declared boxes."""

    observations = [observe_box(box) for box in boxes]
    manifest = BenchmarkManifest(
        schema_version="prime-harness-v0.2-m1",
        interval_name=interval_name,
        delta_u=delta_u,
        zero_table_provenance=zero_table_provenance,
        boxes=observations,
    )
    return manifest.with_computed_hash()


def write_manifest(manifest: BenchmarkManifest, path: str | Path) -> None:
    """Write manifest JSON with sorted keys and stable formatting."""

    data = asdict(manifest)
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
