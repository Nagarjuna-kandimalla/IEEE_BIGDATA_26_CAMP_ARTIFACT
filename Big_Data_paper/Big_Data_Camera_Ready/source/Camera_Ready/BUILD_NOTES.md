# Camera-ready working draft

Only files inside `source/Camera_Ready/` were edited or added. The original submission, shared bibliography, class, style, figures, and other archive entries are unchanged.

## Main document and build

In Overleaf, select `source/Camera_Ready/main.tex` as the main document. Recompile from scratch if old auxiliary files remain. The main file resolves section and bibliography paths from the archive root, `source/`, or `Camera_Ready/`.

For a conventional TeX installation, run from the archive root:

```sh
pdflatex -jobname=camp_bigdata source/Camera_Ready/main.tex
bibtex camp_bigdata
pdflatex -jobname=camp_bigdata source/Camera_Ready/main.tex
pdflatex -jobname=camp_bigdata source/Camera_Ready/main.tex
```

Alternatively use `latexmk -pdf -jobname=camp_bigdata source/Camera_Ready/main.tex`.

The camera-ready-local bibliography is based on the shared original and adds the accepted WORKS citation. The original bibliography path did not point to `source/references.bib` when compiling from the archive root. The prior pipeline PDF was also absent from the archive; the rewritten background explains the pipeline without depending on that missing asset.

## File names

- `2_problem-and-running-example.tex` -> `2_problem_formulation.tex`
- `3_camp_design.tex` -> `3_camp_background_and_relationship.tex`
- `6_related-work.tex` -> `6_related_work.tex`

The class, packages, title/author block, eight input slots, their order, and bibliography position are preserved. Input and bibliography paths were repaired in `main.tex`. The inherited title remains provisional.

## Editorial status

The abstract is provisional. Introduction, problem formulation, and CAMP background/relationship to WORKS have been drafted. Sections IV-VII retain their slots but contain explicit working-draft outlines; their old text is preserved below as noncompiled comments. No new experiment or numerical result is claimed. The six-page final layout will be assessed after experiments, figures, and focused references are written. This draft is not ready for submission.

The WORKS entry uses accepted/to-appear status supplied by the authors; no DOI or page numbers have been invented. Chair disclosure and eligibility remain unresolved as described in the planning handoff outside this archive.

## Verification performed

The source compiled with Tectonic 0.17.0 and its BibTeX pass. The three-page `CAMERA_READY_PREVIEW.pdf` was visually inspected; citations and cross-references resolve, with no missing glyphs or overfull boxes in the preview build. For the local XeTeX-based preview only, a temporary wrapper preloaded T1 font encoding to retain IEEEtran's Times-family fonts. This wrapper is not part of the manuscript skeleton. Use pdfLaTeX for the normal Overleaf build; that engine was not available locally. Remaining local-build notices were underfull lines and an encoding notice in the downloaded algorithm package, not missing citations.

All 38 original archive files outside Camera_Ready were verified byte-for-byte unchanged. The original ZIP is preserved. The preview is a partial working paper, not a completed six-page camera-ready submission.

## Title and abstract revision: online deployment

Updated the title to "Online Deployment and Evaluation of Consumption-Aware Memory Allocation for Scientific Workflows" and rewrote the abstract around the agreed deployment study, measurement/feature ablations, selective auditing and cost, historical/probabilistic baselines, and unseen-input Bowtie2 adaptation. Quantitative findings remain explicit `?` placeholders. This pass changes only the title and abstract manuscript content; Sections I-VII retain their previous drafts and will be aligned section by section (including removal of parked routing/calibration study promises).

Recompiled the three-page preview with Tectonic 0.17.0 and BibTeX using a temporary T1-font wrapper outside the source. All three rendered pages were inspected; references resolve and no overfull boxes or missing characters were reported. Existing notices remain for one underfull paragraph in Section III and an encoding comment in the downloaded algorithm package. This is a partial working draft, not the final six-page paper.

### Existing Bowtie2 results restored to the abstract

The abstract now reports the retained repeated-input cold-to-warm deployment: 6,000 logical tasks per run, 71.96% lower total requested memory, and 99.78% warm-run initial-allocation coverage of recorded peak memory. Coverage is not labeled first-attempt completion. Unseen-input frozen-versus-online evaluation remains explicitly pending. This supersedes the earlier abstract placeholders; no new experiment was run. The three-page PDF was rebuilt and all pages visually checked; references resolve.

## Introduction revision

Rewrote Section I following the accepted WORKS introduction's progression: scheduling problem, concrete information limitations, existing CAMP approach, deployment evidence, extension questions, experimental objectives, and section roadmap. The introduction now covers measurement/feature ablations, downstream selective-audit cost, historical and probabilistic baselines, and unseen-input frozen-versus-online evaluation. Removed promises of standalone routing and calibration ablations. Existing Bowtie2 results are labeled prior evidence and peak coverage is distinguished from execution success. NGBoost and the existing CAMP technical report use entries already present in the camera-ready bibliography. Only Section I manuscript content changed in this pass; later sections still await alignment.

Recompiled with Tectonic and BibTeX. The partial draft now spans four pages; all pages were rendered and visually inspected. No undefined citations/references, overfull boxes, or missing characters were reported. Existing package-comment encoding and Section III underfull-line notices remain. Final six-page length will be assessed when the remaining sections and figures are written.

### Introduction prose completed

