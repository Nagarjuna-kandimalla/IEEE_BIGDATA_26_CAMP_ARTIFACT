# CAMP Live Run Analysis

- Run: `/shared/ubuntu/camp-rq5-reproduction-20261111/live/runs/exp02_cold`
- Decision attempts: 6009
- Completed outcome attempts: 6009
- Successful task instances: 6000 / 6000
- First-attempt OOMs: 0
- Total OOM attempts: 0
- Retried task instances: 9

## Variant comparison

| Variant | q50 median APE (%) | Allocation coverage | Request / peak |
|---|---:|---:|---:|
| A | 0.716 | 0.995 | 5.347 |
| A+P | 1.498 | 1.000 | 38.782 |
| A+P+C | 1.658 | 0.995 | 4.264 |

## Process results

| Process | Tasks | OOMs | Retries | Peak p50 MiB | Peak p95 MiB | Peak max MiB | CAMP coverage | CAMP request / peak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ALIGN_CHUNK | 1974 | 0 | 2 | 44.0 | 44.6 | 46.3 | 0.995 | 1.507 |
| BUILD_INDEX | 1 | 0 | 0 | 118.2 | 118.2 | 118.2 | 1.000 | 10.146 |
| DOWNLOAD_REFERENCE | 1 | 0 | 0 | 9.0 | 9.0 | 9.0 | 1.000 | 125.671 |
| DOWNLOAD_RUN | 38 | 0 | 0 | 9.2 | 9.3 | 9.3 | 1.000 | 656.667 |
| FLAGSTAT_BAM | 1974 | 0 | 3 | 37.0 | 37.9 | 38.8 | 0.995 | 2.586 |
| INDEX_BAM | 1974 | 0 | 4 | 37.1 | 37.9 | 38.6 | 0.995 | 2.910 |
| SPLIT_RUN | 38 | 0 | 0 | 22.2 | 22.4 | 22.6 | 1.000 | 279.300 |

The applied live allocation is `A+P+C`. `A` and `A+P` are
counterfactuals computed at the same prelaunch decision point.
Infrastructure retries are retained and are not counted as OOMs.
