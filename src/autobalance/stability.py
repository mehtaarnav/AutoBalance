from dataclasses import replace

import numpy as np
import pandas as pd

from .metrics import metrics
from .simulation import simulate


def eigenvalues(system, membrane):
    # At x=0 the derivative of P(w)*x with respect to w vanishes.
    # |E| has a cusp; both one-sided Jacobians have these same eigenvalues.
    pstar = membrane.permeability(membrane.target(0.0))
    return [
        -system.area * (1 / system.volume_left + 1 / system.volume_right) * pstar,
        -1 / membrane.tau,
    ]


def phase_diagram(system, membrane, size=16):
    rows = []
    for tau in np.geomspace(5, 3000, size):
        for k in np.geomspace(20, 2000, size):
            m = replace(membrane, k=float(k), tau=float(tau))
            df = simulate(system, m)
            result = metrics(df, system)
            rows.append(
                dict(
                    k=k,
                    tau=tau,
                    classification="stable" if result["settled"] else "too slow",
                    **result,
                )
            )
    return pd.DataFrame(rows)
