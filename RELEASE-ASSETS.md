# Release assets

Nine ZIP archives are prepared in the Git-ignored `release-assets/` folder. Nothing is uploaded. `assets/release-assets.json` records filenames, raw SHA-256, compressed/uncompressed bytes, member counts and manifest paths. `assets/SHA256SUMS` is the concise checksum list.

| Content | Archives |
|---|---|
| First-pass snapshots | `first-pass-new-project.zip`, `first-pass-small-project.zip`, `first-pass-large-project.zip` |
| Normalized review inputs | `review-inputs-new-project.zip`, `review-inputs-small-project.zip`, `review-inputs-large-project.zip` |
| Frozen baselines | `baselines-new-project.zip`, `baselines-small-project.zip`, `baselines-large-project.zip` |

Every archive contains only the 12 selected run IDs for its scenario. Baselines repeat the relevant frozen tree per independent run; new Plain has no files. Text/binary bytes are retained. ZIP timestamps are fixed to the evidence date; source timestamps are not a benchmark metric. Credential files have explicit hash-only exclusions. Git history, installed dependencies and full transcripts are excluded.

Publication plan: complete the redistribution-rights review in `THIRD_PARTY_NOTICES.md`, select a tag tied to the reviewed export commit, and upload only approved files from `assets/release-upload-manifest.json` together with `assets/SHA256SUMS`. Link the committed member manifests and verify downloaded bytes with `python scripts/verify.py --assets`.

The repository's Apache-2.0 grant has the bounded scope in `LICENSE-NOTES.md`. It does not cover archive members. All nine ZIP entries currently carry `prepared_local_awaiting_rights_confirmation`; adding required notices inside an archive creates a new release candidate and requires regenerated asset hashes and member manifests. This local export has no remote, tag, release URL, or upload.
