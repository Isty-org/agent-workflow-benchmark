# V5 corrected large evaluator overlay

This additive evaluator preserves the frozen P2/V5 harness and applies one
auditable correction when the harness is projected into an isolated scratch
directory:

- Russian no-results copy may place the negation after the subject, for example
  `Подходящих записей нет`, as well as before it.

The existing P2 per-test parser remains authoritative. A semantic-copy failure
may fail `L3-A05`, `L3-A10` and the aggregate regression suite `L3-B01`; it does
not change the outcomes of unrelated `L3-A*` checks.

The overlay is used only for the post-hoc corrected evaluation. It does not
replace or mutate the frozen V5 evaluator or report.
