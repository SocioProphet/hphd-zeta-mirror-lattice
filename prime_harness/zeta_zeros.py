"""Zeta-zero table loading for Prime Harness v0.2."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 50


@dataclass(frozen=True)
class ZeroTable:
    """Loaded positive zeta-zero ordinates gamma_n."""

    path: str
    values: tuple[Decimal, ...]

    def require_count(self, n: int) -> None:
        if len(self.values) < n:
            raise ValueError(f"zero table has {len(self.values)} rows; required {n}")

    def as_floats(self, n: int | None = None) -> list[float]:
        vals = self.values if n is None else self.values[:n]
        return [float(v) for v in vals]


def load_zero_table(path: str | Path) -> ZeroTable:
    """Load a one-column or two-column gamma_n table.

    Accepted line formats:
      n gamma
      gamma

    Blank lines and comment lines beginning with # are ignored.
    """

    p = Path(path)
    values: list[Decimal] = []

    for line_no, raw in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.replace(",", " ").split()
        try:
            if len(parts) == 1:
                gamma = Decimal(parts[0])
            else:
                int(parts[0])
                gamma = Decimal(parts[1])
        except Exception as exc:  # pragma: no cover - defensive diagnostic
            raise ValueError(f"invalid zero-table line {line_no}: {raw!r}") from exc
        values.append(gamma)

    if not values:
        raise ValueError(f"zero table is empty: {p}")

    return ZeroTable(path=str(p), values=tuple(values))
