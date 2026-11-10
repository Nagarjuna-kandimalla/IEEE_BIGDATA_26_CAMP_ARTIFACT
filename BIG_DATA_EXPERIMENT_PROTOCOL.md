# Big Data extension: remaining experiment protocols

Updated: 2026-11-10. Status: proposed experiments; no new results are claimed here.

This document describes the experiments to perform and the evidence to save for the six-page Big Data paper. It intentionally excludes AWS provisioning, software installation, environment configuration, and launch commands. The experiments can be evaluated on one node; this is a new deployment condition, not a reproduction of the original 13-node deployment.

## 1. Scope and execution order

1. **First: unseen-input Bowtie2 deployment.** Compare frozen CAMP with fully online CAMP, beginning from independent copies of the same previously learned state.
2. **Next, when external comparisons resume: CAMP versus NGBoost.** Start with an offline, matched-data comparison of allocation safety and reservation cost.
3. **Optional: CAMP versus Ponder.** Compare causal adaptive allocation in a common replay; extend to live execution only if feasible.

The standalone simple memory-history/percentile allocator remains removed from scope, as recorded in the current extension plan. Q-learning, additional routing/calibration/history-scope sweeps, and additional feature ablations are outside this experiment plan. Existing mmap, feature, and auditing results remain supporting evidence in the paper.

**Paper story:** We evaluate how CAMP transfers to unseen workflow inputs and adapts during execution, and whether its allocation decisions offer a useful safety–cost tradeoff against probabilistic and adaptive alternatives.

## 2. What is already available, and what is new

| Evidence | Available now | What it establishes |
|---|---|---|
| Retained Bowtie2 cold/warm executions | Two executions, each with 6,000 logical tasks from the same 38 paired input runs | Improvement after accumulating experience on repeated inputs |
| Retained Bowtie2 requested-memory totals | Cold: 898.3857 GiB; warm: 251.9268 GiB, approximately 71.96% lower | Sum of per-task requests, not simultaneously occupied node memory |
| Retained Bowtie2 below-peak initial requests | 4 cold and 13 warm; recorded first-attempt OOM flags are zero in both | Peak-based coverage and observed OOM are different measurements |
| Frozen versus online CAMP on disjoint inputs | Pending | Transfer to unseen inputs and the additional effect of online adaptation |
| NGBoost / Ponder comparison results | Pending | External comparative evidence once the prescribed experiment is performed |

The original manifest contains `online_unseen` in its filename because those inputs were initially unseen by the cold model. Its warm run repeats those inputs. That filename does not establish a new unseen-input test relative to the warm checkpoint.

Retained sources: [RQ5 results](RESULTS/RQ5/README.md), [workflow description](WORKFLOWS/bowtie2/README.md), and [current manuscript provenance](Big_Data_paper/Big_Data_Camera_Ready/source/Camera_Ready/RESULTS_PROVENANCE.md).

## 3. Experiment 1: Bowtie2 on previously unseen inputs

### 3.1 Question and comparison arms

**Question:** Starting with the same prior experience, does updating CAMP during execution improve memory allocation on previously unseen Bowtie2 inputs compared with keeping CAMP's state fixed?

| Property | Frozen CAMP | Online CAMP |
|---|---|---|
| Initial model, history, calibration, and allocation policy | Identical checkpoint | Identical checkpoint |
| New input manifest and workflow | Identical | Identical |
| Model fitting after the experiment starts | Disabled | Enabled |
| New outcomes entering prediction-time history | Disabled | Enabled after completion and ingestion |
| Residual/calibration updates | Disabled | Enabled under the existing policy |
| Recording outcomes for evaluation | Enabled | Enabled |
| Auditing | Same full-audit policy | Same full-audit policy |
| Retry policy and task CPU assignments | Identical | Identical |

Frozen means **model + history + calibration + policy remain fixed**. Disabling retraining while allowing new memory/consumption histories or residual updates is not this control.

