# Attribution and extraction record

This standalone Ponder baseline was added on 2026-11-10. It is released under
GPL-3.0-or-later; see [COPYING](COPYING). It contains code from the
[Common Workflow Scheduler for Kubernetes](https://github.com/CommonWorkflowScheduler/KubernetesScheduler),
pinned to commit `3046e19d5a3a237c5f6c0df4d16f33e643b31828`.

The original copyright and license notices are preserved. The upstream
`Predictor.java` and `TaskScaler.java` identify Copyright (c) 2023,
Florian Friederici. Other included upstream files retain their original
contents and attribution to their upstream authors. The upstream project
declares GPL-3.0-or-later in its `pom.xml`.

Research attribution: Fabian Lehmann, Jonathan Bader, Ninon De Mecquenem,
Xing Wang, Vasilis Bountris, Florian Friederici, Ulf Leser, and Lauritz Thamsen,
*Ponder: Online Prediction of Task Memory Requirements for Scientific Workflows*,
2024. [Paper](https://arxiv.org/abs/2408.00047).

## What was preserved and what was added

- Nine source files under `upstream/src/` are byte-for-byte copies. These include
  `PonderPredictor`, its unequal-loss regression and weighted residual offset,
  the predictor interfaces, and input/peak extractors. They are compiled directly.
- `upstream/reference/` contains unchanged `MemoryScaler.java`, `TaskScaler.java`,
  and `pom.xml` for inspection. They are not compiled into this adapter.
- `src/` contains new minimal task/logging adapters and the standalone event
  interface. The final request transformation is adapted from `MemoryScaler`.
  These additions are marked with their date and license.
- Scheduler task objects, submission, Kubernetes integration, scheduler-driven
  task re-prediction, retries, and workflow scheduling are not extracted.
- `upstream_manifest.json` records the source commit, file hashes, and separately
  downloaded dependency hashes. Build artifacts/dependency JARs are ignored by Git.

Dependencies retain their own licenses. Their compiled JARs are fetched from
Maven Central at the exact URLs/hashes recorded in the manifest. No license
change to the surrounding CAMP project is asserted by this notice.

This is a pinned implementation extraction, not verification that the pinned
revision is exactly the revision used for every experiment in the 2024 paper.
