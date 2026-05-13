# Prime Harness v0.2 — Implementation Tracker

Status: execution tracker for `docs/05-prime-harness-benchmark-spec-v0-2.md`.

## Current tranche

This tranche lands the corrected benchmark protocol only. It does not claim benchmark results and does not implement primality or residual computations yet.

Repository home: `SocioProphet/hphd-zeta-mirror-lattice`.

Boundary: standalone analytic-number-theory research lane. No connection to `superconscious` is warranted. No connection to the BSD proof program is required.

M0 deliverable format: prose SPEC + claim ledger + implementation tracker. Machine-readable gate/schema files are deferred to M1 unless required by CI wiring.

## M0 — SPEC v0.2 patch

- [x] Put SPEC v0.2 in the standalone zeta mirror-lattice repo.
- [x] Bound `classical ceiling` to declared benchmark parameters.
- [x] Correct `Δu/N` compatibility.
- [x] Replace strict G3 monotonicity with saturation-envelope criterion.
- [x] Repair Model 3 leakage by requiring candidate-only orbit-invariant features.
- [x] Declare primary `λτ(n)` map for cross-ratio invariant features.
- [x] Commit Model 2 primary path to analytic/nonleaking character-sector features.
- [x] Replace naive random split for small intervals with deterministic blocked CV / pooling.
- [x] Reorder implementation to ψ-first, then π residual.
- [x] Add G0 zero-table provenance gate.
- [x] Add claim ledger and false-claim boundaries.
- [x] Promote the real `u`-integral form to normative branch convention N1.
- [x] Add τ-scan promotion rule to prevent hidden hyperparameter search.
- [x] Open M0 as protocol-only tranche; no benchmark results claimed.

## M1 — Infrastructure

- [ ] `prime_harness/intervals.py` — interval definitions and fold schedules.
- [ ] `prime_harness/sieve_truth.py` — bounded segmented sieve / exact oracle.
- [ ] `prime_harness/li_quadrature.py` — offset Li computation and box `L_j`.
- [ ] `prime_harness/psi_residual.py` — ψ box residual target.
- [ ] `prime_harness/zeta_zeros.py` — zero-table loader.
- [ ] `prime_harness/zero_table_provenance.py` — G0 validation.
- [ ] `prime_harness/manifest.py` — deterministic run manifest.
- [ ] tests for G0, Li quadrature, sieve sanity, and manifest determinism.

## M2a — ψ explicit-formula benchmark

- [ ] Implement ψ explicit-formula predictor.
- [ ] Run N-scan over `{1,2,5,10,25,50,100,200}`.
- [ ] Report saturation envelope.
- [ ] Debug if sign coherence or zero-indexing fixtures fail.

## M2b — π explicit-formula benchmark

- [ ] Implement real `u`-integral predictor for π residuals.
- [ ] Compare π residual behavior to ψ residual behavior.
- [ ] Freeze Model 1 conventions.

## M3 — Model 1 at scale

- [ ] Run all primary intervals and blocked folds.
- [ ] Establish measured `N*` per interval/resolution.
- [ ] Freeze explicit-formula baseline output.

## M4 — Model 2A

- [ ] Implement analytic character-sector feature path.
- [ ] Confirm no evaluation-box prime leakage.
- [ ] Test G4 against Model 1 saturation envelope.

## M5 — Model 3

- [ ] Implement candidate-only Möbius invariant feature path.
- [ ] Implement `λτ(n)` map and τ sensitivity sweep.
- [ ] Apply τ-scan promotion rule before reporting any selected τ as more than descriptive.
- [ ] Test G4 against Model 1 and Model 2.

## M6 — Audit

- [ ] Bootstrap CIs or underpowered-fold flags.
- [ ] Calibration regressions.
- [ ] Deterministic manifest replay.
- [ ] Frozen `results/benchmark_v0_2.json`.

## Fail-closed rules

Implementation must fail closed if any of the following occurs:

```text
- γ_n table provenance or indexing fails;
- predictor uses evaluation-box certified primes;
- Model 3 computes invariants over primes instead of candidates;
- a scoring model is described as a primality test;
- a result artifact lacks deterministic manifest metadata;
- a novelty claim is made without passing G4;
- complex-Ei branch conventions are used as primary Model 1 evidence;
- τ sensitivity results are promoted without G4 and scan/multiplicity accounting;
- any connection to superconscious is asserted before a separately validated research-evidence promotion path exists.
```
