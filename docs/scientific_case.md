# AutoBalance: the scientific case

Evidence reviewed 7 October 2026. This is a hypothesis and benchmark, not an experimentally validated battery or membrane. The strongest near-term contribution is an unusually transparent test of when feedback-controlled transport earns its complexity.

## The question worth testing

Can a membrane controller, with fixed parameters and finite response time, outperform both a constant membrane and a timed opening policy when disturbances arrive unpredictably? A nominal trajectory alone cannot answer this. A deterministic feedback trajectory can always be replayed by a clock, producing the same transport without measuring the state.

The falsifiable hypothesis is therefore about robustness to information unavailable to a timer. It is not that time-varying transport is inherently more selective.

## What the equations already prove

Let x_i = c_i,L - c_i,R and C = A(1/V_L + 1/V_R). The passive model gives

    dx_i/dt = -C P_i(t) x_i.
    x_i(t) = x_i(0) exp[-C integral_0^t P_i(s) ds].

This follows by subtracting the reservoir balances and integrating d(log|x_i|)/dt. Reservoir-weighted inventory is conserved because the two flux terms cancel. With positive permeance, an undisturbed imbalance retains its sign and decreases in magnitude; membrane delay cannot create concentration oscillations in this model. A map of fast and slow recovery is not a stability phase transition.

If P_B = alpha P_A, define q(t) = C integral_0^t P_A(s) ds. Then

    x_A(t)/x_A(0) = exp[-q(t)]
    x_B(t)/x_B(0) = exp[-alpha q(t)]
                      = [x_A(t)/x_A(0)]^alpha.

Consequently, for identical initial states, volumes, and alpha, any two policies reaching the same final A imbalance produce the same final B imbalance. For positive initial x_B, B transferred is

    V_L V_R / (V_L + V_R) * [x_B(0) - x_B(t)].

No controller can evade this identity merely by changing the timing of a common permeance multiplier. The default comparison's lower B transfer occurs at a different final A imbalance. It must not be described as improved intrinsic selectivity or suppressed crossover at matched recovery.

Timing can still matter: moving a fixed transport budget earlier makes q(t) larger earlier and lowers integrated squared A imbalance. This explains why opening early and closing later can beat a constant membrane under the chosen objective. It also explains why a strong timed control is essential. An instantaneous high-then-low schedule is a useful ideal reference, but without actuator lag and motion cost it is not a fair hardware comparator.

These identities apply between external disturbances. An A-only pulse changes the relation to the original A state; restart the analytical check from each pulse boundary. Conservation tests must include the explicitly added or redistributed inventory.

## A benchmark that can reject the hypothesis

1. Compare constant permeance, a timed opening policy, and measured-state feedback. Use the same permeance bounds. Give timed and feedback gates the same response equation, initial gate state, and motion cost. Distinguish a practical frozen timer from an oracle that knows future disturbances.
2. Fit every policy on the same declared training scenarios. Freeze parameters before evaluating held-out onset times, amplitudes, signs, repeated disturbances, and sensor bias or delay. Record random seeds and the exact scenarios; never retune on test cases.
3. Report paired objective differences against each comparator, all individual objective components, failure counts, worst cases, and uncertainty across independently generated test scenarios. A seeded finite suite is a stress test, not a population confidence interval or experimental replication.
4. Include nominal replay: save the feedback permeance trace and replay it open-loop. Numerical trajectories should agree within solver tolerance. This separates scheduling value from feedback value.
5. Include matched-final-imbalance checks, a no-disturbance case, and a stuck-open/stuck-closed actuator. Repeat across objective weights, selectivity ratios, and actuator response times. Show regions where feedback loses.

Suggested advance criterion for a future preregistered benchmark: positive mean paired improvement over both trained baselines with a confidence interval excluding zero, acceptable worst-case recovery, and no material worsening of a declared crossover constraint. Choose the application-specific recovery and crossover limits before evaluating the test set. A large mean gain accompanied by catastrophic outliers does not meet this criterion.

The implemented version-1 benchmark trains on four declared cases and evaluates 32 seeded synthetic cases, each with two later A redistributions. It also transfers the frozen designs to smaller/larger membrane area and unequal tank volumes. It compares a constant membrane, a one-switch timer, a four-bin open-loop schedule, and feedback. The four-bin schedule independently selects a target permeance for each quarter of the horizon and uses the same first-order response time. It can open again later without sensing the disturbance. Both timing families remain restricted: a win does not prove superiority over every possible open-loop policy or certify that their finite searches found global optima. Sensor noise, sensor delay, and measured actuation energy are not tested by the area/tank transfer suites.

Version 1 integrates exposure inside the ODE and uses a fixed 800 mol/m3 reference imbalance; its score omits the original nominal experiment's settling penalty. Results from these two objectives must not be combined into one percentage. Weight sensitivity re-scores frozen policies and does not establish optimality under each alternative preference. The common zero gate state is an explicit startup/reset assumption, not a claim that each gate began at its natural undisturbed equilibrium.

