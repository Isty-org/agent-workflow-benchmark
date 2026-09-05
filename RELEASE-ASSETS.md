# Release assets

The `v1.0.0` release uses nine deterministic sanitized evidence packages. Their source Stage 5 ZIPs remain unchanged in the Git-ignored `release-assets/` folder and are excluded from direct upload.

| Content | Public packages |
|---|---|
| First-pass snapshots | `first-pass-{new,small,large}-project-evidence-package.zip` |
| Normalized review inputs | `review-inputs-{new,small,large}-project-evidence-package.zip` |
| Frozen baselines | `baselines-{new,small,large}-project-evidence-package.zip` |

[`assets/release-assets.json`](assets/release-assets.json) and [`assets/SHA256SUMS`](assets/SHA256SUMS) preserve the raw archive identities. [`assets/release-upload-manifest.json`](assets/release-upload-manifest.json) records each public package size, SHA-256, raw source identity, member counts, and `publishable` status. [`assets/PACKAGE-SHA256SUMS`](assets/PACKAGE-SHA256SUMS) is the concise public checksum list.

## Sanitization and accounting

Every permitted source member is copied with identical bytes. Package paths add an `evidence/` prefix. The per-package `MANIFEST.json` records included members and all raw exclusions by path, bytes, SHA-256, and reason.

The public set contains 32,096 evidence members. Sanitization excludes 27 `specs/.me` local identity files and one generated Python cache file. The first-pass raw manifests also retain nine hash-only `.prist/connection.json` exclusions made before raw archive creation.

Each package is self-contained for inspection: it includes the original member manifest, a hash-defined Classic Apache scope, BMAD 6.11.0 MIT/CONTRIBUTORS/TRADEMARK notices, Isty Apache LICENSE/NOTICE, an evidence-rights notice, package README, and member checksums. Included files retain existing component notices inside the evidence tree.

## Build and verify

```text
python scripts/build_evidence_packages.py build
python scripts/build_evidence_packages.py verify
python scripts/verify.py --assets
```

The builder uses stored ZIP members, a fixed timestamp, fixed modes, sorted paths, and canonical LF metadata. A second build must produce the same nine outer SHA-256 values. The verifier compares every included package member directly with the local raw ZIP, checks every excluded-member hash, scans for prohibited paths and secrets, validates notices, and rejects raw ZIP embedding.

Release upload is limited to the nine `publishable` files in the upload manifest. Large snapshots stay outside Git history, keeping ordinary clones compact.
