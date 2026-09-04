# Re-evaluate

Recompute final scores from frozen objective outcomes, original blind-review passes, contract weights and severity caps:

```text
python scripts/reevaluate.py --output work/recomputed-scores.json
```

This validates check-level points and reproduces all 36 official scores. Raw scores are reconstructed from check points; two inherited raw-field discrepancies are explicitly reported in `PROVENANCE.md`. Review aggregation uses rounded mean for two passes, median for three, with a third pass only when the first two review-only totals differ by more than four. Critical findings cap at 49; major findings cap at 69. Product failures remain recorded benchmark outcomes.

Execute product checks on a verified new copy:

```text
npm ci
python scripts/run_checks.py --run v7-new-plain-r1 --output work/new-plain-r1-checks.json
```

The frozen evaluator repeats objective checks three times. New-project checks need Playwright and Chromium (`npx playwright install chromium`). Small-project checks need Docker/PostgreSQL. Large-project checks need the .NET SDK in the archived `global.json` and desktop/headless dependencies. Node 24 was used in the source environment. Environment details and output tails remain in original receipts. Product-test failure may return exit code 1 with a valid receipt; inspect the outcome.

Final small Prist receipts were produced by running frozen tests alongside a PostgreSQL server. The portable command uses the frozen evaluator's isolated Docker database recipe. This changes infrastructure placement and does not promise identical timings/logs. All large runs automatically use the locked supplemental evaluator. New evaluations belong in `work/` or a separate cohort.

For new blind review, materialize original reviewer input and follow the frozen reviewer contract:

```text
python scripts/prepare.py --run v7c-large-prist-r1 --kind review-inputs --destination work/blind-review-copy
```

Assign a fresh opaque folder label before exposing it to a reviewer. Keep method, cost, transcript and task metadata outside the review context. Give reviewers the original contract/rubric and normalized product content, record independent reviews and apply the same aggregation rule. New model reviews can change judgments; score replay uses frozen reviews.
