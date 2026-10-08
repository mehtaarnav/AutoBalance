import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from autobalance.benchmark_view import render_benchmark
from autobalance.membrane import Membrane
from autobalance.metrics import metrics
from autobalance.model import System
from autobalance.optimization import optimize_responsive, optimize_static
from autobalance.simulation import simulate
from autobalance.stability import eigenvalues, phase_diagram

st.set_page_config(
    page_title="AutoBalance | Membrane control lab",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(
    """<style>
    .stApp{background:#0b1220}
    h1{letter-spacing:-1px}
    div[data-testid=stMetric]{background:#152238;padding:12px;border-radius:8px;border:1px solid #23364c}
    div[data-testid=stMetricValue]{font-size:clamp(1.2rem,3vw,2rem)}
    div[data-testid=stMetricLabel] p{white-space:normal}
    </style>""",
    unsafe_allow_html=True,
)
view = st.sidebar.radio("Research lab", ["Frozen benchmark", "Original model lab"])
if view == "Frozen benchmark":
    render_benchmark(Path(__file__).resolve().parents[1])
    st.stop()
st.caption("AUTOBALANCE / COMPUTATIONAL CONTROL LAB / v0.1")
st.title("Let the membrane respond.")
st.write(
    "A two-reservoir experiment in autonomous imbalance recovery. Compare fixed transport with a membrane that responds to an electrochemical error signal."
)
st.info(
    "Research hypothesis: transport and sensing parameters are illustrative. This is not a validated flow battery or a demonstrated autonomous membrane."
)

with st.sidebar:
    st.header("Disturb the system")
    x = st.slider("Initial A imbalance (mol/m³)", -1800, 1800, 800, 100)
    vol = st.slider("Each tank volume (mL)", 50, 500, 100, 10)
    area = st.slider("Membrane area (cm²)", 10, 300, 100, 10)
    st.header("Membrane response")
    pmin = st.number_input("P min (µm/s)", 0.1, 20.0, 0.1, 0.1) * 1e-6
    pmax = (
        st.number_input("P max (µm/s)", float(pmin * 1e6), 20.0, max(20.0, pmin * 1e6), 0.1) * 1e-6
    )
    threshold = st.slider("Threshold (mV)", 0.0, 40.0, 8.0, 0.5) * 0.001
    k = st.slider("Sensitivity (1/V)", 20, 2000, 500, 20)
    tau = st.slider("Response time τ (s)", 5, 3000, 100, 5)
    horizon = st.slider("Experiment duration (h)", 1, 8, 2)
    st.caption(
        "A/B permeability ratio = 12.5 in all cases. B crossover is redistribution, not species destruction."
    )

s = System(
    imbalance=x,
    volume_left=vol * 1e-6,
    volume_right=vol * 1e-6,
    area=area * 1e-4,
    horizon=horizon * 3600,
)
m = Membrane(pmin, pmax, k, threshold, tau)


@st.cache_data(show_spinner=False)
def best_static(system):
    return optimize_static(system)


@st.cache_data(show_spinner=False)
def optimize(system):
    return optimize_responsive(system)


@st.cache_data(show_spinner=False)
def envelope(system, membrane):
    return phase_diagram(system, membrane)


c1, c2, c3 = st.columns(3)
if c1.button("FIXED MEMBRANE", width="stretch"):
    st.session_state["mode"] = "Baseline"
if c2.button("AUTOBALANCE", width="stretch"):
    st.session_state["mode"] = "AutoBalance"
if c3.button("OPTIMIZE", type="primary", width="stretch"):
    with st.spinner("Optimizing both designs under the same objective…"):
        optimum, diagnostics = optimize(s)
        st.session_state["optimum"] = (asdict(s), optimum, diagnostics)
        st.session_state["mode"] = "AutoBalance"

saved = st.session_state.get("optimum")
if saved and saved[0] == asdict(s):
    use_opt = st.checkbox("Use optimized membrane (overrides membrane sliders)", value=True)
    if use_opt:
        m = saved[1]
        st.caption(
            f"Seed {saved[2]['seed']} · {saved[2]['evaluations']} evaluations · {saved[2]['message']}"
        )
with st.spinner("Finding the best constant permeability…"):
    p = best_static(s)
cases = {
    "Baseline": simulate(s, fixed_p=s.baseline_p),
    "Best static": simulate(s, fixed_p=p),
    "AutoBalance": simulate(s, m),
}
scores = {name: metrics(df, s) for name, df in cases.items()}
improvement = 100 * (1 - scores["AutoBalance"]["objective"] / scores["Best static"]["objective"])
cols = st.columns(4)
cols[0].metric("Responsive objective", f"{scores['AutoBalance']['objective']:.4f}")
cols[1].metric("Best static objective", f"{scores['Best static']['objective']:.4f}")
cols[2].metric("Objective improvement", f"{improvement:+.1f}%")
cols[3].metric("Mass balance error", f"{scores['AutoBalance']['conservation_relative']:.1e}")
st.caption(
    "Lower objective is better. A negative improvement is a loss. Best static searches the full 0.1–20 µm/s range, including endpoints."
)
tabs = st.tabs(
    ["Recovery experiment", "Design envelope", "Material feasibility", "Model & exports"]
)
with tabs[0]:
    st.subheader("Disturbance → response → transport → recovery")
    combined = pd.concat([df.assign(Design=name) for name, df in cases.items()], ignore_index=True)
    for col in ["imbalance", "P A (m/s)", "J A (mol/m²/s)", "B crossed (mol)"]:
        st.plotly_chart(
            px.line(
                combined,
                x="time (s)",
                y=col,
                color="Design",
                template="plotly_dark",
                color_discrete_sequence=["#75869e", "#e5aa57", "#45d6c0"],
            ),
            width="stretch",
        )
    selected = st.selectbox(
        "Inspect reservoir and membrane states",
        list(cases),
        index=list(cases).index(st.session_state.get("mode", "AutoBalance")),
    )
    st.plotly_chart(
        px.line(
            cases[selected],
            x="time (s)",
            y=["A left", "A right", "B left", "B right"],
            template="plotly_dark",
        ),
        width="stretch",
    )
    st.plotly_chart(
        px.line(cases[selected], x="time (s)", y="w", template="plotly_dark"), width="stretch"
    )
    st.dataframe(pd.DataFrame(scores).T, width="stretch")
with tabs[1]:
    st.write(
        "Positive permeability makes |x| monotonically decrease. Every valid point is stable; color distinguishes recovery within 5% by the experiment deadline from slow recovery. Oscillatory and unstable regions do not exist in this model."
    )
    st.latex(
        r"\dot{x}=-A(1/V_L+1/V_R)P(w)x,\quad \lambda_1=-A(1/V_L+1/V_R)P(w_*),\quad\lambda_2=-1/\tau"
    )
    st.write("One-sided equilibrium eigenvalues (1/s):", eigenvalues(s, m))
    if st.button("Calculate recovery map"):
        with st.spinner("Sweeping sensitivity and response time…"):
            phase = envelope(s, m)
        st.plotly_chart(
            px.scatter(
                phase,
                x="k",
                y="tau",
                color="classification",
                log_x=True,
                log_y=True,
                template="plotly_dark",
                hover_data=["settling_s", "objective"],
            ),
            width="stretch",
        )
        st.download_button("Download map data", phase.to_csv(index=False), "phase_diagram.csv")
with tabs[2]:
    st.subheader("A quantitative target, with evidence boundaries")
    st.json(
        dict(
            switching_ratio=m.pmax / m.pmin,
            response_tau_s=m.tau,
            threshold_mV=1000 * m.threshold,
            transition_10_to_90_mV=4394.449 / m.k,
            assumed_selectivity=12.5,
        )
    )
    st.warning(
        "FEASIBILITY: UNVERIFIED. Available literature does not jointly establish switching ratio, response time, battery compatibility, and autonomous actuation for this target."
    )
    lit = pd.read_csv(Path(__file__).resolve().parents[1] / "data/responsive_membranes.csv")
    st.dataframe(lit, width="stretch")
    st.write(
        "[Song et al., ACS Nano (2026)](https://pubmed.ncbi.nlm.nih.gov/41925149/) reports K⁺/Li⁺ selectivity of 481.2 under voltage control. This is a different ion system and is not a permeability switching ratio. Missing values are deliberately left blank."
    )
with tabs[3]:
    st.write(
        "SI units: concentration mol/m³; volume m³; area m²; effective permeance P in m/s; flux mol/(m² s). Temperature 298.15 K, z=1. Ideal log-ratio potential is a sensing proxy, not full battery voltage."
    )
    st.latex(
        r"J=\frac{1}{T}\int(x/x_0)^2dt+2\frac{n_{B,\mathrm{cross}}}{n_{B,0}}+0.15\frac{t_{5\%}}{T}+0.01\int\dot w^2dt"
    )
    st.write(
        "Unsettled runs use a settling penalty of 1 and report no settling time. The last term is a phenomenological gate-rate penalty, not energy in joules. No chemical consumption, electrical cycling, solvent flow, or gate energy budget is modeled."
    )
    st.write(
        "With P_B = 0.08 P_A, final B crossover depends only on integrated permeability. The controller can shift transport earlier; it does not improve intrinsic selectivity. All comparisons share initial concentrations, duration, and constitutive law."
    )
    payload = dict(system=asdict(s), membrane=asdict(m), best_static_p=p, metrics=scores)
    st.download_button("Download comparison JSON", json.dumps(payload, indent=2), "comparison.json")
    st.download_button(
        "Download all trajectories", combined.to_csv(index=False), "trajectories.csv"
    )
