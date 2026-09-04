# V3 quality, fidelity and usability rubric

## Product quality — 100

Product quality is blind to condition, usage, transcript and setup metadata.

- Functional behavior: 50 points from frozen harness-owned checks.
- Regression, build and runnable smoke: 20 points from frozen commands and smoke checks.
- Architecture and project fit: 20 points from two independent blind reviews; a third review resolves a difference above four points.
- Scope, UX and security: 10 points from the same blind review procedure.

Objective checks are scored mechanically. Review findings are deduplicated by root cause before severity caps are applied. A critical finding caps the product score at 49; a major finding caps it at 69. The immutable first-pass score never changes.

Harness-owned checks run three times against the same immutable first-pass state. Any inconsistent outcome is recorded as flakiness. Agent-authored flaky tests count as a regression finding; hidden product checks remain independently scorable.

## Workflow fidelity — separate axis

Fidelity answers whether the assigned method was actually discovered and used. It is not included in the product-quality score.

- `engaged`: the frozen method-specific activation evidence exists before the first product-code edit.
- `completed`: the method's required work lifecycle and completion evidence exist.
- `activation_failed`: the repository was ready, but the measured agent did not activate the method.
- `runtime_failed`: activation occurred and the method itself failed during ordinary use.
- `not_applicable`: Plain.

## Usability — separate axis

Usability is observed rather than inferred from product score: automatic discovery, number of method operations, clarification count, method/tool errors, time spent before first product edit, and whether the agent reached a completed lifecycle without coordinator help.

## Reporting

Report product quality, fidelity and usability side by side. Never replace them with one combined rank. Setup/canon cost, late-change cost and full-cycle cost remain separate. All first-snapshot conclusions are labelled `n=1`; large-project replication is labelled `n=3` per condition.

