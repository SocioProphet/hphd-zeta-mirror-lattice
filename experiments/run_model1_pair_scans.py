"""Run paired Model 1 ψ and π N-scans for one interval.

This command is the first audited execution wrapper after G0. It produces two
separate report files and a small index file tying them together. It does not
promote results; reports retain `measurement_only_no_novelty_claim` status.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from prime_harness.intervals import PRIMARY_INTERVALS
from prime_harness.model1_pi_scan import run_model1_pi_scan, write_pi_scan_report
from prime_harness.model1_psi_scan import DEFAULT_N_VALUES, run_model1_psi_scan, write_psi_scan_report


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

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    interval = intervals[args.interval]
    psi_report = run_model1_psi_scan(
        interval=interval,
        delta_u=args.delta_u,
        primary_zero_table_path=args.primary_zero_table,
        independent_zero_table_path=args.independent_zero_table,
        n_values=args.n_values,
    )
    pi_report = run_model1_pi_scan(
        interval=interval,
        delta_u=args.delta_u,
        primary_zero_table_path=args.primary_zero_table,
        independent_zero_table_path=args.independent_zero_table,
        n_values=args.n_values,
    )

    psi_path = output_dir / f"model1_psi_scan_{args.interval}.json"
    pi_path = output_dir / f"model1_pi_scan_{args.interval}.json"
    index_path = output_dir / f"model1_pair_scan_{args.interval}_index.json"
    write_psi_scan_report(psi_report, psi_path)
    write_pi_scan_report(pi_report, pi_path)

    index = {
        "schema_version": "prime-harness-v0.2-m2-pair-scan-index",
        "interval": args.interval,
        "delta_u": args.delta_u,
        "n_values": list(args.n_values),
        "psi_report": str(psi_path),
        "pi_report": str(pi_path),
        "psi_manifest_hash": psi_report.manifest_hash,
        "pi_manifest_hash": pi_report.manifest_hash,
        "result_status": "measurement_only_no_novelty_claim",
    }
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"wrote {psi_path}")
    print(f"wrote {pi_path}")
    print(f"wrote {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