This experiment measures the combined benefit of the online mechanisms. It does not separately attribute improvement to retraining, history, or calibration; that would require additional arms outside the present scope.

### 3.2 Choose the source state before choosing results

Use a checkpoint learned from an earlier, disjoint Bowtie2 source workload. Record its model version, training membership, history membership, calibration state, and configuration. Save fingerprints of all components before making independent copies for the two arms.

Prefer a source checkpoint collected under the same single-node conditions as the new test. This makes input transfer the main change. If using a checkpoint from the original cluster, report that both input and deployment conditions changed. Record the real system metadata; do not relabel old training records to manufacture matching history.

The retained CSVs are measurements, not trained model checkpoints. If the earlier terminal state is unavailable, establish a new source checkpoint on the source inputs first. If instead starting with the non-Bowtie seed model, describe the experiment as cold adaptation to Bowtie2, not transfer from prior Bowtie2 experience.

Never initialize one arm from the other arm's completed test run.

### 3.3 Define genuinely unseen inputs

1. Select new paired-end input samples compatible with the chosen organism, reference, and Bowtie2 workflow.
2. Check run accessions, sample identifiers, and file checksums against the source workload and all checkpoint training/history records. Renaming or re-splitting old reads does not make new inputs.
3. Prefer a disjoint set from the same organism/protocol for the primary experiment. A different study can strengthen the transfer test, but describe any protocol differences.
4. Keep the reference, alignment options, workflow stages, and software versions fixed between arms. A new organism/reference would introduce another experimental factor.
5. Freeze a manifest containing accession, sample identifier, source study, paired file identifiers/checksums, input sizes, and chunk assignments before the final evaluation.
6. Summarize source-versus-test input sizes and sample counts. Call the test a distribution shift only if the measured differences support that description; disjoint samples alone establish unseen-input evaluation.

**Example design, not a selected dataset:** source state from samples A; separate pilot samples B; final evaluation on disjoint samples C. Both arms process exactly C. No result from C is used to select hyperparameters or decide which samples to keep.

Use multiple independent samples rather than creating many shards from one sample. The original 6,000 tasks include preparation, splitting, alignment, indexing, and flagstat; task count is not biological sample count.

### 3.4 Size the experiment around observable adaptation

Choose the sample/chunk count using a separate pilot, before inspecting final-test outcomes. The final run should contain enough eligible completions and remaining tasks to observe several model updates. The existing launcher requests the first update after 128 completions and subsequent updates every 128 completions, with process support 16 and calibration window 64. Preserve these settings unless the pilot justifies a documented change made before the final test.

Having 256 tasks does not guarantee two useful updates: the learner must finish and publish an update while later task decisions still remain. Save actual activation times and count decisions made under each model version. If every decision uses the initial model, the run has not demonstrated model adaptation.

### 3.5 Sequential procedure

1. **Freeze the protocol.** Record dataset membership, source checkpoint, update policy, audit policy, task resource settings, retry rules, planned repetitions, and metrics.
2. **Validate on separate pilot inputs.** Confirm that frozen state does not change and that online outcomes affect only later decisions. Exclude pilot samples from the final dataset.
3. **Reset to the common source checkpoint.** Give each arm an independent copy of all state. Do this before every repetition, including repeated online runs.
4. **Run the first arm on the final manifest.** Execute all workflow tasks afresh. Save decisions, outcomes, attempts, update events, and whole-workflow timing.
5. **Run the other arm on the identical manifest.** Use fresh workflow outputs and the original source checkpoint, not the first arm's updated state.
6. **Repeat if feasible.** Target three paired repetitions, alternating arm order. One pair is a pilot-scale result and does not establish repeatability.
7. **Analyze the entire predefined cohort.** Report unsuccessful and missing tasks as well as successful tasks. Do not retain only the tasks for which online CAMP improved.

