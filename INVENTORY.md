# Export inventory

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
| `assets/` | Nine release-asset definitions, raw checksums and full member inventories |
| `hashes/` | Complete raw SHA-256/byte-count inventory for the Git payload |
| `release-assets/` (Git ignored) | Nine prepared ZIP files: first pass, reviewer inputs and baselines by scenario |

| Scenario | Plain | BMAD | Classic Spec-Driven AI Development | Prist |
|---|---:|---:|---:|---:|
| New project | 3 | 3 | 3 | 3 |
| Small project | 3 | 3 | 3 | 3 |
| Large project | 3 | 3 | 3 | 3 |

First-pass archive content: 11,805 files plus nine credential-only hashes. All archive categories combined: 32,124 file entries. Source snapshot checks: 11,814 historical hashes. Measured-task lineage: 27 V7 + 9 V7C. Official scores reproduced: 36/36. See `PROVENANCE.md` for the selected V7 replacement, uniform large evaluation, both hash conventions and two inherited raw-score-field limitations.

The exact path inventory and sizes are machine-readable in `hashes/export-files.json`. Installed dependencies, scratch outputs and ZIP archives do not enter ordinary Git history. Source repositories remain read-only.
