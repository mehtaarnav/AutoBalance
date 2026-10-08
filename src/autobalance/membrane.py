import math
from dataclasses import dataclass

from scipy.special import expit


@dataclass(frozen=True)
class Membrane:
    """Illustrative gate law; these coefficients are not fitted material data."""

    pmin: float = 1e-7
    pmax: float = 2e-5
    k: float = 500.0
    threshold: float = 0.008
    tau: float = 100.0

    def __post_init__(self):
        if not all(
            math.isfinite(value)
            for value in (self.pmin, self.pmax, self.k, self.threshold, self.tau)
        ):
            raise ValueError("Membrane parameters must be finite")
        if not (
            0 < self.pmin <= self.pmax and self.k >= 0 and self.threshold >= 0 and self.tau > 0
        ):
            raise ValueError("Invalid membrane bounds")

    def target(self, potential):
        # Magnitude makes the controller symmetric to disturbance direction.
        return expit(self.k * (abs(potential) - self.threshold))

    def permeability(self, w):
        return self.pmin + (self.pmax - self.pmin) * w


def undesirable_permeability(pa):
    """Hypothetical SAME constitutive law for static and responsive membranes."""
    return 0.08 * pa
