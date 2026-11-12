# RQ5 live experiments: complete records and reproduction

This guide describes the completed Warm-Transfer and Direct-Transfer studies and the portable
code, data manifests, model bundles and results needed to inspect or repeat them.
Run commands from the **IEEE_BIGDATA_26_CAMP_ARTIFACT repository root**.
No command below pushes to Git, provisions cloud machines, or deletes existing runs.

## 1. What was actually executed

| Experiment | Sequence | Starting state | Paper role |
|---|---|---|---|
| Warm-Transfer | fresh original cold → original warm → new input | Offline seed with no Bowtie2 history | Main live result |
| Direct-Transfer | **reuse the exact Warm-Transfer terminal cold checkpoint → new input** | Warm-Transfer cold model, history and calibration | Extra-warm-pass ablation |

Direct-Transfer did **not** rerun cold. It did not inherit Warm-Transfer's warm or new-input model.
The two new-input arms share the Warm-Transfer cold ancestor; Warm-Transfer additionally executes
the original-data warm pass. Every stage has **6,000 logical tasks**, seven
process types and **1,974** BAM/BAI/flagstat sets. All tasks were audited.

Both new-input arms continue **online training**. These are neither frozen-model
inference benchmarks nor selective-auditing live trials. Selective auditing is
studied in the separate retained replay. Offline fitting is not repeated for
every experiment: a fresh cold run resets to the same offline-trained bundle.

### Model and learning contract

- Offline seed: `fresh-paper-initial-20260804-v1`, seed 1996; **28,490** training
  and history observations from six other workflows, **zero Bowtie2 observations**.
- Seed package includes global/quantile ensembles, process-tail models, consumed
  data proxy, preprocessing/scaling objects, cold-start models and policies,
  base training frame, feature history and matching SQLite database.
- Direct A+P+C allocation, process-to-global fallback, hierarchical residual
  calibration, and the prelaunch information boundary are preserved.
- First update after 128 eligible successful outcomes, then at 128-observation
  thresholds, with asynchronous fitting. The newest 64 observations are held
  out for model-version-matched calibration. A final fit consumes the remaining
  eligible outcomes before the stage is validated.
- Measured consumption is available only after execution. The pending task uses
  predicted consumption. Failed attempts remain diagnostic records rather than
  successful training rows. Every observation actually used is preserved.
- Both studies have zero duplicate successful observations.

| Checkpoint bundle | Successful stage observations | Bowtie2 rows in matching history |
|---|---:|---:|
| `initial` | 0 | 0 |
| `warm_transfer_cold` | 6,000 | 6,000 |
| `warm_transfer_warm` | 6,000 | 12,000 |
| `warm_transfer_new_input` | 6,000 | 18,000 |
| `direct_transfer_new_input` | 6,000 | 12,000 |

`direct_transfer_cold` is an alias of `warm_transfer_cold`, not another independently trained checkpoint.
A continuation needs **model + exact matching feature history + SQLite history +
base training frame**, not just `current_model.json` or one joblib file.

## 2. Repository map

| Location | Contents |
|---|---|
| `SCRIPTS/RQ5/live/` | Portable configuration, Slurm submission, data fetching, restoration and result recomputation |
| `SCRIPTS/RQ5/live/runtime/` | Controller, routing, validated handoff, verified archive, health monitor, BPF tracer and isolation launcher |
| `SCRIPTS/RQ5/experiment_template/` | Exact scientific implementation used in the clean runs: model fitting, allocation, history, calibration and wrappers |
| `WORKFLOWS/bowtie2/`, `WORKFLOWS/common/` | Workflow and normalization/static-manifest code |
| `DATA/RQ5/live/inputs/` | Original/new task manifests, ENA metadata and new-study selection record |
| `DATA/RQ5/live/models/` | Losslessly compressed, deduplicated initial/terminal model-history bundles **and exact SIF containers**, with per-file hashes |
| `RESULTS/RQ5/live_experiments/` | All four stage tables, attempts, decisions, outcomes, learning events, traces, flagstat summaries, validation and archive inventories, comparisons and historical provenance |
| `RESULTS/RQ5/transfer_studies/` | Compact paper-specific copies consumed by the camera-ready asset generator |

Historical paths such as `/shared/ubuntu/...` in the archived records describe
the original execution. They are not dependencies of the portable runner.
Runtime workspace paths and node names are configured explicitly below.

