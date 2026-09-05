# Verify

Requires Python 3.12+; offline verification uses the standard library.

```text
npm run verify
npm run reevaluate
npm run check:public
python scripts/verify.py --assets
python scripts/self_test.py
```

The first command verifies the complete Git payload against `hashes/export-files.json` and `hashes/SHA256SUMS`, 36 unique run/task IDs, 12 cells with replicas 1–3, exact 27+9 measured-task lineage, model/reasoning, first-pass policy, linked usage/cost/timing, final evaluations and three objective repetitions. Means and medians are recomputed from original final row values.

The asset check first verifies all nine local Stage 5 ZIP and member raw SHA-256 values and byte counts, then recomputes every available first-pass historical hash under its recorded algorithm. Nine credential-only hashes complete the original inventory. It also verifies all nine sanitized public packages: outer identity, source raw provenance, complete included/excluded accounting, direct byte equality for 32,096 included members, 28 exclusion hashes, prohibited paths, secret patterns, checksums, pinned notices, and Classic Apache hash scope. Asset verification needs the raw ZIPs in `release-assets/` and public packages in `release-assets/packages/`; Git-only verification does not.

`npm run check:public` validates that both README result tables contain the same 12 cells and match `source-snapshot.json`; checks the Stage 5 byte lock for `data/`, `protocol/` and `evidence/`; reconciles nine raw provenance sources with nine publishable sanitized packages; checks Apache/third-party scope; and scans public-facing files for secret-like values and machine-specific absolute paths. `npm run check` adds score replay and package-builder negative tests to the complete CI-equivalent Git-only sequence.

Single-archive verification in PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'release-assets/first-pass-large-project.zip'
```

Compare a raw provenance source against `assets/SHA256SUMS` and a public package against `assets/PACKAGE-SHA256SUMS`. With GNU tools, `sha256sum -c hashes/SHA256SUMS` verifies the Git payload from the root. The JSON inventory and sums exclude themselves; the Git commit anchors their contents. Raw archives, generated packages, and reproduction scratch directories are excluded from the Git payload index.

`provenance/export-audit.json` and `verification/acceptance.json` record export acceptance. Historical source summaries remain unchanged and describe their original scope. The published verifier needs no original Windows source paths.