Section I now presents a continuous motivation and three evaluation aspects: measurement/features, allocation benefit/cost, and online deployment/adaptation. It explicitly positions the WORKS results and technical-report Bowtie2 study as prior evidence, defines the purpose of historical and probabilistic baselines, and states the frozen-history versus online-update comparison without claiming pending runs have completed. The title, abstract, skeleton, and other manuscript sections were not changed in this pass.

The four-page partial paper was rebuilt; all rendered pages were inspected. Citations and cross-references resolve, with no overfull boxes or missing glyphs. Minor underfull-line notices and the existing algorithm-package comment encoding notice remain. The introduction is complete as prose; experimental findings and the remaining paper sections are still pending.

## Sections II and III completed; technical-report wording corrected (2026-11-10)

Removed the introduction's explicit technical-report sentence and its citation. The current linked 13-page report was checked: its extracted text contains neither Bowtie2/cold/warm discussion nor the quoted deployment values. The previous assertion that this report includes the Bowtie2 case study was unsupported. The introduction now cites the existing artifact for retained deployment results and keeps the WORKS attribution. The unused bibliography entry remains available but does not appear in the compiled reference list. IEEE's general submission policy requires acknowledgment of relevant reused work and disclosure of overlap; it does not prescribe a technical-report discussion in the introduction. Any other publicly circulated version containing reused results must still be accounted for during final disclosure review.

Section II now defines initial allocation, completed/ingested history, audit selection and budget, coverage, unused memory-time and its measurement limits, and frozen versus online state. Section III now explains read return counting, descriptor attribution, task-descendant filtering, filemap_fault entry-event measurement and its 4096-byte assumption, compatibility scopes, consumption proxy cross-fitting, quantile prediction, residual calibration, audit selection, and the actual Nextflow/Bowtie2 integration. It distinguishes generic periodic audit selection, full auditing in retained live runs, and selective-auditing experiments. The relationship to WORKS now matches the agreed scope; independent routing/calibration/scope ablation sweeps remain excluded.

Implementation statements were checked against AUDIT/helper_scripts/exp2/ebpf_audit_py39.py and targeted_ebpf.config, SCRIPTS/RQ2 modeling/calibration/pipeline code, and the RQ5 Nextflow configuration, prediction service, learner, and launcher. No workflow or experiment code was changed and no new experiment was run. All manuscript changes are inside Camera_Ready; the original ZIP and shared files remain unchanged.

The four-page partial draft compiled with Tectonic and BibTeX, all pages were visually checked, and no unresolved citations/cross-references, overfull boxes, or missing glyphs were reported. Minor underfull-line and the existing downloaded-package comment encoding notices remain. Sections IV-VII are still outlines; the six-page final layout is pending their completion.

### Comment cleanup (2026-11-10)

Removed all 472 comment-only lines from Sections IV-VII, including the inherited noncompiled WORKS text. Their active text and labels are unchanged. The earlier note that these files retain old source in comments is superseded. The original submission remains preserved separately. Recompiled with Tectonic/BibTeX; all four pages have identical extracted text and rendered pixels to the previously reviewed PDF.

### Acknowledgment added (2026-11-10)

Added the WORKS funding acknowledgment as an unnumbered section between the conclusion and references: "This work is supported by NASA under grant NASA-AIST-21-0095." Wording and grant number were verified against page 8 of the accepted WORKS PDF; a terminal period was added. No other manuscript content changed. The four-page draft compiled successfully. The first three pages render identically to the previously inspected build; the final page was visually checked, including the acknowledgment and bibliography.

## Sections IV-VI populated with retained evidence

The working draft is now six pages including references. Section IV specifies separate cohorts and protocols; Section V contains mmap, four-feature, downstream-auditing, audit-accounting, and Bowtie2 results; Section VI covers feedback allocation, Sizey, Ponder, NGBoost, and WORKS. Three tables and two vector figures were added inside Camera_Ready. Fixed-configuration comparisons control feature interpretation; parked routing/calibration sweeps were not run. Pending baselines, unseen-input results, and complete deployment costs are marked explicitly. The conclusion is unchanged.

See RESULTS_PROVENANCE.md and result_assets/result_provenance.json for evidence mapping and regeneration. No scientific inputs, workflow code, Original_Submission files, or shared archive files changed. Generated assets compile without Python.

The six-page PDF compiled with Tectonic/BibTeX using the temporary T1-font wrapper. All pages were visually checked; the first three render identically to the previous build. Numerical anchors, citations, section references, figures/tables, acknowledgment, bibliography, and 24 input hashes were verified. No undefined references, overfull boxes, missing characters, or clipped chart labels remain. Minor underfull-line and existing package-comment encoding notices remain. The normal Overleaf/pdfLaTeX path is preserved but was not executed locally.

### Standalone memory-history baseline discarded (2026-11-10)

At the user's request, removed the historical-percentile allocator experiment from the abstract, introduction, background/extension boundary, pending results, and related-work motivation. Updated RESULTS_PROVENANCE.md and the external planning handoff so the removed baseline is not treated as pending. This supersedes earlier baseline-planning notes above. CAMP's own memory-history features, existing A+P evidence, and retained measurements are unchanged. NGBoost and optional Ponder were not removed by this targeted scope edit. Original reviewer notes remain preserved as historical evidence. No baseline experiment was implemented or run.

The six-page draft compiled successfully; all six rendered pages were checked. No unresolved citations/references, overfull boxes, or missing characters were reported. The original shared files and source skeleton remain preserved.