Model files use a SHA256-addressed gzip blob store. Identical weights/history
files across snapshots are stored once. Files exceeding 24 MiB compressed are
split into verified parts, avoiding oversized Git objects without requiring Git
LFS or an external model server. `models.py extract` verifies and reconstructs
every original file, rebases only the handoff's operational paths, and preserves
`handoff.original.json`. Scientific weights and history bytes are unchanged.
Only load trusted joblib/pickle models; checksums verify integrity, not trust.

## 3. Results and limits

All four stages completed and passed task/audit coverage, BAM quickcheck and
model/history/calibration validation. Values below use the original RQ5 logical-
task definition: first CAMP request and final successful peak/runtime.

| Stage | Requests (GiB) | Peak sum (GiB) | Unused (GiB-h) | Coverage (%) | MdAPE (%) |
|---|---:|---:|---:|---:|---:|
| Warm-Transfer cold | 977.79 | 229.33 | 32.86089 | 99.53 | 1.66 |
| Warm-Transfer warm | 241.12 | 229.38 | 0.01847 | 99.58 | 1.13 |
| Warm-Transfer new input | 319.22 | 273.44 | 0.12805 | 94.15 | 4.73 |
| Direct-Transfer new input | 343.56 | 277.96 | 0.22109 | 95.78 | 2.69 |

For each task, unused memory-time is
`max(first_CAMP_request_MiB - final_peak_MiB, 0) * final_runtime_seconds / 3600 / 1024`.
Requests and peaks are summed across tasks, **not simultaneous cluster usage**.
MdAPE concerns the median peak prediction, not the rounded/calibrated request.

A separate **128 MiB per-task execution allowance** was used throughout both studies. It is excluded from requests, coverage and unused
memory-time above. These metrics exclude failed-attempt, audit, inference and
retraining costs and are not cloud-cost or end-to-end saving estimates.
All retained stages record zero OOMs. Zero OOMs under the allowance does not prove nominal request sufficiency.

Warm-Transfer warm reduces requests by 75.34% relative to cold. On new inputs, skipping
its warm pass in Direct-Transfer increases requests by 7.62% and unused memory by 72.65%,
while coverage rises to 95.78%. This is a tradeoff, not universal superiority.

All 1,974 Warm-Transfer/Direct-Transfer new-input flagstat summaries match
exactly. This checks summary agreement, not byte identity of the BAM files.

Only one clean execution per arm and one new study are evaluated. Completion
order affects online updates, and measured memory, consumption and timing vary.
No bitwise/numerical equality, statistical significance, or paper-number match is
promised for a fresh run. Original retained `RESULTS/RQ5/csv/` belongs to an older
cold/warm deployment and remains separate from these new records.

## 4. Fast route: verify and regenerate numbers (no Slurm)

Python 3.9+ standard library is enough for result recomputation and model-store
verification; no model is loaded by these commands.

```bash
python3 SCRIPTS/RQ5/live/reproduce_results.py --output build/rq5-live-results
python3 SCRIPTS/RQ5/live/models.py list
python3 SCRIPTS/RQ5/live/models.py verify --deep
```

The first command checks 6,000 successful unique tasks per stage, recomputes
requests/peaks/unused memory/coverage and point-prediction MdAPE, and compares
flagstat files. Outputs are `results.json` and `metrics.tsv`; reference output is
under `RESULTS/RQ5/live_experiments/recomputed/`.
The deep model check verifies compressed parts **and decoded original bytes**.

To regenerate the manuscript tables/figure, install the analysis dependencies:

```bash
python3.9 -m venv /tmp/camp-rq5-analysis
/tmp/camp-rq5-analysis/bin/pip install -r SCRIPTS/RQ5/requirements.txt
/tmp/camp-rq5-analysis/bin/python \
  Big_Data_paper/Big_Data_Camera_Ready/source/Camera_Ready/build_live_assets.py
```

## 5. Inspect or continue from a recorded checkpoint

Use external storage for restored models and mutable databases:

```bash
python3 SCRIPTS/RQ5/live/models.py extract initial /shared/camp/seed
python3 SCRIPTS/RQ5/live/models.py extract warm_transfer_cold /shared/camp/warm-transfer-cold
python3 SCRIPTS/RQ5/live/models.py extract direct_transfer_new_input /shared/camp/direct-transfer-terminal
```

Destinations must not already exist. `initial` restores the full `artifacts/`
layout, including `workflow_cold/` and policies. A terminal bundle restores
`model/`, matching history TSV/database, learner-state database, and rebased
`handoff.json`. It is a seed for a **fresh next stage**, not permission to reset
retry counters or blindly resume a historical partially completed stage.