Run the arms sequentially on the single node. Keep the workload CPU limits and memory budget comparable. For the primary adaptation comparison, reserve the same controller/learner resource allowance in both arms; it may be idle in the frozen arm. Measure online learning costs separately. Releasing that allowance only for frozen CAMP changes the system comparison and must be identified explicitly.

Use the same input-staging and cache policy for each arm. Fresh Nextflow execution prevents task-result reuse but does not reset operating-system or container caches. Record the policy and alternate order to reduce order effects. If makespan includes downloads, disclose that network variation is included; do not stage inputs in only one arm.

### 3.6 Information allowed at each decision

At decision time, online CAMP may use only outcomes already completed **and ingested**. It may not use current-task peak RSS, current-task measured consumption, later task outcomes, or a model trained on those outcomes. A concurrently running task is not completed history.

Save a decision timestamp, model/calibration version, and last ingested history sequence for each allocation. Record completion and ingestion timestamps separately. These establish that the experiment is causal even when tasks execute concurrently.

Keep hardware/context values truthful. A missing compatible history group should trigger the documented fallback, not an artificial match to old cluster records.

### 3.7 Measurements to save

| Record | Required fields |
|---|---|
| Experiment identity | Arm, repetition, dataset hash, checkpoint hashes, configuration/seed identifiers |
| Logical task | Stable identity shared across arms: process, sample/run, chunk, and relevant input identity |
| Initial decision | Request before retry escalation, predicted quantile, policy/fallback, model/calibration version, history sequence, decision time |
| Attempt | Attempt number, submitted request, peak measurement, start/end time, exit status, scheduler failure reason, explicit OOM evidence |
| Logical outcome | Success/failure, number of attempts, final successful peak/runtime when available |
| Online update | Eligible outcome count, training cutoff, start/end/activation times, model version, update failure if any |
| Costs | Prediction latency, learner CPU time and peak RSS, update duration, whole-workflow makespan, audit policy |

Do not count an OOM-killed attempt's peak as the complete unconstrained demand. Mark it as censored. Preserve failed attempts even if a later retry succeeds.

### 3.8 Primary metrics and exact interpretation

Let `r_i` be the initial request in GiB, `p_i` the final successful observed peak in GiB, and `d_i` that successful attempt's runtime in hours.

| Metric | Definition / interpretation |
|---|---|
| Peak-based initial-request coverage | Fraction with `r_i >= p_i` among tasks with an observed successful peak; disclose denominator and missing outcomes |
| Below-peak requests | Count with `r_i < p_i`; this is not an observed OOM count |
| First-attempt OOM | Explicitly observed OOM on attempt 1, reported separately from other failures |
| Completion and retry counts | Logical tasks successful/failed/missing; all attempts and extra attempts |
| Sum of initial requests | `sum(r_i)`; reservation total across tasks, not peak node occupancy |
| Request-to-peak ratio | Median and upper percentiles of `r_i / p_i`, with zero/missing peaks handled explicitly |
| Initial-request slack proxy | `sum(max(r_i - p_i, 0) * d_i)`; comparable to retained accounting, but not full retry-inclusive cost |
| Actual reserved memory-time | Sum of each attempt's actual requested GiB times its duration in hours, including failed attempts |
| Makespan | Same start/end definition for both arms; report paired repetitions separately |
| Learning/prediction cost | Prediction median/p95 latency; update count/duration; learner CPU time and memory |

Use each arm's own observed peaks and runtimes, and show whether they differ. Match logical task identities for paired request comparisons. Requests alone cannot establish better system efficiency if failures, duration, or learning cost increase.

Measured peak-based slack is not an integral of actual instantaneous unused memory. Do not convert lower reservation totals directly to AWS dollar savings on a fixed-size node.

### 3.9 Figures and table for the paper

