# Agent Workflow Benchmark

**[Русская версия](README.ru.md)**

An evidence-preserving benchmark of four agent-development workflows across three software-change scenarios. The final cohort contains **3 scenarios × 4 methods × 3 independent repetitions = 36 measured first-pass tasks**.

This repository is the portable public export: frozen prompts, scenario inputs, evaluations, machine-readable results, reports, evidence links, verification tools, and release-asset manifests. Original benchmark artifacts remain in their source language.

## Results

Every row below is a median of three measured tasks in the same scenario/method cell. Cost is the provider-reported **measured task cost** under the frozen pricing snapshot. Elapsed time runs from measured-task start to the first final response. Exact milliseconds and exact calculated USD values are shown; the minute value is the report's readable display.

| Scenario | Method | Quality median (/100) | Measured task cost median (USD) | Elapsed median |
|---|---|---:|---:|---:|
| New project | Plain | 69 | $0.42385148 | 2,013,443 ms (33.6 min) |
| New project | BMAD | 69 | $1.36481868 | 3,629,356 ms (60.5 min) |
| New project | Classic | 45 | $3.12769884 | 4,074,624 ms (67.9 min) |
| New project | Prist | 87 | $0.26662576 | 1,257,000 ms (20.9 min) |
| Small existing project | Plain | 35 | $10.077087 | 4,204,885 ms (70.1 min) |
| Small existing project | BMAD | 29 | $1.44226984 | 3,648,434 ms (60.8 min) |
| Small existing project | Classic | 39 | $7.90102716 | 4,194,725 ms (69.9 min) |
| Small existing project | Prist | 69 | $0.43872212 | 1,556,000 ms (25.9 min) |
| Large existing project | Plain | 98 | $4.05826076 | 3,811,712 ms (63.5 min) |
| Large existing project | BMAD | 25 | $0.8408026 | 2,041,483 ms (34.0 min) |
| Large existing project | Classic | 82 | $6.09135428 | 2,394,283 ms (39.9 min) |
| Large existing project | Prist | 98 | $0.2068444 | 815,000 ms (13.6 min) |

In this 36-task snapshot, Prist had the lowest median measured task cost and shortest median elapsed time in all three scenarios. Its quality median was highest for the new and small scenarios and tied Plain at 98 for the large scenario. Plain recorded 69, 35, and 98 quality medians; BMAD recorded 69, 29, and 25; Classic recorded 45, 39, and 82; Prist recorded 87, 69, and 98. These are observed cohort results under the conditions below.

The original Russian [final report](reports/benchmark-v7-final/BENCHMARK-REPORT.md) includes token medians, all 36 task rows, score breakdowns, and scenario commentary. [source-snapshot.json](reports/benchmark-v7-final/source-snapshot.json) is the authoritative machine-readable result source.

## Design: 3 × 4 × 3

### Scenarios

1. **New project:** build a local reading-list web app with three statuses, Russian UI, and persistence across restarts.
2. **Small existing project:** add Telegram message editing and deletion while preserving authorization, queues, retries, deduplication, integration-friendly errors, and documentation.
3. **Large existing project:** add recent-recording search by meeting title or app, live filtering, reset, empty state, and Russian/English UI.

The exact user prompts are preserved in Russian under [protocol prompts](protocol/benchmark-v7-luna-xhigh-n3-2026-09-01/prompts/) and in the frozen evidence.

### Methods

- **Plain:** the source repository and ordinary Codex behavior, with no compared methodology installed.
- **BMAD:** BMAD Method 6.11.0, module `bmm`, Codex integration.
- **Classic:** a repository-based workflow using specifications, Work Items, traceability, and repository checks.
- **Prist:** hosted Prist with a project-local connection kit and service-owned spec-driven workflow.

The Classic condition used the **Russian-language `classic-2026.08` edition**. The planned English-language edition is a translation of that workflow. This cohort did not run or evaluate the English edition, so these results do not measure it.

### Execution conditions

- Three independent runs per scenario/method cell (`n=3/cell`), 12 cells and 36 measured tasks.
- One model/reasoning profile throughout: `gpt-5.6-luna` with `xhigh` reasoning.
- Prepared, frozen baselines. The new-project Plain baseline was empty; existing-project conditions started from their assigned frozen product baseline and prepared method/canon state.
- One first pass, captured at the first final response, with no repair turns. Up to two clarification questions were allowed; the median was zero in every cell.
- Measured agents used no browser/UI and saw only their assigned product/method root.
- Objective checks ran three times against the unchanged first-pass state. Quality combined the frozen objective suite with blind reviews and severity caps.

Quality weights were 50 functional, 20 regression/build/smoke, 20 architecture/project fit, and 10 scope/UX/security. A critical finding capped the official score at 49 and a major finding at 69.

## Measurement boundaries

The cost column covers provider usage for the measured development task. Prepared baseline construction, historical method adoption, historical canon creation, human waiting, and evaluation are outside that metric. The observed cycle incurred no new setup/canon provider cost because prepared baselines were used. The benchmark supports claims about **measured task cost and elapsed time** for this cohort. It does not establish total lifecycle cost.

