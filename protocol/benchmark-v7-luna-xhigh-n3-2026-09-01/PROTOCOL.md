# Benchmark V7 — natural-use method comparison

## Purpose

V7 preserves the validated natural-use routing and blind-evaluation rules from V3/V5/V6. It measures the result a normal user receives from a natural request when each method has been installed and prepared as intended. Earlier series remain preserved as historical evidence and are excluded from V7 numerical comparison.

## Design

The frozen V7 matrix contains three scenarios by four conditions: Plain, BMAD 6.11.0 (`bmm`, Codex integration), hosted Prist, and the repository-based classic spec-driven workflow. Each cell has three independent first-pass runs, producing `n=3` for every scenario/condition cell and 36 measured tasks in total.

Every V7 setup, canary, measured and reviewer task uses `gpt-5.6-luna`, reasoning `xhigh`, one first pass, no repair turn, at most two clarifications, and at most one replacement task for a proven infrastructure failure. Setup tasks do not receive measured prompts or evaluator contracts.

## Exact-root isolation

The saved Codex project `4c35b890-98ac-4ab2-9428-d1bf1c2fd514` is a Git anchor. Each frozen setup commit is imported as an opaque unrelated branch. A measured task is created in a persistent Codex worktree from that exact branch, so the task opens at the product/method root and has no sibling benchmark cells in its working tree. Branch and blind identifiers do not reveal condition. No measured prompt contains condition, run ID, benchmark purpose, evaluator criteria, expected architecture, implementation-file hints, or answers from another run.

## Preparation

All cells start from pinned source commits. Plain preserves source content. New-project method cells install workflow templates while product canon remains empty. Existing-project BMAD, Prist and classic cells receive accurate baseline canon describing only the existing product. Setup agents do not edit existing product code or tests and never see the future task.

Hosted account and connection provisioning is an organizer responsibility completed before a Prist setup agent starts. Its elapsed time, interventions and safe usage evidence are recorded as `organizerProvisioningCost`, separately from Luna canon preparation. V7 performs this provisioning through direct API/MCP against `https://prist.isty.ist`; browser/UI is prohibited for organizer, setup, canary and measured work. Setup and measured agents may not open or control a browser, navigate hosted UI, create a hosted project, repair ownership through UI, or ask the user to do so. They receive an already authenticated, connected repository and use only project-local instructions, files and MCP operations. Codex Desktop intentionally disables Git hooks while creating managed worktrees, so hooks are not a runtime delivery mechanism in V7.

Prist uses only `https://prist.isty.ist` and a fresh hosted project for every independent setup lineage. Freeze requires authenticated identity, `connection_ready`, correct project context, current snapshot, zero pending sync, no legacy project ID, and a browser-free Luna setup receipt. Secret-bearing connection state remains outside Git. Each Prist setup branch tracks a project-local stdio bootstrap and non-secret Codex MCP config; before MCP starts, the bootstrap materializes the ignored connection state from the organizer-owned lineage package and then delegates to the installed Prist bridge. BMAD freeze requires version 6.11.0, module `bmm`, Codex integration, project-local discovery entrypoint and generated workflow. Classic freeze requires the pinned repository workflow, a project-local discovery entrypoint, and a neutral non-secret benchmark developer identity tracked in the classic setup branch so that it exists before a detached managed-worktree task starts. The identity fixture is setup state, contains no product requirement and is excluded from Plain, BMAD and Prist branches.

Every cell records clean status, HEAD/tree, source and method/setup commits, no remotes, dependency readiness, method inventory, canon inventory, prompt-leak scan, and a content fingerprint. Every independent V7 setup lineage receives its own Luna/xhigh read-only activation canary to prove exact-root automatic discovery and usable project-local MCP without browser/UI before measured dispatch. Three measured branches derived byte-for-byte from one frozen setup lineage use the lineage canary plus branch/materialization identity checks. Canary cost is setup cost. A canary that needs browser/UI fails readiness and the cell is rebuilt before freeze.

## Freeze

Before the first measured task, freeze verbatim prompts and envelope, answer bank, quality contracts, fidelity contracts, hidden test IDs and weights, evaluator and extraction code, setup inventory and fingerprints, source-integrity evidence, self-test receipts and a UTC timestamp. Lock inputs do not change after results are visible. An evaluator defect discovered later is reported as a series defect.

## Dispatch and observation

All 36 measured tasks are created immediately after freeze and allowed to run in parallel. Dispatch, actual start/first activity, last activity and final timestamps are recorded separately. The coordinator observes through task status and sends no status prompts, hints, repairs or acceleration requests.

Clarification answers may use only the frozen answer bank and facts already in the assigned repository. A request for a new product decision is escalated to the user. Questions, answers, waiting time and intervention count are evidence.

## First-pass evidence

At the first final response, freeze the task state immediately: exact task and host IDs, actual model/reasoning, final HEAD/tree/status, tracked and untracked hashes, redacted provider usage, timings and safe tool summaries. Do not copy credentials, complete transcripts or sensitive tool payloads. The measured implementation is never edited by the coordinator.

External evaluation uses a detached immutable copy, hides condition and method metadata, runs the frozen checks three times, then performs blind review. Workflow fidelity is evaluated separately from product quality. The measured agent never receives findings.

## Validity and retry

Implementation mistakes, misunderstanding, product-test failures, low score, automatic method-discovery failure after a passed canary, an ordinary method runtime error, and a measured agent choosing or requesting browser/UI after a passed browser-free canary are valid usability outcomes. No browser recovery is performed. A single new task is allowed only for evidence-backed infrastructure failure: wrong model/reasoning, corrupt or missing session log, pre-start configuration defect, required service outage, corrupt checkout, Codex/provider failure, or evaluator/harness failure unrelated to the implementation. A browser/UI dependency discovered before freeze is an organizer setup defect: the lineage is preserved as `invalid_organizer_design`, excluded from measured data, and replaced from its pinned source baseline. The invalid attempt and all evidence remain preserved.

## Metrics and completion

Per run: scenario, condition, exact task ID, model/reasoning, setup identity, four timestamps, elapsed and active time, provider-reported input/cached/cache-write/uncached/output/reasoning/total tokens, safe tool counts/durations, interventions, final Git state, quality score and findings, workflow fidelity/usability, and validity.

Per lifecycle: organizer provisioning cost, method-install cost, baseline-canon cost, activation-canary cost, late-change task cost, external-check cost and full-cycle cost. Reports show absolute values and ratios to Plain within the same scenario.

The V7 snapshot is complete only with 36 valid first-pass records, reproducible JSON plus Markdown/HTML reports and fresh lock/run/evaluation/source verification. An irrecoverable cell after its permitted infrastructure retry produces an exact blocker and prevents a complete matrix claim.


## V7 parameterization

This series keeps the V3 prompts, contracts, evaluator ownership, three-repetition objective procedure, blind normalization and no-repair validity policy byte-for-byte. V5 corrected large-harness behavior and V6 hosted-stage lifecycle safeguards are retained as additive harness lineage evidence. The final freeze remains blocked until the WI-131 Prist stage release supplies an exact commit, image and workflow bundle. All nine Prist setup lineages are candidates only until that signal.
