# APΩ Skill Runtime Architecture

## Status

Design approved in conversation; implementation is not yet started.

## Goal

Build a reusable skill-runtime architecture that continuously discovers, selects, chains, executes, observes, verifies, and—when a capability gap is demonstrated—creates or refines skills so future tasks can reuse the verified capability instead of stopping at documentation lookup.

## Scope

The first implementation slice covers four cooperating capabilities:

1. Capability Router — maps a task to the minimum sufficient capability/skill chain.
2. Skill Contract/Registry — records identity, trigger, source, availability, side effects, authority, evidence requirements, version/provenance, and verification status.
3. Skill Builder — creates/refines skills using pressure-test-first TDD for process documentation.
4. Chain Executor — passes verified artifacts/results between skills, records execution state, and prevents unsupported success claims.

Out of scope for the first slice: autonomous installation of third-party skills, unrestricted external mutation, model training, and a universal planner for every runtime.

## Core Invariants

- READ SKILL != USE SKILL.
- USE SKILL != CHAIN SKILL.
- CHAIN SKILL != SUCCESS.
- SUCCESS != VERIFIED.
- Historical evidence != current execution evidence.
- Capability discovery must precede capability selection when availability is unknown.
- A skill cannot be marked verified merely because its SKILL.md exists or was read.
- A downstream skill may consume an upstream result only when that result has an explicit status and provenance.
- Mutation-capable actions require an authority gate.
- No fabricated execution, success, or verification state.

## Runtime Flow

```text
TASK
  -> CAPABILITY CHECK
  -> DISCOVER
  -> IDENTIFY SOURCE
  -> READ SKILL / SCHEMA / CONTRACT
  -> SELECT MINIMUM SUFFICIENT SET
  -> AUTHORITY / SIDE-EFFECT GATE
  -> EXECUTE
  -> READ RESULT
  -> CROSS-CHECK
  -> VERIFY
  -> PROPAGATE VERIFIED ARTIFACT
  -> NEXT SKILL
  -> FINAL VERIFY
```

For capability gaps:

```text
ROUTER
  -> GAP DETECTED
  -> DISCOVER CANDIDATE
  -> INSPECT CONTRACT
  -> PRESSURE TEST / BASELINE
  -> BUILD OR REFINE SKILL
  -> VERIFY
  -> REGISTER
  -> ROUTER RE-EVALUATES TASK
```

## Components

### 1. Capability Router

Input: task description, target, required output, current state, authority, constraints.

Output: ordered capability chain with rationale, required inputs, expected outputs, evidence requirements, and mutation gates.

Selection factors: task fit, target fit, domain, output contract, availability, authority, side-effect class, evidence quality, determinism, cost, reversibility, and current state.

The router must not force every task through the same chain. It selects the smallest sufficient set and can terminate early when verification is satisfied.

### 2. Skill Registry

Each registered skill record contains at minimum:

```yaml
id: string
name: string
type: technique|pattern|reference|router|builder
source: string
path: string
trigger: string
availability: unknown|available|blocked
side_effect_class: none|read|mutation|external
permission_class: none|user-gated|connector-gated|runtime-gated
version: string
provenance: string
status: discovered|selected|executed|failed|verified|stale
contract_hash: string
last_verified_at: string|null
```

### 3. Chain Executor

Every execution produces a structured result:

```yaml
skill_id: string
run_id: string
status: invoked|returned|observed|failed|partial|verified
input_refs: []
output_refs: []
evidence_refs: []
side_effects: []
error_class: null|string
next_eligible: true|false
```

The executor must refuse to upgrade `returned` to `verified` without explicit evidence.

### 4. Skill Builder

Skill creation follows the `writing-skills` methodology: pressure scenario first, observe baseline failure, write the minimum skill addressing the demonstrated failure, rerun the scenario, then refactor against newly discovered rationalizations.

This is TDD applied to process documentation.

### 5. Verification Layer

Verification checks:

- trigger discoverability;
- contract completeness;
- correct chain selection;
- actual invocation;
- result propagation;
- expected failure behavior;
- authority/mutation gates;
- no-unverified-success invariant;
- repeatability where deterministic behavior is expected.

## Chain Semantics

A chain is not a static list. It is a stateful DAG whose next node is selected from the previous node's actual result.

```text
A -> result(A)
       |
       +-> success -> B
       +-> partial -> recovery/refinement
       +-> blocked -> authority gate / alternate capability
       +-> failed -> diagnosis / fallback
       +-> stale -> refresh evidence
```

A skill may therefore select another skill dynamically when its output exposes a new capability requirement.

## Failure Classes

The runtime recognizes at least:

`MISSING`, `UNAVAILABLE`, `PERMISSION_DENIED`, `WRONG_SCOPE`, `WRONG_TARGET`, `TIMEOUT`, `INVALID_INPUT`, `DEPENDENCY_FAILURE`, `PARTIAL_RESULT`, `STALE_STATE`, `AMBIGUOUS`.

Failures are evidence for routing/refinement, not successful completion.

## First Verification Scenario

Given a task requiring an unavailable specialized capability:

1. Router detects capability uncertainty.
2. Discovery searches installed and approved external capability sources.
3. Candidate skill contracts are inspected.
4. Minimum sufficient chain is selected.
5. Each selected skill is actually invoked.
6. Output from skill N is consumed by skill N+1.
7. A deliberately failing pressure case demonstrates a gap.
8. Skill Builder creates/refines the skill.
9. The same pressure case is rerun.
10. Only passing evidence permits registry status `verified`.
11. Router can select the newly verified skill on a subsequent equivalent task.

## Approval / Mutation Boundary

Third-party skill installation, repository publication, deployment, account changes, payment, deletion, and other external mutations remain gated. Discovery and read-only inspection do not imply authorization to mutate.

## Implementation Sequence

1. Create registry and contract model.
2. Create router selection model.
3. Create chain execution/result model.
4. Add pressure-test harness for skills.
5. Implement skill builder workflow.
6. Integrate verification and registry promotion.
7. Run an end-to-end chain against a real capability-discovery task.
8. Refine based on observed failures.
