"""Train once, freeze every policy, and measure performance on unseen disturbances."""

import argparse
import hashlib
import json
import platform
from dataclasses import asdict, replace
from importlib.metadata import version
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from autobalance.benchmark import Scenario, optimize_policy, run_scenario
from autobalance.model import System

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "benchmark"
LABELS = {
    "static": "Best static",
    "timer": "One-switch timer",
    "schedule": "Four-stage schedule",
    "feedback": "Feedback",
}
COLORS = {"static": "#64748b", "timer": "#d97706", "schedule": "#8b5cf6", "feedback": "#0d9488"}


def training_scenarios():
    """Public training set; none of the held-out scenarios enter optimization."""
    return [
        Scenario("initial_positive", 800.0),
        Scenario("initial_negative", -500.0),
        Scenario("late_positive", 100.0, ((2100.0, 650.0),)),
        Scenario("two_reversals", 0.0, ((600.0, 600.0), (3600.0, -700.0))),
    ]


def test_scenarios(seed=20261007, count=32):
    """A fixed synthetic distribution, not a sample of real battery operation."""
    rng = np.random.default_rng(seed)
    cases = []
    for index in range(count):
        initial = float(rng.uniform(-300, 300))
        times = np.sort(rng.uniform(400, 6400, size=2))
        changes = rng.choice([-1, 1], size=2) * rng.uniform(200, 500, size=2)
        events = tuple((float(t), float(x)) for t, x in zip(times, changes))
        cases.append(Scenario(f"unseen_{index:02d}", initial, events))
    return cases


def source_hashes():
    paths = sorted((ROOT / "src").rglob("*.py")) + [Path(__file__)]
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in paths
    }


def mean_training_score(system, scenarios, policy):
    return float(
        np.mean(
            [
                run_scenario(system, scenario, policy, samples=2)["metrics"]["objective"]
                for scenario in scenarios
            ]
        )
    )


