import numpy as np
from scipy.optimize import differential_evolution, minimize_scalar

from .membrane import Membrane
from .metrics import metrics
from .simulation import simulate

P_BOUNDS = (1e-7, 2e-5)


def optimize_static(system):
    def cost(logp):
        return metrics(simulate(system, fixed_p=10**logp), system)["objective"]

    grid = np.linspace(*np.log10(P_BOUNDS), 181)
    values = [cost(p) for p in grid]
    candidates = [(v, p) for v, p in zip(values, grid)]
    for i in range(1, len(grid) - 1):
        if values[i] <= values[i - 1] and values[i] <= values[i + 1]:
            r = minimize_scalar(cost, bounds=(grid[i - 1], grid[i + 1]), method="bounded")
            candidates.append((r.fun, r.x))
    return float(10 ** min(candidates)[1])


def decode(theta):
    lo, fraction, k, threshold, tau = theta
    pmin = 10**lo
    return Membrane(pmin, pmin + fraction * (P_BOUNDS[1] - pmin), k, threshold, tau)


def optimize_responsive(system, iterations=25, seed=7):
    bounds = [tuple(np.log10(P_BOUNDS)), (0, 1), (30, 2000), (0, 0.04), (5, 1000)]

    def cost(theta):
        return metrics(simulate(system, decode(theta)), system)["objective"]

    result = differential_evolution(
        cost, bounds, seed=seed, maxiter=iterations, popsize=7, polish=False, tol=1e-5
    )
    return decode(result.x), dict(
        evaluations=int(result.nfev),
        converged=bool(result.success),
        message=str(result.message),
        seed=seed,
    )
