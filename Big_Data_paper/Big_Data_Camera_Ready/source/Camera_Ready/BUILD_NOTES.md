# Manuscript build instructions

## Included files

`main.tex` includes the abstract and seven numbered sections in the original
IEEE conference layout. `references.bib` is the manuscript-local bibliography.
`result_assets/` contains generated tables and vector PDF figures.
`CAMERA_READY_PREVIEW.pdf` is the included compiled manuscript.

The shared IEEEtran class and bibliography style are under `source/`.
`source/Original_Submission/` preserves the earlier manuscript source.

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

The included source compiled to six pages with Tectonic 0.17 and BibTeX.
Rendered pages matched the included preview. Citations and cross-references
resolved, with no missing glyphs or overfull boxes. The retained compiler
notices concern underfull lines and an encoding warning in an external
algorithm-package comment.
