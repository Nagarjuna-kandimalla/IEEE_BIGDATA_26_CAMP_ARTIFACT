# CAMP Live Run Analysis

- Run: `/shared/ubuntu/camp-rq5-reproduction-20261111/live/runs/exp02_warm`
- Decision attempts: 6015
- Completed outcome attempts: 6015
- Successful task instances: 6000 / 6000
- First-attempt OOMs: 0
- Total OOM attempts: 0
- Retried task instances: 15

## Variant comparison

| Variant | q50 median APE (%) | Allocation coverage | Request / peak |
|---|---:|---:|---:|
| A | 0.585 | 0.997 | 1.057 |
| A+P | 0.875 | 1.000 | 25.113 |
| A+P+C | 1.128 | 0.996 | 1.051 |

## Process results

| Process | Tasks | OOMs | Retries | Peak p50 MiB | Peak p95 MiB | Peak max MiB | CAMP coverage | CAMP request / peak |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ALIGN_CHUNK | 1974 | 0 | 2 | 44.1 | 44.6 | 46.5 | 0.993 | 1.041 |
| BUILD_INDEX | 1 | 0 | 0 | 118.2 | 118.2 | 118.2 | 1.000 | 6.547 |
| DOWNLOAD_REFERENCE | 1 | 0 | 0 | 9.0 | 9.0 | 9.0 | 1.000 | 84.294 |
| DOWNLOAD_RUN | 38 | 0 | 4 | 9.2 | 9.3 | 9.3 | 1.000 | 1.088 |
| FLAGSTAT_BAM | 1974 | 0 | 4 | 37.1 | 37.9 | 38.6 | 0.997 | 1.049 |
| INDEX_BAM | 1974 | 0 | 4 | 37.1 | 37.9 | 38.7 | 0.996 | 1.047 |
| SPLIT_RUN | 38 | 0 | 1 | 22.2 | 22.4 | 22.5 | 1.000 | 1.058 |

The applied live allocation is `A+P+C`. `A` and `A+P` are
counterfactuals computed at the same prelaunch decision point.
Infrastructure retries are retained and are not counted as OOMs.
