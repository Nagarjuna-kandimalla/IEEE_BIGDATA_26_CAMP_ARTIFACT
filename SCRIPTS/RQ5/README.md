# RQ5: live feedback, new inputs and warm-pass ablation

The completed live studies and their reproduction are documented in
[**LIVE_EXPERIMENTS.md**](LIVE_EXPERIMENTS.md).

- **Warm-Transfer:** clean fresh cold → original-data warm → new input; main paper evidence.
- **Direct-Transfer:** reuse the exact Warm-Transfer cold checkpoint → same new input; no extra warm pass.

All four actual stages have 6,000 successful logical tasks. All use full auditing
and online learning. The new-input study is not frozen-model inference.

## Entry points

```bash
# Recompute all archived metrics and compare flagstats; Python standard library.
python3 SCRIPTS/RQ5/live/reproduce_results.py

# Inspect and verify self-contained model/container bundles.
python3 SCRIPTS/RQ5/live/models.py list
python3 SCRIPTS/RQ5/live/models.py verify --deep

# Configure a new external Slurm workspace; edit cluster.example.json first.
python3 SCRIPTS/RQ5/live/configure.py --root /shared/camp/repeat-01 --config /shared/camp/cluster.json
python3 SCRIPTS/RQ5/live/submit.py --root /shared/camp/repeat-01
```

The full guide includes the exact data manifests/MD5 values, offline rebuild,
checkpoint restoration, direct-from-cold route, auditing prerequisites, hardware,
resource admission, execution allowance, archive restoration, validation and limits.
Models and matching histories are under `DATA/RQ5/live/models/`; stage results and
historical provenance are under `RESULTS/RQ5/live_experiments/`.

The older retained 898.39/251.93 GiB cold/warm tables remain distinct under
`RESULTS/RQ5/csv/`. Their figure can still be regenerated with
`figures/generate_rq5_bowtie_feedback.py`. The prior instructions are preserved
in [LEGACY_COLD_WARM.md](LEGACY_COLD_WARM.md); use the portable live guide for
new execution rather than the original site-specific unattended scripts.
