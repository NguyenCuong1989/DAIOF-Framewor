# Skill Runtime Verification Contract

## Required evidence

A runtime implementation is verified only when CI executes the test suite for the implementation commit and reports the runtime tests passing.

## Assertions

- Router chooses the highest-fit available capability and does not blindly select the shortest trigger.
- Chain execution propagates the previous run identifier into the next skill input references.
- A returned result with verification disabled is not eligible for downstream execution.
- A failed skill stops the chain.
- Registry promotion to verified requires non-empty evidence.
- Runtime result status and evidence remain explicit.

## Pressure case

Register two skills sharing a generic task term and one skill with the exact task phrase. The router must select the exact-fit capability. Then execute a two-node chain and verify that node two consumes node one's run identifier.