**Figure A: adaptation over the new workload.** Two panels: request-to-peak ratio and below-peak request rate over predefined decision-order windows. Mark online model activation points. Use, for example, non-overlapping 128-decision windows selected before looking at results; report window sizes and process composition. Plot a well-populated process such as `ALIGN_CHUNK` separately so a changing mix of stages does not look like learning.

Within-run decision order is not necessarily identical across arms. Use stable task identities for paired aggregates; do not pair the 100th completion in one arm with the 100th completion in the other as if they were the same task.

**Figure B, optional:** distribution of initial request margins, `100 * (r_i / p_i - 1)`, for frozen and online CAMP.

**Main result table:** per arm, task count, coverage, observed OOMs, retries, sum of requests, actual reserved memory-time, and makespan. Put learner cost in the table or a short accompanying sentence. Report repetition-level outcomes rather than treating thousands of dependent shards as independent repeats.

For uncertainty across samples, preserve sample/run groups when resampling. Shared workflow preparation tasks need separate treatment rather than assignment to an arbitrary sample. Such intervals describe dataset variability; they do not replace repeated live executions.

### 3.10 What counts as completion

- Frozen model/history/calibration fingerprints remain unchanged; recorded evaluation outcomes are kept separately.
- Online model activations and causal history ingestion are demonstrated.
- Both arms cover the same predefined input manifest and report all missing/failed tasks.
- No source/pilot/test overlap or cross-arm state carryover is found.
- Raw decisions, attempts, outcomes, update logs, and summaries can regenerate the reported results.
- Any gain is reported together with coverage, failures, and cost; unchanged or worse performance remains a valid finding.

The repository supplies the online workflow, but a true frozen-state control and arbitrary new-manifest evaluation are not established as ready-made modes. Validate those behaviors before the final run. This is a protocol requirement, not a claim that these experiments have already been implemented.

## 4. Experiment 2: CAMP versus NGBoost

### 4.1 Question and baseline definition

**Question:** With the same prelaunch information and evaluation tasks, does CAMP's quantile-based allocation achieve a better safety–reservation tradeoff than a parametric probabilistic predictor?

