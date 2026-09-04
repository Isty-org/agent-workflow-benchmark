# V7 blind review contract

Review receives an opaque blind ID and a normalized immutable product workspace. It does not receive the condition, method, run ID, task ID, setup artifacts, transcript, usage, timing or workflow metadata.

Normalization applies only product code, product tests and neutral user-facing product documentation from the first-pass snapshot to the pinned scenario baseline. Method files, operational state, connection metadata and benchmark identifiers are excluded. Included and excluded paths, source and output trees, and hashes are saved in a normalization receipt.

Two independent Luna/xhigh reviewer passes score the review-owned rubric checks. A third pass is required only when the first two totals differ by more than four points. Root causes are deduplicated before severity caps. The official score is kept separate from fidelity and usability.

Review scripts refuse a workspace that still exposes condition, method, setup, task or transcript metadata in the blind package.
