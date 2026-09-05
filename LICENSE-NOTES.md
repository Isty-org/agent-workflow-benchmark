# License scope

The repository includes the Apache License 2.0 text in `LICENSE`. Its grant covers material authored by the benchmark publisher for this public export:

- top-level public documentation and community files;
- `.github/` repository metadata and CI configuration;
- portable export, verification, replay, package-building, and materialization source in `scripts/`;
- repository-level schemas in `schemas/`;
- publication metadata authored for this export, including package wrapper README, manifests, checksum files, sanitization records, and Stage 6/7 verification records.

Isty-owned Classic Spec-Driven AI Development methodology files are also available under Apache-2.0. [`assets/classic-methodology-scope.json`](assets/classic-methodology-scope.json) identifies this scope by exact source path, raw SHA-256, and byte count at methodology commit `b5c3e3c6576570ec348b79305e0d455469d0642c`. Public package manifests list every member that satisfies all three conditions.

All other preserved or projected benchmark evidence retains its existing terms. This separately licensed scope includes:

- `data/`, `protocol/`, `evidence/`, `reports/`, `evaluator/`, `inputs/`, `manifests/`, and `provenance/`;
- source member inventories and the local byte-preserved Stage 5 raw archives under `release-assets/`;
- BMAD and Prist material, source-project baselines, measured implementations, normalized reviewer inputs, and generated work records outside the exact Classic hash scope;
- third-party packages, lockfile dependencies, hosted services, model access, credentials, names, logos, and trademarks.

Existing copyright, attribution, license, and notice files stay attached to their original components. [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) records official BMAD MIT/trademark sources, Isty Classic licensing, evidence-rights boundaries, sanitization, and the release gate.
