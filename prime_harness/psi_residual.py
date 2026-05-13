"""Chebyshev ψ box residuals for Prime Harness v0.2."""

from __future__ import annotations

import math

from .sieve_truth import segmented_primes, simple_sieve


def psi_increment(x_start: float, x_end: float) -> float:
    """Return ψ(x_end)-ψ(x_start) for the half-open interval [x_start, x_end).

    ψ(x)=Σ_{p^k<=x} log p. Since boxes are half-open, this includes prime
    powers y with x_start <= y < x_end.
    """

    if x_end < x_start:
        raise ValueError("x_end must be >= x_start")
    if x_end <= 2:
        return 0.0

    start_n = max(2, math.ceil(x_start))
    end_n = max(start_n, math.ceil(x_end))
    total = 0.0

    # k = 1 terms.
    for p in segmented_primes(start_n, end_n):
        if x_start <= p < x_end:
            total += math.log(p)

    # k >= 2 terms.
    max_base = math.isqrt(max(0, end_n - 1)) + 1
    for p in simple_sieve(max_base):
        power = p * p
        while power < x_end:
            if power >= x_start:
                total += math.log(p)
            power *= p

    return total


def psi_box_residual(x_start: float, x_end: float) -> float:
    """Return raw ψ residual: ψ increment minus ordinary length."""

    return psi_increment(x_start, x_end) - (x_end - x_start)
