# IEEE Big Data 2026 CAMP Artifact

Research artifact for **Online Deployment and Evaluation of Consumption-Aware
Memory Allocation for Scientific Workflows**.

CAMP uses task metadata, prior peak-memory observations, consumption history,
and predicted consumption to choose task memory requests. This repository
supports the Big Data extension's component evidence, auditing-cost analysis,
and online-deployment study. It includes the inherited WORKS implementation and
retained measurements so the analyses do not depend on a separate checkout.

The included reproduction routes cover signal and feature ablations, selective
auditing, audit-cost accounting, Bowtie2 cold/warm execution records, manuscript
tables and figures, and a standalone Ponder memory-sizing adapter.

## Start here

```bash
git clone https://github.com/Nagarjuna-kandimalla/IEEE_BIGDATA_26_CAMP_ARTIFACT.git
cd IEEE_BIGDATA_26_CAMP_ARTIFACT
```

If the repository is private, cloning requires access to the repository.
All commands below start at this root unless explicitly stated otherwise.
Generated environments, model checkpoints, raw FASTQs, container images, and
Nextflow work directories should remain outside the committed artifact.

| Goal | Route | Requires live workflow execution? |
|---|---|---|
| Verify the downloaded snapshot | A: integrity verification | No |
| Regenerate Big Data tables and figures | B: packaged evidence | No |
| Build the manuscript | C: paper build | No |
| Recompute reviewer analyses or refit their models | D: analysis / fresh training | No workflow execution; fresh fitting can be expensive |
| Reproduce the retained Bowtie2 cold/warm deployment | E: live deployment | Yes, Linux and the documented workflow stack |
| Test or use the extracted Ponder predictor | F: standalone baseline | No scheduler needed |

## Directory map

```text
IEEE_BIGDATA_26_CAMP_ARTIFACT/
  README.md                         Big Data entry point (this file)
  DOCS/                             Artifact contents, verification, source provenance
  Big_Data_paper/
    Big_Data_Camera_Ready/source/
      Camera_Ready/                 TeX, bibliography, generated assets
      Original_Submission/          Preserved earlier source
      Figures/                      Inherited shared figures
  SCRIPTS/
    BIGDATA/                        Integrity verification and paper build helpers
    BASELINES/ponder/               Standalone original-code Ponder predictor
    RQ1/ ... RQ5/                   Inherited data, modeling, figure, live-run code
  Reviewer_Feedbacks/
    W1/                             Earlier matched-budget/coverage analysis
    W2/                             Selective auditing and downstream allocation
    W3/                             Read versus read+mmap ablation
    W5/                             Audit-cost accounting
    chat_ablation/                  Four-feature and fixed-route analyses
  DATA/                             Packaged offline cohorts and assignments
  RESULTS/                          Retained WORKS measurements and figures
  WORKFLOWS/                        Bowtie2 and six-workflow integration
  AUDIT/                            eBPF/STRACE collection and processing
  ARTIFACT_MANIFEST.json             Hashes of the packaged release files
```

Keeping the inherited directory names preserves working data paths and
reproduction scripts. An `RQ*` directory is inherited context, not automatically
a new Big Data contribution. Detailed manuscript provenance is recorded in
[RESULTS_PROVENANCE.md](Big_Data_paper/Big_Data_Camera_Ready/source/Camera_Ready/RESULTS_PROVENANCE.md).

## A. Verify the packaged snapshot

Python 3.9+ and its standard library are sufficient:

```bash
python SCRIPTS/BIGDATA/verify_artifact.py --check-gzip
```

This verifies every file listed in `ARTIFACT_MANIFEST.json`, checks packaged gzip
streams, and fails on missing or modified files. Run it before regeneration:
newly generated PDFs/figures may contain different metadata even when their
scientific values agree. The manifest describes the delivered snapshot; do not
replace it to conceal an unexpected change.

## B. Regenerate the Big Data tables and figures

This is the shortest scientific reproduction route. It reads packaged task
predictions, audit selections/timings, and live task/attempt records; it does
not retrain CAMP or execute a workflow.

