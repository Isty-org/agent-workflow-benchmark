# Third-party and separately licensed material

This file documents the redistribution scope visible in the frozen local snapshots. It does not replace licenses or notices shipped with individual components.

## Method material

### BMAD Method

The benchmark used BMAD Method 6.11.0, module `bmm`, Codex integration. BMAD files are present in frozen baseline and result archives. The isolated new-project baseline contains the captured BMAD installation under `_bmad/` and `.agents/skills/bmad-*`.

The captured BMAD method tree contains no file whose path identifies it as a license or notice. The repository therefore records no license grant for redistributing those archived files. Apache-2.0 in this repository does not apply to them. Archive upload requires a final rights review and any upstream license or attribution required by the rights holder.

### Classic Spec-Driven AI Development

The benchmark used the Russian-language `classic-2026.08` edition. Its frozen method files are included in baseline and result archives. The isolated new-project Classic baseline contains no license/notice file. The planned English edition is a translation and was not tested in this cohort.

Apache-2.0 in this repository does not apply to archived Classic method material. Archive upload requires confirmation of the publisher's authority and the terms intended for those files.

### Prist

The Prist condition used a pinned hosted service environment and a project-local connection kit. The captured new-project kit contains no license/notice file. Credential-bearing `.prist/connection.json` files are excluded from archives and represented only by hashes.

Apache-2.0 in this repository does not apply to the hosted service, kit, service output, names, or trademarks. Archive upload requires confirmation of redistribution terms for the captured kit and any service-originated material.

## Product baselines and implementations

The baseline, first-pass, and reviewer-input archives contain source-project material and measured implementations. Their original notices and lockfiles are preserved as archive members. The large-project snapshots include component-specific notices such as:

- `native/whisper/licenses/openai-whisper-LICENSE.txt`;
- `native/whisper/licenses/whisper.cpp-LICENSE.txt`;
- `packaging/macos/licenses/SourceGear-SQLite.txt`;
- `packaging/windows/notices/licenses/Apache-2.0.txt`;
- `packaging/windows/notices/licenses/MIT.txt`;
- `packaging/windows/notices/licenses/OFL-1.1.txt`;
- component overrides and third-party-notice policy files under `packaging/`.

Those files govern their respective components. A generic license text inside a product snapshot does not grant that license to the complete archive. Package manifests and lockfiles identify additional dependencies whose terms continue to apply.

The frozen new-project and small-project snapshots do not establish a blanket archive-level redistribution grant. Generated or agent-authored measured outputs are also outside the Apache-2.0 scope defined for this public repository.

## Release gate

The nine ZIP files are prepared locally and remain unpublished. `assets/release-upload-manifest.json` marks every archive as awaiting third-party-rights confirmation. Before upload, the publisher must:

1. confirm authority to distribute each method tree, product baseline, measured implementation, and normalized reviewer input;
2. include every license, attribution, source-offer, or notice required by those components;
3. retain the exact archive bytes, filenames, SHA-256 values, and member manifests if the reviewed archives are approved;
4. regenerate archives and their manifests as a new release candidate if any notice must be added inside an archive.

Snapshot evidence for this review is recorded in `verification/license-snapshot-audit.json`. Naming a method or service describes the experimental condition and does not imply endorsement or trademark permission.
