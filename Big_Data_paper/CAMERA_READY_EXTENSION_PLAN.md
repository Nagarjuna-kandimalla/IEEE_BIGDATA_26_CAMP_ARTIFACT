# CAMP Big Data six-page extension: plan and agent handoff

Updated: 2026-11-09. Status: planning document; no new experiments or manuscript revisions have been executed for this plan.

## Current agreed direction — read before the earlier detailed plan

This section supersedes conflicting experimental priorities below. The older detailed proposals are retained as planning history, not permission to launch parked experiments.

### Scope and manuscript constraints

- Routing, calibration, and history-scope ablation experiments (previous list items 5, 6, and 7) are PARKED and out of scope. Keep their settings explicit so feature comparisons are interpretable; do not add experimental sweeps for them.
- Preserve the ZIP's LaTeX skeleton. Any future manuscript edits are restricted to file naming and content inside `source/Camera_Ready/`, including necessary reference-path repairs there. The archive/source edits have not been completed in this conversation.
- Do not repeat the original RQ1-RQ4 presentation. Use a brief cited CAMP background, implementation clarification, focused evidence on information value and cost, new baselines, and an unseen-input deployment study.
- Scope update (2026-11-10): the user removed the standalone simple memory-history/percentile allocator to prioritize the RQ5 online Bowtie2 study. Do not implement, run, or list that baseline as pending. This does not remove CAMP's own historical features or retained A+P evidence.

### Working title and one-sentence story

**Working title:** *Consumption-Aware Memory Allocation in Practice: Ablation, Audit Cost, and Online Adaptation*.

**Study story:** Building on CAMP, this study examines the contribution and cost of consumed-data feedback, compares it with probabilistic and adaptive allocators, and tests its online adaptation to previously unseen workflow inputs.

This is a study description, not a claim of superiority before the new experiments run.

### Paper order

1. **Introduction and relationship to WORKS.** State the unresolved practical questions and explicitly identify the inherited system and reused measurements.
2. **Compact background and implementation.** Explain read versus mmap-fault measurements; task/descendant filtering; Nextflow overlays and launch hooks; Slurm memory requests; completion feedback; and changes required to use the system. Define logical task versus attempt, coverage, offline underallocation versus live OOM, and out-of-fold prediction in plain terms. Address reviewer confusion without a full repeat of the original design section.
3. **Common experimental protocol.** Establish task populations, feature availability, retained versus fresh runs, policy-selection procedure, metrics, and missing-runtime treatment before showing comparisons.
4. **Consumed-data evidence, in order:** (a) read-only versus read+mmap ablation; (b) four feature variants; (c) selective auditing's downstream allocations; (d) allocation saving versus measured audit overhead. Mark already reported WORKS evidence and newly presented detail separately.
5. **New external baselines.** Prioritize NGBoost for an offline prototype and Ponder for an adaptive workflow comparison. Q-learning is conditional/stretch. Compare safety and reservation cost together; do not label all three as distribution predictors.
6. **Online Bowtie2 deployment and unseen-input extension.** Briefly anchor the retained same-input cold/warm result, then evaluate disjoint new inputs from a fixed source checkpoint. Compare frozen transfer and full online learning; a separate history-only allocator is outside the agreed scope. Add a feasible baseline to live evaluation if resources permit.
7. **Limitations, related work, and conclusion.** Explain bounded generality, measurement semantics, retrospective accounting, and which components remain untested. Retain existing file/section organization; fit this content within the current skeleton rather than adding a new hierarchy.

### Exact retained numbers checked on 2026-11-09

The original RQ2 compressed task tables were read directly and `first_allocation_mib < actual_peak_mib` recomputed over 5,026 rows per method:

- `RESULTS/RQ2/csv/a_plus_p_task_predictions.tsv.gz`: **87**.
- `RESULTS/RQ2/csv/a_plus_p_plus_c_task_predictions.tsv.gz`: **31**.
- The associated retained figure is `RESULTS/RQ2/figures/fig_rq2_allocation_tradeoff.png`.

The separate retained four-way ablation is **85 / 46 / 52 / 30**, not 87 / 46 / 52 / 31. See `Reviewer_Feedbacks/chat_ablation/expected_results/paper_configuration/native_metrics.csv`. Its endpoint-reproduction table explicitly distinguishes paper-frozen 87/31 from elastic-reproduction 85/30.

**Do not splice the frozen endpoints into the later four-way study and call it a matched ablation.** Options are: show a clearly labeled original 87/31 anchor alongside the complete later ablation, or reproduce all four variants under a common verified configuration. Never tune a fresh run to force a particular count. The existing paper-route table changes routing between A+P and CAMP variants; with routing ablations parked, either describe it as a system-configuration comparison or use one fixed-route feature comparison, with its actual counts. Fixing a route for fairness is not reopening a routing sweep.

- Read-only versus read+mmap: **32 versus 30**, with requests **41,852.64 versus 34,271.49 GiB**, from `Reviewer_Feedbacks/W3/results/paper_native_metrics.csv`. This is a separate experiment from the original 31 endpoint.
- Downstream auditing at 20%: **265.8 versus 305.8** mean underallocations after the first model update, **13.1% fewer**, with **2.4% more requests**. W2's README retains preliminary status. These are replay diagnostics, not observed live OOM counts.
- W5 pre-audit allocation saving: **23.596 GiB-hours**. Mean net savings: **+17.597 at 5%**, **+11.161 at 10%**, **+5.913 at 15%**, **-0.429 at 20%** (interval crosses zero); larger retained budgets have negative means.
- W5 charges positive paired eBPF runtime overhead at each audited task's frozen CAMP memory request. It holds allocation saving fixed across budgets. It does not measure complete model-training/controller cost and does not prove that each selected audit budget generated the assumed saving. Call it audit-cost accounting, not total end-to-end model profit.

### Implementation facts to describe accurately

