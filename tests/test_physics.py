import numpy as np

from autobalance.membrane import Membrane
from autobalance.metrics import metrics
from autobalance.model import System
from autobalance.simulation import simulate
from autobalance.stability import eigenvalues


def test_conservation_unequal_tanks():
    s = System(volume_right=2e-4)
    d = simulate(s)
    assert metrics(d, s)["conservation_relative"] < 1e-9
    assert d[["A left", "A right", "B left", "B right"]].min().min() > 0
    assert d.w.between(0, 1).all()


def test_fixed_analytic():
    s = System(volume_right=2e-4)
    p = 3e-6
    d = simulate(s, fixed_p=p)
    exact = s.imbalance * np.exp(
        -s.area * p * (1 / s.volume_left + 1 / s.volume_right) * d["time (s)"]
    )
    np.testing.assert_allclose(d.imbalance, exact, rtol=3e-6, atol=1e-5)


def test_equilibrium_and_sign_symmetry():
    d = simulate(System(imbalance=0))
    assert abs(d.imbalance).max() < 1e-10
    pos = simulate()
    neg = simulate(System(imbalance=-800))
    np.testing.assert_allclose(pos.imbalance, -neg.imbalance, atol=1e-4)
    assert (np.diff(abs(pos.imbalance)) <= 1e-6).all()
    assert max(eigenvalues(System(), Membrane())) < 0


def test_transport_budget_identity():
    # Same integrated exposure gives the same final B transport regardless of timing.
    s = System()
    d = simulate(s)
    ratio = d.imbalance.iloc[-1] / s.imbalance
    predicted = 900 * ratio**0.08
    np.testing.assert_allclose(d["B left"].iloc[-1] - d["B right"].iloc[-1], predicted, rtol=1e-4)


def test_tighter_solver_agrees():
    s = System()
    a = metrics(simulate(s), s)["objective"]
    b = metrics(simulate(s, rtol=1e-9), s)["objective"]
    assert abs(a - b) < 1e-6
