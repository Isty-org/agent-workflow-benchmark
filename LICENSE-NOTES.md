# License scope

The repository includes an Apache License 2.0 text in `LICENSE`. Its grant applies to material authored by the benchmark publisher for this public export:

- top-level public documentation and community files;
- `.github/` repository metadata and CI configuration;
- portable export, verification, replay, and materialization source in `scripts/`;
- repository-level schemas in `schemas/`;
- publication-specific metadata created for this export, including `assets/release-upload-manifest.json` and Stage 6 verification records.

The Apache-2.0 grant does not extend to preserved or projected benchmark payload whose rights may belong to other parties. Excluded scope includes:

- `data/`, `protocol/`, `evidence/`, `reports/`, `evaluator/`, `inputs/`, `manifests/`, and `provenance/`;
- `assets/manifests/`, `assets/release-assets.json`, `assets/SHA256SUMS`, and every file represented by them;
- the Git-ignored `release-assets/` archives and all archive members;
- BMAD, Classic, and Prist method material; source-project baselines; measured implementations and normalized reviewer inputs;
- third-party packages, lockfile dependencies, hosted services, model access, credentials, names, logos, and trademarks.

The exclusions define licensing scope and do not alter the benchmark's integrity or availability for verification. Existing copyright, attribution, license, and notice files remain attached to their original components. [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) records the local snapshot review and the publication gate for release archives.