Validate a restored cold checkpoint with the pinned environment:

```bash
/shared/camp/python39/bin/python \
  SCRIPTS/RQ5/experiment_template/camp/live_online_learning/scripts/preflight_run_inputs.py \
  --workflow bowtie2 --model-root /shared/camp/warm-transfer-cold/model \
  --history-features /shared/camp/warm-transfer-cold/history_features.tsv \
  --history-db /shared/camp/warm-transfer-cold/history.sqlite3 \
  --base-training-frame /shared/camp/warm-transfer-cold/model/base_training_frame.tsv \
  --expected-workflow-rows 6000
```

Expected: PASS, 6,000 Bowtie2 history/training/SQLite rows and 64 calibration
rows matching the cold checkpoint’s recorded model version. Other snapshot counts are in §1.

## 6. Data and exact tool images

- Original study: **PRJEB11501**, 38 paired runs, 15.14 GiB compressed FASTQ.
- New study: **PRJNA486148**, 38 paired runs, 15.20 GiB; 34 runs at 75 bases and
  four at 102 bases, versus original 102-base reads.
- Manifests include exact URLs, compressed byte sizes and per-run chunk counts.
  ENA metadata supplies per-file MD5 and sample IDs; selection uses metadata,
  not task outcomes. The two studies have no selected identity/MD5 overlap.
- The reference URL is pinned to Ensembl release 116 in the launch script.
  `DATA/RQ5/live/inputs/reference/` also contains the exact decompressed FASTA
  as a lossless gzip snapshot, its FAI, and original-sequence SHA256. The live
  DOWNLOAD_REFERENCE command still uses the pinned URL, preserving its behavior.
- Exact Apptainer SIF images are included in the `containers` model-store bundle:
  Bowtie2 2.4.2 and samtools 1.20. Their original SHA256 values are verified on
  extraction and before stage launch. No mutable container tag is needed.

The Git checkout contains metadata and scientific records, **not ~30 GiB of raw
FASTQ or hundreds of GiB of BAM/work files**. Those large input bytes are publicly
retrievable and verified by MD5. Use the following optional prefetch/verification
commands (the workflow otherwise downloads the exact URLs itself):

```bash
python3 SCRIPTS/RQ5/live/fetch_inputs.py --dataset original --output /shared/fastq/original
python3 SCRIPTS/RQ5/live/fetch_inputs.py --dataset new --output /shared/fastq/new
python3 SCRIPTS/RQ5/live/fetch_inputs.py --dataset new --output /shared/fastq/new --verify-only
```

The fetcher accepts `--limit 1` for a one-pair network test. It never promotes a
partial or MD5-mismatched file as a validated FASTQ. Prefetching does not silently
replace live DOWNLOAD_RUN commands with local copies, which would change their
measured execution. ENA availability is an external prerequisite.

Original large payloads were byte-compared and SHA256-verified into archives on
the original persistent worker disks. Their inventories, hashes, original node
locations and restore commands are packaged as provenance. Those site-local
archives are **not presented as publicly hosted downloads**. Re-execution creates
new BAMs. The complete scientific task tables/attempts/outcomes/decisions,
terminal histories/models and all flagstats are in this checkout.

## 7. Full Slurm route: repeat Warm-Transfer and shared-cold Direct-Transfer

### Prerequisites and capacity

Use shared storage mounted at the same absolute paths on head and workers.
Install Linux x86-64, Slurm (original 23.11.4), Java 21, Nextflow **25.10.7**,
Apptainer (original 1.5.5), GNU wget with `--retry-on-http-error`, `gzip`, GNU tar,
`rg`, `setfacl`, and `/usr/bin/time`. Workers need system Python with BCC,
matching kernel headers and passwordless sudo for the audit launcher. See
`AUDIT/README.md`. Model fitting uses pinned Python 3.9 dependencies:

```bash
python3.9 -m venv /shared/camp/python39
/shared/camp/python39/bin/pip install -r SCRIPTS/RQ5/requirements.txt
```

Keep this environment at one path visible on every node. Do not load checkpoint
joblibs under an arbitrary sklearn/LightGBM version.

The recorded Warm-Transfer cluster had a 16-vCPU/64-GiB main node and three
16-vCPU/64-GiB workers, with 50 GiB admitted per worker to Slurm. Controller:
8 CPUs/8 GiB; learner: 4 CPUs/16 GiB; monitor: 1 CPU/256 MiB. The recorded Direct-Transfer
main node was downsized to 8 vCPU/32 GiB, with controller 2 CPUs/4 GiB and the
same learner and workers. Maintain headroom for OS/NFS and **16 × 384 MiB**
separately isolated auditors per worker. Auditors are not inside task grants.

