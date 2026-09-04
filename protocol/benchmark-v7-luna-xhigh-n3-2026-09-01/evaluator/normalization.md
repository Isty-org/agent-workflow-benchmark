# Blind workspace normalization

For product-quality evaluation, construct a new repository from the scenario's pinned Plain baseline and apply only measured product-code, product-test and user-facing product-documentation changes from the immutable first-pass state.

Exclude method installation files, workflow state, operational WorkItems, benchmark identifiers, connection metadata and setup-only canon. Preserve product canon that was already present in the pinned source. If a measured change updates a product specification, include a neutral copy in the review bundle without method lifecycle metadata. Record every included and excluded path and its SHA-256. The normalized workspace has no remote, one opaque blind ID, and no condition field.

The normalization receipt is retained outside the reviewer workspace and verified against setup and first-pass trees. Normalization never changes executable product content.

