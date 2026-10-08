# AutoBalance demo script

Target: 60–75 seconds. The held-out results below were checked against `results/benchmark/manifest.json` and `scores.csv`. Record the saved plots or implemented app views.

End-card repository: [github.com/mehtaarnav/AutoBalance](https://github.com/mehtaarnav/AutoBalance). Confirm the release files are published before recording the end card. No public hosted app URL is assumed.

| Time | Show | Say |
| --- | --- | --- |
| 0–10 s | A recovery plot with identical initial conditions | "AutoBalance asks whether a membrane that responds to imbalance can outperform fixed transport." |
| 10–20 s | Permeability aligned below recovery | "Opening early can speed recovery. Closing later can limit additional transfer. But a timer might do that too." |
| 20–30 s | Constant, timer, four-stage schedule, and feedback together | "We trained four policies on four scenarios, froze them, and tested 32 unseen synthetic cases." |
| 30–45 s | Aggregate held-out results, then first seeded scenario | "Feedback's mean model objective was 35.7 percent lower than the timer's and 37.1 percent lower than the four-stage schedule's. It won all 32 cases against each. This is a simulation score, not battery efficiency." |
| 45–55 s | Transport-budget identity or matched-recovery plot | "There is a limit: with fixed species selectivity, the same final recovery requires the same unwanted transfer. Timing helps; selectivity stays unchanged." |
| 55–75 s | Assumptions, optimizer status, downloadable evidence | "The membrane is hypothetical, and every dynamic search hit its iteration cap. These are best-found candidates. Next: stronger challengers and measured membrane dynamics. Code and evidence are open to inspection." |

Use `held_out_results.png` for the aggregate and `surprise_disturbances.png` for the first seeded case. Feedback's mean score is 0.130586, compared with 0.213460 for constant, 0.202996 for timer, and 0.207622 for schedule. The improvement against constant is 38.8%. Percentages are calculated from mean objectives, not averaged scenario percentages. The benchmark uses a different objective from the original nominal experiment.

## Most useful UI addition

One shared time axis with two panels: normalized imbalance on top, membrane permeability below. Four consistent colors identify constant, timer, four-stage schedule, and feedback. Thin vertical lines mark external disturbances. A small label identifies the scenario, policy-training provenance, and simulation status.

This connects cause, action, and result immediately. A single scenario is illustrative; keep aggregate benchmark statistics visible nearby so a selected trace cannot stand in for the whole test set.

## Capture checklist

- Use the same scenario and physical bounds for all displayed policies.
- Keep units, legend, and simulation label readable at phone size.
- If using a percentage, name the metric and challenger in the same frame.
- Show solver/search status when discussing optimized results.
- Describe the original no-forcing identity as applying between disturbances.
- Link a public repository or hosted demo only after confirming access outside the local machine.

## Questions worth inviting

What measurement would falsify the assumed gate response? How much delay removes the benefit? When is a timer sufficient? Which transport effects must be added before predicting battery performance?

The demo should make those questions easier to answer, rather than presenting a simulated objective as a battery-efficiency claim.
