# Verification during Big Data packaging

Date: 2026-11-10. This record concerns the separate Big Data artifact checkout.
Earlier logs copied from WORKS/reviewer packages describe their own runs.

## Executed here

- Regenerated the manuscript result assets from the copied repository alone.
  Assertions passed for eight feature/configuration rows, two published
  endpoints, two mmap arms, 25 paired downstream summaries, 40 audit-budget
  selections, and both retained Bowtie2 executions.
- Compiled the paper with the included `build_paper.py` helper using Tectonic
  0.17 and its BibTeX pass. Output has six pages. No undefined references,
  missing citations, missing characters, or overfull boxes were found. Existing
  underfull-line notices and an algorithm-package comment-encoding warning remain.
- Ran the standalone Ponder test command in this repository: all 123 checks
  passed, including 48 exact original-core comparisons on synthetic histories.
- Verified copied upstream Ponder source and dependency hashes during that build.
- Checked the package for GitHub's per-file size limit and recognizable credential
  patterns in text files before upload. No matching credentials were found.
- Verified the delivered snapshot using `verify_artifact.py --check-gzip` before
  upload; the file manifest records the exact files in this initial artifact.

Local analysis used Python 3.13, NumPy 2.2.2, pandas 2.2.3, and Matplotlib 3.10.0;
Ponder used JDK 11. Historical model-training packages retain their own Python
3.9 requirements. The manuscript asset checks validate scientific numerical
summaries, not byte-identical PDF metadata across different toolchains.

The manuscript checks recompute metrics from retained measurements. The Ponder
checks exercise the isolated predictor on synthetic histories. Historical
experiment and training verification records are included with their respective
reproduction packages.
