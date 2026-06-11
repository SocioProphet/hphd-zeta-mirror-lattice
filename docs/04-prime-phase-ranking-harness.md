# Prime Phase Ranking Harness v0.1

Status: Draft v0.1  
Lane: HPHD / zeta mirror-lattice / reproducible analytic-number-theory experiments  
Purpose: Convert the current next-prime phase-gate draft into a falsifiable, pre-registered ranking benchmark with hard claim boundaries.

## 1. Scope

This harness evaluates a deterministic ranking policy over a finite next-prime corridor. It does not define a primality test, certificate, theorem, or proof of any zeta-level hypothesis.

Given a starting prime `p`, the next prime `q` is known to lie in the finite doubling corridor:

```math
p < q < 2p.
```

The harness constructs a survivor set inside that corridor, ranks the survivors using one or more pre-registered policies, and then measures where the true next prime appears in each ranked list.

The only admissible research claim for v0.1 is comparative:

```text
A fixed ranking policy is useful only if it places the true next prime earlier than declared baselines under identical filters and independent audit.
```

## 2. Claim boundary

### 2.1 Allowed claim types

The harness may produce:

- definitions;
- computational experiments;
- receipts;
- benchmark reports;
- conjectures explicitly labeled as conjectures;
- falsification records;
- baseline comparisons.

### 2.2 Disallowed claim promotion

The harness must not assert that the phase score establishes primality, compositeness, RH, BSD, or any theorem-level result.

The Riemann-hypothesis-adjacent role is limited to motivation for a log-harmonic lens and an envelope-normalization discussion. It does not justify any specific gate.

The phase constants are treated as pre-registered experimental constants, not as derived canonical constants.

## 3. Layer separation invariant

The architecture has three layers.

### 3.1 Sieve layer

The sieve layer may remove an integer `n` from the corridor only when one of the following is true:

- `n` is outside the corridor;
- `gcd(n, M) != 1` for a pre-registered wheel modulus `M`;
- `n` is certified composite by a declared deterministic filter.

Formal invariant:

```text
n not in S(p) => n is outside scope, wheel-inadmissible, or certified composite.
```

### 3.2 Ranking layer

The ranking layer assigns scores to survivors. A score may order candidates, but it never certifies primality or compositeness.

Formal invariant:

```text
G(n) is only an ordering score.
G(n) never removes n from S(p).
G(n) never proves n prime.
G(n) never proves n composite.
```

### 3.3 Audit layer

The audit layer determines primality independently of the ranking score.

Acceptable audit methods for v0.1:

- deterministic trial division for small fixtures;
- deterministic Miller-Rabin for declared integer ranges;
- proof-producing methods such as ECPP or APR-CL in later large-scale lanes.

The audit method must be written into the receipt before promotion of any benchmark result.

## 4. Pre-registration discipline

Every benchmark run must freeze the following before results are inspected:

- benchmark ID;
- source code revision;
- input prime list or generation rule;
- magnitude bands;
- wheel policy;
- modulus `M` or the rule that determines `M`;
- survivor filters;
- ranking policies;
- ranking direction;
- audit method;
- random seeds for stochastic baselines;
- success metrics;
- output receipt path.

A run is invalid if any of these are changed after observing outcomes without creating a new benchmark ID.

## 5. Wheel policy

`M` is a first-class experimental parameter and must not be silently tuned.

Allowed v0.1 wheel policies:

```text
fixed_30:  M = 2 * 3 * 5
fixed_210: M = 2 * 3 * 5 * 7
primorial_B: M = product of primes ell <= B, with B frozen before the run
```

Disallowed v0.1 wheel policy:

```text
changing M after seeing a benchmark failure
choosing M per window unless the rule is frozen before the run
using an undeclared adaptive modulus
```

## 6. Symbol discipline

Use distinct symbols for distinct roles.

- `d` is a square-shell offset in identities such as `(n-d)(n+d) = n^2 - d^2`.
- `c_M(n)` is the wheel-channel index of `n` modulo `M`.
- `k` is not used as both an offset and a channel index.

