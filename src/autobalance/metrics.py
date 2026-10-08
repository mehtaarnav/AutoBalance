import numpy as np
from scipy.integrate import trapezoid


def metrics(df, system):
    t = df["time (s)"].to_numpy()
    x = abs(df.imbalance.to_numpy())
    tolerance = max(abs(system.imbalance) * 0.05, 1e-6)
    outside = np.flatnonzero(x > tolerance)
    settled = bool(len(outside) == 0 or outside[-1] < len(t) - 1)
    settle = 0.0 if len(outside) == 0 else (float(t[outside[-1] + 1]) if settled else None)
    exposure = float(trapezoid((x / max(abs(system.imbalance), 1e-6)) ** 2, t) / system.horizon)
    loss = float(df["B crossed (mol)"].iloc[-1])
    loss_fraction = loss / (1000 * system.volume_left + 100 * system.volume_right)
    # Censored settling penalty: unmet target receives 1; flag remains explicit.
    score = (
        exposure
        + 2 * loss_fraction
        + 0.15 * (settle / system.horizon if settled else 1)
        + 0.01 * float(df["gate proxy"].iloc[-1])
    )
    residuals = []
    for species in ("A", "B"):
        mass = (
            system.volume_left * df[f"{species} left"]
            + system.volume_right * df[f"{species} right"]
        )
        residuals.append(float(abs(mass - mass.iloc[0]).max() / mass.iloc[0]))
    return dict(
        objective=score,
        settling_s=settle,
        settled=settled,
        B_crossed_mol=loss,
        imbalance_exposure=exposure,
        conservation_relative=max(residuals),
    )