Use Python 3.10+ for this analysis-only environment:

```bash
python3 -m venv /path/outside/repo/bigdata-analysis-env
/path/outside/repo/bigdata-analysis-env/bin/python -m pip install -r SCRIPTS/BIGDATA/requirements-analysis.txt
/path/outside/repo/bigdata-analysis-env/bin/python Big_Data_paper/Big_Data_Camera_Ready/source/Camera_Ready/build_result_assets.py
```

On Windows, use the environment's `Scripts/python.exe` instead of `bin/python`.
The historical training packages have their own pinned Python 3.9 environments;
do not assume this plotting environment replaces those environments.

Outputs are under `Big_Data_paper/Big_Data_Camera_Ready/source/Camera_Ready/result_assets/`:

- `mmap_table.tex`, `feature_table.tex`, and `bowtie_table.tex` plus their row files;
- `audit_tradeoffs.pdf/.png` and `bowtie_margins.pdf/.png`;
- `result_provenance.json`, with input hashes and computed numerical summaries.

The builder verifies paired task identities, peaks, allocation counts, request
totals, downstream summary consistency, all retained audit-budget/seed costs,
and Bowtie2 task/attempt statistics. It does not imply fresh model fitting.

### Expected evidence and interpretation

| Study | Packaged result / population | Interpretation |
|---|---|---|
| Read versus read+mmap | 32 versus 30 below-peak requests on 5,026 tasks | Separate signal-ablation experiment |
| Four feature views | Native configurations: 85 / 46 / 52 / 30 | Native rows differ in routing; use fixed-route tables for feature interpretation |
| Published WORKS endpoints | 87 versus 31 | Frozen published result, distinct from the later reproduction |
| Selective downstream auditing | At 20%: mean 265.8 versus 305.8 events, with 2.4% more requests | Replay; retained uncertainty interval includes zero |
| Audit accounting | Fixed gross saving 23.59556 GiB-h; mean net +17.597 / +11.161 / +5.913 / -0.429 at 5/10/15/20% budgets | Fixed-saving accounting; excludes full learning/inference/retry cost |
| Bowtie2 cold/warm | 6,000 tasks each; requests 898.3857 versus 251.9268 GiB | Cold/warm executions on repeated inputs |

Underallocation is a request below recorded peak, not an observed OOM.
Recorded first-attempt OOM flags for the retained Bowtie2 runs are zero.
Summed requests are not simultaneous node occupancy. Missing-runtime conventions
and failure-cost exclusions are documented in manuscript provenance.

## C. Build the paper

The manuscript source is
[Camera_Ready/main.tex](Big_Data_paper/Big_Data_Camera_Ready/source/Camera_Ready/main.tex).
The compiled [PDF](Big_Data_paper/Big_Data_Camera_Ready/source/Camera_Ready/CAMERA_READY_PREVIEW.pdf)
is included alongside the source.

With an existing TeX installation, use the isolated build helper:

```bash
python SCRIPTS/BIGDATA/build_paper.py --engine latexmk
```

Alternatively, with Tectonic 0.17 available:

```bash
python SCRIPTS/BIGDATA/build_paper.py --engine tectonic
```

Both build in ignored `build/paper/` and produce `build/paper/camp_bigdata.pdf`.
The helper copies the original project layout and leaves the manuscript source
untouched. The Tectonic route uses a T1-font wrapper to match the verified preview.
Tectonic may download TeX resources on first use. `--executable` can select an
explicit compiler path. For Overleaf, upload the contents of
`Big_Data_paper/Big_Data_Camera_Ready/` and choose
`source/Camera_Ready/main.tex` as the main file.

## D. Recompute analyses or train fresh models

Choose the relevant package; each has local data, retained references, and
separate instructions distinguishing analysis from fresh fitting:

