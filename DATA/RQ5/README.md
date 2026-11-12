# RQ5 data

`inputs/split_manifest_primary.tsv.gz` is the compressed train/calibration/test
assignment used to rebuild the RQ5 seed-1996 initial model. It covers the same
33,516 tasks stored in `../RQ2/camp_ml_cohort_33516.csv.gz`.

The RQ5 workspace preparation command expands both files outside the Git tree:

```bash
python3 SCRIPTS/RQ5/prepare_workspace.py \
  --artifact-root "$(pwd -P)" \
  --work-root "${CAMP_RQ5_WORK_ROOT:?set CAMP_RQ5_WORK_ROOT}"
```

The Bowtie2 live-run manifest is under `WORKFLOWS/bowtie2/data`; it supplies
the ENA HTTPS URLs and chunk counts used to create the 6,000-task workflow.

Verify the split input with:

```bash
gzip -t DATA/RQ5/inputs/split_manifest_primary.tsv.gz
echo '8f394de506a8e27448611af57eaa0235c1c6291b8657b6485dd09b0fe744f7ce  DATA/RQ5/inputs/split_manifest_primary.tsv.gz' | sha256sum -c -
```

## Completed live experiments

`live/inputs/` contains the original/new ENA manifests and MD5 metadata.
`live/models/` contains exact offline/terminal model-history snapshots and SIF
containers in a deduplicated verified blob store. See
[the complete live reproduction guide](../../SCRIPTS/RQ5/LIVE_EXPERIMENTS.md).
Raw FASTQs are fetched from their exact public URLs with MD5 verification;
the large input/output payload bytes are not ordinary Git objects.