The portable default example matches Warm-Transfer reservations and needs at least
13 schedulable main-node CPUs and 24.25 GiB Slurm memory. The saved-cold route
below uses Direct-Transfer reservations (7 CPUs and 20.25 GiB in aggregate).
The example is a topology description, not a cloud provisioning script.
For a full clean repeat on an 8-vCPU/32-GiB main node, explicitly set
`controller_cpus` to 2 and `controller_memory` to `4G`; retain learner 4 CPUs/16G.
This is a new hardware realization, not the original Warm-Transfer controller allocation.

Allow at least 58 GiB free shared scratch before each stage. With verified
archiving between stages, only the current ~50–60 GiB task payload stays on
shared scratch, plus histories/models/logs. Existing worker-local archive disks
need room for assigned stage archives plus an 8-GiB reserve. Without archiving,
plan roughly 300 GiB or more shared free storage for the four-stage repeat;
task failures and logs can add more. Do not delete persistent archive disks.

### Configure your cluster

```bash
cp SCRIPTS/RQ5/live/config/cluster.example.json /shared/camp/cluster.json
# Edit node names, partition names, Python/Nextflow paths and archive location.
python3 SCRIPTS/RQ5/live/configure.py \
  --root /shared/camp/repeat-01 --config /shared/camp/cluster.json
```

The root must not exist. Configuration restores the exact offline seed and SIFs,
copies the scientific source/workflow, creates a frozen checksum manifest, and
writes `experiments/plan.json`. It does **not** submit jobs or overwrite results.

Crucially, `task_partition` controls **both submission and Nextflow monitoring**.
`controller_partition` hosts only control/learning. A mismatch previously caused
long tasks to be falsely declared lost despite Slurm completing them.
Node names in `workers` must be the actual Slurm/host names, not node ranges.
`archive_directory` is a persistent local path on each selected worker. Set
`archive_between_stages` to false only if shared disk capacity is sufficient.

Configure keeps the scientific system-context encoding used during training
(13 workers, 32 vCPU, 244.14 GiB), even though physical hardware differs; changing
those feature values is a different scientific configuration. The original
per-task execution allowance stays **128 MiB**, not an extra model feature.
The isolated auditor cap is 384 MiB and task admission is at most 16 per worker.

### Submit and monitor

```bash
python3 SCRIPTS/RQ5/live/submit.py --root /shared/camp/repeat-01
cat /shared/camp/repeat-01/experiments/jobs.json
cat /shared/camp/repeat-01/experiments/status.json
squeue -u "$USER"
```

This submits one sequential chain:

1. Warm-Transfer cold from the restored zero-Bowtie2 offline seed.
2. Validate coverage, audit outcomes, BAMs and exact model/history projection;
   archive/verify payloads, then remove only verified staging bytes.
3. Warm-Transfer original-data warm from that cold checkpoint; validate/archive.
4. Warm-Transfer new input from that warm checkpoint; validate/archive.
5. Direct-Transfer same new input **from step 1's cold checkpoint**, not step 4; validate/archive.
6. Generate `experiments/comparison/reproduction-results.json` and stop monitoring.

The controller uses the pinned environment; all actual task submissions go through
an explicitly scoped portable router. Predictions and actual grants are recorded
separately. A health job may resume a stopped child only after matching the audit
readiness PID and Slurm cgroup. It never resumes an unaudited task by timeout.
Every task has up to three retries. Wget also has ten internal network attempts,
including retryable HTTP errors; those are not extra Nextflow task attempts.
Unrecoverable failures block validated downstream handoffs and write failure logs.
No completion or equality is fabricated, and no failed experiment is skipped.

`submit.py` refuses duplicate submission. It checks head CPU/memory capacity first.
Do not alter scientific source/configuration during a running chain. Logs,
controllers, immutable decisions/outcomes and validated checkpoints are external
to the checkout. The runner does not change Slurm configuration or EC2 instances.
Runtime and asynchronous model trajectories can differ on a smaller main node.
Use the same hardware for a more controlled comparison than the original downsized arm.

### Repeat only the exact recorded shared-cold branch

To run Direct-Transfer from the packaged Warm-Transfer cold checkpoint without repeating Warm-Transfer:

```bash
python3 SCRIPTS/RQ5/live/configure.py \
  --root /shared/camp/direct-cold-01 --config /shared/camp/cluster.json --saved-cold
python3 SCRIPTS/RQ5/live/submit.py --root /shared/camp/direct-cold-01
```

