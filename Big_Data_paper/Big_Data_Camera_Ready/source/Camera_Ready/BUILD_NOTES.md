# Manuscript build instructions

## Included files

`main.tex` includes the abstract and seven numbered sections in the original
IEEE conference layout. `references.bib` is the manuscript-local bibliography.
`result_assets/` contains generated tables and vector PDF figures.
`CAMERA_READY_PREVIEW.pdf` is the included compiled manuscript.

The IEEEtran class and bibliography style are under `source/`. The package
contains the camera-ready source and its referenced tables and figures.

## Build from the artifact root

The build helper copies the manuscript project into `build/paper/` and runs the
selected compiler there:

```bash
python SCRIPTS/BIGDATA/build_paper.py --engine latexmk
```

For Tectonic 0.17:

```bash
python SCRIPTS/BIGDATA/build_paper.py --engine tectonic
```

Use `--executable /path/to/compiler` when the compiler is not on `PATH`.
The output is `build/paper/camp_bigdata.pdf`. The Tectonic path uses a temporary
T1-font wrapper; manuscript sections and shared style files are unchanged.

## Direct TeX and Overleaf builds

From `Big_Data_paper/Big_Data_Camera_Ready/`, run:

```bash
pdflatex -jobname=camp_bigdata source/Camera_Ready/main.tex
bibtex camp_bigdata
pdflatex -jobname=camp_bigdata source/Camera_Ready/main.tex
pdflatex -jobname=camp_bigdata source/Camera_Ready/main.tex
```

Alternatively:

```bash
latexmk -pdf -jobname=camp_bigdata source/Camera_Ready/main.tex
```

For Overleaf, upload the project directory and select
`source/Camera_Ready/main.tex` as the main document. Recompile from scratch
when switching from the original submission to this source.

The main file resolves section and bibliography paths from the project root,
`source/`, or `Camera_Ready/`. Its bibliography commands use the local
`references.bib` and the shared `IEEEtran.bst`.

## Regenerate tables and figures

From the artifact root:

```bash
python Big_Data_paper/Big_Data_Camera_Ready/source/Camera_Ready/build_result_assets.py
```

The analysis dependencies are pinned in
`SCRIPTS/BIGDATA/requirements-analysis.txt`. TeX compilation uses the included
assets and does not require Python. See [RESULTS_PROVENANCE.md](RESULTS_PROVENANCE.md)
for data sources, metrics, and interpretation.

## Verified build

The included source compiled to seven pages with Tectonic 0.17 and BibTeX.
The preview was rebuilt after integrating the completed Warm-Transfer/Direct-Transfer results and all four pages were inspected. Citations and cross-references
resolved, with no missing glyphs or overfull boxes. The retained compiler
notices concern underfull lines and an encoding warning in an external
algorithm-package comment.


## Completed live-study revision

The live methods and results use Warm-Transfer as the main cold/warm/new-input sequence
and Direct-Transfer as a shared-cold-checkpoint warm-pass ablation. Both new-input arms
continue learning; there is no frozen-model arm. Nominal CAMP metrics exclude
the 128 MiB execution allowance. The control-node downsizing and retained
system-feature encoding are disclosed as validity limits. Only the two named studies enter the published comparison.

`build_result_assets.py` now also calls `build_live_assets.py`, which reads the
self-contained `RESULTS/RQ5/transfer_studies/` copies. TeX builds still need
only the included generated assets. `MANUSCRIPT_REVIEW.md` records the scope
and remaining evidence limits; it is not part of the submitted manuscript.
