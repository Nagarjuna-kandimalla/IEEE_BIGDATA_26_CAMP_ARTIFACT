# RQ5 live data and checkpoints

See [the full experiment/reproduction guide](../../../SCRIPTS/RQ5/LIVE_EXPERIMENTS.md).

- `inputs/`: exact original/new task manifests, ENA metadata with FASTQ MD5,
  selection records and the reference FASTA/FAI snapshot.
- `models/index.json`: five unique scientific bundles (offline seed and four
  terminal model/history snapshots), plus exact Apptainer containers. Direct-Transfer cold
  aliases the Warm-Transfer cold checkpoint. Original source paths are provenance only.
- `models/blobs/`: SHA256-addressed lossless gzip bytes, split into <=24 MiB parts
  when needed; duplicates are stored once. No Git LFS server is needed.

```bash
python3 SCRIPTS/RQ5/live/models.py verify --deep
python3 SCRIPTS/RQ5/live/models.py extract warm_transfer_cold /shared/camp/cold
```

The extractor verifies compressed and uncompressed hashes and safely restores
relative paths. It rebases only the operational handoff paths and keeps the
original handoff. Use the pinned Python/model library versions before loading
trusted joblib models. Full model/feature/history bytes are included locally;
large sample FASTQs remain public ENA objects fetched with MD5 validation.
`SHA256SUMS` verifies every packaged data file from this directory.
