"""A shareable figure whose claims come directly from the frozen benchmark."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def main():
    output = Path(__file__).resolve().parents[1] / "results" / "benchmark"
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    names = {
        "static": "Static",
        "timer": "One-switch timer",
        "schedule": "Four-stage schedule",
        "feedback": "Feedback",
    }
    colors = ["#94a3b8", "#fbbf24", "#a78bfa", "#2dd4bf"]
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "text.color": "#e2e8f0",
            "axes.labelcolor": "#e2e8f0",
            "xtick.color": "#94a3b8",
            "ytick.color": "#94a3b8",
            "axes.edgecolor": "#334155",
            "font.size": 11,
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(13.33, 7.5), gridspec_kw={"width_ratios": [1, 1.3]})
    fig.patch.set_facecolor("#0b1220")
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.25, top=0.73, wspace=0.45)
    fig.text(0.08, 0.91, "Does feedback earn its complexity?", fontsize=25, weight="bold")
    fig.text(
        0.08,
        0.85,
        "AutoBalance  /  train once, freeze, then test surprises",
        fontsize=14,
        color="#94a3b8",
    )
    for axis in axes:
        axis.set_facecolor("#0b1220")
        axis.spines[["top", "right"]].set_visible(False)
    mean = manifest["summary"]["held_out"]["mean_objectives"]
    axes[0].barh(list(names.values()), [mean[name] for name in names], color=colors, height=0.55)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Mean test objective · lower is better")
    axes[0].set_xlim(0, max(mean.values()) * 1.25)
    for index, name in enumerate(names):
        axes[0].text(mean[name] + 0.005, index, f"{mean[name]:.3f}", va="center")
    for (name, label), color in zip(names.items(), colors, strict=True):
        frame = pd.read_csv(output / f"demo_{name}.csv")
        axes[1].plot(frame["time (s)"] / 60, frame.imbalance, label=label, color=color, linewidth=2)
    for time, _ in manifest["held_out"][0]["disturbances"]:
        axes[1].axvline(time / 60, color="#64748b", linestyle=":")
    axes[1].set(
        xlabel="Time (min)",
        ylabel="A imbalance (mol/m³)",
        title="First seeded test case · not a selected best case",
    )
    improvement = manifest["summary"]["held_out"]["feedback_vs"]["schedule"][
        "mean_objective_improvement_percent"
    ]
    fig.text(
        0.08,
        0.14,
        f"{improvement:.1f}% lower mean objective vs four-stage schedule",
        fontsize=17,
        color="#2dd4bf",
        weight="bold",
    )
    fig.text(
        0.08,
        0.085,
        "32 synthetic test cases · 3 optimizer seeds per active design · finite search, no global guarantee",
        fontsize=10,
    )
    fig.text(
        0.08,
        0.045,
        "Hypothetical transport and ideal sensing. Not measured battery performance.   github.com/mehtaarnav/AutoBalance",
        fontsize=10,
        color="#94a3b8",
    )
    fig.savefig(output / "launch.png", dpi=150, facecolor=fig.get_facecolor())
    fig.savefig(output / "launch.svg", facecolor=fig.get_facecolor())
    svg = output / "launch.svg"
    svg.write_text(
        "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)


if __name__ == "__main__":
    main()
