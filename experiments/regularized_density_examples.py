"""Regularized density examples for the HPHD zeta mirror-lattice lane.

This script deliberately separates ordinary divergent partial sums from
zeta-regularized analytic-continuation assignments.

It does not claim that divergent series converge in the ordinary sense.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import mpmath as mp


@dataclass(frozen=True)
class RegularizedAssignment:
    """A typed zeta-regularized assignment, not an ordinary sum."""

    series_label: str
    ordinary_status: str
    regularization_method: str
    regularized_expression: str
    regularized_value_decimal: str
    regularized_value_exact: str
    equality_type: str
    claim_boundary: str


def constant_partial_sum(n: int) -> int:
    """Return the nth partial sum of 1 + 1 + ... + 1."""
    if n < 0:
        raise ValueError("n must be non-negative")
    return n


def triangular_partial_sum(n: int) -> int:
    """Return the nth partial sum of 1 + 2 + ... + n."""
    if n < 0:
        raise ValueError("n must be non-negative")
    return n * (n + 1) // 2


def build_receipt(sample_sizes: list[int]) -> dict[str, Any]:
    """Build a receipt showing divergence separately from zeta regularization."""
    mp.mp.dps = 80

    ordinary_partial_sums = {
        "1+1+1+...": [
            {"n": n, "partial_sum": constant_partial_sum(n)} for n in sample_sizes
        ],
        "1+2+3+...": [
            {"n": n, "partial_sum": triangular_partial_sum(n)} for n in sample_sizes
        ],
    }

    assignments = [
        RegularizedAssignment(
            series_label="1+1+1+...",
            ordinary_status="diverges by ordinary partial-sum convergence",
            regularization_method="zeta analytic continuation",
            regularized_expression="zeta(0)",
            regularized_value_decimal=mp.nstr(mp.zeta(0), 50),
            regularized_value_exact="-1/2",
            equality_type="zeta-reg only",
            claim_boundary="regularized invariant, not ordinary equality",
        ),
        RegularizedAssignment(
            series_label="1+2+3+4+...",
            ordinary_status="diverges by ordinary partial-sum convergence",
            regularization_method="zeta analytic continuation",
            regularized_expression="zeta(-1)",
            regularized_value_decimal=mp.nstr(mp.zeta(-1), 50),
            regularized_value_exact="-1/12",
            equality_type="zeta-reg only",
            claim_boundary="regularized invariant, not ordinary equality",
        ),
    ]

    return {
        "experiment": "regularized_density_examples_v0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "draft",
        "claim_boundary": "numerical/analytic illustration, not proof of RH, BSD, or ordinary convergence",
        "ordinary_partial_sums": ordinary_partial_sums,
        "regularized_assignments": [asdict(item) for item in assignments],
        "quality_gates": {
            "ordinary_divergence_shown_separately": True,
            "regularized_values_shown_separately": True,
            "ordinary_equals_regularized_value": False,
            "zeta_reg_marker_required": True,
        },
    }


def parse_sample_sizes(raw: str) -> list[int]:
    """Parse comma-separated positive sample sizes."""
    values = [int(part.strip()) for part in raw.split(",") if part.strip()]
    if not values:
        raise argparse.ArgumentTypeError("at least one sample size is required")
    if any(value < 0 for value in values):
        raise argparse.ArgumentTypeError("sample sizes must be non-negative")
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--samples",
        type=parse_sample_sizes,
        default=[1, 2, 5, 10, 100, 1000],
        help="Comma-separated partial-sum cutoffs.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("receipts/regularized_density_examples_v0.json"),
        help="Receipt JSON path.",
    )
    args = parser.parse_args()

    receipt = build_receipt(args.samples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
