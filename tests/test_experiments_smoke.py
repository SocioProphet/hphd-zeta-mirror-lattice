from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def test_regularized_density_examples_emits_receipt(tmp_path: Path) -> None:
    out = tmp_path / "receipts"
    receipt = out / "rd.json"

    proc = run(
        [
            sys.executable,
            "experiments/regularized_density_examples.py",
            "--output",
            str(receipt),
        ]
    )

    assert receipt.exists(), proc.stderr
    data = json.loads(receipt.read_text(encoding="utf-8"))

    assert data["experiment"] == "regularized_density_examples_v0"
    assert "ordinary_partial_sums" in data
    assert "regularized_assignments" in data

    # Ensure we do NOT assert ordinary equality between divergent sums and regularized values.
    assert data["quality_gates"]["ordinary_equals_regularized_value"] is False


def test_explicit_formula_decomposition_emits_receipt(tmp_path: Path) -> None:
    out = tmp_path / "receipts"
    receipt = out / "ef.json"

    proc = run(
        [
            sys.executable,
            "experiments/explicit_formula_decomposition.py",
            "--xmin",
            "10",
            "--xmax",
            "100",
            "--steps",
            "7",
            "--out",
            str(out),
            "--receipt",
            receipt.name,
        ]
    )

    assert receipt.exists(), proc.stderr
    data = json.loads(receipt.read_text(encoding="utf-8"))

    assert data["experiment"] == "explicit_formula_decomposition_v0"
    assert data["parameters"]["nontrivial_zero_count"] == 0

    rows = data["term_breakdown"]
    assert len(rows) == 7
    # Ensure required term classes are present and non-empty strings.
    for row in rows:
        assert "completion_constant" in row
        assert "trivial_lattice_term" in row
        assert isinstance(row["completion_constant"], str) and row["completion_constant"]
        assert isinstance(row["trivial_lattice_term"], str) and row["trivial_lattice_term"]
