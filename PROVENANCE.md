# Final-cohort provenance

`data/cohort.json` selects exactly 36 results by task ID from the unchanged final `source-snapshot.json`. Each selection identifies its first-pass record, usage, final objective receipt, final evaluation, method lock and prompt evidence. Original source JSON, evaluations, prompts and inputs retain their language and values.

The Classic condition is the Russian-language `classic-2026.08` edition captured in the frozen setup trees. A future English edition is a translation and was not run or evaluated by this cohort.

The 27 Plain/BMAD/Classic task records come from V7. The nine Prist task records come from permissions-corrected V7C. The selected V7 Classic small/r3 task is `01a061d1-f717-7bd3-9b76-60c62ac807d4`, the permitted infrastructure replacement captured in V7 `retry-1`. Only that selected first pass is exported for its cell. It has no repair turns. Its dispatch projection records the frozen-envelope/scenario policy.

All 12 large-project final scores use the same V7C supplemental uniform evaluator. The nine large comparator implementations, task IDs, usage and timing still come from V7. `evaluationSeries` distinguishes evaluation provenance from measured-task provenance. This does not add measured tasks. The final evaluator lock identifies the original harness and additive semantic-copy correction. Existing frozen-check references inside original evaluations remain historical pointers; the cohort's `references.checks` identifies the final scoring input.

Complete original manifests are retained as source documents. Historical status fields, including `complete_verified_first_snapshot_n1`, are preserved; final sample size is established by 36 selected task IDs and 12 groups with replicas 1–3. Pending fields in early capture records remain historical metadata. Final evaluations and cohort references determine the exported result.

## Hash conventions

- 26 selected original V7 records: SHA-256 of Node UTF-8 decoding (replacement characters for invalid byte sequences), followed by CRLF-to-LF conversion and UTF-8 encoding. This historical transformation also touched binary files; it is reproduced only for comparison with the recorded digest.
- V7 Classic small/r3 replacement and all nine V7C records: SHA-256 of raw bytes.
- Every exported file, archive and archive member: SHA-256 of raw bytes, with byte counts. `sourceHashAlgorithm` explicitly chooses the historical verifier per row. Archive bytes are never normalized. `.gitattributes` disables checkout newline conversion in this export.

The source audit matched all 11,814 first-pass file hashes under their recorded conventions. Nine credential-bearing `.prist/connection.json` files are represented by hashes only. First-pass archives contain 11,805 files, with nine explicit exclusions completing the historical inventory. Method baselines are built from raw Git blobs at exact setup commits; the offline verifier reconstructs all 36 Git trees, including the empty new Plain tree. This avoids archive-time newline transformations. Baseline executable modes come from Git; first-pass/review records did not capture modes and those archive members use regular-file mode 0644. Reviewer inputs are the original normalized review folders, separately archived.

`provenance/file-origins.json` distinguishes byte-for-byte copies from JSON projections. `provenance/source-file-hashes.json` identifies source working-tree bytes: many final source artifacts were outside the control repository's HEAD, so its commit alone is insufficient provenance. `provenance/source-integrity-selected.json` preserves the relevant projection of the historical source-integrity index; the original count 2,349 describes that verifier's scope, not the public-export file count.

V7 stores frozen prompt components and a launch composition declaration. V7C stores complete frozen launch strings. The V7 launch declaration is not a recovered full dispatch transcript. Rerun prompts are explicit compositions using original components and a new assigned root.

Historical bundle pointers in first-pass records did not supply standalone bundle files. Release ZIPs and member manifests provide portable content, including captured uncommitted files. Newly materialized repositories have new Git identities; source HEAD/tree identities remain recorded in metadata.

The original `artifact-verification.json` also lists `PRIST-SERVICE-IMPROVEMENTS.md`. That service-improvement document is outside this comparison export. Its identity is preserved, and it is the sole intentional omission from the original report artifact list.

## Inherited raw-score field limitation

Two V7 evaluations omit an explicit `rawScore` field. The final report inherited the capped official value into `quality.rawBeforeSeverityCap`: new/BMAD/r3 reports 69 while its check points sum to 85; new/Plain/r2 reports 69 while its check points sum to 81. Both have a major-finding cap of 69. This export preserves those source fields exactly and returns the separately reconstructed raw values during score replay. All 36 official scores, aggregates, task identities and 27+9 lineage remain unchanged. The verifier treats only these two exact inherited cases as disclosed limitations and rejects any additional discrepancy.
