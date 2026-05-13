"""Interval and logarithmic-box definitions for Prime Harness v0.2."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Interval:
    """Half-open ordinary-scale interval [start, end)."""

    name: str
    start: int
    end: int

    def validate(self) -> None:
        if self.start < 2:
            raise ValueError(f"interval {self.name!r} starts below 2")
        if self.end <= self.start:
            raise ValueError(f"interval {self.name!r} must have end > start")


@dataclass(frozen=True)
class LogBox:
    """A logarithmic box with both log-scale and ordinary-scale endpoints."""

    index: int
    u_start: float
    u_end: float
    x_start: float
    x_end: float

    @property
    def width_u(self) -> float:
        return self.u_end - self.u_start


PRIMARY_INTERVALS: tuple[Interval, ...] = (
    Interval("I1", 10**5, 2 * 10**5),
    Interval("I2", 10**6, 12 * 10**5),
    Interval("I3", 10**7, 102 * 10**5),
    Interval("I4", 10**8, 1005 * 10**5),
)


def make_log_boxes(start: int | float, end: int | float, delta_u: float) -> list[LogBox]:
    """Partition [log(start), log(end)] into boxes of width at most delta_u.

    The ordinary-scale boxes are interpreted as half-open [x_start, x_end).
    The final box is shortened if the interval length is not a multiple of delta_u.
    """

    if start <= 1:
        raise ValueError("log boxes require start > 1")
    if end <= start:
        raise ValueError("end must be greater than start")
    if delta_u <= 0:
        raise ValueError("delta_u must be positive")

    u0 = math.log(start)
    u1 = math.log(end)
    boxes: list[LogBox] = []
    i = 0
    u = u0

    while u < u1 - 1e-15:
        v = min(u + delta_u, u1)
        boxes.append(
            LogBox(
                index=i,
                u_start=u,
                u_end=v,
                x_start=math.exp(u),
                x_end=math.exp(v),
            )
        )
        i += 1
        u = v

    return boxes


def deterministic_blocked_folds(num_boxes: int, k: int = 5) -> list[tuple[list[int], list[int]]]:
    """Return deterministic blocked CV folds.

    Each fold uses a contiguous block as evaluation and all other boxes as training.
    This avoids random tiny held-out sets for small intervals.
    """

    if num_boxes <= 1:
        raise ValueError("at least two boxes required for blocked folds")
    if k <= 1:
        raise ValueError("k must be greater than 1")

    k_eff = min(k, num_boxes)
    folds: list[tuple[list[int], list[int]]] = []
    indices = list(range(num_boxes))

    for fold in range(k_eff):
        start = (fold * num_boxes) // k_eff
        end = ((fold + 1) * num_boxes) // k_eff
        eval_idx = indices[start:end]
        train_idx = indices[:start] + indices[end:]
        if eval_idx and train_idx:
            folds.append((train_idx, eval_idx))

    return folds
