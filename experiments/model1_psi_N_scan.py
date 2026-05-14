"""CLI for the Prime Harness Model 1 ψ N-scan.

This command requires two independent zero-table files. It is intended for
M2a execution after G0 zero-table provenance is available.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from prime_harness.intervals import PRIMARY_INTERVALS
from prime_harness.model1_psi_scan import DEFAULT_N_VALUES, run_model1_psi_scan, write_psi_scan_report


def _parse_n_values(raw: str) -> tuple[int, ...]:
    values = tuple(int(part.strip()) for part in raw.split(",") if part.strip())
    if not values:
        raise argparse.ArgumentTypeError("at least one N value is required")
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Model 1 ψ explicit-formula N-scan")
    parser.add_argument("--interval", default="I1", help="Interval name from PRIMARY_INTERVALS")
    parser.add_argument("--delta-u", type=float, default=0.0025)
    parser.add_argument("--primary-zero-table", required=True)
    parser.add_argument("--independent-zero-table", required=True)
    parser.add_argument("--output", required=True)
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

    report = run_model1_psi_scan(
        interval=intervals[args.interval],
        delta_u=args.delta_u,
        primary_zero_table_path=args.primary_zero_table,
        independent_zero_table_path=args.independent_zero_table,
        n_values=args.n_values,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    write_psi_scan_report(report, output)
    print(f"wrote {output}")
    print(f"manifest_hash={report.manifest_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
