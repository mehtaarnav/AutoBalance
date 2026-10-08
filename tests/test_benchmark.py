from dataclasses import replace

import numpy as np
import pytest

from autobalance.benchmark import P_MAX, P_MIN, Policy, Scenario, run_scenario
from autobalance.model import System


def test_static_matches_analytic_solution_and_integrated_exposure():
    system = System(volume_right=2e-4)
    scenario = Scenario("analytic")
    result = run_scenario(system, scenario, Policy("static"))
    frame, scores = result["trajectory"], result["metrics"]
    decay = system.area * (1 / system.volume_left + 1 / system.volume_right) * 2e-6
    np.testing.assert_allclose(frame.imbalance, 800 * np.exp(-decay * frame["time (s)"]), rtol=1e-6)
    expected_exposure = -np.expm1(-2 * decay * system.horizon) / (2 * decay * system.horizon)
    assert scores["imbalance_exposure"] == pytest.approx(expected_exposure, rel=1e-7)
    assert scores["gate_penalty"] == 0


@pytest.mark.parametrize("kind", ["static", "timer", "feedback", "schedule"])
def test_disturbances_conserve_inventory_and_have_exact_jump(kind):
    system = System(volume_right=2e-4)
    scenario = Scenario("repeated", disturbances=((2500, -500), (5000, 600)))
    result = run_scenario(system, scenario, Policy(kind))
    frame = result["trajectory"]
    assert result["metrics"]["conservation_relative"] < 1e-12
    assert frame[["A left", "A right", "B left", "B right"]].min().min() > 0
    assert frame.w.between(-1e-8, 1 + 1e-8).all()
    for time, change in scenario.disturbances:
        event = frame.loc[frame["time (s)"] == time]
        assert len(event) == 2
        assert event.imbalance.iloc[1] - event.imbalance.iloc[0] == pytest.approx(change)
        assert event.w.iloc[1] == event.w.iloc[0]


def test_objective_is_independent_of_plot_sampling():
    system = System()
    scenario = Scenario("off-grid event", disturbances=((2345, 500),))
    policy = Policy("feedback")
    coarse = run_scenario(system, scenario, policy, samples=2)["metrics"]
    fine = run_scenario(system, scenario, policy, samples=2001)["metrics"]
    assert coarse["objective"] == pytest.approx(fine["objective"], abs=1e-12)


def test_timer_gate_has_exact_finite_response():
    policy = Policy("timer", switch_time=1000)
    frame = run_scenario(System(), Scenario("timer"), policy)["trajectory"]
    time = frame["time (s)"].to_numpy()
    expected = np.where(
        time <= 1000, -np.expm1(-time / 100), -np.expm1(-10) * np.exp(-(time - 1000) / 100)
    )
    np.testing.assert_allclose(frame.w, expected, atol=2e-8)


def test_zero_schedule_matches_passive_minimum_and_target_has_finite_response():
    system, scenario = System(), Scenario("schedule")
    scheduled = run_scenario(system, scenario, Policy("schedule", schedule_targets=(0.0,) * 4))
    passive = run_scenario(system, scenario, Policy("static", static_p=P_MIN))
    assert scheduled["metrics"]["objective"] == pytest.approx(
        passive["metrics"]["objective"], rel=1e-7
    )
    frame = run_scenario(system, scenario, Policy("schedule", schedule_targets=(0.3,) * 4))[
        "trajectory"
    ]
    expected = 0.3 * -np.expm1(-frame["time (s)"].to_numpy() / 100)
    np.testing.assert_allclose(frame.w, expected, atol=2e-8)


def test_constant_requests_share_physical_startup_and_motion_cost():
    requested = 8e-6
    target = (requested - P_MIN) / (P_MAX - P_MIN)
    policies = [
        Policy("timer", low=requested, high=requested),
        Policy("feedback", low=requested, high=requested),
        Policy("schedule", schedule_targets=(target,) * 4),
    ]
    results = [
        run_scenario(System(), Scenario("common startup"), policy, rtol=1e-10)
        for policy in policies
    ]
    common_time = results[0]["trajectory"]["time (s)"].to_numpy()
    for result in results:
        frame = result["trajectory"]
        assert frame["P A (m/s)"].iloc[0] == P_MIN
        expected = P_MIN + (requested - P_MIN) * -np.expm1(-frame["time (s)"] / 100)
        np.testing.assert_allclose(frame["P A (m/s)"], expected, rtol=1e-6)
        assert result["metrics"]["objective"] == pytest.approx(
            results[0]["metrics"]["objective"], rel=1e-7
        )
        assert result["metrics"]["gate_penalty"] == pytest.approx(
            results[0]["metrics"]["gate_penalty"], rel=1e-6
        )
        # Policies introduce different segment boundaries; compare the shared plotting grid.
        shared = frame[frame["time (s)"].isin(common_time)]
        reference = results[0]["trajectory"]
        reference = reference[reference["time (s)"].isin(shared["time (s)"])]
        np.testing.assert_allclose(shared.imbalance, reference.imbalance, rtol=1e-6, atol=1e-6)


def test_sign_reversal_symmetry():
    scenario = Scenario("positive", disturbances=((3000, 400),))
    reverse = replace(
        scenario, name="negative", initial_imbalance=-800, disturbances=((3000, -400),)
    )
    positive = run_scenario(System(), scenario, Policy("feedback"))
    negative = run_scenario(System(), reverse, Policy("feedback"))
    assert positive["metrics"]["objective"] == pytest.approx(
        negative["metrics"]["objective"], rel=1e-7
    )


def test_tighter_solver_preserves_objective_with_disturbances():
    scenario = Scenario("convergence", disturbances=((2345, -650), (5001, 500)))
    policy = Policy("feedback", k=1900, threshold=0.003)
    default = run_scenario(System(), scenario, policy)["metrics"]["objective"]
    tighter = run_scenario(System(), scenario, policy, rtol=1e-10)["metrics"]["objective"]
    assert abs(default - tighter) < 1e-7


def test_invalid_scenarios_and_policies_fail_explicitly():
    with pytest.raises(ValueError):
        Scenario("bad", disturbances=((100, 1), (100, 2)))
    with pytest.raises(ValueError):
        Policy("feedback", high=float("nan"))
    with pytest.raises(ValueError):
        run_scenario(
            System(),
            Scenario("negative concentration", disturbances=((10, 5000),)),
            Policy("static"),
        )
    with pytest.raises(ValueError):
        run_scenario(
            System(), Scenario("past horizon", disturbances=((8000, 1),)), Policy("static")
        )
    with pytest.raises(ValueError):
        run_scenario(System(), Scenario("invalid tolerance"), Policy("static"), rtol=float("nan"))
