# Agent workflow benchmark — technical export

Final cohort: **3 scenarios × 4 methods × 3 repetitions = 36 first-pass tasks**.
Methods: Plain, BMAD, Classic Spec-Driven AI Development, Prist. Model/reasoning: `gpt-5.6-luna` / `xhigh`.

- [Final report](reports/benchmark-v7-final/BENCHMARK-REPORT.md) and [original machine-readable results](reports/benchmark-v7-final/source-snapshot.json).
- [Authoritative cohort and evidence links](data/cohort.json): 27 V7 comparator tasks + 9 permissions-corrected V7C Prist tasks.
- [Verify](VERIFY.md), [Re-evaluate](REEVALUATE.md), [Rerun](RERUN.md).
- [Release assets](RELEASE-ASSETS.md), [lineage and hashes](PROVENANCE.md), [license notes](LICENSE-NOTES.md).

Quick offline checks, using Python 3.12 or newer:

```text
python scripts/verify.py
python scripts/reevaluate.py
python scripts/verify.py --assets
```

The last command requires nine archives in the Git-ignored `release-assets/` folder. No release has been published. This README is a technical index; public bilingual presentation is a separate publication stage.
