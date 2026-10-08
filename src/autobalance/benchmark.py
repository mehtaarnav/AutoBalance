"""Frozen-policy experiments: fit on training disturbances, then evaluate unseen ones.

The plant is a transport toy model. The timer baseline separates the benefit of
front-loading transport from the benefit of responding to new information.
"""

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.optimize import differential_evolution, minimize_scalar
from scipy.special import expit

from .electrochemistry import error_potential
from .model import System

P_MIN = 1e-7
P_MAX = 2e-5
GATE_TAU = 100.0
REFERENCE_IMBALANCE = 800.0


@dataclass(frozen=True)
class Scenario:
    name: str
    initial_imbalance: float = 800.0
    disturbances: tuple[tuple[float, float], ...] = ()

    def __post_init__(self):
        if not self.name or not np.isfinite(self.initial_imbalance):
            raise ValueError("A scenario needs a name and finite initial imbalance")
        times = [event[0] for event in self.disturbances]
        if any(not np.isfinite(event).all() for event in self.disturbances):
            raise ValueError("Disturbances must be finite (time, imbalance change) pairs")
        if any(time <= 0 for time in times) or any(b <= a for a, b in zip(times, times[1:])):
            raise ValueError("Disturbance times must be positive and strictly increasing")


@dataclass(frozen=True)
class Policy:
    kind: Literal["static", "timer", "feedback", "schedule"]
    low: float = P_MIN
    high: float = P_MAX
    k: float = 500.0
    threshold: float = 0.008
    switch_time: float = 1200.0
    static_p: float = 2e-6
    schedule_targets: tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)

    def __post_init__(self):
        if self.kind not in ("static", "timer", "feedback", "schedule"):
            raise ValueError("Unknown policy kind")
        values = (self.low, self.high, self.k, self.threshold, self.switch_time, self.static_p)
        if not np.isfinite(values).all():
            raise ValueError("Policy parameters must be finite")
        if not P_MIN <= self.low <= self.high <= P_MAX or not P_MIN <= self.static_p <= P_MAX:
            raise ValueError("Every policy shares the same permeability bounds")
        if self.k < 0 or self.threshold < 0 or self.switch_time < 0:
            raise ValueError("Policy response parameters must be nonnegative")
        if (
            len(self.schedule_targets) != 4
            or not np.isfinite(self.schedule_targets).all()
            or any(target < 0 or target > 1 for target in self.schedule_targets)
        ):
            raise ValueError("Schedule needs four finite gate targets in [0, 1]")
        if self.kind == "schedule" and (self.low != P_MIN or self.high != P_MAX):
            raise ValueError("Schedule uses the common global permeability range")