| Evidence | Instructions | Fresh-training entry point |
|---|---|---|
| mmap contribution | [W3](Reviewer_Feedbacks/W3/README.md) | `fresh_training.py NEW_DIRECTORY --threads 8` |
| Four feature variants | [chat_ablation](Reviewer_Feedbacks/chat_ablation/README.md) | Follow its `run_full_ablation.sh` section |
| Downstream selective auditing | [W2](Reviewer_Feedbacks/W2/README.md) | `fresh_training.py NEW_DIRECTORY --workers 2 --threads 8` |
| Audit-cost accounting | [W5](Reviewer_Feedbacks/W5/README.md) | Analysis only; no model training required |
| Earlier matched-budget comparison | [W1](Reviewer_Feedbacks/W1/README.md) | Follow its package instructions |

For example, on Linux with Python 3.9 and the documented LightGBM prerequisites:

```bash
cd Reviewer_Feedbacks/W3
bash setup.sh
bash reproduce.sh
```

Its standard reproduction recomputes from retained predictions. A genuinely
fresh fit is a separate command from that directory:

```bash
.venv/bin/python fresh_training.py /path/outside/repo/new-w3-run --threads 8
```

Fresh destinations must not already exist. Numerical variation across hardware
must be evaluated, not replaced with frozen counts. Retained package verification
logs describe earlier verification; [this repository's verification record](DOCS/VERIFICATION.md)
states what was actually executed during this packaging pass.

## E. Retained live Bowtie2 cold/warm deployment

Follow [SCRIPTS/RQ5/README.md](SCRIPTS/RQ5/README.md) from its full-run entry point.
It describes initial-state rebuilding, causal online feedback, source inputs,
execution, artifact collection, and plotting. The original run used 12 task
workers plus one controller/learner worker. The inherited launch defaults describe
that deployment; they are not ready-made single-node AWS defaults.

The Bowtie2 workflow and chunk mapping come from the WORKS source revision
recorded in [source provenance](DOCS/SOURCE_MANIFEST.json).

Raw sequence data and deployable terminal model checkpoints are not bundled.
Public-input acquisition and initial-state rebuild instructions are included.
The retained CSVs cannot substitute for an actual trained checkpoint.

## F. Ponder memory-sizing adapter

[SCRIPTS/BASELINES/ponder](SCRIPTS/BASELINES/ponder/README.md) compiles nine unchanged
upstream Java predictor files pinned to commit `3046e19`. Python's standard library
launches the adapter; an existing JDK 11+ is required. No Kubernetes installation
is needed. Dependency downloads are version- and checksum-pinned.

```bash
python SCRIPTS/BASELINES/ponder/ponder.py test
python SCRIPTS/BASELINES/ponder/ponder.py run --events events.tsv --output ponder_predictions.tsv
```

The test suite contains 123 checks, including 48 exact comparisons with direct
original-core predictions. This verifies the adapter on synthetic histories;
it is not a CAMP/Ponder performance result. The README specifies the event schema,
causal ordering, source-history seeding, defaults, caps, and failure handling.

The chosen configuration keeps Ponder's internal offset and omits the additional
outer offset (`ponder-offset=none`). Bare upstream `ponder` has an additional
default offset wrapper. State this choice in any comparison; do not claim an
exact reproduction of the original scheduler experiments.

## Provenance and licensing

This artifact derives from [IEEE_WORKS_26_ARTIFACT](https://github.com/Nagarjuna-kandimalla/IEEE_WORKS_26_ARTIFACT).
The source commit, copied-file hashes, exclusions, and workflow choice are in
[DOCS/SOURCE_MANIFEST.json](DOCS/SOURCE_MANIFEST.json).
Duplicate ZIP exports, local caches, `Not_Needed/`, and the acceptance-email PDF
were excluded. Manuscripts, scientific documentation, review-response material,
and reproduction packages are included. See the [contents guide](DOCS/CONTENTS.md).

Preserve citations to WORKS for reused methods/results and identify new
experiments separately. No DOI or final publication metadata has been invented.
Ponder's copied code and adapter carry GPL-3.0-or-later with notices and source.
Other third-party files retain their existing notices. No new blanket license
is imposed on CAMP; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
