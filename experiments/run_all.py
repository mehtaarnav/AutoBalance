"""Reproduce the comparison, numerical envelope, and material specification."""

import json
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from autobalance.metrics import metrics
from autobalance.model import System
from autobalance.optimization import optimize_responsive, optimize_static
from autobalance.simulation import simulate
from autobalance.stability import eigenvalues, phase_diagram


def main():
    out = Path(__file__).resolve().parents[1] / "results"
    out.mkdir(exist_ok=True)
    s = System()
    p = optimize_static(s)
    m, diagnostics = optimize_responsive(s)
    cases = {
        "Baseline": simulate(s, fixed_p=s.baseline_p),
        "Best static": simulate(s, fixed_p=p),
        "AutoBalance": simulate(s, m),
    }
    scores = {name: metrics(df, s) for name, df in cases.items()}
    report = dict(
        system=asdict(s),
        membrane=asdict(m),
        static_p=p,
        metrics=scores,
        optimizer=diagnostics,
        improvement_percent=100
        * (1 - scores["AutoBalance"]["objective"] / scores["Best static"]["objective"]),
        eigenvalues=eigenvalues(s, m),
        claims="Hypothetical transport coefficients; no validated material or energetic autonomy.",
    )
    (out / "comparison.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    for name, df in cases.items():
        df.to_csv(out / (name.lower().replace(" ", "_") + ".csv"), index=False)
        for ax, col in zip(
            axes.flat, ["imbalance", "P A (m/s)", "J A (mol/m²/s)", "B crossed (mol)"]
        ):
            ax.plot(df["time (s)"] / 60, df[col], label=name)
            ax.set(xlabel="Time (min)", ylabel=col)
            ax.grid(alpha=0.2)
    axes[0, 0].legend()
    fig.suptitle("AutoBalance | same disturbance, same transport law")
    fig.savefig(out / "comparison.png", dpi=170)
    plt.close(fig)
    phase = phase_diagram(s, m)
    phase.to_csv(out / "phase_diagram.csv", index=False)
    pivot = phase.assign(recovered=(phase.classification == "stable").astype(int)).pivot(
        index="tau", columns="k", values="recovered"
    )
    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    mesh = ax.pcolormesh(
        pivot.columns, pivot.index, pivot.values, vmin=0, vmax=1, cmap="viridis", shading="nearest"
    )
    ax.set(
        xscale="log",
        yscale="log",
        xlabel="Sensitivity k (1/V)",
        ylabel="Response time (s)",
        title="Recovery envelope: all points analytically stable",
    )
    fig.colorbar(mesh, ax=ax, ticks=[0, 1]).ax.set_yticklabels(
        ["Too slow at 2 h", "Within 5% at 2 h"]
    )
    fig.savefig(out / "phase_diagram.png", dpi=170)
    plt.close(fig)
    spec = {
        "P_min_m_s": m.pmin,
        "P_max_m_s": m.pmax,
        "switch_ratio": m.pmax / m.pmin,
        "response_tau_s": m.tau,
        "threshold_V": m.threshold,
        "10_to_90_transition_width_V": 4.394449 / m.k,
        "assumed_A_B_selectivity": 12.5,
        "hysteresis_allowance": "not modeled",
        "cycles_required": "not established",
        "gate_energy_J": "not established; objective uses a rate-squared proxy",
    }
    (out / "material_specification.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
