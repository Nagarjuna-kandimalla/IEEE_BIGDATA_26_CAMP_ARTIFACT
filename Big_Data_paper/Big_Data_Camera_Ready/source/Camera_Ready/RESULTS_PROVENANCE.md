# Retained evidence in the six-page working draft

Sections IV-VI use existing artifact records. No new model training, workflow execution, baseline evaluation, or unseen-input experiment was run. Figures are newly drawn from retained results; their appearance does not make the observations new experiments. Published WORKS results are attributed in the paper.

## Manuscript mapping

Paths below are relative to the artifact root.

| Item | Source | Interpretation |
|---|---|---|
| Table I: mmap | `Reviewer_Feedbacks/W3/results/paper_native_metrics.csv` and `runs/*/seed_1996/task_predictions.tsv.gz` | Two arms on 5,026 paired tasks, with native development-selected requests: 32 versus 30 underallocations. Median prediction error worsens. |
| Table II: features | `Reviewer_Feedbacks/chat_ablation/results/route_analysis/route_stratified_metrics.csv` and eight `reference_predictions/seed_1996/*/task_predictions.tsv` | Four features within each fixed model configuration. This controls feature interpretation; it is not a newly run routing ablation. |
| Published endpoints | `Reviewer_Feedbacks/chat_ablation/published_reference/` and `results/route_analysis/paper_endpoint_reproduction.csv` | Preserve WORKS 87/31 separately from reproduction 85/30. |
| Figure 1a: downstream feedback | `Reviewer_Feedbacks/W2/results/downstream_allocation/per_repetition_metrics.tsv` and `paired_summary.tsv` | Five sampling seeds per budget, fixed model seeds, 17,067 tasks after the first update. Native request settings. Paired bootstrap intervals include zero, including at 20%. |
| Figure 1b: audit accounting | `Reviewer_Feedbacks/W5/inputs/task_level_full_ebpf_net_benefit.csv`, `audit_selections.tsv.gz`, and `results/budget_summary.csv` | All 40 budget/seed costs and seed-mean intervals were recomputed. The allocation saving is fixed at 23.59556 GiB-h, not caused by each budget. Savings have 4,577 known runtimes and 449 zero-weighted missing runtimes; all paired audit timings exist. Excludes inference, retraining, and retry costs. |
| Table III / Figure 2: Bowtie2 | `RESULTS/RQ5/csv/bowtie2_{cold,warm}_{task_instances.tsv,attempts.csv}.gz` | Two existing executions on repeated inputs, 6,000 logical tasks each. Initial requests and final recorded peaks/runtimes define allocation metrics. Failed-attempt costs are excluded from unused memory-time. Recorded first-attempt OOM flags are zero; below-peak requests are not observed OOMs. |

The builder checks task identities and peaks across feature variants, recomputes allocation counts and requests, verifies mmap arms, checks downstream summary consistency, recomputes audit costs and seed-mean intervals, and recomputes live metrics. It does not rerun the W2 replay or retrain its models.

## Regeneration

From the full artifact checkout, run:

```text
python Big_Data_paper/Big_Data_Camera_Ready/source/Camera_Ready/build_result_assets.py
```

Requirements: Python, numpy, pandas, matplotlib. From an extracted standalone paper, pass `--repo-root` pointing to the full artifact. The ZIP includes generated tables and vector PDF figures, so ordinary TeX compilation needs neither Python nor the raw records.

`result_assets/result_provenance.json` records summaries and SHA-256 hashes for 24 input files. Inputs are read-only. Source precision is preserved; manuscript tables round only for display. Table II requests are in thousands of GiB.

## Related-work sources checked

- Witt et al.: author-hosted paper on the Humboldt University WBI publications site; existing `witt2019feedback` entry.
- Sizey: https://arxiv.org/abs/2407.16353
- Ponder: https://arxiv.org/html/2408.00047v1
- NGBoost: https://proceedings.mlr.press/v119/duan20a.html

Existing bibliography entries are used. No comparison results for Ponder or NGBoost have been invented.

## Remaining work

NGBoost, optional Ponder, unseen-input frozen-versus-online Bowtie2, and prediction/retraining costs remain pending and marked `?` in Section V. The simple historical-percentile allocator was removed from scope at the user's request on 2026-11-10; it is not a pending experiment. CAMP's own memory-history features and retained A+P comparisons remain. The conclusion remains a draft. When new results arrive, revise abstract and introduction claims, the protocol, and the conclusion consistently, then rebalance the six-page layout. This build preserves the IEEE class, typography, margins, and section order.
