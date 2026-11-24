## Verdict: CONCERNS

Checked the changed stubs, tests, helpers and evidence against T012, the fixed interfaces, specification, data model, routing reference and workbench contract. Stub signatures match; recorded results distinguish the expected red tests from passing helper tests.

## Findings

- [WARNING] The required during-wave building case is exercised only in phase `bauen` — `tests/kern/test_bewegung.py:305`
  Failure: An implementation that rejects every `baue` call in phase `welle` can pass these tests, despite T012 explicitly requiring mid-wave placement and rerouting. The evidence defers this to T014, but T014’s listed cases do not explicitly cover it.
  Fix: Add a rerouting case with the match explicitly in phase `welle`, asserting successful placement, completion of the current step and avoidance of the blocked cell.
  Confidence: 99

- [WARNING] Invalid named-map fallback has no test — `specs/001-rudersdorf-2/evidence/T012.md:141`
  Failure: A named map file containing two village gates could propagate `ValueError` instead of selecting `flusstal` and explaining the problem, while every current map test passes. Invalid `kartentext` and missing filenames exercise different paths.
  Fix: Add a test using a temporary map directory or mocked file read that supplies invalid content for an existing name; assert fallback and a German reason without modifying shipped maps.
  Confidence: 98

## Could not check

- Did not run tests or lint; assessed the recorded results in `evidence/T012.md`. The final `make check` result remains pending.
- Did not inspect the external throwaway engine, mutation script, tree copies or raw logs; they are outside the permitted repository boundary. Mutation and satisfiability claims therefore remain independently unverified.