Inspection of `AUDIT/helper_scripts/exp2/ebpf_audit_py39.py` confirms positive `read`/`pread64` return accounting with descriptor-to-name attribution, descendant tracking, and a `filemap_fault` entry probe that adds 4,096 bytes per attributable invocation. Do not describe this as mmap allocation length, unique bytes read, disk I/O, or exact resident memory. Descriptor attribution and fixed-page event accounting have limitations; the opening code comment is less specific than the actual implementation and should not override it.

There are two distinct filters: the Nextflow overlay's process selection and the tracer's tracked task/descendant filter. `--no-filter` disables the latter and must not be portrayed as normal task-isolated tracing. The generic overlay also supports every-N sampling; that is not the learned selective-audit policy.

The repository supplies additive overlays for unmodified nf-core workflow sources. The live custom Bowtie2 path additionally needs task metadata, a prelaunch allocation closure, prediction service, outcome recorder, learner, and model/history state. State what configuration/integration is needed rather than claiming every workflow works without any adaptation.

### Baseline feasibility assessment — proposed, not timed

Primary sources checked:

- [NGBoost paper](https://proceedings.mlr.press/v119/duan20a.html) and [official Python implementation](https://github.com/stanfordmlgroup/ngboost).
- [Ponder paper](https://arxiv.org/html/2408.00047v1), whose implementation uses [nf-cws](https://github.com/CommonWorkflowScheduler/nf-cws) and [Common Workflow Scheduler](https://github.com/CommonWorkflowScheduler/KubernetesScheduler). The linked [MemorySizingExperiments](https://github.com/CommonWorkflowScheduler/MemorySizingExperiments) repository is an evaluation repository, not by itself the full allocator deployment.
- [RL resource-allocation paper](https://arxiv.org/html/2211.12076v2). Its Q-learning agent jointly chooses CPU and memory; the study uses repeated workflow executions, including 100 Q-learning runs. The cited publication is the Big Data 2022 BPOD workshop.

Engineering assessment: NGBoost is likely the quickest first offline adapter because of its Python fit/predict-distribution interface. Validate response distribution, preprocessing, upper-tail selection, dependencies, and pilot timing; no training/runtime benchmark has been performed here. Ponder is highly relevant but native deployment has scheduler/plugin dependencies that differ from the CAMP Slurm setup. A faithful replay/adapter must be validated and labeled separately from native Ponder. Q-learning is the highest-risk fast-turnaround choice because CPU actions, rewards, exploration, and execution effects need faithful treatment; frozen memory traces cannot establish counterfactual CPU-dependent runtimes. Do not substitute generic memory-only Q-learning and claim reproduction of that paper.

Recommended execution order: verify retained evidence; smoke-test NGBoost offline; assess Ponder's sizing component and integration; then new-input CAMP deployment with feasible comparator(s). Keep Q-learning out of the minimum six-page deliverable unless a faithful runnable implementation is established quickly. Do not promise elapsed times without pilots.

### Bowtie2 readiness and new-data requirements

Available: seven-stage custom workflow, exact original 38-run input manifest, splitting script, eBPF integration, allocation service, online learner, initial-state rebuild route, preflight checks, and cold/warm attempt/task tables. The 6,000 logical tasks span preparation, splitting, alignment, indexing, and flagstat; they are not 6,000 independent alignment jobs or 6,000 input samples.

Retained cold/warm requests recomputed from task tables: **898.3857 / 251.9268 GiB**. Documentation reports observed peak totals **238.50 / 238.82 GiB**, unused memory-time **23.954 / 0.018 GiB-hours**, and 6,000 logical tasks in each run. Comparing first requests to final measured peak gives **4 / 13 below-peak tasks**; this is not automatically the recorded `first_attempt_oom` count. Use that explicit field when reporting actual OOMs.

Not yet ready for a new dataset without work:

1. Repair the existing empty chunk-tuple mapping in a controlled working copy before execution.
2. Locate external terminal models/history or rebuild them. Result CSVs are not deployable model checkpoints; their availability does not establish that the old terminal state is present.
3. Acquire and verify disjoint new sample/run inputs compatible with the selected reference and protocol. Freeze identity/hash manifests and check overlap against seed history and original live inputs.
4. Parameterize the runner's hardcoded original manifest, snapshot filename, dataset labels, and any affected task-count checks. The existing figure loader requires exactly 6,000 tasks even with `--new-run`.
5. Confirm Linux/Slurm/BCC/Apptainer/shared-storage resources and external downloads. Availability has not been established.
6. Implement and validate a true frozen-state mode if using the frozen/online comparison; the current documented runner launches the learner and updates every 128 completed outcomes. A zero-change flag cannot be assumed to exist.
7. Start comparison arms from independent copies of the same checkpoint. Preserve unseen-input boundaries and only admit outcomes completed before decisions. Record live model versions, failures, retries, and update/prediction costs.

The old run used 12 task workers plus one controller/learner worker. This is a reproduction specification, not proof that every extension requires that scale. A smaller pilot can estimate feasibility; any changed deployment scale must be reported. Full auditing can isolate online learning behavior, but does not demonstrate live selective-audit savings.

### Compact presentation and priority

Six-page target: brief implementation explanation; compact mmap and feature evidence; a small downstream/net-cost table; one new-baseline comparison figure/table; and one new-input online figure. Existing evidence is supporting context; new-baseline and unseen-input results should carry the extension. Do not reprint every old figure. All publication-disclosure requirements in section 3 still apply.

## 1. Purpose and user intent

Prepare a six-page IEEE Big Data camera-ready short paper that makes a substantive, clearly disclosed contribution beyond the accepted SC WORKS paper. The memory-allocation problem and CAMP system remain the foundation. Briefly describe CAMP as prior work; concentrate the new paper on additional scientific questions, controlled analyses, stronger baselines, and potentially new-input experiments.

The user explicitly wants to:

1. Address the Big Data reviewers' comments.
2. Distinguish the new contribution from the exact accepted WORKS manuscript.
3. Consider detailed ablations, including results only briefly mentioned in WORKS.
4. Add meaningful experiments, including comparisons with distribution-aware methods.
5. Follow the explanatory writing pattern of the WORKS paper.
6. Fit six pages including figures, tables, and references.
7. Comply with prior-publication, overlapping-submission, attribution, and camera-ready requirements.

The professor's guidance, supplied by the user, was: keep the problem; describe CAMP briefly as published work; add experiments and detailed ablations not previously shown; compare with distribution methods as well as the point-based Sizey baseline.

This document proposes a research plan, not a guarantee of publication eligibility. Final experimental scope, baseline choices, manuscript title, and chair approval remain unresolved. Do not interpret proposed experiments as completed or their expected benefits as measured findings.

## 2. Essential sources and reading order

Paths below are relative to this file unless stated otherwise.

| Source | Role |
|---|---|
| [Accepted WORKS paper](../IEEE_WORKS_26_Sasank.pdf) | Primary boundary for what has already been reported; eight pages. |
| [Submitted Big Data paper](BigD1136_3793_CAMP.pdf) | Ten-page submission that needs substantive revision and compression. |
| [Acceptance email](Big_Data_Acceptance_Mail.pdf) | Saved acceptance conditions and reviewer reports. |
| [Big Data reviewer comments](Big_Data_Reviewer_Comments) | Full text of four reviews. |
| [Author's working notes](temp_1.md) | User's proposed responses; NAE means new experiment/explanation needed, JE means explanation. These are informal notes, not completed-work certification. |
| [Artifact overview](../README.md) | RQ1-RQ5 reproduction routes and directory map. |
| [Reviewer package overview](../Reviewer_Feedbacks/README.md) | Existing W1/W2/W3/W5 and C-hat evidence. |
| [Reviewer verification record](../Reviewer_Feedbacks/VERIFICATION.md) | What historical reproduction actually verified. |
| [Ablation interpretation](../Reviewer_Feedbacks/chat_ablation/RESULTS.md) | Four feature variants and the model-routing confound. |

Read the WORKS PDF itself before deciding that an analysis is new. The repository contains older protocols, frozen predictions, revised analyses, and two manuscript versions; they are not interchangeable sources of novelty.

At the final handoff check, a new root archive appeared: [IEEE_BigData_CAMP26 (2).zip](../IEEE_BigData_CAMP26%20%282%29.zip). Its directory listing contains 47 entries, including `source/Camera_Ready/main.tex`, `source/Original_Submission/main.tex`, section files for both versions, `source/references.bib`, and `source/IEEEtran.cls`. This archive was not present in the earlier inventory. Only its directory listing has been inspected; its source contents, build, and correspondence to the PDFs have not been verified. Inspect it in a separate workspace before creating another manuscript project, and preserve both versions. Do not assume the folder named Camera_Ready already implements this extension plan. The user asked to exclude `Not_Needed/`; do not search it without later authorization.

## 3. Publication conditions and unresolved eligibility

### 3.1 Recorded acceptance conditions

The saved acceptance email identifies submission BigD1136 as a **short paper**. It states:

- Six pages, including figures, tables, and references.
- Up to two additional purchased pages were offered, but the user's chosen target is six pages.
- Camera-ready submission and author registration deadline: November 14, 2026.
- Video deadline: December 1, 2026; short-paper video at most 15 minutes.
- Oral slot: 15 minutes, including questions.

These are facts from the saved email, not a substitute for checking the current submission portal before delivery. On 2026-11-02 the official dates page also listed November 14 for the main-conference camera-ready deadline. Do not confuse the ten-page initial-submission limit with this paper's six-page acceptance category.

### 3.2 Official policy sources checked during planning

- [IEEE conference submission policies](https://conferences.ieeeauthorcenter.ieee.org/author-ethics/guidelines-and-policies/submission-policies/)
- [IEEE conference ethical requirements](https://conferences.ieeeauthorcenter.ieee.org/author-ethics/ethical-requirements/)
- [Big Data 2026 call for papers](https://bigdataieee.org/BigData2026/calls/papers/)
- [Big Data 2026 important dates](https://bigdataieee.org/BigData2026/important-dates/)

IEEE's guidance requires disclosure of related prior publications and current submissions, citation, and a clear account of differences. Evolutionary publication requires substantial additional technical information and appropriate peer review. The cited policies do not supply a universal percentage of new text or results that guarantees eligibility.

**No Big Data-specific authorization for this particular conference-to-conference extension has been established.** Do not borrow a journal-extension rule and treat it as automatic permission for a second conference paper.

Both papers have already been accepted according to the user. The original submission dates, review overlap, disclosures, and the chairs' knowledge are not established here. A substantially revised camera-ready does not retroactively settle a possible earlier overlap issue.

### 3.3 Required disclosure work before final submission

Prepare a concrete package for the corresponding author to send to the Big Data chairs:

1. Exact accepted WORKS PDF and accurate publication status: published or accepted/to appear.
2. Submitted Big Data PDF and paper ID.
3. Submission/acceptance timeline and what related work was disclosed, supplied by the authors.
4. A table of shared material, previously reported results, newly reported analyses, and new experiments.
5. Proposed six-page outline and the scientific differences from both accepted/submitted versions.
6. A request for the chairs' determination on eligibility and whether additional review is needed for the changes.

Do not send email or messages on the user's behalf without an explicit instruction. Do not promise compliance based solely on adding citations, changing the title, rewriting text, or including more figures.

When reusing text, data, or figures, acknowledge the source and check applicable reuse/copyright requirements. Prefer a short newly written background summary. A redrawn plot of already reported results remains prior evidence, not a new experiment. Public repository availability alone does not automatically disqualify a result, but its provenance must be disclosed.

IEEE's submission-policy page also contains AI-generated-content disclosure guidance. Before submission, assess actual writing/figure/code assistance against that policy; grammar-only editing is distinguished from generated content. Do not fabricate a disclosure or omit one automatically.

## 4. WORKS background: what CAMP does

Scientific workflow tasks need memory reservations before execution. Requests below demand risk failure; excessive reservations consume capacity. CAMP adds runtime consumption information from completed tasks to static metadata and prior peak-memory history.

### 4.1 Keep these quantities distinct

- `s_t`: features available before launch, including workflow/process metadata and staged input size.
- `y_t`: measured post-execution peak RSS.
- `c_t`: measured consumed-byte signal, available after an audited task finishes.
- `h_m,t`: summaries of prior peak-memory observations.
- `h_c,t`: summaries of prior audited consumption observations.
- `c_hat_t`: prelaunch prediction of current-task consumption.
- `y_hat_t`: submitted memory request, distinct from the central peak-memory prediction.

Access/A+P uses static features and peak history. Full CAMP/A+P+C adds consumed history and predicted consumption. A+P is a learned baseline, not the simple historical-percentile allocator requested by reviewer 1.

### 4.2 Core mechanisms

1. eBPF attributes positive read returns and file-backed mmap page-fault activity to task process trees.
2. I0-I5 histories pool completed observations at varying compatibility levels.
3. A global consumption estimator predicts `c_hat` from static features and peak history.
4. Quantile LightGBM ensembles estimate peak memory; workflow/process tails and broader fallbacks are used according to the experiment's route.
5. A development-selected allocation policy and hierarchical log-residual calibration turn predictions into integer-MiB requests.
6. Selective auditing prioritizes risk, information, and discovery under an audit-count budget.
7. Live deployment records completed outcomes and publishes updated models/history.

Scopes organize evidence; model routing selects predictors. These are separate mechanisms and must not be conflated.

### 4.3 Data and original experiments

| Experiment | Population and purpose |
|---|---|
| RQ1 | Matched baseline, STRACE, and eBPF workflow runs; signal visibility and runtime overhead. |
| RQ2 | 33,516 tasks; primary 28,490 development / 5,026 test split; Access versus CAMP and repeated split/seed evaluation. |
| RQ3 | Sizey-eligible 30,478 tasks; 9,141 initial / 21,337 test tasks; task-matched Sizey comparison. |
| RQ4 | Frozen initial/test inputs on the 9,141 / 21,337 population; equal-count selective-audit evaluation. |
| RQ5 | Live 6,000-logical-task Bowtie2 cold and fresh warm runs; model/history feedback. |

The six offline workflows are GATK, Minimap2, Sarek, Seqinspector, Taxprofiler, and Viralmetagenome. Bowtie2 is separate. GATK and Minimap2 are synthetic custom workloads; the other four use the documented bioinformatics datasets. Do not describe every task as an independent dataset or all inputs as naturally occurring production data.

Offline underallocation is a comparison of a request against recorded peak RSS, not an observed scheduler OOM. Aggregate request sums are not simultaneous cluster RAM usage or a direct measurement of throughput. Distinguish these throughout the new paper.

## 5. Exact WORKS overlap boundary

The accepted PDF already reports the following, including short additions that a new agent could easily overlook:

| Existing claim/material | WORKS location | Implication for Big Data |
|---|---|---|
| CAMP architecture, scopes, proxy, quantiles, calibration, gates | Sections II-III | Cite and summarize; do not reintroduce as a new system contribution. |
| Audit signal and overhead | V-A | Prior evidence; fresh overhead experiments would need an additional question. |
| Primary 87 versus 31 underallocations; 31.50% more requests and 37.18% less unused memory-time | V-B | Existing primary comparison, not new evidence. |
| Adding C-hat to consumption history: 46 to 30 underallocations, 80,853 to 34,271 GiB requests, MdAPE 21.32% to 26.51% | V-B | A brief ablation is already published/accepted; extended analysis must identify what is additional. |
| Explicit reads versus read+mmap: 32 versus 30 underallocations | V-B | Existing mmap ablation. |
| Equal-budget Access: 2 versus CAMP 31 underallocations; CAMP lower unused memory-time | V-B | Existing tradeoff, not a new uniformly favorable result. |
| Native Sizey versus CAMP: 3,597 versus 287 underallocations, larger CAMP reservations | V-C | Existing baseline result. |
| Equal-budget Sizey: 1,119 versus CAMP 287; matched 95.004% coverage with lower CAMP requests | V-C | Already reported matched comparisons. |
| Selective-audit target recall | V-D | Existing selection-yield evidence. |
| Downstream selective auditing at 20%: 265.8 versus 305.8 mean underallocations, 2.4% more requests | V-D | Already reported downstream comparison. |
| Bowtie2 live study | Mentioned as residing in the technical report | Not developed as a full result section in WORKS, but cannot automatically be called wholly unpublished; investigate the cited report and disclosures. |

The full four-way feature table, common-route analysis, new baseline implementations, and new-input tests are potential extension material. Each needs a provenance check against both the WORKS paper and its cited report before a novelty claim.

**Known inconsistency:** text extraction of WORKS V-B shows Access unused memory-time as `1433.19` while the W1 validated table gives `143.19` GiB-hours. The stated 72.2% reduction agrees with 39.87 versus 143.19. Verify visually and against source tables before drafting; do not propagate the apparent extra digit.

**Another reconciliation task:** WORKS describes favorable split results while the Big Data manuscript discusses failures at 30/70, 70/30, and 90/10. The repository includes global-tail, process-tail, and legacy-mixed route results. Resolve exactly which route supports each plot and sentence; do not combine them into a single robustness claim.

## 6. Existing evidence and its limitations

### 6.1 Reviewer packages

| Package | Evidence | Limits |
|---|---|---|
| [W1](../Reviewer_Feedbacks/W1/README.md) | Equal-request and matched-coverage comparisons using frozen predictions. | Retrospective operating points; not a deployment policy selected without test labels. Several results already in WORKS. |
| [W2](../Reviewer_Feedbacks/W2/README.md) | Paired selective/random auditing with downstream allocation and equal quotas. | Batch replay using recorded outcomes; not fresh eBPF executions. Standard reproduction does not retrain. |
| [W3](../Reviewer_Feedbacks/W3/README.md) | Read-only versus read+mmap signal ablation. | Primary 32/30 result already in WORKS; frozen histories used for exact reproduction. |
| [W5](../Reviewer_Feedbacks/W5/README.md) | Allocation saving minus audit cost in GiB-hours. | Allocation savings held fixed across budgets; not evidence that each audit budget caused those savings. |
| [C-hat ablation](../Reviewer_Feedbacks/chat_ablation/README.md) | Four feature views, paper-route and common-route outputs, grouped bootstrap. | Main table changes both features and routing; fresh model-training agreement across machines not established by standard reproduction. |

W5 reports positive net benefit at 5%, 10%, and 15%, approximately break-even at 20%, and negative mean net benefit at larger retained budgets. Do not claim selective auditing is universally cost beneficial.

### 6.2 Four-way feature study

From [native metrics](../Reviewer_Feedbacks/chat_ablation/expected_results/paper_configuration/native_metrics.csv) and [interpretation](../Reviewer_Feedbacks/chat_ablation/RESULTS.md):

| Variant | MdAPE (%) | Underallocations | Requested GiB, rounded |
|---|---:|---:|---:|
| A+P | 21.75 | 85 | 26,075 |
| A+P+CH | 21.32 | 46 | 80,853 |
| A+P+CHAT | 24.41 | 52 | 123,958 |
| A+P+CH+CHAT | 26.51 | 30 | 34,271 |

CH is consumed-byte history; CHAT is predicted current consumption. The reference endpoint 87/31 and the later ablation endpoint 85/30 are different retained runs. Label them separately; never silently substitute one for the other.

The table above uses the global route for A+P and process-tail routes for the other variants. It does not isolate feature effects. The [route-stratified table](../Reviewer_Feedbacks/chat_ablation/expected_results/route_analysis/route_stratified_metrics.csv) provides:

| Common route | A+P | +CH | +CHAT | +CH+CHAT |
|---|---:|---:|---:|---:|
| Global: underallocations | 85 | 81 | 105 | 74 |
| Process-tail: underallocations | 24 | 46 | 52 | 30 |

Request costs are essential: process-tail A+P requests approximately 603,467 GiB, versus approximately 34,271 GiB for full CAMP. Counts alone would misrepresent this comparison. C-hat alone also does not uniformly improve prediction or allocation. These mixed findings are scientifically useful and must remain visible.

### 6.3 What verification means

Historical package verification recomputed results from retained task predictions. It did not repeat all training or live runs. During the current repository orientation:

- 1,210 files were inventoried outside `Not_Needed/` and Git internals.
- 148 Python files parsed successfully for syntax.
- 899 immutable reviewer-package checksum entries passed.
- 681 tables and 180 JSON files parsed; the compressed reference and eight NPZ archives were read/integrity checked.
- Manuscript text/layout and packaged PNG figures were inspected.
- Model/history pickle/joblib files were inventoried, not executed.

These are orientation/integrity checks, not a line-by-line correctness audit, fresh scientific reproduction, or proof of numerical validity for every table.

## 7. Reviewer concerns mapped to responses

| Concern | Existing support | Proposed additional work | Priority |
|---|---|---|---|
| R1: why consumption helps beyond peak history | Four-way ablation, partially mentioned in WORKS | Common-route analysis, cost-aware comparisons, repeated seeds; investigate where consumption helps or hurts | Core |
| R1: why so much model complexity | No completed standalone simple-percentile comparison identified | Standalone history baseline removed by user on 2026-11-10; this reviewer request is not experimentally resolved | Out of scope |
| R1/R3/R4: safety bought with more memory | W1 matched comparisons already in WORKS | Matched evaluation for new baselines and ablation variants | Core |
| Professor: compare distribution methods | CAMP quantiles alone are not an independent external baseline | Select and implement appropriate probabilistic/quantile/conformal comparator(s) | Core |
| R1/R3: historical observations on new input data | Existing fixed-population studies insufficient | New-data or controlled input-shift test with an untouched test population | High |
| R3: scopes and gates unclear | Implementation contains detailed criteria | Compact background explanation; component ablation if claiming necessity | Writing required; experiment optional |
| R3: eBPF/Slurm/Nextflow integration unclear | Audit wrappers, Nextflow overlays, online scripts | Concise integration paragraph/diagram with a precise portability statement | Writing required |
| R3: Bowtie2 study narrow, no Sizey baseline | One retained cold/warm pair | Another workload or new Bowtie2 inputs, simple/distribution baseline, and optionally Sizey | High if live study selected |
| R4: split and seed robustness | Repeated results and route-contract tables | Resolve route differences; rerun selected comparisons across fixed seeds | Core robustness |
| R4: non-bioinformatics generality | Not established | Optional non-bioinformatics workload; otherwise state limitation | Stretch |
| Cost of auditing and cold start | W5 accounting and RQ5 traces | Account for training/inference/audit costs in any new experiment where feasible | Supporting |

Reviewer 2 is favorable. Reviewers 1, 3, and 4 still identify technical issues worth addressing. Do not turn the main paper into a reviewer-by-reviewer response letter; organize around scientific questions.

## 8. Recommended scientific focus and provisional questions

Working framing, not a final title:

> When does consumption-aware prediction improve the safety-reservation tradeoff against distribution-aware memory predictors during online deployment?

Candidate extension questions:

- **E1 - Attribution:** What do consumed history and predicted consumption contribute when model routing and evaluation conditions are controlled?
- **E2 - Comparative value:** Does CAMP improve the safety-cost tradeoff against distribution-aware baselines?
- **E3 - Transfer:** Do the gains persist on new inputs or changed input distributions, and how does online adaptation affect them?

These can become RQ1-RQ3 of the new paper after scope selection. Explain their relationship to WORKS rather than inheriting the old numbering silently.

A strong feasible package would combine E1 and E2 with one carefully scoped E3 experiment. If time/resources do not permit E3, narrow the scientific claim and discuss the reduced extension with the professor/chairs. Do not replace missing evidence with broader language.

## 9. Experiment specifications

All experiments below are PROPOSED unless explicitly identified as analysis of existing retained evidence.

### E1. Controlled feature, routing, and calibration study

**Starting point:** inspect and reproduce the retained four-way and common-route tables before new training.

**Design:** four feature sets `{A+P, A+P+CH, A+P+CHAT, A+P+CH+CHAT}` crossed with `{global-tail, process-tail}` where supported. Use identical tasks, development/test assignments, model seed schedules, preprocessing rules, target definitions, and fitting budgets. Keep quantile levels and calibration procedure consistent for attribution comparisons.

Two distinct analyses can be useful and must be labeled:

1. Each method selects its policy on development data under the same rule: compare deployable end-to-end systems.
2. A fixed common allocation rule or retrospective matched operating points: analyze feature/routing effects under a controlled operating condition.

Do not present the second as a policy selected without test outcomes if its multiplier uses observed test coverage.

**Calibration sub-study:** compare uncalibrated tail requests, global residual calibration, and hierarchical residual calibration on selected configurations. Tune any selectable hyperparameters on development data. Report coverage and reservations together. If scope contributions are studied, distinguish scope-derived feature removal from changing residual-scope selection or model routing.

**Metrics:** underallocation count/rate, first-request coverage, total requested GiB, request/peak ratio, q50 MdAPE, quantile pinball loss, empirical quantile coverage, and runtime-weighted unused memory where valid. Investigate per-workflow/process heterogeneity rather than only global averages.

**Replication:** use a predefined seed list, ideally 1996-2000 where comparable, and document which randomness changes. Grouped bootstrap can describe uncertainty on fixed predictions; it does not replace retraining seeds or independent workloads.

**Outputs:** task-level predictions/requests, policy-selection records, seed summaries, paired comparisons, and one compact multipanel figure. Existing runs can establish a baseline; fresh runs must be labeled separately.

### E2a. Removed from scope

The standalone historical-percentile allocator was discarded at the user's request on 2026-11-10. No implementation or experiment was performed. Retain original reviewer notes as historical context, but do not treat this comparison as a required or pending task.

### E2b. Distribution-aware comparators

Baseline selection is not yet complete. Conduct a primary-source literature review before claiming a method is established for this application or choosing an implementation.

Candidate families to evaluate for suitability, not final selections:

- Quantile regression forests as a conditional-quantile comparator.
- Distributional boosting, such as an appropriate NGBoost configuration, if its response distribution and tail assumptions fit nonnegative heavy-tailed memory.
- Conformalized quantile regression or another calibrated upper-bound method as an uncertainty-calibration comparator.

Quantile, parametric-distribution, and conformal methods are not identical categories. Do not describe a conformal upper bound as a complete predicted distribution, or claim standard exchangeability-based guarantees under chronological drift without justification.

Choose one or two defensible methods rather than many shallow baselines. Use a documented implementation/version, comparable tuning budget, identical legal feature views and splits, and development-only operating-point selection.

Separate two questions:

1. **Model family:** compare predictors with matched input features and a common allocation/evaluation procedure.
2. **Information contribution:** compare A+P and full consumed-data features within each family where feasible.

Without this separation, a comparison confounds model family, feature information, and calibration. Sizey remains useful as an established system baseline; a point predictor with a safety margin is not automatically a distribution model. Do not rerun every original Sizey experiment unless needed for the selected extension.

### E3. New-input generalization and adaptation

**Question:** does completed-task consumption history transfer to previously unseen inputs?

Preferred practical design: choose a workload with controllable, meaningfully varied inputs and measurable memory variation. Train/seed history on one set of input identities, then evaluate disjoint new inputs. Document overlap at sample, input, task-instance, reference, and process levels. Avoid treating a different random seed on the same input as a new dataset.

Possible routes:

- New real input samples for a retained bioinformatics workflow.
- Controlled input-size/composition changes in GATK or Minimap2, explicitly labeled synthetic.
- Bowtie2 on new samples/chunk sizes with enough variation to test transfer, rather than simply repeating the old cold inputs.

Distinguish:

- **Frozen transfer:** weights and allocation policy fixed; state updates, if any, specified.
- **Online adaptation:** prior completed observations update history/models under a predefined schedule.

Use common seed history and retry/resource settings across methods. Measure requests before revealing outcomes. Include selected distribution-aware baselines where feasible; the standalone simple-history allocator is excluded.

For live runs, record scheduler OOM exits, retries, success, requested memory, peak RSS, runtimes, model versions, and decision/completion timestamps. Collect observed peak outcomes for all comparable tasks without allowing failures or missing records to disappear from the denominator. State the handling of censored/failed-attempt peaks.

One new-input workflow establishes a bounded transfer result, not generality across all scientific domains. More diverse live workflows or a non-bioinformatics workload are stretch goals.

### Optional cost study

If new live experiments are run, measure audit, training, prediction, and coordination overhead separately where possible. Retain W5 as cited historical accounting if used. A new claim about the net benefit of a selected audit budget should use allocations actually generated under that budget, rather than assuming frozen full-information savings apply at every budget.

## 10. Scientific controls and metric definitions

- Freeze split identities before fitting or selecting policies. Keep related samples/groups together.
- Fit transformations and hyperparameters only on allowed development data.
- Enforce current-task label exclusion. Inspect whether development histories are leave-one-out, fold-restricted, or chronological; these are different guarantees.
- The existing RQ2 history builder constructs development snapshots with current-row exclusion and then sequential test snapshots. Do not infer strict temporal development-history causality merely from function names.
- For any new chronological claim, audit that the relevant outcome completed before the decision time. Batch replay is a distinct protocol.
- Distinguish model-weight updates, history updates, residual updates, and allocation-policy reselection.
- Use identical task sets when reporting paired comparisons. Publish exclusions and missingness by method/workflow.
- In W1 RQ2 memory-time accounting, 449 missing runtimes receive the historical zero weighting. New analyses should explicitly state denominators and missing-runtime treatment, not silently inherit it.
- Use request and peak in consistent units; distinguish MiB/GiB from MB/GB.
- Underallocation: `request < recorded peak`. Coverage: one minus underallocation rate.
- Requested memory: sum of first requests; request/peak ratio: sum of requests divided by sum of peaks.
- Unused memory-time: sum of positive `(request - peak) * runtime`, with units and runtime convention stated.
- Compare predictive quantiles using pinball loss and empirical coverage, not only central prediction error.
- Preserve observed live OOM counts separately from counterfactual underallocations.
- Retrospective matched coverage is a diagnostic. Evaluate a deployable coverage-targeted policy using development-selected settings.
- Specify independent units for bootstrap; task rows from one workflow/sample are not automatically independent.
- Report adverse results, seed variation, and workload differences. No seed/split selection based on favorable outcomes.

## 11. Implementation map and artifact layout

| Task | Starting code/evidence |
|---|---|
| Offline features/models/calibration | `SCRIPTS/RQ2/{history,modeling,calibration,run_offline_experiment,train_process_tail}.py` |
| Model settings | `SCRIPTS/RQ2/config/experiment.json` |
| Four-way ablation | `Reviewer_Feedbacks/chat_ablation/pipeline/`, its run scripts, and retained predictions |
| Route comparisons | `SCRIPTS/RQ2/aggregate_route_contracts.py`; `RESULTS/RQ2/csv/route_contract_repetition_effects.csv` |
| Sizey adapter and shared population | `SCRIPTS/RQ3/harness/scripts/` and `SCRIPTS/RQ3/scripts/` |
| Audit gates | `SCRIPTS/RQ4/scripts/selective_gates.py` |
| Downstream selective replay | `Reviewer_Feedbacks/W2/scripts/experiment.py` |
| Matched request/coverage metrics | `Reviewer_Feedbacks/W1/scripts/paper_metrics.py` |
| Audit cost | `Reviewer_Feedbacks/W5/analyze.py` |
| Live allocation and updates | `SCRIPTS/RQ5/experiment_template/camp/live_online_learning/` |
| Persistent completion-safe history | `SCRIPTS/RQ5/experiment_template/WORKS_ML/camp_ml/online_history.py` |
| eBPF attribution and wrappers | `AUDIT/helper_scripts/exp2/` |
| Workflow definitions and input manifests | `WORKFLOWS/` |

Do not overwrite frozen original predictions, reviewer reference results, or original paper figures. Preserve old checksums. Proposed new layout, to create only when implementation begins:

```text
Big_Data_paper/
  CAMERA_READY_EXTENSION_PLAN.md
  manuscript/                  # new source and bibliography
  experiments/
    README.md                  # exact reproduction order
    configs/                   # frozen designs/splits/seeds
    scripts/                   # new runners/adapters/analysis
    manifests/                 # identities, provenance, checksums
  results/                     # compact publishable tables only
  figures/                     # final figures and source mapping
  evidence/                    # claim ledger, overlap matrix, run summaries
```

Large data downloads, environments, models, and work directories should remain outside Git. Existing original code has duplicate copies intentionally retained for reproducibility; avoid mass deduplication during extension work.

Every new run should record code revision/diff, dependency versions, input hashes, split IDs, seed, method/feature/route/calibration settings, resources, timing, and output hashes. Separate smoke runs from paper runs. Distinguish historical reproduced output from freshly fitted output.

## 12. Known repository issues before execution

1. `WORKFLOWS/bowtie2/main.nf` has a pre-existing uncommitted edit: the `.map { row -> ... }` that creates chunk tuples is empty, around line 178. This no longer supplies the required alignment inputs. Preserve the user's edit and investigate before any Bowtie2 execution; do not silently restore the repository wholesale.
2. The root README's recorded hashes disagree with the current RQ2 CAMP seed-variance PNG and RQ3 Sizey-comparison PNG. Determine whether figure changes are intentional or hashes stale. A mismatch does not itself prove scientific corruption.
3. `Big_Data_paper/`, the WORKS PDF, and `Not_Needed/` were untracked at the start of this work. Do not add/commit them automatically.
4. Local shell is Windows PowerShell and Python is 3.13.13. Reproduction documentation primarily targets Linux/Python 3.9 and pinned packages. AST parsing on the local interpreter does not establish runtime compatibility.
5. Full Slurm/eBPF execution requires the documented Linux cluster, kernel/BCC support, permissions, containers, and shared storage. No cluster availability has been established in this conversation.
6. W2's original experiment plan contains historical status/scope text. Use current package README, actual retained outputs, and verification records to determine completed work, while retaining the old plan as provenance.

## 13. Writing pattern to preserve and improve

The WORKS writing pattern is:

- Abstract: problem, gap, approach, evaluation, quantitative findings.
- Introduction: practical importance, specific limitations, response, contributions.
- Formulation: define available information and unknown outcomes before mechanisms.
- Method: explain purpose, operation, equation if useful, and reason for the design.
- Experiment: population, variants, controls, protocol, questions, metrics.
- Results: comparison/figure orientation, numerical evidence, interpretation, limitation.
- Related work: group by approach and explain the difference.
- Conclusion: short scientific takeaway.

For Big Data, compress the existing CAMP design into a cited background section. The introduction must identify the unanswered question left by WORKS. Contributions should name the new evidence or method rather than repeat the original CAMP contributions.

Useful provisional relationship wording:

> Our prior WORKS paper introduced CAMP and reported selected allocation and ablation outcomes. This study extends that evaluation through [completed additional analyses/experiments].

Fill the bracket only after results exist. Use the accurate publication status. If a result is reused, state that it was previously reported; if only its analysis is new, say so.

Preserve consistent notation but avoid large notation tables that consume short-paper space. Define CH and C-hat once. Explain scopes concretely. Avoid claiming consumption must correlate with memory for all programs: streaming workloads are a counterexample, and the value is conditional on the task/context.

Improve on ambiguous OOM terminology, excessive axis narration, unsupported universal superiority/novelty statements, and unqualified causal explanations. Explain design intuitions as hypotheses unless tested. Do not carry over the claim of being the first distribution-based memory predictor without a thorough literature basis.

### Provisional six-page budget

| Content | Pages |
|---|---:|
| Title, abstract, introduction | 1.00 |
| CAMP background and distinction from WORKS | 0.50 |
| Study design, baselines, controls | 1.00 |
| Results and analysis, including figures | 2.25 |
| Related work, limitations, conclusion | 0.50 |
| References | 0.75 |
| Total | 6.00 |

This is a planning budget, not a verified typeset layout. References count. Do not assume supplementary material or appendices are permitted; the initial call disallowed an appendix, and final requirements must be checked.

### Figure/table plan

Target approximately three compact figures and one methods table:

1. **Attribution figure:** controlled feature/routing comparisons with both safety and reservation cost; optionally calibration panels.
2. **Baseline figure:** safety-cost operating points/curves for CAMP and selected distribution-aware methods, clearly marking native versus retrospective comparisons.
3. **Transfer figure:** new-input/frozen-transfer versus adaptation outcomes, only if the experiment is completed.
4. **Methods table:** feature access, predictor family, calibration, and update policy for each comparator.

If E3 is not selected, use its space for a defensible robustness analysis rather than a recycled original figure. Label sample sizes, units, seeds, interval meanings, and directions of improvement. Keep colors consistent across methods. Generate publication plots from tables with standard plotting tools, not image generation.

## 14. End-to-end execution order and completion criteria

### Phase A - Establish the boundary

- Read exact WORKS and Big Data PDFs plus reviewer notes.
- Build a claim/figure-level overlap matrix, including the cited technical report when available.
- Obtain author-provided timeline/disclosure context and actual manuscript source location.
- Prepare the chair-disclosure package; the author resolves eligibility and review expectations before final submission.

### Phase B - Freeze the scientific plan

- Agree on E1/E2/E3 scope and resources.
- Review primary literature for distribution-aware baselines; record reasons for inclusion/exclusion.
- Freeze cohorts, split groups, feature access, tuning budgets, seeds, metrics, and stopping rules.
- Record expected computational cost based on smoke timing, not guesswork.

### Phase C - Verify existing evidence

- Reproduce existing analyses in a disposable copy or new output directory using a compatible environment.
- Resolve 87/31 versus 85/30, route-dependent split conclusions, missing runtimes, and apparent manuscript/table typos.
- Create a source ledger for each retained number. Do not edit frozen outputs to make them agree with prose.

### Phase D - Implement and validate additions

- Build baseline adapters and controlled experiments without changing original scientific references.
- Test scientific invariants: hidden labels cannot influence a decision; split groups stay separate; quotas/pairing align; units and metric formulas agree.
- Use tiny smoke runs to validate the complete path, then execute predefined paper runs.
- Preserve unfavorable and failed outcomes with explanations.

### Phase E - Analyze and write

- Produce compact tables/figures and paired uncertainty estimates.
- Fill the claim ledger with evidence and limitations.
- Write methods and results first; write abstract/conclusion after findings stabilize.
- Keep prior CAMP background short and clearly cited.
- Check every contribution against WORKS and the submitted Big Data version.

### Phase F - Final publication checks

- Confirm chairs' disposition of overlap and substantial changes.
- Confirm six-page limit and the current required IEEE template/portal checks.
- Cite WORKS accurately; identify reused results/figures and satisfy reuse requirements.
- Check all figures, captions, references, equations, units, and numbers against source tables.
- Render and visually inspect the final PDF at readable resolution.
- Follow the actual camera-ready PDF validation, copyright, registration, and upload instructions; do not invent a conference ID or portal setting.
- Review applicable AI-content disclosure based on actual assistance.
- Obtain author sign-off; do not submit, register, pay, or transfer copyright without explicit authorization.

Done means: a scientifically supported six-page manuscript, documented difference from WORKS, resolved eligibility with the responsible chairs, reproducible new evidence, verified formatting, and author-approved submission materials. A polished draft alone is not proof of publication eligibility.

## 15. Claim ledger template

Maintain one row per important assertion:

| Proposed claim | Prior/new status | Evidence path and exact rows | Population/route | Uncertainty | Limitation | Manuscript location |
|---|---|---|---|---|---|---|
| Example: C-hat improves allocation under condition X | To establish | Pending | Must specify | Pending | Must specify cost and baseline | Pending |

Use explicit statuses: `prior WORKS result`, `existing artifact newly analyzed`, `fresh experiment completed`, `proposed`, `unsupported`. Never change `proposed` to `completed` because code or a plot template exists.

## 16. Immediate next steps for a continuing agent

1. Read this document and the exact WORKS PDF; preserve the excluded `Not_Needed/` boundary.
2. Produce the detailed overlap matrix and investigate the technical-report boundary before claiming novelty for RQ5 or detailed ablations.
3. Present a small, ranked experiment slate to the user/professor: controlled ablation, one or two justified uncertainty/distribution comparators, and one feasible new-input test; exclude the discarded simple-history baseline.
4. Prepare the disclosure text and comparison table for the corresponding author. No email is authorized yet.
5. Establish available Linux/cluster resources, and inspect the newly arrived `IEEE_BigData_CAMP26 (2).zip` source archive before launching expensive work or authoring a final layout.
6. Start with read-only analysis of retained common-route ablation and route-contract tables; do not start all proposed training runs automatically.

The current user authorization is to create this end-to-end planning/handoff Markdown file. It is not authorization to claim experiments were run, send messages, publish a paper, or change the frozen artifact.