def run_scenario(
    system: System, scenario: Scenario, policy: Policy, samples: int = 501, rtol: float = 1e-8
):
    """Return a trajectory and objective computed by adaptive ODE integration.

    Repeated timestamps mark instantaneous, mass-conserving A redistributions.
    Output sample spacing affects plots only, never the optimized objective.
    Every dynamic gate starts at the global minimum permeance. Passive static
    material starts at its chosen permeance and has no actuator-motion cost.
    """
    dimensions = (
        system.volume_left,
        system.volume_right,
        system.area,
        system.mean_a,
        system.horizon,
    )
    if not np.isfinite(dimensions).all() or min(dimensions) <= 0:
        raise ValueError("System dimensions must be positive and finite")
    if not isinstance(samples, int) or samples < 2:
        raise ValueError("At least two output samples are required")
    if not np.isfinite(rtol) or not 0 < rtol < 1:
        raise ValueError("Relative solver tolerance must be finite and between zero and one")
    if any(time >= system.horizon for time, _ in scenario.disturbances):
        raise ValueError("Disturbances must occur before the experiment ends")
    left, right = system.volume_left, system.volume_right
    total_volume = left + right
    x0 = scenario.initial_imbalance
    # These offsets change the concentration difference while preserving inventory.
    y = np.array(
        [
            system.mean_a + right / total_volume * x0,
            system.mean_a - left / total_volume * x0,
            1000.0,
            100.0,
            0.0,
            0.0,
            0.0,
            0.0,
        ]
    )
    if min(y[:4]) <= 0:
        raise ValueError("Initial concentrations must be positive")
    initial_mass = np.array([left * y[0] + right * y[1], left * y[2] + right * y[3]])
    events = dict(scenario.disturbances)
    boundaries = {0.0, system.horizon, *events}
    if policy.kind == "timer" and 0 < policy.switch_time < system.horizon:
        boundaries.add(policy.switch_time)
    if policy.kind == "schedule":
        boundaries.update(system.horizon * index / 4 for index in (1, 2, 3))
    boundaries = sorted(boundaries)
    grid = np.linspace(0, system.horizon, samples)
    times, states = [0.0], [y.copy()]

    for start, end in zip(boundaries, boundaries[1:]):
        # Freeze timer mode per segment so the solver never integrates across its jump.
        timer_target = float(start < policy.switch_time)
        scheduled_target = policy.schedule_targets[min(int(4 * start / system.horizon), 3)]

        def rhs(time, state, timer_target=timer_target, scheduled_target=scheduled_target):
            al, ar, bl, br, gate = state[:5]
            if policy.kind == "static":
                permeability, velocity = policy.static_p, 0.0
            else:
                if policy.kind == "timer":
                    requested = policy.low + (policy.high - policy.low) * timer_target
                    target = (requested - P_MIN) / (P_MAX - P_MIN)
                elif policy.kind == "schedule":
                    target = scheduled_target
                else:
                    opening = expit(policy.k * (abs(error_potential(al, ar)) - policy.threshold))
                    requested = policy.low + (policy.high - policy.low) * opening
                    target = (requested - P_MIN) / (P_MAX - P_MIN)
                # A single physical coordinate makes startup and motion cost comparable.
                velocity = (target - gate) / GATE_TAU
                permeability = P_MIN + (P_MAX - P_MIN) * gate
            transport_a = system.area * permeability * (al - ar)
            transport_b = system.area * 0.08 * permeability * (bl - br)
            return [
                -transport_a / left,
                transport_a / right,
                -transport_b / left,
                transport_b / right,
                velocity,
                abs(transport_b),
                ((al - ar) / REFERENCE_IMBALANCE) ** 2,
                velocity**2,
            ]

        output_times = np.unique(np.r_[grid[(grid > start) & (grid < end)], end])
        solution = solve_ivp(
            rhs,
            (start, end),
            y,
            t_eval=output_times,
            method="LSODA",
            rtol=rtol,
            atol=min(1e-10, rtol * 0.01),
        )
        if not solution.success:
            raise RuntimeError(solution.message)
        times.extend(solution.t)
        states.extend(solution.y.T)
        y = solution.y[:, -1].copy()
        if end in events:
            y[0] += right / total_volume * events[end]
            y[1] -= left / total_volume * events[end]
            if min(y[:2]) <= 0:
                raise ValueError(f"Disturbance at {end:g} s would create nonpositive concentration")
            times.append(end)
            states.append(y.copy())

    frame = pd.DataFrame(
        states,
        columns=[
            "A left",
            "A right",
            "B left",
            "B right",
            "w",
            "B crossed (mol)",
            "exposure integral",
            "gate proxy",
        ],
    )
    frame.insert(0, "time (s)", times)
    frame["imbalance"] = frame["A left"] - frame["A right"]
    frame["P A (m/s)"] = (
        policy.static_p if policy.kind == "static" else P_MIN + (P_MAX - P_MIN) * frame.w
    )
    frame["P B (m/s)"] = 0.08 * frame["P A (m/s)"]
    frame["J A (mol/m²/s)"] = frame["P A (m/s)"] * frame.imbalance
    frame["J B (mol/m²/s)"] = frame["P B (m/s)"] * (frame["B left"] - frame["B right"])
    frame["error (V)"] = error_potential(frame["A left"], frame["A right"])
    masses = np.column_stack(
        [
            left * frame[f"{species} left"] + right * frame[f"{species} right"]
            for species in ("A", "B")
        ]
    )
    exposure = float(y[6] / system.horizon)
    crossover = float(y[5] / initial_mass[1])
    gate_penalty = float(0.01 * y[7])
    scores = dict(
        objective=exposure + 2 * crossover + gate_penalty,
        imbalance_exposure=exposure,
        B_crossed_mol=float(y[5]),
        B_crossed_fraction=crossover,
        gate_penalty=gate_penalty,
        conservation_relative=float(np.max(abs(masses - initial_mass) / initial_mass)),
        final_imbalance=float(y[0] - y[1]),
    )
    return {"trajectory": frame, "metrics": scores}