Wheel residues are:

```math
R_M = \{r \in \{0,1,\ldots,M-1\}: \gcd(r,M)=1\}.
```

With residues ordered by a declared traversal, the channel index is:

```math
c_M(n)=\operatorname{index}(n \bmod M \text{ in } R_M).
```

The numeric-order traversal is the v0.1 default. CRT traversal and multiplicative-order traversal are later ablations.

## 7. Candidate gate family

The initial candidate gate is a fixed experimental scoring functional:

```math
G(n)=\cos\left(n\alpha_M\left(\pi+\frac{1}{60}\right)+e^\pi+2c_M(n)\left(\frac{90}{\pi}\right)\right),
```

where:

```math
\alpha_M=\frac{2\pi}{\varphi(M)}.
```

This formula is not canonical in v0.1. It is a pre-registered object under test.

The comma-separated transcription that appeared in earlier notes is not the implementation formula. The implementation formula uses ordinary addition and multiplication inside a one-argument cosine.

## 8. Required baselines

The gate must be evaluated against all mandatory baselines under the same survivor set `S(p)`.

Mandatory v0.1 baselines:

1. ascending order by integer value;
2. random order with fixed seed ledger;
3. wheel-channel order;
4. distance-from-`p` order;
5. local-density prior score using the declared approximation around `1 / log(x)`;
6. gate order.

Optional ablations:

- log-space gate variant;
- CRT channel traversal;
- multiplicative-order traversal where available;
- threshold score as an ablation only, not as a core acceptance rule.

## 9. Metrics

For every window, record:

```text
p
q
M
wheel_policy_id
survivor_count
rank_gate
rank_ascending
rank_random_mean
rank_wheel
rank_distance
rho_gate
rho_ascending
rho_random_mean
rho_wheel
rho_distance
delta_rank_vs_ascending
delta_rho_vs_ascending
audit_method
receipt_hash
```

The primary success metric is comparative improvement against ascending order after identical filters.

A gate that beats random order but fails to beat ascending order is not a successful next-prime search policy.

## 10. Falsifier

For a prime window, define:

```math
\rho_G(p)=\frac{m_G(p)}{|S(p)|},
```

where `m_G(p)` is the rank of the true next prime under the gate ordering.

The v0.1 falsifier is:

```text
If gate rank does not improve over ascending rank across stratified magnitude bands, the gate has not shown useful next-prime search value.
```

This falsifier is intentionally stronger than random-order comparison.

## 11. Benchmark tiers

```text
smoke_30:        30 stratified windows; detects obvious failure only
initial_1000:    1,000 windows; estimates preliminary effect size
scale_100k:      100,000+ windows; tests stability across bands
publication:     millions of windows; requires adversarial review and frozen receipts
```

No publication-grade language is allowed before the scale tiers are complete.

## 12. Receipt requirements

Every run emits a JSON receipt conforming to `schemas/prime_phase_harness.schema.json`.

Minimum receipt properties:

- run metadata;
- pre-registration block;
- code revision;
- input policy;
- frozen wheel policy;
- frozen formula ID;
- audit method;
- baseline list;
- per-window metrics;
- aggregate metrics;
- claim boundary statement.

## 13. Promotion rules

A result may be promoted from exploratory to candidate signal only when:

1. the benchmark was pre-registered;
2. all mandatory baselines are present;
3. ascending order is beaten on the primary metric;
4. performance is stable across magnitude bands;
5. receipts are committed;
6. the claim remains typed as computational evidence, not proof.

## 14. First implementation sequence

1. Add this specification, schema, and claim-boundary tests.
2. Add a minimal harness with small deterministic fixtures.
3. Add mandatory baselines and metric emission.
4. Run `smoke_30` and commit receipts.
5. Run `initial_1000` only after smoke results are reproducible.

## 15. Current status

```text
Specification:          v0.1 draft
Executable harness:     not yet implemented
Benchmark receipts:     not yet emitted
Claim status:           computational experiment only
Theorem status:          none
```
