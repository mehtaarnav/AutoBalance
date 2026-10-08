# First physical feasibility check

The next decision is whether an actual membrane and measurement system can support the proposed controller. No responsive membrane has yet been identified that satisfies the simulated specification.

## The battery target must change

The released Wang et al. vanadium transport model distinguishes V(II), V(III), V(IV), and V(V). Its opposing flux ratio depends on the positive/negative concentration ratio and both tanks' state of charge. Using the released script's coefficients, equal opposing flux requires positive/negative concentration ratios of approximately 0.471, 0.941, and 1.486 at shared SOC 0%, 50%, and 100%, respectively.

Therefore, driving one generic concentration difference to zero is not a sufficient vanadium-battery objective. A shared permeability multiplier cancels from the instantaneous opposing-flux ratio. To affect the cycle-integrated imbalance, timing must correlate with changes in flux direction, or the gate must affect species differently. Neither mechanism is established by the original A/B benchmark.

The new `vanadium.py` calculation reproduces the structure of the authors' relative-flux calculation. It does not predict absolute permeance, side reactions, capacity, or efficiency.

## Published measurements are now in the workflow

The authors' Figshare deposit supplies experimental concentration endpoints and computed flux-ratio data. Their source sheet Fig. 2e records initial negative/positive concentrations of 1.70/1.70 M and final concentrations of 1.17/1.91 M at a tabulated 107 h. The paper gives the more precise time as 107.56 h. This is evidence against imposing equal concentrations as a universal operational target; it is not a measured responsive-gate result.

The literal released-script translation was checked against all 760 values in Fig. 2a. It does not reproduce the table at its displayed precision: maximum absolute ratio discrepancy 0.0334, RMSE 0.00861. Using the supplement's more precise coefficient set reduces the maximum discrepancy to 0.0137, but does not remove it. Do not fit away this discrepancy or attribute it to an author error without clarification. The coefficient set and conditions need confirmation.

Run `python experiments/check_published_transport.py` after installing `.[research]`. The source files, license, cell references, checksum, and numerical result are committed. These are other researchers' data, not AutoBalance measurements.

## The material request is now quantitative

The current synthetic benchmark candidate has a 193.5-fold commanded permeance range, a 7.32 mV signal threshold, a 2.20 mV 10–90% signal-transition width, and an assumed 100 s gate response. These describe one optimized candidate. They are not proven minimum requirements and none is experimentally established for an identified membrane.

The sensed voltage and the actuation voltage are different quantities. An ideal 7 mV concentration signal does not show that a membrane can be actuated at 7 mV or supply its own actuation energy.

Before another optimizer search, obtain existing data for one membrane:

1. Species-specific concentration-time traces in both reservoirs at two or more gate settings, with area, thickness, volumes, electrolyte composition, and temperature.
2. Gate-step traces for opening and closing, with current and voltage logged.
3. Repeated runs or uncertainty estimates, plus information about adsorption, reaction, water transfer, and measurement withdrawals.
4. Independent signal-versus-composition measurements if voltage is to infer imbalance.

First fit transport and gate response on separate calibration runs. Reserve entire runs for validation. Only then replace the hypothetical transport law and rerun comparisons. If chemistry or transport is incompatible, abandon that membrane rather than widening the optimizer's assumptions.

Sources: [Wang et al., Nature Communications](https://doi.org/10.1038/s41467-026-70872-8); [released source data and script, CC BY 4.0](https://doi.org/10.6084/m9.figshare.28938164). Partner contacts and supporting institutional sources are in [PARTNER_TARGETS.md](PARTNER_TARGETS.md).
