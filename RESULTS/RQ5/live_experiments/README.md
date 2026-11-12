# Warm-Transfer and Direct-Transfer results

See [the complete reproduction guide](../../../SCRIPTS/RQ5/LIVE_EXPERIMENTS.md).

Four recorded stages are included: `warm_transfer_cold`, `warm_transfer_warm`,
`warm_transfer_new_input`, and `direct_transfer_new_input`. Each contains 6,000
successful tasks, full attempt tables, decisions/outcomes, learning events,
execution/audit traces, all 1,974 flagstats, and validated model metadata.
Direct-Transfer starts from the exact Warm-Transfer cold checkpoint; cold is not rerun.

`studies.json` defines lineage. `recomputed/` contains reference metrics, generated
by `SCRIPTS/RQ5/live/reproduce_results.py`. `reproduction-validation.json` records
restoration, integrity and simulated orchestration checks; these do not constitute
another complete biological execution. Models/containers are under `DATA/RQ5/live/`.

Public filenames and study labels use descriptive names. Original run/model IDs
inside scientific records remain immutable for traceability to fitted weights.
Large raw FASTQs are fetched from ENA with MD5 verification; BAMs are regenerated.
Exploratory runs and their site-specific recovery history are not published here.