All dynamic policies now use the same physical gate coordinate, normalized across the global permeance limits. They start at the global minimum permeance, share the 100-second actuator response time, and incur the same squared-coordinate-velocity penalty. The passive constant membrane starts at its chosen permeance and incurs no actuation penalty. This removes dependence of the proxy penalty on a policy's chosen low/high range, but still does not make the proxy a physical energy model.

The recorded version-1 results show 38.8%, 35.7%, and 37.1% lower mean objective against the frozen static, one-switch, and four-bin policies, respectively, on the 32 held-out cases. Feedback wins each of those 32 paired comparisons. Those percentages are ratios of mean objectives, not mean per-case percentage improvements. The transfer suites reuse the same 32 disturbance realizations with changed plant parameters; they are not 96 new independent disturbance trials. The four training cases are hand-selected and do not constitute a random training sample from the test distribution. No test scenarios enter parameter fitting or seed selection in the recorded runner; this code-level separation is not an independently preregistered or blinded study. Further model or policy choices informed by these results require a fresh final test set.

If the timer matches feedback under unseen disturbances, the autonomy hypothesis fails for that distribution. If improvement vanishes when delay, sensor error, or measured actuation energy enters the model, the proposed implementation fails even if the ideal controller works.

## Prior art and the remaining distinction

This is a targeted primary-source review, not a complete novelty or patent search.

| Primary work | Established result relevant here | What AutoBalance still has to show |
| --- | --- | --- |
| [Smith and Monroe, 2021](https://www.frontiersin.org/journals/chemical-engineering/articles/10.3389/fceng.2021.748865/full) | Demonstrated camera-based reservoir-volume feedback through differential pump control; released software and firmware. | Feedback balancing itself is not new. Here the proposed actuator is membrane transport, and the present evidence is simulation. |
| [Jafari, Sakti and Botterud, 2021 preprint](https://arxiv.org/abs/2107.03339) | Optimized electrolyte-rebalancing service count and timing for economic operation. | Scheduling rebalancing is prior art; a claim must isolate the value of state-responsive membrane actuation. |
| [Wang et al., Nature Communications, 2026](https://www.nature.com/articles/s41467-026-70872-8) | Tuned electrolyte concentration and valence to balance opposing vanadium fluxes; reported battery cycling experiments. | Dynamic flux balance and reduced capacity decay are not new claims. This work changes electrolyte formulation; AutoBalance proposes a variable membrane gate, without comparable hardware evidence. |
| [Song et al., ACS Nano, 2026](https://pubs.acs.org/doi/10.1021/acsnano.5c20748) | Demonstrated voltage-controlled ion transport in a Prussian-blue/carbon-nanotube membrane; abstract reports K+/Li+ selectivity 481.2. | Redox-responsive membranes already exist. That selectivity is neither a switching ratio nor proof of autonomous battery operation, response time, or compatibility with the hypothetical A/B species. |

The defensible public description is: an open, falsifiable benchmark for state-responsive transport, including the limits imposed by shared selectivity and comparisons against time-based control. Do not claim a world first, a material discovery, a percentage improvement in battery efficiency, or a validated self-powered device. Potential research novelty would require a literature-complete argument plus a new experimentally supported coupling, mechanism, or robust control result.

## Minimum experiment that changes the evidence level

Start with a controlled two-reservoir transport cell and a characterized responsive membrane, before claiming a full battery. Independently measure both species in both reservoirs, volumes, temperature, gate potential and current, and an independently measured imbalance signal. Fit P_A and P_B versus gate state, their response times, hysteresis, and drift from separate calibration runs. Verify inventory closure and identify adsorption or chemical reaction rather than counting every concentration change as transfer.

Test the sensing hypothesis separately. The implemented RT/F log(c_L/c_R) is an ideal concentration-cell proxy. Real redox electrodes depend on oxidized/reduced activities, electron number, reference potentials, junction potentials, and often other species. Calibrate measured voltage against independently assayed composition across operating conditions. Test whether the same voltage maps to materially different imbalances; if it does, the single-signal controller needs an observer or extra measurement. Do not rename cell voltage as an imbalance sensor without this test.

Then compare frozen static, timer, and feedback policies with randomized disturbances and independent membrane replicates. Match final recovery when discussing selectivity. Reserve additional specimens or runs for validation after fitting.

To establish energetic autonomy, identify the physical source that powers sensing and gating. Measure gate work integral V_gate I_gate dt, sensor/control consumption, startup energy, and any changes in stored chemical or electrical energy. Include leakage and reset costs over repeated cycles. A precharged gate that gradually discharges is stored-energy operation, not sustained autonomy. Demonstrate repeatable recovery without an external power source while closing the energy balance within measurement uncertainty. The current squared-gate-velocity penalty is not an energy measurement and cannot support that claim.

Only a subsequent chemistry-specific cycling experiment can connect this architecture to coulombic efficiency, energy efficiency, capacity retention, and lifetime. Charge transport, electroneutrality, migration, water transfer, reaction kinetics, and membrane resistance belong in that model. The present A/B transport demonstration predicts none of those battery metrics.
