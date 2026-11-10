# Artifact contents

| Artifact | Included material | Instructions |
|---|---|---|
| mmap signal ablation | Paired read/read+mmap inputs, prediction records, training and analysis code | [W3](../Reviewer_Feedbacks/W3/README.md) |
| Four-feature analysis | Matched cohort, split assignments, native and fixed-route predictions, fitting and plotting code | [Feature ablation](../Reviewer_Feedbacks/chat_ablation/README.md) |
| Downstream auditing | Selective/random replay records, audit budgets, sampling seeds, analysis and fitting code | [W2](../Reviewer_Feedbacks/W2/README.md) |
| Audit-cost accounting | Paired timing measurements, frozen allocations, audit selections, accounting and bootstrap code | [W5](../Reviewer_Feedbacks/W5/README.md) |
| Matched-budget/coverage analysis | Retained inputs, comparison code, numerical references | [W1](../Reviewer_Feedbacks/W1/README.md) |
| Bowtie2 cold/warm deployment | Workflow, input manifest, online allocation code, task/attempt records, plotting code | [RQ5](../SCRIPTS/RQ5/README.md) |
| Ponder adapter | Pinned original predictor source, standalone event interface, correctness checks, license and attribution | [Ponder](../SCRIPTS/BASELINES/ponder/README.md) |
| Manuscript | TeX sections, bibliography, IEEE style files, tables, figures, compiled PDF | [Build notes](../Big_Data_paper/Big_Data_Camera_Ready/source/Camera_Ready/BUILD_NOTES.md) |
| Reproduction helpers | Snapshot verification, analysis requirements, isolated paper build | [Root README](../README.md) |

The retained WORKS data and implementation use their original directory names
to preserve reproduction paths. [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json)
records the imported source revision and file hashes.
[VERIFICATION.md](VERIFICATION.md) records executed checks. The root
`ARTIFACT_MANIFEST.json` lists the files and hashes in the distributed snapshot.
