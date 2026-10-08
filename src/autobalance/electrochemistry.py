import numpy as np


def error_potential(left, right, temperature=298.15, z=1):
    """Ideal concentration-cell proxy in V; not a full battery OCV model."""
    left, right = np.asarray(left), np.asarray(right)
    if not (
        np.isfinite(left).all()
        and np.isfinite(right).all()
        and np.isfinite(temperature)
        and temperature > 0
        and np.isfinite(z)
        and z > 0
    ):
        raise ValueError("Concentrations, temperature, and charge number must be finite and valid")
    if np.any(np.asarray(left) <= 0) or np.any(np.asarray(right) <= 0):
        raise ValueError("Concentrations must be positive")
    return 8.314462618 * temperature / (z * 96485.33212) * np.log(left / right)
