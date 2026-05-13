"""Offset logarithmic integral and normative real-u quadrature."""

from __future__ import annotations

import math
from typing import Callable

import mpmath as mp

mp.mp.dps = 50


def offset_li(x: float | int) -> float:
    """Return offset Li(x) = ∫_2^x dt/log(t).

    Implemented as li(x)-li(2) for stability away from the singularity at 1.
    """

    if x < 2:
        raise ValueError("offset Li is defined here only for x >= 2")
    return float(mp.li(x) - mp.li(2))


def li_box_expected(x_start: float | int, x_end: float | int) -> float:
    """Expected prime count in [x_start, x_end) under Li density."""

    if x_end < x_start:
        raise ValueError("x_end must be >= x_start")
    if x_start < 2:
        raise ValueError("Li boxes require x_start >= 2")
    return offset_li(x_end) - offset_li(x_start)


def integrate_real_u(
    func: Callable[[mp.mpf], mp.mpf],
    a: float,
    b: float,
    *,
    error_target: float = 1e-8,
) -> float:
    """Integrate a real-valued function over [a,b] in u-space.

    The primary implementation uses mpmath's adaptive quadrature. The explicit
    formula code calls this for the normative real-u branch convention.
    """

    if b < a:
        raise ValueError("integration end must be >= start")
    if a == b:
        return 0.0

    value = mp.quad(func, [mp.mpf(a), mp.mpf(b)])
    result = float(value)
    if not math.isfinite(result):
        raise ArithmeticError("non-finite quadrature result")
    # error_target is recorded by callers/manifests; mpmath does not expose
    # the adaptive error estimate in this interface.
    _ = error_target
    return result


def pi_zero_integral(gamma: float, a: float, b: float) -> float:
    """Normative real-u integral I_n(a,b) for π residual Model 1."""

    arg_rho = math.atan2(gamma, 0.5)

    def integrand(u: mp.mpf) -> mp.mpf:
        return mp.e ** (u / 2) / u * mp.cos(gamma * u - arg_rho)

    return integrate_real_u(integrand, a, b)


def zero_resolution_ok(delta_u: float, gamma_n: float, factor: float = 1.0) -> bool:
    """Return true iff Δu · γ_N <= factor."""

    return delta_u * gamma_n <= factor
