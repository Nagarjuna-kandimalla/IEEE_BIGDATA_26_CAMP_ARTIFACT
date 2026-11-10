# Current artifact status

Updated 2026-11-10. This file and the root README take precedence over historical
planning/status paragraphs in copied notes.

| Component | Status | Next action |
|---|---|---|
| mmap, four-feature, downstream, audit-cost evidence | Retained measurements and analysis code included | Recompute using the documented routes; label reuse |
| Current Big Data figures/tables | Builder and inputs included | Regenerate and verify assertions |
| Six-page paper | Working draft with unresolved results and draft conclusion | Insert completed new experiments and finalize wording |
| Existing Bowtie2 cold/warm | Code, manifests, task and attempt records included | Optional live reproduction with documented infrastructure |
| Bowtie2 on new disjoint samples | Protocol only | Select samples/state; implement and validate frozen/new-manifest controls; execute |
| Ponder sizing core | Extracted original code with tested adapter | Map trace fields and compare under common history-release rules |
| Ponder original-study configuration | Not fully reproduced | Verify offset/default choices before claiming paper-equivalent behavior |
| NGBoost | Protocol and upstream link only | Implement and validate matched-feature comparison |
| Historical-percentile allocator / Q-learning | Out of minimum scope | No current implementation planned |

The Ponder adaptation is explicitly configured without the additional outer
offset. Its internal buffer and weighted residual offset remain active.
Synthetic equality checks are not experimental superiority evidence.

The source WORKS checkout had an uncommitted empty Bowtie2 chunk mapping. This
new repository uses the committed version at the source commit recorded in
`SOURCE_MANIFEST.json`; the source working tree was left untouched.

The paper skeleton and section ordering are preserved. Historical WORKS and
reviewer READMEs remain useful for their own experiments but may describe earlier
scope, machines, or verification dates. They do not certify fresh execution here.

The acceptance-email PDF and duplicate export ZIPs are not packaged. References
to them in archival notes describe the original author's workspace. Scientific
data dependencies are included or have the documented acquisition/rebuild route.

See [experiment protocols](../BIG_DATA_EXPERIMENT_PROTOCOL.md) and
[verification performed here](VERIFICATION.md).
