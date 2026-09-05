# Rerun

A rerun needs an available `gpt-5.6-luna` model with reasoning `xhigh`, sanitized method-baseline packages, scenario dependencies and access to the pinned hosted release for Prist. Hosted model/service availability is external to this export. Baseline packages supply public tracked method files and baseline product canon.

Use the archived Russian-language `classic-2026.08` baseline for a condition-matched Classic rerun. A future English translation is a different experimental condition because this cohort did not test it.

Prepare an independent repository and prompt without dispatching a task:

```text
python scripts/prepare.py --run v7-new-bmad-r1 --kind baselines --destination work/rerun-new-bmad-r1 --prompt-output work/rerun-new-bmad-r1.txt
```

Place the downloaded sanitized package at the path named by `assets/release-upload-manifest.json` under `release-assets/packages/`. The script verifies package hashes, source provenance, sanitization, notices, and member checksums; refuses an existing destination; preserves evidence bytes/executable modes; creates a fresh Git repository without remotes; and writes original scenario/envelope components with the new assigned root. The materialization commit records public package bytes. Source setup identities remain in `inputs/method-locks.json`. An empty new-project Plain baseline is intentional. The script dispatches no task and incurs no model usage.

For a Classic rerun, create the local identity after materialization by copying `specs/.me.template` to `specs/.me` and replacing its placeholders with the assigned local identity. Keep this Git-ignored file outside snapshots and public packages. Record the local setup step in the new cohort provenance. The 27 historical `specs/.me` members were removed from public packages with path/size/SHA-256 accounting.

For Prist, complete browser-free organizer provisioning before measurement: a fresh project/connection per run, stage revision/image and kit digest from `inputs/method-locks.json`, and the full operation profile in the V7C manifest. Credential state is absent. Replace runtime references to organizer-owned Windows paths with fresh local connection state using the archived kit's setup flow; record this environment-specific projection. Verify `connection_ready`, required operations and a disposable repeated-start/cancel lifecycle canary under the V7C protocol. Keep existing-project canon equal to the archived baseline and new-project canon empty. A different deployed revision is a new experimental condition.

Launch every prepared repository independently under the original policy: one first pass, no repairs, at most two clarification questions, no browser/UI by the measured agent and only its assigned product/method root. Keep the export, evaluator, outcomes and other cells outside that root. Repeat for all 36 entries. At the first final response, capture exact task ID, model/reasoning, dispatch/start/final times, provider usage, HEAD/tree/status and tracked/untracked hashes. Preserve a byte-hashed snapshot before evaluation. Use the frozen answer bank for permitted clarifications.

The V7 protocol, rubric/answer bank and V7C addendum contain the frozen contracts. Original inputs remain unchanged; new launch-path composition, provisioning, runtime differences and evaluator reruns become new provenance.
