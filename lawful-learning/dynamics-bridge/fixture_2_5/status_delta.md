# Fixture 2.5 — SU(2) Spin-ℓ Commutator Calibration

Status: **PASS** at machine precision.

Program lane: Lawful Learning / dynamics-bridge fixture ladder.

Repository placement: this lives in `SocioProphet/hphd-zeta-mirror-lattice`, not in `SocioProphet/yang-mills`. The Yang-Mills relation is a cross-program calibration touchpoint only: the same SU(2) spin-ℓ generators appear in Phase 3d Wigner-Eckart work and Lane VII spin-network coefficients.

## Purpose

Fixture 2.5 inserts a calibration between Fixture 2 and Fixture 3. Fixture 1/2 test known-abelian cases. Fixture 3 is intended to test overlapping U(2) blocks with non-commuting holonomy. Before Fixture 3 can be interpreted, the commutator diagnostic must be calibrated against a known non-abelian Lie algebra.

The calibration target is the standard SU(2) spin-j representation for:

```text
j in {0, 1/2, 1, 3/2, 2}
```

For each j, the fixture constructs `J_x`, `J_y`, `J_z` and checks:

```text
[J_x, J_y] = i J_z
[J_y, J_z] = i J_x
[J_z, J_x] = i J_y
```

It also checks Hermiticity and the Casimir relation:

```text
J_x^2 + J_y^2 + J_z^2 = j(j+1) I
```

## Observed transcript

| j | dim | abelian | max commutator norm | max structure residual | Casimir residual |
|---:|---:|---|---:|---:|---:|
| 0 | 1 | yes | 0.000000e+00 | 0.000000e+00 | 0.000000e+00 |
| 1/2 | 2 | no | 7.071068e-01 | 0.000000e+00 | 0.000000e+00 |
| 1 | 3 | no | 1.414214e+00 | 3.254052e-16 | 4.440892e-16 |
| 3/2 | 4 | no | 2.236068e+00 | 4.440892e-16 | 0.000000e+00 |
| 2 | 5 | no | 3.162278e+00 | 7.162069e-16 | 1.256074e-15 |

All four cross-checks pass:

1. spin-0 trivial representation is abelian;
2. spin-j >= 1/2 representations are non-abelian;
3. SU(2) structure constants are recovered to < 1e-13;
4. Casimir and Hermiticity are recovered to machine precision.

## What this confirms

This confirms the commutator diagnostic returns zero on a known abelian target, returns nonzero on known non-abelian targets, and recovers the actual SU(2) Lie-algebra structure constants rather than merely producing arbitrary nonzero values.

## What this does not confirm

This fixture does **not** test:

- the U(2) lift on overlapping gate blocks;
- the χ_p ↔ Floquet realization conjecture;
- Lawful Learning loss surfaces, projection methods, or constraint operators;
- a new Yang-Mills theorem;
- Phase 3d itself;
- continuum Yang-Mills;
- any Riemann Hypothesis, BSD, or Clay-problem claim.

## Bundle artifacts

```text
fixture_2_5_calibration.py
fixture_2_5.json
fixture_2_5_output.txt
status_delta.md
```

Source upload: `fixture2toreview.zip`

Source upload SHA-256:

```text
96433c18fe438e9647b938922b724bc65bcf0b38415b5666002172bf20623378
```
