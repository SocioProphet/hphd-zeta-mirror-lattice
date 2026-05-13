"""Explicit-formula decomposition experiment (v0).

This experiment is intentionally conservative: it demonstrates *structure* rather than claiming
prime-counting accuracy.

We implement the explicit-formula decomposition for the Chebyshev function ψ(x):

  ψ(x) = x - Σ_ρ x^ρ/ρ - log(2π) - 1/2 log(1 - x^{-2})

In v0, we default to *no* non-trivial zeros (Σ_ρ term is empty) because fetching zeros is a
separate dependency and claim surface. The harness goal here is:

- compute and emit each term class deterministically,
- make the trivial/completion correction term visible,
- enforce typed language (we never claim a proof or convergence statement).

Run:
  python experiments/explicit_formula_decomposition.py --xmin 10 --xmax 1000 --steps 25 --out receipts

Receipt schema is stable and designed for regression testing.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import mpmath as mp


@dataclass(frozen=True)
class TermBreakdown:
    x: float
    main_term: str
    nontrivial_term: str
    completion_constant: str
    trivial_lattice_term: str
    assembled: str


def psi_explicit_terms(x: mp.mpf, zeros: Iterable[mp.mpc]) -> tuple[mp.mpf, mp.mpf, mp.mpf, mp.mpf, mp.mpf]:
    """Return (main, nontrivial, completion_const, trivial_lattice, assembled)."""

    main = x

    # Σ_ρ x^ρ/ρ
    nontrivial = mp.mpf("0")
    for rho in zeros:
        nontrivial += (x ** rho) / rho

    completion_const = mp.log(2 * mp.pi)
    trivial_lattice = mp.mpf("0.5") * mp.log(1 - x ** (-2))  # note: this is negative

    assembled = main - nontrivial - completion_const - trivial_lattice
    return main, nontrivial, completion_const, trivial_lattice, assembled


def geometric_grid(xmin: float, xmax: float, steps: int) -> list[float]:
    if xmin <= 1 or xmax <= xmin or steps < 2:
        raise ValueError("Require xmin>1, xmax>xmin, steps>=2")
    ratio = (xmax / xmin) ** (1.0 / (steps - 1))
    xs = [xmin * (ratio**i) for i in range(steps)]
    return xs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xmin", type=float, default=10.0)
    parser.add_argument("--xmax", type=float, default=1000.0)
    parser.add_argument("--steps", type=int, default=25)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("receipts"),
        help="Output directory for receipt JSON (default: receipts).",
    )
    parser.add_argument(
        "--receipt",
        type=str,
        default="explicit_formula_decomposition_v0.json",
        help="Receipt filename.",
    )
    # Future extension: accept a JSON list of zeros. v0 is intentionally empty.
    args = parser.parse_args()

    mp.mp.dps = 80

    xs = geometric_grid(args.xmin, args.xmax, args.steps)

    zeros: list[mp.mpc] = []

    rows: list[TermBreakdown] = []
    for x in xs:
        mx = mp.mpf(x)
        main_t, nt_t, cc_t, triv_t, assembled = psi_explicit_terms(mx, zeros)
        rows.append(
            TermBreakdown(
                x=float(x),
                main_term=mp.nstr(main_t, 40),
                nontrivial_term=mp.nstr(nt_t, 40),
                completion_constant=mp.nstr(cc_t, 40),
                trivial_lattice_term=mp.nstr(triv_t, 40),
                assembled=mp.nstr(assembled, 40),
            )
        )

    receipt: dict[str, Any] = {
        "experiment": "explicit_formula_decomposition_v0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "draft",
        "claim_boundary": "structure demonstration only; non-trivial zeros omitted by default; not a proof",
        "formula": "psi(x)=x - sum_{rho} x^rho/rho - log(2*pi) - 1/2*log(1-x^-2)",
        "parameters": {
            "xmin": args.xmin,
            "xmax": args.xmax,
            "steps": args.steps,
            "nontrivial_zero_count": len(zeros),
            "grid": "geometric",
            "mp_dps": int(mp.mp.dps),
        },
        "term_breakdown": [asdict(r) for r in rows],
        "quality_gates": {
            "nontrivial_term_empty_by_design": True,
            "trivial_lattice_term_present": True,
            "completion_constant_present": True,
        },
    }

    args.out.mkdir(parents=True, exist_ok=True)
    outpath = args.out / args.receipt
    outpath.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
