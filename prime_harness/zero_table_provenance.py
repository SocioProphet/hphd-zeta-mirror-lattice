"""G0 zero-table provenance validation for Prime Harness v0.2."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
from hashlib import sha256
from pathlib import Path

from .zeta_zeros import ZeroTable, load_zero_table


# Hardcoded fixture ordinates. These are not computed from a loaded table.
# Values are rounded/truncated from standard zeta-zero tables.
FIXTURE_GAMMAS: dict[int, Decimal] = {
    1: Decimal("14.134725141734693790457251983562470270784257115699"),
    50: Decimal("143.11184580762063273940512386891392996623310243035"),
    100: Decimal("236.52422966581620580247550795566297868952949521219"),
    200: Decimal("396.3818542225921869319994544917305290637615996881"),
}


@dataclass(frozen=True)
class ZeroTableProvenance:
    """Deterministic report emitted by the G0 validator."""

    primary_path: str
    independent_path: str
    n_check: int
    primary_sha256: str
    independent_sha256: str
    precision: str
    fixture_indices: tuple[int, ...]
    max_cross_source_delta: str
    status: str = "validated"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _file_sha256(path: str | Path) -> str:
    h = sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _require_strictly_increasing(table: ZeroTable, n_check: int) -> None:
    table.require_count(n_check)
    for idx in range(1, n_check):
        if table.values[idx] <= table.values[idx - 1]:
            raise ValueError(
                f"zero table is not strictly increasing at rows {idx} and {idx + 1}"
            )


def _require_fixtures(table: ZeroTable, tolerance: Decimal) -> None:
    for index, expected in FIXTURE_GAMMAS.items():
        table.require_count(index)
        observed = table.values[index - 1]
        if abs(observed - expected) > tolerance:
            raise ValueError(
                f"zero-table fixture mismatch at gamma_{index}: "
                f"observed={observed}, expected={expected}, tolerance={tolerance}"
            )


def validate_zero_table(
    table_path: str | Path,
    independent_source_path: str | Path,
    n_check: int = 200,
    tolerance: Decimal = Decimal("1e-12"),
) -> ZeroTableProvenance:
    """Validate a primary zero table against an independent source.

    This is the fail-closed G0 gate. It requires two source files, monotone
    ordinates, fixture checks, cross-source agreement, and deterministic hashes.
    """

    if Path(table_path).resolve() == Path(independent_source_path).resolve():
        raise ValueError("G0 requires two distinct zero-table source files")

    primary = load_zero_table(table_path)
    independent = load_zero_table(independent_source_path)

    primary.require_count(n_check)
    independent.require_count(n_check)
    _require_strictly_increasing(primary, n_check)
    _require_strictly_increasing(independent, n_check)
    _require_fixtures(primary, tolerance)
    _require_fixtures(independent, tolerance)

    max_delta = Decimal("0")
    for i in range(n_check):
        delta = abs(primary.values[i] - independent.values[i])
        max_delta = max(max_delta, delta)
        if delta > tolerance:
            raise ValueError(
                f"zero-table cross-source mismatch at row {i + 1}: "
                f"delta={delta}, tolerance={tolerance}"
            )

    return ZeroTableProvenance(
        primary_path=str(Path(table_path)),
        independent_path=str(Path(independent_source_path)),
        n_check=n_check,
        primary_sha256=_file_sha256(table_path),
        independent_sha256=_file_sha256(independent_source_path),
        precision="Decimal(50)",
        fixture_indices=tuple(sorted(FIXTURE_GAMMAS)),
        max_cross_source_delta=str(max_delta),
    )
