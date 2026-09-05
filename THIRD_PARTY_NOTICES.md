# Third-party and separately licensed material

This document records the rights and notice boundaries for the repository and its nine public sanitized evidence packages. Component-specific license and notice files inside evidence trees retain their original effect.

## BMAD Method 6.11.0

The BMAD condition used BMAD Method 6.11.0, module `bmm`, with Codex integration. The official annotated [`v6.11.0` tag](https://github.com/bmad-code-org/BMAD-METHOD/releases/tag/v6.11.0) has tag object `178414679b11a171ca1597b0ebc1723ed488fc73` and resolves to commit [`9ce3c397c9b238de96f7365da8019f6f66b059da`](https://github.com/bmad-code-org/BMAD-METHOD/commit/9ce3c397c9b238de96f7365da8019f6f66b059da). Its `package.json` declares the MIT license.

Each public package includes exact copies from that tag:

| Upstream file | Bytes | SHA-256 |
|---|---:|---|
| [`LICENSE`](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.11.0/LICENSE) | 1,572 | `0aa79baf6328b4a1e694ce10a12ffc36d7666554da128dff0e8fcda0fc536a66` |
| [`CONTRIBUTORS.md`](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.11.0/CONTRIBUTORS.md) | 1,331 | `1f0d0736ff06fcea2c504834b9d13196f37ca57fae5cf9054899dcec4ed36ad4` |
| [`TRADEMARK.md`](https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.11.0/TRADEMARK.md) | 2,805 | `ce57ad749e43277c6021e5d5085980b33c9bf8f67a070bbbf07e041ccdddc58b` |

The MIT permission and copyright notice applies to BMAD software. The upstream TRADEMARK terms govern the BMad, BMad Method, BMad Core, BMad Code, logo, branding, and tagline marks. This benchmark uses those names descriptively to identify the measured condition. BMad Code, LLC has provided no endorsement, approval, certification, or sponsorship of this benchmark.

## Classic Spec-Driven AI Development

The Classic condition used the Russian `classic-2026.08` edition from [Spec-Driven AI Development](https://github.com/Isty-org/spec-driven-ai-dev). Isty licenses its Classic methodology files under Apache-2.0. Every public package includes the exact Apache license and Isty NOTICE:

- Apache-2.0 LICENSE: `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`;
- Isty NOTICE: `2159c5eb9c573e8dbe7d6f11ecdb8d49beea36c1c709bbc1754d765c0ae38049`.

[`assets/classic-methodology-scope.json`](assets/classic-methodology-scope.json) defines the licensed scope by 39 accepted source paths, byte counts, and SHA-256 values at methodology commit `b5c3e3c6576570ec348b79305e0d455469d0642c`. A package member receives the Classic Apache scope only when its Classic-run relative path, byte count, and raw SHA-256 all match that definition. Product code, generated work records, local identities, and modified files retain their own evidence terms.

## Prist and other preserved evidence

The Prist condition used a pinned hosted service environment and a project-local connection kit. Public evidence is provided under the benchmark publisher's authorization for inspection and verification. Publication grants no additional reuse rights for the Prist service or kit, service output, product snapshots, measured implementations, normalized reviewer inputs, names, logos, or trademarks. Existing third-party terms continue to apply.

The large-project evidence retains component notices including OpenAI Whisper, whisper.cpp, SourceGear SQLite, Apache-2.0, MIT, OFL-1.1, and packaging-specific notice policies. Dependency manifests and lockfiles remain available for further component-level review.

Credential-bearing `.prist/connection.json` files were excluded before the Stage 5 raw archives were built. Nine SHA-256-only records preserve their provenance in [`provenance/credential-exclusions.json`](provenance/credential-exclusions.json).

## Sanitized public packages

The nine Stage 5 raw ZIPs remain local byte-for-byte provenance anchors and are never direct release assets. [`assets/SHA256SUMS`](assets/SHA256SUMS) records their identities.

The nine public release assets are deterministic sanitized derivatives. The builder transfers every permitted source member with byte-for-byte content identity and records all decisions in the package `MANIFEST.json`. Across the nine packages:

- 32,096 raw members are included with matching source SHA-256 and byte counts;
- 27 `specs/.me` local identity members are excluded;
- one `__pycache__/serve.cpython-312.pyc` generated cache member is excluded;
- nine earlier `.prist/connection.json` credential exclusions remain hash-only provenance records;
- absolute, traversal, backslash, directory, and drive-qualified source paths are rejected;
- high-confidence secret patterns are rejected, with exact known test-fixture hashes classified separately.

Each package contains `README.md`, `MANIFEST.json`, `SOURCE-MEMBER-MANIFEST.json`, `CLASSIC-FILE-SCOPE.json`, `SHA256SUMS`, the applicable notices, and its sanitized evidence tree. Package metadata states that the asset is a derivative and provides no claim of exact archive completeness.

The release upload gate is recorded in [`assets/release-upload-manifest.json`](assets/release-upload-manifest.json). Every listed asset reached `publishable` only after deterministic rebuild, package-to-raw comparison, path checks, notice validation, license-scope validation, and secret scanning.
