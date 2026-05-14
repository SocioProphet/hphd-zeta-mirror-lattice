"""Run paired Model 1 ψ and π N-scans for one interval.

This command is the first audited execution wrapper after G0. It produces two
separate report files and a small index file tying them together. It does not
promote results; reports retain `measurement_only_no_novelty_claim` status.
"""

from __future__ import annotations

import argparse

from prime_harness.intervals import PRIMARY_INTERVALS
from prime_harness.model1_psi_scan import DEFAULT_N_VALUES
from prime_harness.pair_scans import run_pair_scans


def _parse_n_values(raw: str) -> tuple[int, ...]:
    values = tuple(int(part.strip()) for part in raw.split(",") if part.strip())
    if not values:
        raise argparse.ArgumentTypeError("at least one N value is required")
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Run paired Model 1 ψ/π scans")
    parser.add_argument("--interval", default="I1", help="Interval name from PRIMARY_INTERVALS")
    parser.add_argument("--delta-u", type=float, default=0.0025)
    parser.add_argument("--primary-zero-table", required=True)
    parser.add_argument("--independent-zero-table", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--n-values",
        type=_parse_n_values,
        default=DEFAULT_N_VALUES,
        help="Comma-separated N values, e.g. 1,2,5,10,25,50,100,200",
    )
    args = parser.parse_args()

    intervals = {interval.name: interval for interval in PRIMARY_INTERVALS}
    if args.interval not in intervals:
        raise SystemExit(f"unknown interval {args.interval!r}; valid: {sorted(intervals)}")

    index = run_pair_scans(
        interval=intervals[args.interval],
        delta_u=args.delta_u,
        primary_zero_table_path=args.primary_zero_table,
        independent_zero_table_path=args.independent_zero_table,
        output_dir=args.output_dir,
        n_values=args.n_values,
    )

    print(f"wrote {index.psi_report}")
    print(f"wrote {index.pi_report}")
    print(f"psi_manifest_hash={index.psi_manifest_hash}")
    print(f"pi_manifest_hash={index.pi_manifest_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
