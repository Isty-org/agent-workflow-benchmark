# Verify

Requires Python 3.12+; offline verification uses the standard library.

```text
python scripts/verify.py
python scripts/reevaluate.py
python scripts/verify.py --assets
python scripts/self_test.py
```

The first command verifies the complete Git payload against `hashes/export-files.json` and `hashes/SHA256SUMS`, 36 unique run/task IDs, 12 cells with replicas 1–3, exact 27+9 measured-task lineage, model/reasoning, first-pass policy, linked usage/cost/timing, final evaluations and three objective repetitions. Means and medians are recomputed from original final row values.

The asset check verifies archive/member raw SHA-256 values and byte counts, then recomputes every available first-pass historical hash under its recorded algorithm. Nine credential-only hashes complete the original inventory. Asset verification needs `release-assets/`; Git-only verification does not.

Single-archive verification in PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath 'release-assets/first-pass-large-project.zip'
```

Compare against `assets/SHA256SUMS`. With GNU tools, `sha256sum -c hashes/SHA256SUMS` verifies the Git payload from the root. The JSON inventory and sums exclude themselves; the Git commit anchors their contents. Archives and reproduction scratch directories are excluded from the Git payload index.

`provenance/export-audit.json` and `verification/acceptance.json` record export acceptance. Historical source summaries remain unchanged and describe their original scope. The published verifier needs no original Windows source paths.
