"""CLI for G0 zero-table provenance validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from prime_harness.zero_table_provenance import validate_zero_table


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate two independent zeta-zero tables")
    parser.add_argument("--primary-zero-table", required=True)
    parser.add_argument("--independent-zero-table", required=True)
    parser.add_argument("--n-check", type=int, default=200)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    report = validate_zero_table(
        table_path=args.primary_zero_table,
        independent_source_path=args.independent_zero_table,
        n_check=args.n_check,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"validated zero tables; wrote {output}")
    print(f"primary_sha256={report.primary_sha256}")
    print(f"independent_sha256={report.independent_sha256}")
    print(f"max_cross_source_delta={report.max_cross_source_delta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
