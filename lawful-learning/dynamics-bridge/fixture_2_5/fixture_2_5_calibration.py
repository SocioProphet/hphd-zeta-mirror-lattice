#!/usr/bin/env python3
"""Fixture 2.5 — SU(2) spin-j commutator calibration.

Validates the commutator diagnostic against standard SU(2) spin-j
representations before Fixture 3 uses the same diagnostic on overlapping U(2)
gate-block holonomy.

Boundary: calibration only. No new Yang-Mills, RH, BSD, continuum, or Clay claim.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports" / "lawful-learning" / "fixture_2_5"
J_VALUES = [0.0, 0.5, 1.0, 1.5, 2.0]
TOL = 1e-13


def spin_J_matrices(j: float):
    dim = int(round(2 * j + 1))
    m_values = np.array([j - i for i in range(dim)], dtype=float)
    J_z = np.diag(m_values).astype(complex)
    J_plus = np.zeros((dim, dim), dtype=complex)
    for k in range(dim - 1):
        m = m_values[k + 1]
        J_plus[k, k + 1] = np.sqrt(j * (j + 1) - m * (m + 1))
    J_minus = J_plus.conj().T
    J_x = (J_plus + J_minus) / 2.0
    J_y = (J_plus - J_minus) / (2.0j)
    return J_x, J_y, J_z


def commutator(A, B):
    return A @ B - B @ A


def calibration_check(j: float) -> dict[str, Any]:
    J_x, J_y, J_z = spin_J_matrices(j)
    dim = int(round(2 * j + 1))
    pairs = [
        ("[J_x, J_y]", commutator(J_x, J_y), 1.0j * J_z),
        ("[J_y, J_z]", commutator(J_y, J_z), 1.0j * J_x),
        ("[J_z, J_x]", commutator(J_z, J_x), 1.0j * J_y),
    ]
    residuals = []
    comm_norms = []
    relations = []
    for label, lhs, rhs in pairs:
        residual = float(np.linalg.norm(lhs - rhs, ord="fro"))
        comm_norm = float(np.linalg.norm(lhs, ord="fro"))
        residuals.append(residual)
        comm_norms.append(comm_norm)
        relations.append({
            "relation": label,
            "commutator_norm": comm_norm,
            "residual_vs_structure_const": residual,
        })
    max_residual = float(max(residuals))
    max_comm_norm = float(max(comm_norms))
    return {
        "j": j,
        "dim": dim,
        "is_abelian": max_comm_norm < TOL,
        "max_residual_vs_structure_constants": max_residual,
        "max_commutator_norm": max_comm_norm,
        "structure_constants_pass": max_residual < TOL,
        "relations": relations,
    }


def phase3d_correspondence_check(j: float) -> dict[str, Any]:
    J_x, J_y, J_z = spin_J_matrices(j)
    dim = int(round(2 * j + 1))
    I = np.eye(dim, dtype=complex)
    herm_residual = max(
        float(np.linalg.norm(J_x - J_x.conj().T, ord="fro")),
        float(np.linalg.norm(J_y - J_y.conj().T, ord="fro")),
        float(np.linalg.norm(J_z - J_z.conj().T, ord="fro")),
    )
    J2 = J_x @ J_x + J_y @ J_y + J_z @ J_z
    casimir_pred = j * (j + 1)
    casimir_residual = float(np.linalg.norm(J2 - casimir_pred * I, ord="fro"))
    return {
        "j": j,
        "dim": dim,
        "hermiticity_residual": herm_residual,
        "casimir_eigenvalue_predicted": casimir_pred,
        "casimir_residual_vs_predicted": casimir_residual,
        "hermiticity_pass": herm_residual < TOL,
        "casimir_pass": casimir_residual < TOL,
    }


def main() -> int:
    results = []
    for j in J_VALUES:
        results.append({
            "spin_j": j,
            "dim_2j_plus_1": int(round(2 * j + 1)),
            "calibration": calibration_check(j),
            "phase_3d_correspondence": phase3d_correspondence_check(j),
        })

    spin0 = results[0]["calibration"]
    higher = [item["calibration"] for item in results[1:]]
    correspondences = [item["phase_3d_correspondence"] for item in results]

    G1_pass = spin0["is_abelian"] and spin0["max_commutator_norm"] < TOL
    G2_pass = all(not item["is_abelian"] and item["max_commutator_norm"] > TOL for item in higher)
    G3_pass = all(item["structure_constants_pass"] for item in [r["calibration"] for r in results])
    G4_pass = all(item["hermiticity_pass"] and item["casimir_pass"] for item in correspondences)
    overall = G1_pass and G2_pass and G3_pass and G4_pass

    output = {
        "fixture": "2.5_phase3d_calibration",
        "description": "SU(2) spin-j commutator calibration of the Fixture-3 diagnostic",
        "claim_boundary": [
            "Calibration only.",
            "Does not test overlapping U(2) gate-block holonomy.",
            "Does not claim a new Yang-Mills theorem.",
            "Does not claim continuum or Clay result.",
        ],
        "predictions": {
            "spin_0_abelian": True,
            "spin_geq_half_nonabelian": True,
            "structure_constants_recovered": True,
            "casimir_recovered": True,
        },
        "cross_checks": {
            "G1_spin0_abelian": bool(G1_pass),
            "G2_higher_spin_nonabelian": bool(G2_pass),
            "G3_structure_constants_machine_precision": bool(G3_pass),
            "G4_casimir_hermiticity_machine_precision": bool(G4_pass),
            "overall": bool(overall),
        },
        "results_per_j": results,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "fixture_2_5.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Fixture 2.5 Result",
        "",
        f"overall: {overall}",
        f"G1_spin0_abelian: {G1_pass}",
        f"G2_higher_spin_nonabelian: {G2_pass}",
        f"G3_structure_constants_machine_precision: {G3_pass}",
        f"G4_casimir_hermiticity_machine_precision: {G4_pass}",
        "",
        "| j | dim | abelian | max_comm_norm | max_structure_residual | casimir_residual |",
        "|---:|---:|---|---:|---:|---:|",
    ]
    for item in results:
        cal = item["calibration"]
        corr = item["phase_3d_correspondence"]
        lines.append(
            f"| {item['spin_j']} | {item['dim_2j_plus_1']} | {cal['is_abelian']} | "
            f"{cal['max_commutator_norm']:.6e} | {cal['max_residual_vs_structure_constants']:.6e} | "
            f"{corr['casimir_residual_vs_predicted']:.6e} |"
        )
    (OUT / "fixture_2_5_result.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("fixture_2_5_calibration: PASS" if overall else "fixture_2_5_calibration: FAIL")
    print(f"j_count={len(J_VALUES)}")
    print(f"max_structure_residual={max(r['calibration']['max_residual_vs_structure_constants'] for r in results):.6e}")
    print(f"max_casimir_residual={max(r['phase_3d_correspondence']['casimir_residual_vs_predicted'] for r in results):.6e}")
    print(f"overall={overall}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
