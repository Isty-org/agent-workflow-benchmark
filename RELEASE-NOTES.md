# Agent Workflow Benchmark v1.0.0

## Summary

This first public release contains the final 36-task cohort comparing Plain, BMAD 6.11.0, Classic `classic-2026.08`, and Prist across new, small existing, and large existing projects. Each scenario/method cell has three independent first-pass runs using `gpt-5.6-luna` with `xhigh` reasoning.

## Result medians

Quality / measured task cost / elapsed time:

| Scenario | Plain | BMAD | Classic | Prist |
|---|---:|---:|---:|---:|
| New project | 69 / $0.42385148 / 33.6 min | 69 / $1.36481868 / 60.5 min | 45 / $3.12769884 / 67.9 min | 87 / $0.26662576 / 20.9 min |
| Small existing | 35 / $10.077087 / 70.1 min | 29 / $1.44226984 / 60.8 min | 39 / $7.90102716 / 69.9 min | 69 / $0.43872212 / 25.9 min |
| Large existing | 98 / $4.05826076 / 63.5 min | 25 / $0.8408026 / 34.0 min | 82 / $6.09135428 / 39.9 min | 98 / $0.2068444 / 13.6 min |

The metrics cover measured tasks. Historical setup, method adoption, canon construction, and evaluation sit outside this cost boundary. External evaluation for the nine Prist rows is recorded separately at 29,710,054 tokens and $1.14781888.

## Provenance

- 27 Plain/BMAD/Classic tasks come from V7.
- 9 permissions-corrected Prist tasks come from V7C.
- All 12 large-project rows use the final uniform supplemental evaluator.
- Two inherited `rawBeforeSeverityCap` discrepancies remain disclosed for `v7-new-bmad-r3` and `v7-new-plain-r2`; all 36 official scores replay exactly.
- The Classic cohort used the Russian `classic-2026.08` edition. The later English translation was not tested.

## Verification

```text
npm run check
python scripts/verify.py --assets
```

The first command verifies the Git payload, replays all scores, runs package-builder negative tests, checks public documentation, and confirms frozen payload locks. The asset command additionally verifies the nine local raw sources and nine sanitized packages member by member.

## Public evidence packages

Nine release assets provide sanitized first-pass, review-input, and baseline evidence for the three scenarios. They contain 32,096 source members with byte-identical content and exclude 27 local `specs/.me` identity files plus one generated `.pyc` cache. Nine credential files remain represented only by their historical SHA-256 values.

Every package includes its source raw ZIP identity, complete included/excluded accounting, checksums, original member manifest, BMAD 6.11.0 MIT and trademark terms, Isty Classic Apache LICENSE/NOTICE, a hash-defined Classic scope, and the benchmark evidence-rights notice. The raw Stage 5 ZIPs are provenance inputs and are not release assets.

Package sizes and SHA-256 values are in the [upload manifest](https://github.com/Isty-org/agent-workflow-benchmark/blob/v1.0.0/assets/release-upload-manifest.json) and [public checksum list](https://github.com/Isty-org/agent-workflow-benchmark/blob/v1.0.0/assets/PACKAGE-SHA256SUMS). Rights and trademark boundaries are documented in [THIRD_PARTY_NOTICES.md](https://github.com/Isty-org/agent-workflow-benchmark/blob/v1.0.0/THIRD_PARTY_NOTICES.md).
