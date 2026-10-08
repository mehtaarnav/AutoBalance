# Research partners for measured membrane evidence

Verified 7 October 2026. No one has been contacted. These are research-fit recommendations, not confirmed offers of samples or collaboration. Start with a request for existing data; physical samples only help once a partner can run the transport experiment.

## 1. Michael Hickner — Michigan State University

Best first contact for a characterized redox-responsive polymer membrane. Hickner is the corresponding author of [Capparelli et al., Anion Exchange Membranes with Dynamic Redox-Responsive Properties (2019), DOI 10.1021/acsami.9b04622](https://pubs.acs.org/doi/10.1021/acsami.9b04622). His [current official MSU profile](https://engineering.msu.edu/directory/faculty/mhickner) lists **mhickner@msu.edu** and research on ion-containing polymers, including flow-battery projects. The article's Penn State email is historical; prefer the current institutional address.

The primary abstract reports reversible viologen-state changes, resistance increases of 40.6–111.6% on reduction, and reduced permselectivity. These are measured resistance/permselectivity changes, not separate active-species permeances or an on/off transport ratio. The accessible supporting-information excerpt identifies 0.5 M NaCl for resistance measurements. Numerical switching voltage and response time were not verified from the accessible evidence. Battery-electrolyte compatibility is therefore not established by this review.

Specific ask: can the group share raw oxidized/reduced transport measurements, the redox-conditioning protocol, and any transient switching traces—or advise whether remaining samples can be characterized with two probe species? In particular, was switching performed electrically in the transport cell or by chemical conditioning? A constitutive model must distinguish those cases. Request membrane thickness, salt composition, reference-electrode convention, oxygen exposure, and cycling history with the data.

## 2. Da Lei / Xiaogang Hao — Qinghai Institute of Salt Lakes, CAS / Taiyuan University of Technology

Closest match to direct voltage-controlled ion transport. Both are corresponding authors of [Song et al., ACS Nano (2026), DOI 10.1021/acsnano.5c20748](https://pubs.acs.org/doi/10.1021/acsnano.5c20748). Public work contacts are **leida@isl.ac.cn**, confirmed by the [official UCAS profile](https://people.ucas.ac.cn/~leida.isl), and **xghao@tyut.edu.cn**, confirmed by the [official Taiyuan faculty page](https://ccet.tyut.edu.cn/info/1705/3891.htm). Treat this as one joint research line, not two independent validations.

The paper reports a conductive carbon-nanotube/Prussian-blue membrane with voltage-controlled K+/Li+ separation and selectivity 481.2. That is evidence of electrically adjustable transport in this material system. It is not a membrane switching ratio, a validated 100-second response time, or a flow-battery result. The accessible abstract does not establish a numerical operating gate voltage or transient response time. The materials and monovalent-ion system differ from both acidic vanadium electrolytes and unspecified A/B species; compatibility must be measured rather than assumed.

Specific ask: can they share separate K+ and Li+ concentration-versus-time traces at each applied potential, electrode/reference geometry, membrane thickness/area, potential-step transients, and gate-current traces? Ask whether a repeatable two-potential switching test is feasible with their existing cell. This directly determines whether useful selectivity changes with gate state and what energy/latency it costs. Begin with their demonstrated chemistry; do not initially ask them to validate an invented battery electrolyte.

## 3. Geoffrey Geise — University of Virginia

Best complementary partner for independent transport characterization and chemistry selection. Geise coauthored the 2019 responsive-AEM study. His [official engineering profile](https://engineering.virginia.edu/faculty/geoff-geise) describes ion-specific transport and nonaqueous redox-flow-battery membranes. The [official UVA directory](https://med.virginia.edu/faculty/faculty-listing/gmg9j/) lists **gmg9j@virginia.edu**; the [research group's contact page](https://geisegroup.github.io/contact/) lists **geise@virginia.edu**.

This is a collaborator from the same 2019 paper, not a third independently demonstrated responsive material. Ask for help choosing a chemically coherent two-species system, identifying existing sorption/diffusion/permselectivity data, and designing measurements that separate conductivity from undesired active-species crossover. Availability of characterized responsive specimens is unconfirmed. His lab's broader battery-membrane expertise does not establish that the 2019 membrane is compatible with a chosen battery electrolyte.

## The concrete collaboration request

Offer an existing open simulation and reproducible analysis workflow. Request one narrow evidence contribution: an existing raw dataset or a paired-state transport experiment that identifies **P_A(gate), P_B(gate), switching latency, and actuation current** under stated conditions. In exchange, provide traceable parameter fitting, uncertainty analysis, and frozen comparisons against static and time-based control. Do not lead with the simulated percentage gain as if it predicts their material.

Minimum useful data package: concentration-time measurements from both reservoirs, reservoir volumes, membrane area/thickness, temperature, electrolyte composition/pH, applied potential and its reference, electrode layout, current-time trace, sampling corrections, and independent repeats. Resistance or permselectivity alone cannot uniquely supply both species' permeances.

Success for the first exchange is permission to analyze a real dataset or agreement on one feasible measurement. A negative result is useful: if response is too slow, selectivity worsens, or conditioning cannot be performed during operation, the software can reject the proposed mechanism before anyone builds a battery.