External evaluation for the nine Prist rows used 29,710,054 tokens and cost $1.14781888. It is recorded separately and excluded from method ratios. Equivalent external-evaluation cost was not collected for all four methods, so evaluator-cost comparisons are outside the benchmark.

## Provenance and known evidence limitations

The authoritative cohort combines **27 V7 Plain/BMAD/Classic tasks** with **9 permissions-corrected V7C Prist tasks**. The selected Classic small-project replica 3 is the permitted V7 infrastructure replacement. All 12 large-project scores use the same V7C supplemental uniform evaluator; comparator implementations, usage, and timing still come from V7. [PROVENANCE.md](PROVENANCE.md) documents the selection and hash conventions.

Two inherited V7 evaluations lack an explicit raw-score field. The report therefore carries the capped official value in `quality.rawBeforeSeverityCap` for `v7-new-bmad-r3` (69 reported; 85 reconstructed from checks) and `v7-new-plain-r2` (69 reported; 81 reconstructed). Both official scores remain 69 under the major-finding cap. Re-evaluation reports these two known discrepancies and rejects any additional one.

Prompts, scenario inputs, evaluations, JSON, reports, and evidence are retained in their original language and content. Historical absolute local paths remain only inside unchanged evidence and locks. Public documentation and runnable instructions use repository-relative paths.

## Reproducibility levels

### 1. Verify

Verify the complete Git payload, cohort structure, task identities, lineage, evidence links, pricing, timing, scores, and aggregate medians. Python 3.12+ is required.

```text
npm run verify
```

The asset check requires the nine byte-preserved local raw ZIPs and nine sanitized packages under the Git-ignored `release-assets/` directory. It verifies every package member against its raw source:

```text
python scripts/verify.py --assets
```

Details: [VERIFY.md](VERIFY.md).

### 2. Re-evaluate

Replay the scoring logic from frozen objective outcomes, blind reviews, weights, and severity caps:

```text
npm run reevaluate
```

This recomputes 36 scores and reproduces every official score. Details: [REEVALUATE.md](REEVALUATE.md).

### 3. Rerun

Materialize a verified baseline and compose a fresh launch prompt for a new experimental cohort:

```text
python scripts/prepare.py --run v7-new-bmad-r1 --kind baselines --destination work/rerun-new-bmad-r1 --prompt-output work/rerun-new-bmad-r1.txt
```

A rerun requires the original model/reasoning profile, scenario dependencies, sanitized release packages, and an available pinned Prist environment. Local identity files are recreated from `specs/.me.template` after materialization and stay outside public evidence. New runs create new provenance. Details: [RERUN.md](RERUN.md).

For the CI-equivalent Git-only suite:

```text
npm run check
```

## Repository map

| Location | Purpose |
|---|---|
| `data/cohort.json`, `data/rows/` | Authoritative 36-row selection and exact result projections |
| `reports/benchmark-v7-final/` | Original Russian Markdown/HTML report and source JSON |
| `protocol/`, `inputs/` | Frozen prompts, rubric, contracts, baselines, launch components, and method locks |
| `evidence/`, `manifests/` | Selected first-pass, usage, evaluation, review, check, freeze, and source-manifest records |
| `evaluator/`, `scripts/`, `schemas/` | Frozen check harnesses and portable verification/replay/materialization tools |
| `provenance/`, `verification/`, `hashes/` | Source lineage, acceptance evidence, payload locks, and raw SHA-256 inventory |
| `assets/` | Raw provenance, sanitized package definitions, member inventories, Classic license scope, checksums, and upload manifest |

See [INVENTORY.md](INVENTORY.md) for counts and [RELEASE-ASSETS.md](RELEASE-ASSETS.md) for archive handling.

## Limitations

- `n=3/cell` is a first comparative snapshot. It does not estimate long-run variance or establish behavior across other tasks, models, reasoning profiles, or tool versions.
- The three scenarios represent three project sizes and specific changes. Other domains can produce different rankings.
- Prepared baselines make this a measured-task comparison. Historical adoption and canon-construction costs were not measured.
- First-pass and browser-free constraints describe the benchmark protocol. Interactive or repaired workflows can behave differently.
- Medians compress within-cell variation. All 36 rows remain available in the final report and machine-readable snapshot.
- Prist evaluation cost was collected separately; a four-method evaluator-cost comparison is unavailable.
- The English Classic edition was not part of the cohort.
- The two inherited `rawBeforeSeverityCap` discrepancies described above remain source limitations.

## License and publication status

Apache-2.0 applies to the benchmark publisher's repository scaffolding, public documentation, verification tooling, package metadata, and hash-matched Isty-owned Classic methodology files within [LICENSE-NOTES.md](LICENSE-NOTES.md). Other frozen inputs, evidence, reports, method material, product baselines, generated implementations, dependencies, service names, and trademarks retain their existing terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

The `v1.0.0` [upload manifest](assets/release-upload-manifest.json) approves nine deterministic sanitized evidence packages. Across them, 32,096 source members retain byte-identical content; 27 local `specs/.me` identities and one generated `.pyc` cache are excluded with hash accounting. The nine raw ZIPs remain unchanged local provenance inputs and are never direct release assets. Package hashes are listed in [assets/PACKAGE-SHA256SUMS](assets/PACKAGE-SHA256SUMS).
