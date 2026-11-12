# Live Warm-Transfer/Direct-Transfer paper records

Four stages, 6,000 unique successful tasks each. Warm-Transfer: cold -> warm -> new input.
Direct-Transfer: reuse the exact Warm-Transfer cold checkpoint -> same new input; cold is not rerun.
All stages use full auditing and online learning. Model requests exclude the
separate 128 MiB execution allowance. The main node was downsized for Direct-Transfer.

Regenerate manuscript assets from the repository root:

```bash
python Big_Data_paper/Big_Data_Camera_Ready/source/Camera_Ready/build_live_assets.py
```

Each stage includes its task table, summary and validated handoff. The packaged
manifests/ENA metadata and selection report identify the datasets. Absolute paths
inside handoffs record the original execution; regeneration uses these local copies.
`SHA256SUMS` verifies the packaged source files. See the manuscript's
`RESULTS_PROVENANCE.md` for definitions and interpretation limits.
