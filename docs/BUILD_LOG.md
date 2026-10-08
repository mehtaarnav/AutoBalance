# AutoBalance build log

Public repository: [mehtaarnav/AutoBalance](https://github.com/mehtaarnav/AutoBalance).

## October 7, 2026 — Turn the demo into a testable research question

We began with a two-reservoir transport simulation. A responsive membrane candidate beat the numerical best constant membrane on a chosen composite objective after one known concentration disturbance. The recorded nominal improvement was 40.1%. This was a simulation result under hypothetical transport parameters, not a measured improvement in battery efficiency, capacity, or lifetime.

The council identified the central missing comparison: a known disturbance can reward opening early and closing later. A simple timer might capture that benefit. Beating a constant membrane does not establish that feedback is useful.

Our next question is therefore: **when does feedback outperform a timed transport schedule under disturbances it was not tuned to?**

### A useful limit, before another optimization

In the original passive model, both species share the same permeability history with a fixed ratio, P_B = 0.08 P_A. Between external disturbances,

    x_B(t) / x_B(0) = [x_A(t) / x_A(0)]^0.08

where x denotes the concentration difference between reservoirs. The relation assumes nonzero starting differences and no intervening forcing. The differences retain their signs during passive recovery.

This means all policies have the same B redistribution at exactly the same remaining A imbalance. Responsive control can change the timing of transport; it cannot create better intrinsic selectivity under this constitutive law. The nominal endpoint crossover comparison used different final A imbalances and must not be presented as matched-recovery selectivity improvement.

With repeated disturbances, this relation applies separately between events. It must not be applied across jumps as though the system were unforced. Gross crossover and net redistribution also differ when flux reverses; benchmark reports must identify which quantity is scored.

### The benchmark being built

Compare an optimized constant membrane, an optimized timer, and a responsive membrane under the same physical bounds and scoring rules. Tune policies on declared training scenarios, freeze their parameters, and evaluate unseen repeated disturbances. Record the seeds, scenarios, parameter bounds, objective terms, search budgets, and optimizer status.

A timer must not receive hidden knowledge of future test disturbances. If event-triggered timing is included, label it as a separate controller with access to an event signal. If a policy is retuned per scenario, label it as an oracle rather than a deployable fixed policy.

Report paired results against both challengers, including cases where feedback loses. Show the individual costs as well as the weighted total. A win across a finite synthetic test set is evidence within that set, not a universal guarantee or experimental validation.

### Completed frozen-policy benchmark

The saved `results/benchmark/manifest.json` and `scores.csv` now contain four trained policies, four training cases, and 32 held-out synthetic cases generated with seed 20261007. The policies are constant transport, a one-switch timer, a four-stage schedule, and feedback. None was retuned per held-out case.

| Policy | Mean training objective | Mean held-out objective |
| --- | ---: | ---: |
| Constant | 0.296033 | 0.213460 |
| One-switch timer | 0.264518 | 0.202996 |
| Four-stage schedule | 0.266099 | 0.207622 |
| Feedback | 0.165995 | 0.130586 |

Feedback lowered the mean held-out objective by 38.824% against constant, 35.671% against timer, and 37.104% against the four-stage schedule. Each percentage is one minus the ratio of mean objectives, multiplied by 100. Feedback won all 32 paired comparisons against each challenger; the worst paired improvement was 16.82%, 12.20%, and 15.42%, respectively. This is a result within one synthetic test distribution, not a universal guarantee.

The dynamic-policy searches used seeds 7, 19, and 41 and a 20-iteration budget. Every dynamic search hit its iteration limit; candidates were selected by training objective. The static refinement reported convergence but no global certificate. All results concern the best candidates found within the specified families and search budgets. A stronger schedule or more extensive optimization could change the comparison.

The benchmark score omits the settling penalty in the original nominal experiment. The old 40.1% result and these percentages are different experiments with different scores. No battery-efficiency, capacity, lifetime, or material-feasibility claim follows from either experiment.

The public launch draft is now populated from these artifacts. It has not been posted.

### What would change our mind

- If the timer matches feedback, the simpler schedule is a successful result and a better starting design for the tested setting.
- If feedback wins only under one narrow objective weighting, the result is preference-dependent.
- If realistic delay or parameter uncertainty removes the benefit, the material requirements need revision.
- If a measured membrane cannot provide the assumed transport response, this remains an illustrative control study.

### Related work and the evidence boundary

Electrochemically gated ion separation already has experimental precedents: [Song et al., ACS Nano, 2026](https://pubs.acs.org/doi/abs/10.1021/acsnano.5c20748). Its ion system and external actuation do not validate AutoBalance's assumed material or autonomous operation.

Flow-battery crossover estimation also has prior work with a laboratory prototype: [An Adaptive Observer Design for Charge-State and Crossover Estimation, 2019](https://arxiv.org/abs/1903.04073). Feedback and crossover estimation are not new categories invented by this project.

Electrolyte engineering can control transmembrane flux and has actual cycling evidence: [Wang et al., Nature Communications, 2026](https://www.nature.com/articles/s41467-026-70872-8). Membrane design also addresses coupled crossover and water migration: [Tan et al., Advanced Science, 2023](https://advanced.onlinelibrary.wiley.com/doi/10.1002/advs.202206888).

Our candidate contribution is an inspectable control benchmark, its limits, and a route to measurable material requirements. We have not established scientific priority, battery-level benefit, or material feasibility.