def optimize_policy(system: System, scenarios, kind: str, iterations: int = 12, seed: int = 7):
    """Minimize training mean; callers must keep evaluation scenarios out of this call."""
    scenarios = tuple(scenarios)
    if not scenarios:
        raise ValueError("Training scenarios cannot be empty")
    if kind not in ("static", "timer", "feedback", "schedule"):
        raise ValueError("Unknown policy kind")
    if not isinstance(iterations, int) or iterations < 1:
        raise ValueError("Optimization requires at least one generation")
    evaluations = 0

    def evaluate(policy):
        nonlocal evaluations
        evaluations += 1
        return float(
            np.mean(
                [
                    run_scenario(system, scenario, policy, samples=2)["metrics"]["objective"]
                    for scenario in scenarios
                ]
            )
        )

    if kind == "static":

        def cost(log_p):
            return evaluate(Policy("static", static_p=float(np.clip(10**log_p, P_MIN, P_MAX))))

        grid = np.linspace(np.log10(P_MIN), np.log10(P_MAX), 81)
        values = [cost(log_p) for log_p in grid]
        candidates = list(zip(values, grid))
        for index in range(1, len(grid) - 1):
            if values[index] <= min(values[index - 1], values[index + 1]):
                result = minimize_scalar(
                    cost, bounds=(grid[index - 1], grid[index + 1]), method="bounded"
                )
                candidates.append((result.fun, result.x))
        score, log_p = min(candidates)
        policy = Policy("static", static_p=float(np.clip(10**log_p, P_MIN, P_MAX)))
        diagnostics = dict(
            converged=True, message="Bounded refinement of sampled minima; no global certificate"
        )
    else:

        def decode(theta):
            if kind == "schedule":
                permeabilities = np.clip(10 ** np.asarray(theta), P_MIN, P_MAX)
                targets = tuple(
                    float(value) for value in (permeabilities - P_MIN) / (P_MAX - P_MIN)
                )
                return Policy(kind, schedule_targets=targets)
            low = float(np.clip(10 ** theta[0], P_MIN, P_MAX))
            high = float(np.clip(low + theta[1] * (P_MAX - low), low, P_MAX))
            if kind == "timer":
                return Policy(kind, low=low, high=high, switch_time=float(theta[2]))
            return Policy(kind, low=low, high=high, k=float(theta[2]), threshold=float(theta[3]))

        bounds = [(np.log10(P_MIN), np.log10(P_MAX)), (0, 1)]
        bounds += [(0, system.horizon)] if kind == "timer" else [(30, 2000), (0, 0.04)]
        if kind == "schedule":
            bounds = [(np.log10(P_MIN), np.log10(P_MAX))] * 4
        result = differential_evolution(
            lambda theta: evaluate(decode(theta)),
            bounds,
            seed=seed,
            maxiter=iterations,
            popsize=7,
            polish=False,
            tol=1e-5,
        )
        policy, score = decode(result.x), float(result.fun)
        diagnostics = dict(converged=bool(result.success), message=str(result.message))
        # Explicit constant boundaries prevent finite searches from missing zero-range designs.
        # Constant requests above P_MIN still ramp from the common physical initial state.
        for permeability in (P_MIN, P_MAX):
            if kind == "schedule":
                target = (permeability - P_MIN) / (P_MAX - P_MIN)
                candidate = Policy(kind, schedule_targets=(target,) * 4)
            else:
                candidate = Policy(
                    kind, low=permeability, high=permeability, switch_time=0.0, k=0.0, threshold=0.0
                )
            candidate_score = evaluate(candidate)
            if candidate_score < score:
                policy, score = candidate, candidate_score
                diagnostics["selected_boundary_constant"] = True
    diagnostics.update(
        evaluations=evaluations,
        seed=seed,
        training_objective=float(score),
        training_scenarios=[scenario.name for scenario in scenarios],
    )
    return policy, diagnostics
