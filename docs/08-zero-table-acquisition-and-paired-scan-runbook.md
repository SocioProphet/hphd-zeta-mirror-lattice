# Zero-Table Acquisition and Paired Scan Runbook

Status: M2 execution support for Prime Harness v0.2.

This runbook describes how to execute the first real paired Model 1 scans once two independent zero-table files are available. It does not ship zero tables and does not claim benchmark results.

## Boundary

The benchmark requires two independent zero-table sources before Model 1 can run. The G0 gate fails closed if only one source is supplied, if the files are identical paths, if the first `N_check` values disagree beyond tolerance, if the ordinates are not strictly increasing, or if hardcoded fixture checks fail.

No ψ or π scan result should be treated as a benchmark artifact unless the paired zero-table validation report is preserved with the scan output.

## Expected zero-table format

Each file may be either one-column or two-column text:

```text
14.134725141734693790457251983562470270784257115699
21.022039638771554992628479593896902777334340524903
...
```

or:

```text
1 14.134725141734693790457251983562470270784257115699
2 21.022039638771554992628479593896902777334340524903
...
```

Blank lines and `#` comments are ignored.

## Required files

```text
data/zeros/odlyzko_first_zeros.txt
 data/zeros/lmfdb_first_zeros.txt
```

The path names are examples. The files must be independently sourced.

## Step 1 — G0 validation

```bash
python experiments/validate_zero_table.py \
  --primary-zero-table data/zeros/odlyzko_first_zeros.txt \
  --independent-zero-table data/zeros/lmfdb_first_zeros.txt \
  --n-check 200 \
  --output results/prime_harness_v0_2/g0_zero_table_provenance.json
```

Expected result: the command exits 0 and records hashes, precision convention, fixture indices, and maximum cross-source delta.

## Step 2 — paired I1 ψ/π scan

Primary-A resolution:

```bash
python experiments/run_model1_pair_scans.py \
  --interval I1 \
  --delta-u 0.0025 \
  --primary-zero-table data/zeros/odlyzko_first_zeros.txt \
  --independent-zero-table data/zeros/lmfdb_first_zeros.txt \
  --n-values 1,2,5,10,25,50,100,200 \
  --output-dir results/prime_harness_v0_2/i1_primary_a
```

This writes:

```text
model1_psi_scan_I1.json
model1_pi_scan_I1.json
model1_pair_scan_I1_index.json
```

Each report is explicitly marked:

```text
measurement_only_no_novelty_claim
```

## Step 3 — review gates

Before treating the outputs as benchmark measurements, verify:

```text
- G0 provenance report exists and hashes both zero sources.
- ψ and π reports have the same zero-table provenance hash pair.
- ψ and π reports have deterministic manifest hashes.
- Saturation envelope is present for each scan.
- No novelty claim appears in the reports.
- No Model 2 or Model 3 feature is evaluated yet.
```

## Step 4 — archived result path

Only after audit, copy reviewed outputs into a frozen results path:

```text
results/prime_harness_v0_2/frozen/model1_i1_pair_scan/
```

Future result PRs must include the G0 provenance report and both ψ/π scan JSON files. Raw zero-table data should not be committed unless licensing and provenance are clear.

## Non-claims

This runbook does not claim:

```text
- a completed M2 benchmark;
- a result for VarExpl(1,N);
- a feature-family promotion;
- a primality test;
- any replacement for established primality algorithms.
```
