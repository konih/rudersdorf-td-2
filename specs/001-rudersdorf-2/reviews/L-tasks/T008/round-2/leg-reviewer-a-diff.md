## Verdict: CONCERNS

## Findings
- [WARNING] M8 accepts strategies that mutate the candidate list, contrary to the contract — `tests/missionen/test_m08.py:95`
  Failure: A sixth strategy that sorts `kandidaten` by `rest_weg` in place, then returns the first flyer or otherwise the first candidate, passes all three checks while changing the caller’s list. The contract explicitly prohibits argument mutation (`specs/001-rudersdorf-2/contracts/werkstatt-api.md:28`); the evidence incorrectly treats reordering as unspecified.
  Fix: Snapshot each candidate list before calling the strategy and assert its original order remains unchanged. Include this condition in `erfuellt_alles` so a mutating entry cannot displace a valid alternative.
  Confidence: 99

Checked the M6–M10 cases, stand-in tests, helper changes, contract, workshop/reference stubs, workbench integration, constitution, and recorded red/lint results. The requested boundary, selection, chain, upgrade, and stand-in cases are otherwise covered.

## Could not check
- Tests and lint were not run; results were assessed from the recorded verification matrix.
- The reference copy and mutation harness are outside the repository and were not accessed.
- Final `make check` remains marked pending in `specs/001-rudersdorf-2/evidence/T008.md:60`.
- Other reviewers’ reports were not consulted.