NGBoost predicts a conditional distribution. Convert its upper quantile to a memory request. It is a prediction method; the quantile-to-request rule and safeguards are part of our experimental allocator, not a native workflow scheduler. Sources: [NGBoost paper](https://proceedings.mlr.press/v119/duan20a.html) and [official usage guide](https://stanfordmlgroup.github.io/ngboost/useage/).

Start with an offline comparison. Re-executing all six workflows is unnecessary for comparing requests against their recorded peaks. Offline results cannot establish observed OOMs, retries, or makespan under NGBoost.

### 4.2 Dataset and controlled information

Use the existing 33,516-task population with its preserved seed-1996 membership: 28,490 development tasks and 5,026 evaluation tasks. Preserve the existing fit/calibration divisions inside development, or document a new development-only division before training. Do not randomly repartition the evaluation set.

For the primary model comparison, provide both methods the same available prelaunch feature view: static information, memory history, consumption history, and predicted consumption. Never provide current-task measured consumption or peak memory. Predicted consumption in training must be generated without fitting its proxy to that row's target, using the established cross-fitting procedure. Test predictions must come from a development-trained proxy.

Freeze model parameters, calibration, and allowed history state for the primary held-out comparison. Construct history features from eligible prior development records only, with task-specific causal cutoffs. Recompute CAMP under the same frozen evaluation contract; do not mix a newly frozen NGBoost run with a CAMP prediction file that used a different history-update contract.

This equal-feature comparison isolates the modeling/allocation approach. It gives NGBoost access to CAMP-derived features and is not evidence that NGBoost supplies consumption instrumentation itself. Any additional comparison using each system's native information should be labeled separately and is optional.

### 4.3 Sequential procedure

1. Freeze task IDs, targets, units, feature availability, preprocessing, and development/evaluation membership.
2. Select a positive-support response distribution supported by the chosen NGBoost implementation; a log-normal model is a candidate. Validate finite quantiles and strictly positive usable targets on development data. State the choice explicitly.
3. Fit preprocessing on fitting data only. Use identical underlying information for CAMP and NGBoost, while permitting model-appropriate encoding. Define handling of unseen categories and missing histories.
4. Train a small, predeclared development-only model grid. A practical proposed grid is 200/500 boosting iterations, learning rates 0.03/0.05, and shallow base trees of depth 2/3. Pilot its cost first; these are proposed settings, not repository defaults or validated best values.
5. Select model settings using development validation and an appropriate distributional loss. Select the allocation operating point on a separate calibration subset within development.
6. Form requests from predicted upper quantiles. Candidate quantiles are 0.95, 0.99, and 0.995; apply the same unit rounding and admissible request bounds used for CAMP. Record all floors, caps, and fallback events.
7. Predeclare a primary target coverage, for example 99%, and select each method's lowest-reservation setting meeting that target on calibration data. If none qualifies, report that failure rather than silently lowering the target.
8. Evaluate the locked methods once on the 5,026 tasks. Report achieved test coverage; calibration success does not guarantee test coverage.
9. Save per-task requests and distribution parameters/quantiles, model configuration, fitting and inference times, and the complete calibration selection record.

If extra residual calibration is added to NGBoost, identify the method as NGBoost plus that calibration. Do not add undocumented CAMP safeguards to one arm and attribute the entire result to the underlying predictor.

Do not adjust quantiles after seeing test underallocation counts. A test safety–cost curve may show all previously declared operating points; it must not hide the originally selected primary point.

### 4.4 Metrics and presentation

- Primary: underallocation count/rate and sum of requests at the development-selected operating point.
- Secondary: median/p95 request-to-peak ratio and per-workflow breakdown.
- Runtime-weighted slack: use the same known-runtime subset for both methods and report its size. The retained accounting has 4,577 known runtimes and 449 missing runtimes; do not silently treat unknown duration as measured zero.
- Quantile quality: pinball loss at shared quantiles, where both methods provide them. Keep calibrated allocation requests distinct from predictive quantiles.
- Computational cost: fit time, peak fitting memory, and inference median/p95 latency under a common measurement protocol.

**Paper output:** one compact CAMP/NGBoost table and, if space permits, a safety–reservation plot. Include per-workflow results in the saved experiment record even if the paper reports only aggregate results.

The published WORKS 87/31 underallocation endpoints and the later 85/30 reproduction are separate evidence. A new matched baseline experiment must use its own actual CAMP result; never replace it with 31 to force agreement with the published endpoint.

## 5. Experiment 3, optional: CAMP versus Ponder

### 5.1 Question and faithful baseline

**Question:** Does CAMP improve allocation safety or reservation efficiency compared with a workflow-specific method that adapts from completed task input sizes and peak-memory observations?

**Implementation update (2026-11-10):** a [standalone Ponder adapter](SCRIPTS/BASELINES/ponder/README.md) now compiles the authors' predictor code unchanged at a pinned commit. It passed synthetic branch/interface checks and 48 exact comparisons against direct original-core calls. It uses Ponder's internal offset with no additional outer offset; that choice must be reported. Dataset-field mapping and comparative experiments remain pending. This does not change Ponder's optional priority or constitute a completed baseline evaluation.

Ponder selects among history-based safeguards and regression according to available observations and memory-demand behavior. Use the published algorithm and implementation as the specification. A generic historical maximum or generic linear regression must not be named Ponder. Source: [Ponder, Sections III–IV](https://arxiv.org/html/2408.00047v1).

Validate the adapter on cases covering empty/small history, weak input–memory correlation, regression, and inputs outside the observed range. Record default requests, buffer units, bounds, weighting, and other paper-defined behavior. Label a port as **Ponder memory-sizing algorithm adapted to our evaluation**, distinguishing it from reproduction of the original scheduler deployment.

### 5.2 Common causal replay

1. Choose an existing trace cohort with verified input sizes, process identities, peaks, and a defensible outcome-release order. Keep development and evaluation membership fixed.
2. Give both methods eligible prior observations from the same source population. Each may use its native information: Ponder input-size/peak pairs and CAMP its documented features. This is a system-method comparison, not an equal-feature model ablation.
3. Before every decision, expose only outcomes already released by the common replay schedule. Group history by compatible workflow/process/context; never pool unrelated process memory indiscriminately.
4. Predict each task before revealing its outcome. Let each method update using its prescribed policy; identical observation availability does not require identical update algorithms.
5. If trustworthy execution timing is absent, use explicit fixed batches and reveal outcomes only at batch boundaries. Describe the result as batched replay, not reconstructed live execution.
6. Re-evaluate CAMP in this same replay. Do not compare an adaptive Ponder replay directly with CAMP's separate frozen-test aggregate.
7. Report requests, underallocation, fallback frequency, and behavior as compatible history grows. Keep task population, history opportunities, and available request limits common.

The original trace's completion schedule is held fixed in replay. Predictions do not change that schedule. Therefore the experiment estimates allocation behavior, not counterfactual scheduling or failure performance. Offline underprediction must not automatically create simulated OOMs with invented runtimes.

### 5.3 Optional live extension

If the adapter is validated and time permits, add Ponder as a third arm on the same unseen Bowtie2 inputs. Initialize it with compatible observations from the same source workload used for CAMP; do not give one method previous test outcomes. Keep task CPU assignments, retry behavior, input manifest, and resource envelope common.

Then measure actual OOMs, retries, makespan, and attempt-inclusive memory-time using Experiment 1's definitions. Record native instrumentation and learning costs for each method; do not claim an overhead advantage from an offline request comparison.

**Paper output:** add Ponder to a comparison table only after actual results exist. If only replay is completed, place it in the replay table, not among live deployment results.

## 6. Deliverables and paper integration

For each completed experiment preserve:

1. A protocol record identifying inputs, splits, checkpoint/state, comparison arms, causal rules, selected parameters, and deviations from this plan.
2. Per-task prediction/decision records and, for live runs, all attempt/outcome/update records.
3. A summary table with denominators, units, missing-data treatment, and repetition/seed identifiers.
4. A script or analysis notebook that regenerates the table and figures from those records.
5. A short interpretation stating what improved, what worsened or remained unchanged, and what the experiment cannot establish.

Recommended six-page presentation order: brief retained deployment context; new unseen-input frozen/online result; compact external-baseline comparison when available. Describe protocols in Section IV and outcomes in Section V; update the abstract only with completed, verified results. Keep pending values as `?` during drafting and resolve or remove them before the final paper.

The minimum new experimental package is the paired unseen-input Bowtie2 study plus the NGBoost comparison once external-baseline work resumes. Ponder is an optional addition. Replotting the retained cold/warm or ablation measurements does not make those observations newly collected results.

## 7. Repository evidence to consult

- [Current extension scope and prior-work boundary](Big_Data_paper/CAMERA_READY_EXTENSION_PLAN.md).
- [Manuscript result provenance and pending experiments](Big_Data_paper/Big_Data_Camera_Ready/source/Camera_Ready/RESULTS_PROVENANCE.md).
- [Existing live experiment behavior](SCRIPTS/RQ5/README.md).
- [Retained task and attempt records](RESULTS/RQ5/README.md).
- [Original Bowtie2 manifest](WORKFLOWS/bowtie2/data/public_runs_prjeb11501_online_unseen_6000.tsv).
- [Current online prediction service](SCRIPTS/RQ5/experiment_template/camp/live_online_learning/scripts/serve_predictions.py): prediction-time history synchronization must be disabled for a true frozen control.

These references establish what exists. They do not imply that new datasets have been selected, checkpoints located, frozen mode validated, or external baselines executed.
