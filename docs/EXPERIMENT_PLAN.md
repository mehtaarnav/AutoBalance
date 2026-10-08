# The next experiment: replace an assumed law with measured transport

The next evidence milestone is a calibrated two-reservoir transport cell. It is not yet a full flow battery. The test asks whether a real gate changes useful and undesirable transport in the way the controller needs, and whether that effect survives uncertainty and operating costs.

## 1. Measure the membrane before optimizing it

Choose an actual membrane and chemically compatible species with independently measurable concentrations. Declare which transfer is useful and why. Keep reservoir volume, temperature, area, mixing, and pressure difference controlled. Measure both species in both reservoirs and include sampling withdrawals in the inventory balance.

For several prescribed gate settings, measure concentrations over time. Estimate each permeance independently from the flux and concentration difference. Use replicates and report uncertainty, adsorption, degradation, and any inventory deficit. Do not infer selectivity from one reservoir alone.

Apply opening and closing steps to measure response time, hysteresis, and repeatability. Hold back entire specimens or experimental runs for validation. Interpolation within measured settings is acceptable; extrapolation beyond them must be flagged and excluded from headline predictions.

Proposed data columns:

    specimen_id, run_id, time_s, gate_command, gate_voltage_V,
    gate_current_A, temperature_K, volume_left_m3, volume_right_m3,
    A_left_mol_m3, A_right_mol_m3, B_left_mol_m3, B_right_mol_m3

Derived calibration tables should store P_A and P_B separately, their uncertainty, gate setting, temperature, measurement method, and source run identifiers. An empirical gate law belongs behind the same simulation interface as the hypothetical constant-ratio law. Keep both models so the effect of adding measurements remains visible.

Falsifier: the achievable gate range or speed cannot meet the declared recovery constraint, or the improvement disappears across the calibration uncertainty. A constant measured P_B/P_A means temporal control still cannot improve final B transfer at matched final A recovery in the passive model.

## 2. Test whether the proposed signal observes imbalance

Independently assay composition while recording the proposed voltage signal across the intended operating range. For redox electrodes, include both oxidation states and relevant activity or reference-electrode effects. Fit the signal model on calibration runs and test it on different runs.

The current RT/F log(c_left/c_right) expression is a concentration-cell proxy. It is not a universal battery-voltage equation. If two materially different imbalances yield indistinguishable voltages within measurement error, a single voltage is insufficient; add a measurement or an observer before testing autonomous control.

Falsifier: held-out signal errors cause the gate to open in the wrong operating region or miss disturbances that violate the recovery requirement. Report the actual error and latency distribution, then replay them in simulation.

## 3. Run a frozen comparison with surprises

Use separate calibration/training and validation runs. Freeze the static setting, timer, four-bin schedule, and feedback parameters before validation. Randomize disturbance timing and order across independent replicates. Apply the same hardware limits and initial conditions. Record the full trajectories, failed trials, and individual objective components.

Set the minimum useful recovery improvement and maximum allowable undesirable transfer before collecting validation data. Compare matched-final-recovery trials when claiming selectivity. Use independently measured concentrations for scoring; the controller's own sensor cannot be the sole judge of success.

Falsifier: feedback fails the predefined recovery/crossover constraints or does not improve on the strongest frozen comparator within experimental uncertainty. That is a useful result, not a reason to change the score after seeing the data.

## 4. Close the energy balance before claiming autonomy

Measure gate energy as the time integral of gate voltage times gate current, and meter sensing/control power, startup, leakage, and reset. Identify whether power comes from an external supply, stored charge, or the system's chemical free energy. Account for that source over repeated cycles; count replenishment as an input.

Externally powered feedback establishes automatic control. Sustained energetic autonomy additionally requires repeatable operation without external power and an energy balance that explains where every actuation cycle gets its energy. The simulation's gate-motion proxy establishes neither.

Falsifier: sensing and actuation require an unaccounted energy source, or net useful system performance deteriorates after these costs are included. Report that result before attempting battery-efficiency claims.

## What can be built overnight

Implement and test a measured-law import interface, uncertainty propagation, and calibration-versus-validation separation. Use clearly labeled synthetic fixtures to verify the interface while real measurements are unavailable. Do not label those fixtures as experimental evidence or choose state-dependent selectivity merely to make the controller win. A completed data interface is infrastructure; a validated constitutive law requires observations.
