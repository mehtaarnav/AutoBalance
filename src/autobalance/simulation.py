import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

from .electrochemistry import error_potential
from .membrane import Membrane, undesirable_permeability
from .model import System, rhs


def simulate(system=None, membrane=None, fixed_p=None, samples=501, rtol=1e-7):
    """Original single-disturbance experiment; benchmark.py handles repeated forcing."""
    system = System() if system is None else system
    membrane = Membrane() if membrane is None else membrane
    if not isinstance(samples, int) or samples < 2:
        raise ValueError("At least two output samples are required")
    if not np.isfinite(rtol) or rtol <= 0:
        raise ValueError("Solver tolerance must be positive and finite")
    if fixed_p is not None and (not np.isfinite(fixed_p) or fixed_p <= 0):
        raise ValueError("Fixed permeability must be positive")
    y0 = [
        system.mean_a + system.imbalance / 2,
        system.mean_a - system.imbalance / 2,
        1000.0,
        100.0,
        float(membrane.target(0.0)),
        0.0,
        0.0,
    ]
    sol = solve_ivp(
        rhs,
        (0, system.horizon),
        y0,
        args=(system, membrane, fixed_p),
        t_eval=np.linspace(0, system.horizon, samples),
        method="LSODA",
        rtol=rtol,
        atol=1e-9,
    )
    if not sol.success:
        raise RuntimeError(sol.message)
    df = pd.DataFrame(
        sol.y.T,
        columns=["A left", "A right", "B left", "B right", "w", "B crossed (mol)", "gate proxy"],
    )
    df.insert(0, "time (s)", sol.t)
    df["imbalance"] = df["A left"] - df["A right"]
    df["P A (m/s)"] = fixed_p if fixed_p is not None else membrane.permeability(df.w)
    df["P B (m/s)"] = undesirable_permeability(df["P A (m/s)"])
    df["J A (mol/m²/s)"] = df["P A (m/s)"] * df.imbalance
    df["J B (mol/m²/s)"] = df["P B (m/s)"] * (df["B left"] - df["B right"])
    df["error (V)"] = error_potential(df["A left"], df["A right"])
    return df
