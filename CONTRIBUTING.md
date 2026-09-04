# Contributing

Contributions that improve reproducibility, documentation, portability, or verification are welcome.

## Frozen benchmark boundary

The final cohort is a preserved historical result. Changes to `data/`, `protocol/`, `evidence/`, frozen reports, evaluations, prompts, scenario inputs, or source snapshots require a new cohort with new provenance. Corrections to public explanations should cite the existing machine-readable source and keep English/Russian facts aligned.

## Before opening a pull request

1. Use Python 3.12+ and Node.js 24.
2. Run `npm run check` from the repository root.
3. Keep release ZIPs and scratch output outside Git; `release-assets/` and `work/` are ignored.
4. Regenerate `hashes/export-files.json` and `hashes/SHA256SUMS` with `python scripts/index_export.py` after reviewed repository edits.
5. Confirm that public-facing files contain no credentials, private endpoints, or machine-specific absolute paths.
6. Explain whether the change affects licensing scope or the archive publication gate.

Contributions are submitted under Apache-2.0 only for the repository-owned scope in `LICENSE-NOTES.md`. A contribution must not relicense frozen or third-party material.
