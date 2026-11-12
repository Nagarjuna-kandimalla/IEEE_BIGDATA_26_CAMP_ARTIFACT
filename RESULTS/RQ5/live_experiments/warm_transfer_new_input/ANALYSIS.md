# CAMP Live Run Analysis

- Run: `/shared/ubuntu/camp-rq5-reproduction-20261111/live/runs/exp02_new_input`
- Decision attempts: 6005
- Completed outcome attempts: 6005
- Successful task instances: 6000 / 6000
- First-attempt OOMs: 0
- Total OOM attempts: 0
- Retried task instances: 5

## Variant comparison

| Variant | q50 median APE (%) | Allocation coverage | Request / peak |
|---|---:|---:|---:|
| A | 4.640 | 0.916 | 1.218 |
| A+P | 5.570 | 1.000 | 20.995 |
| A+P+C | 4.735 | 0.942 | 1.167 |

## Process results

| Process | Tasks | OOMs | Retries | Peak p50 MiB | Peak p95 MiB | Peak max MiB | CAMP coverage | CAMP request / peak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ALIGN_CHUNK | 1974 | 0 | 2 | 68.2 | 96.4 | 99.3 | 0.831 | 1.225 |
| BUILD_INDEX | 1 | 0 | 0 | 118.1 | 118.1 | 118.1 | 1.000 | 14.524 |
| DOWNLOAD_REFERENCE | 1 | 0 | 0 | 9.1 | 9.1 | 9.1 | 1.000 | 188.268 |
| DOWNLOAD_RUN | 38 | 0 | 0 | 9.2 | 9.2 | 9.2 | 1.000 | 1.086 |
| FLAGSTAT_BAM | 1974 | 0 | 3 | 36.0 | 37.6 | 38.7 | 0.995 | 1.087 |
| INDEX_BAM | 1974 | 0 | 0 | 36.0 | 37.6 | 38.5 | 0.996 | 1.088 |
| SPLIT_RUN | 38 | 0 | 0 | 22.2 | 22.4 | 22.6 | 1.000 | 1.152 |

The applied live allocation is `A+P+C`. `A` and `A+P` are
counterfactuals computed at the same prelaunch decision point.
Infrastructure retries are retained and are not counted as OOMs.