def plot_results(table, trajectories, out):
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    pivot = table[table.suite == "held_out"].pivot(
        index="scenario", columns="policy", values="objective"
    )
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout="constrained")
    for kind in ("static", "timer", "schedule"):
        improvement = 100 * (1 - pivot.feedback / pivot[kind])
        axes[0].plot(np.sort(improvement), label=f"vs {LABELS[kind]}", color=COLORS[kind])
    axes[0].axhline(0, color="black", linewidth=1)
    axes[0].set(
        xlabel="Sorted scenario rank (each line sorted separately)",
        ylabel="Feedback objective improvement (%)",
        title="Every held-out result, including losses",
    )
    axes[0].legend()
    for kind in LABELS:
        part = table[(table.suite == "held_out") & (table.policy == kind)]
        axes[1].scatter(
            part.imbalance_exposure,
            part.B_crossed_mol * 1000,
            label=LABELS[kind],
            color=COLORS[kind],
            alpha=0.65,
        )
    axes[1].set(
        xlabel="Normalized imbalance exposure",
        ylabel="B transferred (mmol)",
        title="The trade-off behind the score",
    )
    axes[1].legend()
    fig.savefig(out / "held_out_results.png", dpi=180)
    plt.close(fig)

    # Choose the first seeded case, never the case with the largest win.
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True, layout="constrained")
    for kind, frame in trajectories.items():
        for axis, column in zip(axes, ["imbalance", "P A (m/s)", "B crossed (mol)"]):
            axis.plot(frame["time (s)"] / 60, frame[column], label=LABELS[kind], color=COLORS[kind])
            axis.set_ylabel(column)
    axes[0].legend(ncol=3)
    axes[0].set_title("Unseen scenario 00 · policies frozen before evaluation")
    axes[-1].set_xlabel("Time (min)")
    fig.savefig(out / "surprise_disturbances.png", dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--seeds", type=int, nargs="+", default=[7, 19, 41])
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    system = System()
    train = training_scenarios()
    held_out = test_scenarios()
    policies, diagnostics = {}, {}
    for kind in LABELS:
        candidates = []
        for seed in args.seeds[:1] if kind == "static" else args.seeds:
            print(f"Training {kind}, seed {seed}", flush=True)
            policy, info = optimize_policy(
                system, train, kind, iterations=args.iterations, seed=seed
            )
            score = mean_training_score(system, train, policy)
            candidates.append((score, policy, info))
        winner = min(candidates, key=lambda candidate: candidate[0])
        policies[kind] = winner[1]
        diagnostics[kind] = [
            {"training_objective": c[0], "policy": asdict(c[1]), "search": c[2]} for c in candidates
        ]
        print(f"Frozen {kind}: training objective {winner[0]:.6f}", flush=True)

    rows, demo = [], {}
    suites = [("training", system, train), ("held_out", system, held_out)]
    # Transfer tests change the plant without retuning the frozen designs.
    suites.extend(
        [
            ("smaller_area", replace(system, area=0.007), held_out),
            ("larger_area", replace(system, area=0.013), held_out),
            ("unequal_tanks", replace(system, volume_right=1.5e-4), held_out),
        ]
    )
    for suite, plant, scenarios in suites:
        for scenario in scenarios:
            for kind, policy in policies.items():
                result = run_scenario(plant, scenario, policy)
                rows.append(
                    dict(suite=suite, scenario=scenario.name, policy=kind, **result["metrics"])
                )
                if suite == "held_out" and scenario.name == held_out[0].name:
                    demo[kind] = result["trajectory"]
                    result["trajectory"].to_csv(OUT / f"demo_{kind}.csv", index=False)
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "scores.csv", index=False)
    summary = {}
    for suite, group in table.groupby("suite", sort=False):
        pivot = group.pivot(index="scenario", columns="policy", values="objective")
        comparisons = {}
        for kind in ("static", "timer", "schedule"):
            differences = pivot[kind] - pivot.feedback
            improvement = 100 * (1 - pivot.feedback / pivot[kind])
            comparisons[kind] = dict(
                mean_objective_improvement_percent=float(
                    100 * (1 - pivot.feedback.mean() / pivot[kind].mean())
                ),
                median_paired_improvement_percent=float(improvement.median()),
                worst_paired_improvement_percent=float(improvement.min()),
                wins=int((differences > 1e-8).sum()),
                losses=int((differences < -1e-8).sum()),
                scenarios=len(pivot),
            )
        summary[suite] = dict(
            mean_objectives={k: float(pivot[k].mean()) for k in LABELS}, feedback_vs=comparisons
        )

    # Freeze objective components so alternative weights can be inspected without retuning.
    sensitivity = []
    held = table[table.suite == "held_out"]
    for crossover_weight in (0.5, 1.0, 2.0, 4.0, 8.0):
        for kind, group in held.groupby("policy"):
            value = (
                group.imbalance_exposure
                + crossover_weight * group.B_crossed_fraction
                + group.gate_penalty
            ).mean()
            sensitivity.append(
                dict(crossover_weight=crossover_weight, policy=kind, mean_objective=float(value))
            )
    pd.DataFrame(sensitivity).to_csv(OUT / "weight_sensitivity.csv", index=False)

    manifest = dict(
        protocol_version="1.0",
        system=asdict(system),
        training=[asdict(s) for s in train],
        held_out_seed=20261007,
        held_out=[asdict(s) for s in held_out],
        policies={kind: asdict(policy) for kind, policy in policies.items()},
        optimization=diagnostics,
        iterations=args.iterations,
        optimizer_seeds=args.seeds,
        summary=summary,
        source_sha256=source_hashes(),
        python=platform.python_version(),
        packages={name: version(name) for name in ("numpy", "scipy", "pandas", "matplotlib")},
        caveats=[
            "Synthetic scenarios and hypothetical transport law",
            "One-switch timer and four-stage schedule are restricted open-loop families",
            "Finite searches do not certify global optima",
            "Objective excludes settling penalty used by the original nominal experiment",
            "Weight sensitivity re-scores frozen policies; it does not re-optimize",
        ],
    )
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    plot_results(table, demo, OUT)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
