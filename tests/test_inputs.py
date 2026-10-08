"""Invalid physical inputs must fail before a solver produces misleading output."""

import numpy as np
import pytest

from autobalance.electrochemistry import error_potential
from autobalance.membrane import Membrane
from autobalance.model import System
from autobalance.simulation import simulate


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_nonfinite_physics_rejected(value):
    with pytest.raises(ValueError):
        System(area=value)
    with pytest.raises(ValueError):
        Membrane(tau=value)
    with pytest.raises(ValueError):
        error_potential(value, 1.0)


@pytest.mark.parametrize("samples", [0, 1, -1, 2.5])
def test_insufficient_output_rejected(samples):
    with pytest.raises(ValueError):
        simulate(samples=samples)
