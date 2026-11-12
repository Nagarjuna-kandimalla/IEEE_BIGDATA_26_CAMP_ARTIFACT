# CAMP Live Run Analysis

- Run: `/shared/ubuntu/camp-rq5-reproduction-20261111/live/runs/exp03_new_input`
- Decision attempts: 6010
- Completed outcome attempts: 6010
- Successful task instances: 6000 / 6000
- First-attempt OOMs: 0
- Total OOM attempts: 0
- Retried task instances: 10

## Variant comparison

| Variant | q50 median APE (%) | Allocation coverage | Request / peak |
|---|---:|---:|---:|
| A | 1.767 | 0.949 | 1.154 |
| A+P | 2.301 | 1.000 | 20.795 |
| A+P+C | 2.685 | 0.958 | 1.236 |

## Process results

| Process | Tasks | OOMs | Retries | Peak p50 MiB | Peak p95 MiB | Peak max MiB | CAMP coverage | CAMP request / peak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ALIGN_CHUNK | 1974 | 0 | 5 | 68.2 | 95.4 | 99.1 | 0.883 | 1.422 |
| BUILD_INDEX | 1 | 0 | 0 | 118.1 | 118.1 | 118.1 | 1.000 | 6.551 |
| DOWNLOAD_REFERENCE | 1 | 0 | 0 | 9.0 | 9.0 | 9.0 | 1.000 | 83.675 |
| DOWNLOAD_RUN | 38 | 0 | 2 | 9.2 | 9.2 | 9.2 | 1.000 | 1.089 |
| FLAGSTAT_BAM | 1974 | 0 | 1 | 36.9 | 37.7 | 38.7 | 0.996 | 1.050 |
| INDEX_BAM | 1974 | 0 | 2 | 36.8 | 37.7 | 38.6 | 0.992 | 1.053 |
| SPLIT_RUN | 38 | 0 | 0 | 22.2 | 22.4 | 22.5 | 1.000 | 1.183 |

The applied live allocation is `A+P+C`. `A` and `A+P` are
counterfactuals computed at the same prelaunch decision point.
Infrastructure retries are retained and are not counted as OOMs.
