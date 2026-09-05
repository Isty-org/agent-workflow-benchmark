# Export inventory

English [README.md](README.md) is the primary public entry point; [README.ru.md](README.ru.md) provides fact-aligned Russian documentation. Repository-owned material is Apache-2.0 within [LICENSE-NOTES.md](LICENSE-NOTES.md), with archive and method scope in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

| Location | Content |
|---|---|
| `data/cohort.json` | Authoritative 36-row selection, task IDs, evidence and hash-algorithm mapping |
| `data/rows/` | 36 exact result-value projections from the final report |
| `reports/benchmark-v7-final/` | Original Markdown/HTML report, source JSON and two verification summaries |
| `inputs/method-locks/` | 36 selected setup-lock projections |
| `inputs/launch/` | 27 V7 frozen launch-component declarations |
| `protocol/` | V7 frozen scenarios, prompts, rubric, answer bank, contracts/runtime files; V7C addendum |
| `evidence/` | Only selected first-pass/usage/evaluation/review evidence, final check receipts, pricing and locks |
| `manifests/` | Original V7 and V7C source manifests |
| `evaluator/`, `schemas/`, `scripts/` | Frozen final check harnesses, schemas and portable verification/replay/materialization tools |
| `provenance/`, `verification/` | Source-byte lineage, source audit, explicit credential exclusions and acceptance evidence |
| `assets/` | Raw provenance, nine sanitized package definitions, raw/package checksums, Classic license scope and full member inventories |
| `hashes/` | Complete raw SHA-256/byte-count inventory for the Git payload |
| `release-assets/` (Git ignored) | Nine byte-preserved raw ZIPs plus nine generated sanitized public packages |
| `.github/`, community files | Cross-platform Git-only CI, issue/PR templates and contribution/security guidance |
| `verification/stage5-payload-lock.json` | Immutable aggregate lock for Stage 5 `data/`, `protocol/` and `evidence/` bytes |
| `assets/release-upload-manifest.json` | Approved upload list with package hashes, raw provenance and sanitization counts |

| Scenario | Plain | BMAD | Classic Spec-Driven AI Development | Prist |
|---|---:|---:|---:|---:|
| New project | 3 | 3 | 3 | 3 |
| Small project | 3 | 3 | 3 | 3 |
| Large project | 3 | 3 | 3 | 3 |

First-pass raw content: 11,805 files plus nine credential-only hashes. All raw archive categories combined: 32,124 file entries. The public packages include 32,096 evidence members after 28 path-accounted exclusions. Source snapshot checks: 11,814 historical hashes. Measured-task lineage: 27 V7 + 9 V7C. Official scores reproduced: 36/36. See `PROVENANCE.md` for the selected V7 replacement, uniform large evaluation, both hash conventions and two inherited raw-score-field limitations.

The exact path inventory and sizes are machine-readable in `hashes/export-files.json`. Installed dependencies, scratch outputs, raw ZIPs, and generated packages stay outside ordinary Git history. Source repositories remain read-only.

The Git-only CI suite is `npm run check`. It runs verification, score replay, package-builder negative tests, bilingual result/source parity, frozen-payload validation, license/upload-manifest checks, and a public secret/local-path scan. Raw and sanitized package bytes are verified together with `python scripts/verify.py --assets`.
