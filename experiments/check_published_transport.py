"""Compare a literal author-script translation with the released numerical table.

Read-only workbook extraction. No parameters are fitted to eliminate discrepancies.
Run with the research dependency: pip install -e '.[research]'.
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import openpyxl

# Allow a separate analysis runtime to read the same source checkout.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main():
    from autobalance.vanadium import RelativeTransport, balance_ratio, opposing_flux_ratio

    source = ROOT / "data" / "literature" / "wang2026" / "figure2.xlsx"
    workbook = openpyxl.load_workbook(source, read_only=True, data_only=True)
    rows = list(workbook["Fig. 2a"].values)
    concentration_ratio = np.array([row[0] for row in rows[1:]], dtype=float)
    soc = np.array(rows[0][1:], dtype=float) / 100
    observed = np.array([row[1:] for row in rows[1:]], dtype=float)
    prediction = opposing_flux_ratio(concentration_ratio[:, None], soc[None, :])
    # Supplement Table S1 is a second published coefficient set, not a fitted fix.
    supplement = RelativeTransport(5.261, 1.933, 4.095, 3.538)
    alternate = opposing_flux_ratio(
        concentration_ratio[:, None], soc[None, :], transport=supplement
    )
    benchmark = json.loads((ROOT / "results" / "benchmark" / "manifest.json").read_text())
    policy = benchmark["policies"]["feedback"]
    result = {
        "source_doi": "10.6084/m9.figshare.28938164",
        "article_doi": "10.1038/s41467-026-70872-8",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "table": "Fig. 2a!A1:U39",
        "data_type": "Published computed flux ratios, not experimental gate measurements",
        "values_compared": int(observed.size),
        "author_script_max_absolute_discrepancy": float(abs(prediction - observed).max()),
        "author_script_rmse": float(np.sqrt(np.mean((prediction - observed) ** 2))),
        "supplement_coefficients_max_absolute_discrepancy": float(abs(alternate - observed).max()),
        "verdict": "Released script does not reproduce the table to its five-decimal precision; clarification needed",
        "balance_concentration_ratio_at_soc_0_50_100": balance_ratio(
            np.array([0, 0.5, 1])
        ).tolist(),
        "experimental_concentrations": {
            "source_cells": "Fig. 2e!B2:F5",
            "initial_negative_M": workbook["Fig. 2e"]["C2"].value,
            "initial_positive_M": workbook["Fig. 2e"]["D3"].value,
            "final_negative_M": workbook["Fig. 2e"]["E4"].value,
            "final_positive_M": workbook["Fig. 2e"]["F5"].value,
            "time_h_as_tabulated": workbook["Fig. 2e"]["B4"].value,
            "limitation": "End-state measurements alone cannot identify permeance; volumes and redox reactions matter",
        },
        "current_hypothetical_candidate": {
            "switch_ratio": policy["high"] / policy["low"],
            "threshold_mV": policy["threshold"] * 1000,
            "transition_10_to_90_width_mV": 2 * np.log(9) / policy["k"] * 1000,
            "tau_s": 100,
            "status": "Candidate specification, not demonstrated material performance or a proven minimum requirement",
        },
    }
    output = ROOT / "results" / "published_transport_check.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
