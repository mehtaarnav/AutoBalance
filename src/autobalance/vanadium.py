"""Instantaneous opposing vanadium fluxes, following Wang et al., Fig. 2a.

These are relative transport calculations, not a cycling battery model. The
author script does not identify coefficient units, so no absolute flux is claimed.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RelativeTransport:
    """Coefficient ratios transcribed from the released Fig. 2a MATLAB script."""

    v2: float = 5.26
    v3: float = 1.93
    v4: float = 4.10
    v5: float = 3.54

    def __post_init__(self):
        if not all(np.isfinite(v) and v > 0 for v in (self.v2, self.v3, self.v4, self.v5)):
            raise ValueError("Relative transport coefficients must be positive and finite")


def _soc(value):
    value = np.asarray(value, dtype=float)
    if not np.isfinite(value).all() or np.any((value < 0) | (value > 1)):
        raise ValueError("State of charge must lie between zero and one")
    return value


def balance_ratio(soc_positive, soc_negative=None, transport=None):
    """Positive/negative concentration ratio giving equal opposing fluxes.

    Positive SOC specifies the V(V) fraction; negative SOC the V(II) fraction.
    Equal SOC is the restricted assumption in the paper's main Fig. 2a sweep.
    """
    transport = RelativeTransport() if transport is None else transport
    positive = _soc(soc_positive)
    negative = positive if soc_negative is None else _soc(soc_negative)
    positive_transport = transport.v4 * (1 - positive) + transport.v5 * positive
    negative_transport = transport.v3 * (1 - negative) + transport.v2 * negative
    return negative_transport / positive_transport


def opposing_flux_ratio(concentration_ratio, soc_positive, soc_negative=None, transport=None):
    """Positive-to-negative flux divided by negative-to-positive flux.

    One means instantaneous balance. A shared multiplicative permeability gate
    cancels from this ratio and cannot move its instantaneous zero-drift point.
    """
    concentration_ratio = np.asarray(concentration_ratio, dtype=float)
    if not np.isfinite(concentration_ratio).all() or np.any(concentration_ratio <= 0):
        raise ValueError("Concentration ratio must be positive and finite")
    return concentration_ratio / balance_ratio(soc_positive, soc_negative, transport)
