"""Presentation of frozen benchmark artifacts, separate from the transport solver."""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from .benchmark import Policy, Scenario, run_scenario
from .model import System

LABELS = {
    "static": "Best static",
    "timer": "One-switch timer",
    "schedule": "Four-stage schedule",
    "feedback": "Feedback",
}
COLORS = {
    "static": "#94a3b8",
    "timer": "#fbbf24",
    "schedule": "#a78bfa",
    "feedback": "#2dd4bf",
}


def render_benchmark(root: Path) -> None:
    st.caption("AUTOBALANCE / OPEN RESEARCH / FROZEN-POLICY BENCHMARK")
    st.title("Does feedback earn its complexity?")
    st.write(
        "Train four designs on the same disturbances. Freeze their parameters. "
        "Then introduce events they were never tuned on."
    )
    artifact = root / "results" / "benchmark" / "manifest.json"
    if not artifact.exists():
        st.info(
            "The reproducible benchmark is being generated. The original model lab is available in the sidebar."
        )
        return
    manifest = json.loads(artifact.read_text(encoding="utf-8"))
    scores = pd.read_csv(artifact.parent / "scores.csv")
    system = System(**manifest["system"])
    policies = {name: Policy(**parameters) for name, parameters in manifest["policies"].items()}
    summary = manifest["summary"]["held_out"]
    columns = st.columns(3)
    for column, competitor in zip(columns, ("static", "timer", "schedule"), strict=True):
        comparison = summary["feedback_vs"][competitor]
        column.metric(
            f"Feedback vs {LABELS[competitor].lower()}",
            f"{comparison['mean_objective_improvement_percent']:+.1f}%",
        )
        column.caption(
            f"Lower mean objective · {comparison['wins']}/{comparison['scenarios']} individual wins"
        )
    st.caption(
        "Percentage change in mean test objective, not battery efficiency. Negative values mean feedback loses. "
        "Synthetic transport model; no material or energetic-autonomy validation."
    )

    tabs = st.tabs(["Surprise experiment", "Every result", "Limits & proof", "Reproduce"])
    with tabs[0]:
        selected = st.selectbox("Unseen scenario", [case["name"] for case in manifest["held_out"]])
        record = next(case for case in manifest["held_out"] if case["name"] == selected)
        scenario = Scenario(
            record["name"], record["initial_imbalance"], tuple(map(tuple, record["disturbances"]))
        )
        custom = st.checkbox(
            "Try your own disturbance (exploration, outside the recorded benchmark)"
        )
        if custom:
            left, right = st.columns(2)
            onset = left.slider("Surprise arrives (min)", 5, 110, 55)
            magnitude = right.slider("Redistributed imbalance (mol/m³)", -1000, 1000, 600, 50)
            scenario = Scenario("interactive", 0.0, ((float(onset * 60), float(magnitude)),))
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06)
        component_rows = []
        for name, policy in policies.items():
            result = run_scenario(system, scenario, policy)
            frame = result["trajectory"]
            for row, (variable, scale) in enumerate(
                (("imbalance", 1), ("P A (m/s)", 1e6), ("B crossed (mol)", 1000)), start=1
            ):
                fig.add_trace(
                    go.Scatter(
                        x=frame["time (s)"] / 60,
                        y=frame[variable] * scale,
                        name=LABELS[name],
                        legendgroup=name,
                        showlegend=row == 1,
                        line={"color": COLORS[name], "width": 2.5},
                    ),
                    row=row,
                    col=1,
                )
            component_rows.append({"Design": LABELS[name], **result["metrics"]})
        for time, _ in scenario.disturbances:
            fig.add_vline(x=time / 60, line_dash="dot", line_color="#64748b")
        fig.update_yaxes(title_text="A imbalance (mol/m³)", row=1, col=1)
        fig.update_yaxes(title_text="Permeance (µm/s)", row=2, col=1)
        fig.update_yaxes(title_text="B transferred (mmol)", row=3, col=1)
        fig.update_xaxes(title_text="Time (min)", row=3, col=1)
        fig.update_layout(
            height=760,
            template="plotly_dark",
            legend={"orientation": "h", "y": 1.07},
            margin={"t": 50},
        )
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "Dotted lines mark mass-conserving redistributions of A. The policies are frozen; changing the disturbance does not retrain them."
        )
        st.dataframe(pd.DataFrame(component_rows).set_index("Design"), width="stretch")
    with tabs[1]:
        suite = st.selectbox("Evaluation conditions", list(manifest["summary"]))
        part = scores[scores.suite == suite]
        pivot = part.pivot(index="scenario", columns="policy", values="objective")
        paired = pd.DataFrame(
            {
                LABELS[name]: 100 * (1 - pivot.feedback / pivot[name])
                for name in ("static", "timer", "schedule")
            }
        )
        figure = px.bar(
            paired.reset_index().melt(
                id_vars="scenario", var_name="Comparator", value_name="Improvement (%)"
            ),
            x="scenario",
            y="Improvement (%)",
            color="Comparator",
            barmode="group",
            template="plotly_dark",
        )
        figure.add_hline(y=0, line_color="white")
        st.plotly_chart(figure, width="stretch")
        st.dataframe(part, width="stretch")
        st.write(
            "Transfer tests alter membrane area or reservoir volume without retuning. The finite suite is not a confidence bound for real battery operation."
        )
        weights = pd.read_csv(artifact.parent / "weight_sensitivity.csv")
        weights["Design"] = weights.policy.map(LABELS)
        st.plotly_chart(
            px.line(
                weights,
                x="crossover_weight",
                y="mean_objective",
                color="Design",
                markers=True,
                template="plotly_dark",
            ),
            width="stretch",
        )
        st.caption(
            "Sensitivity re-scores the same frozen policies. It does not optimize a fresh controller for each weight."
        )
    with tabs[2]:
        st.subheader("Control can change timing. It cannot create selectivity.")
        st.latex(r"\frac{x_B(t)}{x_B(0)} = \left[\frac{x_A(t)}{x_A(0)}\right]^{0.08}")
        st.write(
            "Between disturbances, all policies obey this identity. At equal final A recovery they cause equal B transfer. Any reduction at different endpoints is a timing trade-off, not improved intrinsic selectivity."
        )
        st.latex(r"\dot{x}=-A(1/V_L+1/V_R)P(t)x")
        st.write(
            "Positive permeance makes undisturbed imbalance decay monotonically. This model cannot produce an unstable or oscillatory recovery region."
        )
        st.write(
            "The schedule sees the clock; feedback sees an ideal concentration-cell voltage proxy. Sensing noise, chemical reactions, real gate energy, and full battery cycling are not modeled. Four-stage schedules do not represent every possible open-loop controller."
        )
        st.link_button(
            "Read the scientific case and prior art",
            "https://github.com/mehtaarnav/AutoBalance/blob/main/docs/scientific_case.md",
        )
    with tabs[3]:
        st.write(
            "Training uses four declared scenarios. Optimizer seeds are chosen before evaluation; the winner is selected only by training score. The 32 test scenarios come from seed 20261007."
        )
        st.latex(
            r"J=\frac{1}{T}\int (x/800)^2\,dt + 2\frac{n_{B,\mathrm{cross}}}{n_{B,0}} + 0.01\int\dot{w}^2\,dt"
        )
        st.write(
            "The objective is integrated with the differential equations and does not depend on plot sampling. The gate-rate penalty is a stated proxy, not energy in joules. The nominal model lab uses a different objective with settling time; its scores cannot be mixed with this benchmark."
        )
        st.code(
            'python -m pip install -e ".[test]"\npython -m pytest -q\npython experiments/benchmark.py\npython -m streamlit run app/dashboard.py',
            language="shell",
        )
        st.download_button(
            "Download reproducibility manifest",
            artifact.read_bytes(),
            "manifest.json",
            "application/json",
        )
        st.download_button(
            "Download every score",
            (artifact.parent / "scores.csv").read_bytes(),
            "scores.csv",
            "text/csv",
        )
        with st.expander("Frozen parameters and optimizer status"):
            st.json({"policies": manifest["policies"], "optimization": manifest["optimization"]})
        st.link_button("Source code", "https://github.com/mehtaarnav/AutoBalance")
