# AutoBalance

**A reproducible control-architecture experiment for state-responsive membranes.**

AutoBalance compares a fixed baseline, an optimized constant membrane, and an optimized responsive membrane after the same concentration disturbance. It models two conserved species in two well-mixed reservoirs. It does not claim a new battery, a validated material, or experimentally demonstrated autonomous actuation.

## Recorded default experiment

The seeded search found a responsive objective of **0.2746**, versus **0.4583** for the numerical best static design: **40.1% lower**. Recovery to 5% took approximately **30 minutes versus 78 minutes**. B transfer over two hours was **0.01089 versus 0.01388 mol**, about 21.5% lower. These endpoints have different final A imbalances; this is not a claim of better intrinsic selectivity at matched final imbalance.

The responsive search exhausted its 25-generation budget, so this is the best candidate found, not a certified optimum. Re-evaluation with 10,001 output points and relative tolerance 1e-10 retained a 40.10% improvement. Conservation residuals were below 2e-15. The underlying parameters and optimizer status are preserved in `results/comparison.json`.

## Run

Python 3.10 or newer; no GPU required.

```powershell
python -m pip install -e ".[test]"
python -m pytest -q
python experiments/run_all.py
python -m streamlit run app/dashboard.py
```

The dashboard exposes imbalance, tank size, area, permeance bounds, sensitivity, threshold, and membrane response time. FIXED MEMBRANE and AUTOBALANCE select the detailed state view while preserving the comparison. OPTIMIZE runs a seeded search and displays its convergence status. Simulation and optimization run locally.

Generated results include `comparison.json`, all three trajectories, `comparison.png`, `phase_diagram.csv`, `phase_diagram.png`, and `material_specification.json`. Reproduce these with `experiments/run_all.py`. The optimizer is a finite numerical search, not a global-optimality certificate.

## Model and assumptions

For species i, J_i = P_i(c_i,L − c_i,R), with V_L dc_i,L/dt = −A J_i and V_R dc_i,R/dt = +A J_i. Concentrations use mol/m³, time seconds, volumes m³, area m², and P m/s. P is an effective permeance (diffusivity divided by membrane thickness), not a diffusivity.

The ideal concentration-cell proxy is ΔE = RT/F ln(c_A,L/c_A,R), at 298.15 K. This is not a full redox battery OCV relation. The controller uses |ΔE| so either sign of disturbance opens the membrane. Its target state is sigmoid[k(|ΔE|−E₀)], with τ dw/dt = w_eq−w and P_A = P_min+w(P_max−P_min). The gate starts at its undisturbed equilibrium state. The initial concentration offset represents a disturbance at t=0.

Species B initially has concentrations 1000 and 100 mol/m³. Its crossover is undesirable by assumption, but B is conserved; “loss” means transfer out of its original reservoir, not chemical destruction. Both designs use **P_B = 0.08 P_A**. This selectivity is hypothetical, identical across designs, and independent of gate state. No hidden selectivity bonus is granted to AutoBalance.

Default tanks are each 100 mL, membrane area 100 cm², A concentrations 1400/600 mol/m³, duration two hours. The baseline has P=2 µm/s. All optimized designs obey 0.1 ≤ P_A ≤ 20 µm/s. Responsive search also bounds k to 30–2000 V⁻¹, threshold to 0–40 mV, and τ to 5–1000 s. The dashboard map extends response times to 3000 s.

## Fair objective and optimization

The dimensionless objective is normalized integrated squared imbalance + 2×fraction of initial B inventory transferred + 0.15×normalized settling time + 0.01×integrated squared gate velocity. The last coefficient implicitly carries the units needed for normalization. It is a phenomenological penalty, **not a physical gate-energy calculation**. Static gates incur zero gate-motion penalty. Weights are explicit and encode a chosen engineering preference; superiority is not universal.

Settling means remaining within 5% of the initial imbalance through the horizon. Unsettled runs have null settling time and receive a normalized settling penalty of 1. Settling is resolved on 501 output times; objective comparisons should not imply precision below that time spacing. Exactly zero initial imbalance uses a small absolute tolerance.

Static optimization evaluates 181 logarithmically spaced points, retains endpoints, and refines every sampled local minimum. Responsive optimization uses SciPy differential evolution, seed 7, population multiplier 7, and 25 generations. Five parameters are optimized, with a transformed parameter enforcing ordered permeability bounds. Budget exhaustion is reported, not disguised as convergence.

The decisive comparison is against **Best static**, not the baseline. Negative improvement must be reported as a loss. Repeat searches with other seeds, tighten solver/output resolution, and vary objective weights before making broader claims.

## What the stability map can actually say

For positive P, ẋ = −A(1/V_L+1/V_R)P(w)x. Consequently x keeps its sign and |x| decreases monotonically. Since P_min>0, imbalance converges exponentially. Membrane delay cannot produce concentration oscillations or instability in this passive model. Inventing those regions would be incorrect.

At equilibrium, the one-sided Jacobians (the absolute-value signal has a cusp) are triangular, with eigenvalues −A(1/V_L+1/V_R)P(w*) and −1/τ. Both are negative throughout the valid domain. There is **no analytical stability boundary to overlay**. The plotted boundary is finite-time performance: stable and within tolerance, versus stable but too slow. Reactions, driven currents, or active pumping would require a richer model before instability claims were possible.

There is also a transport-budget identity: with P_B=0.08 P_A, x_B(t)/x_B(0)=[x_A(t)/x_A(0)]^0.08. Responsive control cannot reduce final B crossover for exactly the same final A imbalance in this model. It can improve the time distribution of imbalance and therefore the stated composite objective by opening early and closing later. This is the demonstrated control mechanism, not enhanced selectivity.

## Literature and feasibility

`data/responsive_membranes.csv` contains a source-traceable experimental ion-selectivity value from [Song et al., ACS Nano 2026, DOI 10.1021/acsnano.5c20748](https://pubmed.ncbi.nlm.nih.gov/41925149/): K⁺/Li⁺ selectivity 481.2 under voltage control. This establishes related redox-controlled ion transport in a different system. It does not validate these hypothetical A/B species, an autonomous gate, or this parameter range.

Switching ratio and response time are blank because the accessed abstract does not provide verified values for them. Ion selectivity is not a switching ratio. No invented literature range or LIKELY feasibility label is displayed. Current feasibility is **UNVERIFIED**. The material specification reports model targets, not proven material capabilities. Hysteresis, cycle life, energy requirements, and compatibility remain unestablished.

## Scope and validation

Implemented: conservative two-species dynamics, finite membrane response, sign-symmetric sensing, best-static and responsive optimization, interactive plots and exports, a numerical recovery map, analytical stability, and a material specification.

Tests cover unequal-volume mass conservation, positive concentrations, gate bounds, the exact fixed-membrane solution, equilibrium, disturbance-sign symmetry, monotone recovery, the transport-budget identity, and tighter-solver consistency.

Not modeled: actual redox chemistry, electroneutrality and counterions, charge/discharge, capacity fade, electro-osmosis, tank hydraulics, activity coefficients, physical gating energy, material degradation, hysteresis, or repeated random disturbances. These omissions prevent interpreting results as predicted battery performance. The demo is a hypothesis generator for transport-control experiments.

## 60-second demo

1. Show the same initial imbalance and the fixed-membrane trajectory.
2. Select AUTOBALANCE and show the delayed permeability response.
3. Run OPTIMIZE and compare objective values against Best static.
4. Explain that the map separates fast and slow recovery; all valid points are stable.
5. Show the membrane target and the unverified feasibility assessment.

“AutoBalance asks what happens when the membrane becomes part of the battery's control system.”
