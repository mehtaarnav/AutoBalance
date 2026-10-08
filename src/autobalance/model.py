import math
from dataclasses import dataclass

from .electrochemistry import error_potential
from .membrane import undesirable_permeability


@dataclass(frozen=True)
class System:
    """Well-mixed reservoir geometry and initial state, expressed in SI units."""

    volume_left: float = 1e-4
    volume_right: float = 1e-4
    area: float = 0.01
    mean_a: float = 1000.0
    imbalance: float = 800.0
    horizon: float = 7200.0
    baseline_p: float = 2e-6

    def __post_init__(self):
        values = (
            self.volume_left,
            self.volume_right,
            self.area,
            self.mean_a,
            self.imbalance,
            self.horizon,
            self.baseline_p,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("System parameters must be finite")
        if (
            min(
                self.volume_left,
                self.volume_right,
                self.area,
                self.mean_a,
                self.horizon,
                self.baseline_p,
            )
            <= 0
        ):
            raise ValueError("Physical dimensions must be positive")
        if abs(self.imbalance) >= 2 * self.mean_a:
            raise ValueError("Initial concentrations must be positive")


def rhs(t, y, system, membrane, fixed_p=None):
    """Opposite reservoir fluxes conserve inventory for each species."""
    al, ar, bl, br, w, _, _ = y
    pa = fixed_p if fixed_p is not None else membrane.permeability(w)
    ja = pa * (al - ar)
    jb = undesirable_permeability(pa) * (bl - br)
    dw = (
        0.0
        if fixed_p is not None
        else (membrane.target(error_potential(al, ar)) - w) / membrane.tau
    )
    a = system.area
    return [
        -a * ja / system.volume_left,
        a * ja / system.volume_right,
        -a * jb / system.volume_left,
        a * jb / system.volume_right,
        dw,
        a * abs(jb),
        dw * dw,
    ]
