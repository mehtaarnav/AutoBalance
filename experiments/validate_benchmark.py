"""Independently re-evaluate frozen policies and demonstrate nominal open-loop replay."""

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid

from autobalance.benchmark import Policy, Scenario, run_scenario
from autobalance.model import System


def main():
    output = Path(__file__).resolve().parents[1] / "results" / "benchmark"
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    system = System(**manifest["system"])
    policies = {name: Policy(**values) for name, values in manifest["policies"].items()}
    recorded = pd.read_csv(output / "scores.csv")
    differences = []
    for record in manifest["held_out"]:
        scenario = Scenario(
            record["name"], record["initial_imbalance"], tuple(map(tuple, record["disturbances"]))
        )
        for name, policy in policies.items():
            result = run_scenario(system, scenario, policy, samples=1001, rtol=1e-10)
            original = recorded[
                (recorded.suite == "held_out")
                & (recorded.scenario == scenario.name)
                & (recorded.policy == name)
            ].iloc[0]
            differences.append(abs(result["metrics"]["objective"] - original.objective))
    maximum_difference = float(max(differences))
    assert maximum_difference < 1e-6, maximum_difference

    # Replay uses only the saved permeability trace, not a sensed concentration.
    nominal = Scenario("nominal_replay", 800.0)
    trace = run_scenario(system, nominal, policies["feedback"], samples=10001, rtol=1e-10)[
        "trajectory"
    ]
    coefficient = system.area * (1 / system.volume_left + 1 / system.volume_right)
    exposure = cumulative_trapezoid(trace["P A (m/s)"], trace["time (s)"], initial=0)
    replay = 800 * np.exp(-coefficient * exposure)
    replay_error = float(np.max(abs(replay - trace.imbalance)) / 800)
    assert replay_error < 1e-5, replay_error
    pd.DataFrame(
        {
            "time_s": trace["time (s)"],
            "feedback_imbalance": trace.imbalance,
            "open_loop_replay_imbalance": replay,
        }
    ).to_csv(output / "nominal_replay.csv", index=False)

    controls = [
        Scenario("quiet", 0.0),
        Scenario("nominal_positive", 800.0),
        Scenario("nominal_negative", -800.0),
    ]
    rows = [
        {"scenario": case.name, "policy": name, **run_scenario(system, case, policy)["metrics"]}
        for case in controls
        for name, policy in policies.items()
    ]
    pd.DataFrame(rows).to_csv(output / "negative_controls.csv", index=False)
    validation = {
        "held_out_reevaluations": len(differences),
        "tight_solver_rtol": 1e-10,
        "max_objective_absolute_difference": maximum_difference,
        "nominal_replay_max_error_relative_to_initial_imbalance": replay_error,
        "replay_method": "Numerically integrate saved permeance and evaluate exact passive decay; no feedback signal",
        "negative_controls": [asdict(case) for case in controls],
    }
    (output / "validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
