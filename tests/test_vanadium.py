import numpy as np
import pytest

from autobalance.vanadium import balance_ratio, opposing_flux_ratio


def test_balanced_concentrations_depend_on_state_of_charge():
    soc = np.linspace(0, 1, 21)
    required = balance_ratio(soc)
    np.testing.assert_allclose(opposing_flux_ratio(required, soc), 1)
    assert required[0] < 1 < required[-1]
    assert not np.allclose(opposing_flux_ratio(1, soc), 1)


def test_different_tank_soc_is_supported():
    assert balance_ratio(0, 1) == pytest.approx(5.26 / 4.10)
    assert balance_ratio(1, 0) == pytest.approx(1.93 / 3.54)


@pytest.mark.parametrize("soc", [-0.1, 1.1, np.nan])
def test_invalid_soc_is_rejected(soc):
    with pytest.raises(ValueError):
        balance_ratio(soc)
