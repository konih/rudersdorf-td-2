## Verdict: CONCERNS

## Findings

- [WARNING] The “never generated” sentinel conflicts with the wave-generation contract — `rudersdorf/daten.py:392`
  Failure: Passing `GEGNER` to the contracted generator for wave 1 with budget 4 selects `schleimling`: it is non-boss, costs 4, and satisfies `ab_welle <= nummer`. It therefore spawns without a slime splitting. No implemented caller filters it out.
  Fix: Explicitly require filtering entries with `ab_welle == 0` before calling the generator, and add a regression check covering the actual catalog.
  Confidence: 95

- [WARNING] Tower validation misses required combat keys — `tests/kern/test_daten.py:160`
  Failure: Removing `nachladezeit` from `BAUWERKE["kanone"]["werte"]` passes the checks: neither its upgrades nor the validators require that field. The resulting tower lacks its firing interval.
  Fix: Validate required base combat keys for every tower, plus kind-specific keys; add a faulty-copy case deleting `nachladezeit`.
  Confidence: 99

Checked geometry, content tables, formulas, village prerequisites and cycle detection, ability/spell signatures, all five maps, validation self-tests, and the recorded verification matrix against the data model and workshop contract.

## Could not check

- Did not run tests, as instructed. T002 records an early successful `make check` with 53 tests; final-tree verification remains pending.
- External scratch mutation scripts and their raw results were outside the permitted repository boundary and were not read.
- Runtime integration and gameplay balance: engine consumers are not implemented in this revision.
