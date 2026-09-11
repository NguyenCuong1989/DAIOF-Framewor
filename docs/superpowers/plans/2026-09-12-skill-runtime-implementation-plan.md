# Skill Runtime Implementation Plan

## Objective
Implement the approved APΩ Skill Runtime slice with test-first contracts for registry, router, chain execution, provenance, and verification.

## Sequence
1. RED: add pressure tests for minimum-chain selection, result propagation, no-unverified-success, failure stop, and registry promotion.
2. GREEN: implement the smallest registry/router/executor satisfying those tests.
3. REFACTOR: strengthen contract fields, deterministic selection, and explicit evidence propagation without changing behavior.
4. Integrate a reusable skill contract document and verification scenario.
5. Run CI through a pull request against `main`.
6. Inspect CI result and fix failures until green or report a verified blocker.

## Completion Criteria
- All runtime tests pass.
- The router selects the minimum sufficient available capability.
- Chain output is consumed by the next skill with provenance references.
- Returned/failed results cannot become eligible as verified results without evidence.
- Registry refuses unsupported verified promotion.
- Verification evidence is current and tied to the implementation commit.
