"""Exact bounded prime oracle for Prime Harness v0.2.

This module is the only M1 component that is allowed to certify prime membership.
Downstream predictors must not call it on evaluation boxes.
"""

from __future__ import annotations

from math import isqrt


def simple_sieve(limit: int) -> list[int]:
    """Return primes <= limit using an ordinary sieve."""

    if limit < 2:
        return []

    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"

    for p in range(2, isqrt(limit) + 1):
        if flags[p]:
            start = p * p
            count = ((limit - start) // p) + 1
            flags[start : limit + 1 : p] = b"\x00" * count

    return [i for i in range(limit + 1) if flags[i]]


def segmented_primes(start: int, end: int) -> list[int]:
    """Return primes in the half-open interval [start, end)."""

    if end <= start:
        return []
    if end <= 2:
        return []

    start = max(start, 2)
    width = end - start
    flags = bytearray(b"\x01") * width

    base_primes = simple_sieve(isqrt(end - 1) + 1)
    for p in base_primes:
        first = max(p * p, ((start + p - 1) // p) * p)
        if first >= end:
            continue
        for multiple in range(first, end, p):
            flags[multiple - start] = 0

    return [start + i for i, is_prime in enumerate(flags) if is_prime]


def prime_count(start: int, end: int) -> int:
    """Return number of primes in [start, end)."""

    return len(segmented_primes(start, end))


def is_prime_by_trial(n: int) -> bool:
    """Small deterministic primality predicate used in tests and assertions."""

    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True
