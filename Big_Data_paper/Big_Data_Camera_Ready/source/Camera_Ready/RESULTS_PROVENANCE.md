# Manuscript result provenance

Sections IV-VI analyze retained component-study measurements and the new live Warm-Transfer/Direct-Transfer executions. Figures and tables are generated from those records. Published WORKS results are attributed in the paper.

## Manuscript mapping

Paths below are relative to the artifact root.

| Item | Source | Interpretation |
|---|---|---|
| Table I: mmap | `Reviewer_Feedbacks/W3/results/paper_native_metrics.csv` and `runs/*/seed_1996/task_predictions.tsv.gz` | Two arms on 5,026 paired tasks, with native development-selected requests: 32 versus 30 underallocations. Median prediction error worsens. |
| Table II: features | `Reviewer_Feedbacks/chat_ablation/results/route_analysis/route_stratified_metrics.csv` and eight `reference_predictions/seed_1996/*/task_predictions.tsv` | Four features within each fixed model configuration. This controls feature interpretation; it is not a newly run routing ablation. |
| Published endpoints | `Reviewer_Feedbacks/chat_ablation/published_reference/` and `results/route_analysis/paper_endpoint_reproduction.csv` | Preserve WORKS 87/31 separately from reproduction 85/30. |
| Figure 1a: downstream feedback | `Reviewer_Feedbacks/W2/results/downstream_allocation/per_repetition_metrics.tsv` and `paired_summary.tsv` | Five sampling seeds per budget, fixed model seeds, 17,067 tasks after the first update. Native request settings. Paired bootstrap intervals include zero, including at 20%. |
| Figure 1b: audit accounting | `Reviewer_Feedbacks/W5/inputs/task_level_full_ebpf_net_benefit.csv`, `audit_selections.tsv.gz`, and `results/budget_summary.csv` | All 40 budget/seed costs and seed-mean intervals were recomputed. The allocation saving is fixed at 23.59556 GiB-h, not caused by each budget. Savings have 4,577 known runtimes and 449 zero-weighted missing runtimes; all paired audit timings exist. Excludes inference, retraining, and retry costs. |
| Historical Bowtie2 assets (not included in the revised manuscript) | `RESULTS/RQ5/csv/bowtie2_{cold,warm}_{task_instances.tsv,attempts.csv}.gz` | Two existing executions on repeated inputs, 6,000 logical tasks each. Initial requests and final recorded peaks/runtimes define allocation metrics. Failed-attempt costs are excluded from unused memory-time. Recorded first-attempt OOM flags are zero; below-peak requests are not observed OOMs. |

The builder checks task identities and peaks across feature variants, recomputes allocation counts and requests, verifies mmap arms, checks downstream summary consistency, recomputes audit costs and seed-mean intervals, and recomputes live metrics. It does not rerun the W2 replay or retrain its models.

## Regeneration

From the full artifact checkout, run:

```text
python Big_Data_paper/Big_Data_Camera_Ready/source/Camera_Ready/build_result_assets.py
```

Requirements: Python, numpy, pandas, matplotlib. From an extracted standalone paper, pass `--repo-root` pointing to the full artifact. The manuscript directory includes generated tables and vector PDF figures, so ordinary TeX compilation needs neither Python nor the raw records.

`result_assets/result_provenance.json` records summaries and SHA-256 hashes for 24 input files. Inputs are read-only. Source precision is preserved; manuscript tables round only for display. Table II requests are in thousands of GiB.

## Related-work sources checked

- Witt et al.: author-hosted paper on the Humboldt University WBI publications site; existing `witt2019feedback` entry.
- Sizey: https://arxiv.org/abs/2407.16353
- Ponder: https://arxiv.org/html/2408.00047v1
- NGBoost: https://proceedings.mlr.press/v119/duan20a.html

The related-work references are included in the manuscript bibliography.


## New live experiments used in the manuscript

`RESULTS/RQ5/transfer_studies/` packages the four successful task-instance
TSVs, summaries and validated handoffs, with SHA256 checksums. These are
copies of completed execution records, not new model fits or reruns.

- Table III (`warm_transfer_table.tex`): Warm-Transfer cold, original-data warm, new input.
- Table IV (`direct_transfer_table.tex`): Warm-Transfer new input after warm versus Direct-Transfer
  new input directly from the exact Warm-Transfer cold checkpoint and history.
- Figure 2 (`live_margins.pdf`): first CAMP request margins for all four stages.
- `build_live_assets.py` verifies 6,000 unique successful tasks per stage,
  positive peaks, zero duplicate successful observations, coverage, and
  point-prediction MdAPE. It computes request/peak sums and unused memory-time
  from task rows. `live_result_provenance.json` retains source hashes and
  full-precision metrics. The main asset builder invokes this generator.

The original and new manifests select disjoint PRJEB11501 and PRJNA486148
runs. `new_dataset_selection.json` records metadata-based selection and
checks against the original project; ENA metadata includes FASTQ MD5 values.
All stages audited every task and continued online learning. Direct-Transfer reused
Warm-Transfer cold, rather than repeating cold or starting from the warm model.

Both studies use continued online learning; neither is a frozen-versus-online trial.

Reported requests, coverage and unused memory-time exclude the 128 MiB
per-task execution allowance and failed-attempt, audit, prediction and
retraining costs. Actual grants therefore differ from the nominal model
requests. Direct-Transfer's main node was downsized to 8 vCPU/32 GiB from 16 vCPU/64 GiB;
workers and the learner's four-CPU reservation were unchanged. Runtime
comparisons are not controlled. Static system features retained their
original training encoding rather than describing the physical cluster.
