"""Metrics for Prime Harness v0.2."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class VarExplResult:
    sse: float
    sst: float
    var_expl: float


def variance_explained(observed: list[float], predicted: list[float]) -> VarExplResult:
    """Return 1-SSE/SST against the held-out mean baseline."""

    if len(observed) != len(predicted):
        raise ValueError("observed and predicted lengths differ")
    if not observed:
        raise ValueError("at least one observation required")

    mean_obs = sum(observed) / len(observed)
    sse = sum((o - p) ** 2 for o, p in zip(observed, predicted, strict=True))
    sst = sum((o - mean_obs) ** 2 for o in observed)
    if sst == 0:
        var = 0.0 if sse == 0 else float("-inf")
    else:
        var = 1.0 - sse / sst
    return VarExplResult(sse=sse, sst=sst, var_expl=var)


def saturation_envelope(values: list[tuple[int, float]]) -> list[tuple[int, float]]:
    """Return monotone envelope over (N, VarExpl) points."""

    best = -math.inf
    out: list[tuple[int, float]] = []
    for n, value in values:
        best = max(best, value)
        out.append((n, best))
    return out


def standardized_residual(raw: float, expected: float) -> float:
    """Return R/sqrt(max(L,1))."""

    return raw / math.sqrt(max(expected, 1.0))
