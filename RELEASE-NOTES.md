# Agent Workflow Benchmark — first public export

## Summary

This release candidate packages the final 36-task cohort comparing Plain, BMAD 6.11.0, Classic `classic-2026.08`, and Prist across new, small existing, and large existing projects. Each of the 12 scenario/method cells has three independent first-pass runs using `gpt-5.6-luna` with `xhigh` reasoning.

The public repository adds aligned English and Russian documentation, Apache-2.0 licensing for repository-owned material, explicit third-party scope, community metadata, cross-platform Git-only CI, payload immutability evidence, and an asset upload manifest.

## Result medians

Quality / measured task cost / elapsed time:

| Scenario | Plain | BMAD | Classic | Prist |
|---|---:|---:|---:|---:|
| New project | 69 / $0.42385148 / 33.6 min | 69 / $1.36481868 / 60.5 min | 45 / $3.12769884 / 67.9 min | 87 / $0.26662576 / 20.9 min |
| Small existing | 35 / $10.077087 / 70.1 min | 29 / $1.44226984 / 60.8 min | 39 / $7.90102716 / 69.9 min | 69 / $0.43872212 / 25.9 min |
| Large existing | 98 / $4.05826076 / 63.5 min | 25 / $0.8408026 / 34.0 min | 82 / $6.09135428 / 39.9 min | 98 / $0.2068444 / 13.6 min |

The metrics cover measured tasks. Historical setup, method adoption, and canon construction are outside the cost boundary. External evaluation for the nine Prist rows is recorded separately at 29,710,054 tokens and $1.14781888.

## Provenance

- 27 Plain/BMAD/Classic tasks come from V7.
- 9 permissions-corrected Prist tasks come from V7C.
- All 12 large-project rows use the final uniform supplemental evaluator.
- Two inherited `rawBeforeSeverityCap` discrepancies remain disclosed for `v7-new-bmad-r3` and `v7-new-plain-r2`; all 36 official scores replay exactly.
- The Classic cohort used the Russian `classic-2026.08` edition. A future English translation was not tested.

## Reproducibility

- Verify: `npm run verify`
- Re-evaluate: `npm run reevaluate`
- Public/package checks: `npm run check:public`
- Full Git-only CI equivalent: `npm run check`
- Optional local archive audit: `python scripts/verify.py --assets`

## Assets

Nine ZIP files are prepared locally: first-pass snapshots, normalized reviewer inputs, and frozen baselines for each scenario. Their hashes, sizes, member manifests, and upload gates are in `assets/release-upload-manifest.json` and `assets/SHA256SUMS`.

Archive publication requires final confirmation of redistribution rights documented in `THIRD_PARTY_NOTICES.md`. No remote, tag, release, or upload is created by this stage.

## Final publication checklist

1. Review the Stage 6 commit and rerun `npm run check` on Linux or Windows.
2. Confirm the archive redistribution gate for BMAD, Classic, Prist kit material, product baselines, implementations, and reviewer inputs.
3. Select a release tag tied to the reviewed commit.
4. Upload only the approved files listed in `assets/release-upload-manifest.json` without changing bytes.
5. Verify downloaded assets with `python scripts/verify.py --assets` and publish the SHA-256 list.
