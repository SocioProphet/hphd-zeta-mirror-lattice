"""Explicit-formula predictors for Prime Harness v0.2.

Primary π residual computation uses the normative real-u integral form.
"""

from __future__ import annotations

import cmath
import math
from decimal import Decimal

from .li_quadrature import pi_zero_integral


def rho_abs(gamma: float) -> float:
    """Return |1/2 + i gamma|."""

    return math.hypot(0.5, gamma)


def psi_zero_integral_closed(gamma: float, a: float, b: float) -> complex:
    """Return ∫_a^b exp((1/2+iγ)u) du exactly in floating arithmetic."""

    rho = complex(0.5, gamma)
    return (cmath.exp(rho * b) - cmath.exp(rho * a)) / rho


def psi_model1_prediction(gammas: list[float] | tuple[float, ...], a: float, b: float, n: int) -> float:
    """Predict ψ residual over [a,b] using first n positive zeta zeros."""

    if n < 0:
        raise ValueError("n must be non-negative")
    if len(gammas) < n:
        raise ValueError(f"need {n} zeros, got {len(gammas)}")
    total = 0.0
    for gamma in gammas[:n]:
        total += psi_zero_integral_closed(gamma, a, b).real
    return -2.0 * total


def pi_model1_prediction(gammas: list[float] | tuple[float, ...], a: float, b: float, n: int) -> float:
    """Predict π residual over [a,b] using the normative real-u integral form."""

    if n < 0:
        raise ValueError("n must be non-negative")
    if len(gammas) < n:
        raise ValueError(f"need {n} zeros, got {len(gammas)}")
    total = 0.0
    for gamma in gammas[:n]:
        total += (2.0 / rho_abs(gamma)) * pi_zero_integral(gamma, a, b)
    return -total


def decimal_gammas_as_float(values: tuple[Decimal, ...], n: int) -> list[float]:
    """Convert the first n Decimal ordinates to floats for model computation."""

    if len(values) < n:
        raise ValueError(f"need {n} zeros, got {len(values)}")
    return [float(v) for v in values[:n]]