This restores recorded `warm_transfer_cold`, uses its rebased handoff and 6,000 Bowtie2 rows,
and schedules only new input → validation → archive → report. It automatically
uses the recorded Direct-Transfer controller reservation (2 CPUs/4 GiB).


## 8. Optional: rebuild the offline state from source

The source datasets and fixed split are already under `DATA/RQ2/` and `DATA/RQ5/`.
Use another fresh workspace rather than overwriting the packaged seed:

```bash
python3 SCRIPTS/RQ5/prepare_workspace.py \
  --artifact-root "$(pwd -P)" --work-root /shared/camp/offline-rebuild
RQ5_PYTHON=/shared/camp/python39/bin/python \
  bash SCRIPTS/RQ5/build_initial_state.sh /shared/camp/offline-rebuild/fresh_experiment 4
python3 SCRIPTS/RQ5/live/configure.py \
  --root /shared/camp/rebuilt-repeat \
  --config /shared/camp/cluster.json \
  --initial-state /shared/camp/offline-rebuild/fresh_experiment/artifacts
```

Run the build in an appropriate Slurm allocation, not an under-sized login shell;
the original build used a larger allocated node. See the legacy guide's build
resources and `slurm_build_initial_state.sh`. The build trains the offline
quantile/proxy/policy bundle and zero-Bowtie2 history. Configure itself never
re-trains offline models. Rebuilding and live repeating verify procedures;
the archived exact bundle is the source of the reported numerical realizations.

## 9. Checks and known operational issues

Reusable local integration checks (requires the pinned model environment):

```bash
python3 -m unittest discover -s SCRIPTS/RQ5/live/tests -v
/shared/camp/python39/bin/python SCRIPTS/RQ5/live/selfcheck.py
/shared/camp/python39/bin/python SCRIPTS/RQ5/live/predict_smoke.py \
  --checkpoint /shared/camp/warm-transfer-cold --initial /shared/camp/seed
```

`selfcheck.py` deep-verifies the store, recomputes archived results, restores
models into new paths, checks seed/terminal preflight, builds a workspace with
spaces, and substitutes stub Slurm commands to test gates and duplicate-submit
refusal. It does not launch biological tasks. `predict_smoke.py` loads the restored
joblibs and makes three unseen-instance predictions without changing training.



- Read `RESULTS/RQ5/live_experiments/reproduction-validation.json` for the packaging
  checks actually executed. A portable configuration and simulated scheduler test
  do not constitute another full biological rerun.
- Check dataset task coverage, nonempty peak/consumption observations, all 1,974
  BAMs with `samtools quickcheck`, exact history IDs, calibration/version and
  expected Bowtie2 row counts before warm continuation. MD5 checks protect inputs.
- The copied cold checkpoint checksum list originally included ephemeral SQLite
  WAL/SHM sidecars. Bundles exclude sidecars and store committed matching database
  bytes. Their checksum and SQLite integrity/model-history preflight are checked.
- For NFS root-squash, the audit directory needs the configured anonymous UID ACL;
  `nfs_audit_uid` defaults to 65534. Validate local user/UID and export permissions.
- The supplied BCC launcher enables raw-openat attribution and header compatibility
  flags for the original kernel environment. Validate known-file attribution on
  another kernel before claiming measured consumption equivalence. Do not suppress
  a failed BCC import/readiness check.
- Nextflow cache must not cross scientific stages. An interrupted same-stage resume
  needs cumulative attempt bookkeeping and exact learner state; do not just rerun
  a fresh-stage command over an old directory. Historical recovery code and records
  are provided for provenance, not as a universal automatic recovery policy.
- Do not infer read-count completeness from BAM structural validity alone. Compare
  flagstat read totals and inputs, when verifying a new execution.
- Live inference/retraining completes asynchronously; a frozen seed does not freeze
  the running learner. Never label this study a frozen-versus-online comparison.

The paper uses the Warm-Transfer and Direct-Transfer studies.

## Naming and provenance policy

Warm-Transfer (`warm_transfer`) and Direct-Transfer (`direct_transfer`) are the
public study names. Filenames, bundle keys, result keys, commands and generated
run labels use these names. The direct cold checkpoint is an alias, not another
execution. Recorded internal model versions, observation IDs and original
identifiers embedded in task records or compressed model/history files are
immutable provenance; they are not rewritten just to change presentation.
Exploratory run records and checkpoints are outside the Git publication package.
