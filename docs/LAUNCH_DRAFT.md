# AutoBalance public launch draft

Prepared October 7 for October 8, 2026. Draft only; nothing here has been posted. Numbers were checked against the saved benchmark manifest and scores.

## Six-post thread

1/ I'm building AutoBalance in public: a simulation lab asking whether responsive membrane control earns its complexity. The real test: can feedback beat a timer when concentration disturbances arrive unexpectedly?

2/ We trained four policies on 4 scenarios, then froze them: constant transport, a one-switch timer, a four-stage schedule, and feedback. They faced the same 32 held-out synthetic scenarios. No policy was retuned on those cases.

3/ Feedback reduced mean model objective by 38.8% vs constant, 35.7% vs timer, and 37.1% vs four-stage schedule. It won all 32 cases against each. These are ratios of mean scores, not battery-efficiency gains or a guarantee beyond this test set.

4/ A hard limit: during undisturbed recovery, fixed species selectivity means the same final recovery requires the same unwanted transfer. Feedback changes timing; it doesn't invent selectivity. Repeated disturbances make timing worth testing.

5/ The limits matter: synthetic scenarios, hypothetical membrane, restricted timer/schedule families. All dynamic-policy searches hit their iteration cap. These are best-found candidates, not certified optima. No real battery or material has been validated.

6/ Code, assumptions, seeds, individual results, and reproduction steps are public. Next: stronger challengers and measured membrane dynamics. If you work on responsive membranes, which assumption should we test first? https://github.com/mehtaarnav/AutoBalance

## Standalone post

AutoBalance: feedback beat a timer by 35.7% on mean model objective across 32 held-out synthetic cases. Hypothetical transport, finite searches, no validated battery gain. Code, assumptions, and every result: https://github.com/mehtaarnav/AutoBalance

## Evidence behind the wording

| Policy | Mean training objective, 4 cases | Mean held-out objective, 32 cases |
| --- | ---: | ---: |
| Constant | 0.296033 | 0.213460 |
| One-switch timer | 0.264518 | 0.202996 |
| Four-stage schedule | 0.266099 | 0.207622 |
| Feedback | 0.165995 | 0.130586 |

Each improvement is `100 * (1 - mean(feedback objective) / mean(challenger objective))`: 38.8243567%, 35.6707464%, and 37.1039884%, respectively. It is not the mean of scenario-level percentage improvements. The minimum paired improvement was 16.82% against constant, 12.20% against timer, and 15.42% against schedule. Each comparison had 32 wins and zero losses in this held-out suite.

Policies were selected using four training scenarios. The held-out seed is 20261007. Dynamic-policy searches used seeds 7, 19, and 41 with 20 iterations; all reported budget exhaustion. Static refinement reported convergence without a global certificate. Equal iteration limits do not imply identical function-evaluation counts. The timer and four-stage schedule are restricted open-loop families, not every possible schedule.

The benchmark objective excludes the settling penalty used in the original nominal experiment. Do not compare its percentage directly with the older 40.1% headline as though they were the same test. These synthetic results establish neither physical actuation feasibility nor gains in battery efficiency, capacity, or life.

## Visual and public links

Lead with [all held-out results](https://github.com/mehtaarnav/AutoBalance/blob/main/results/benchmark/held_out_results.png). Follow with [the first seeded disturbance scenario](https://github.com/mehtaarnav/AutoBalance/blob/main/results/benchmark/surprise_disturbances.png), which was selected by index rather than largest improvement. Keep all four policies visible.

- [Benchmark manifest](https://github.com/mehtaarnav/AutoBalance/blob/main/results/benchmark/manifest.json): policies, search status, seeds, source hashes, summary.
- [Individual scores](https://github.com/mehtaarnav/AutoBalance/blob/main/results/benchmark/scores.csv): the numerical basis for these claims.
- [Build log](https://github.com/mehtaarnav/AutoBalance/blob/main/docs/BUILD_LOG.md): the change in research question and related work.

Confirm these release files are visible in the repository before posting. A public hosted app URL has not been supplied; localhost is not a public demo.
