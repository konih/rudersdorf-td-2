## Verdict: CONCERNS

## Findings

- [WARNING] Tests do not enforce the documented lookup of stand-ins on every call — `rudersdorf/ersatz.py:8`, `tests/kern/test_werkbank.py:240`
  Failure: An implementation copies `ERSATZ` when constructing `Werkbank`; every current stand-in test still passes because registration precedes construction. Replacing an entry afterward would incorrectly keep using the old stand-in.
  Fix: Add a test that constructs an open workbench, calls its stand-in, replaces that registry entry, and verifies the next call returns the replacement’s result.
  Confidence: 100

- [NOTE] The requested T004 cases are represented, and the stub failures are intentional — `tests/kern/test_werkbank.py:223`, `specs/001-rudersdorf-2/evidence/T004.md:49`
  Failure: None identified in the required case coverage. Checked routing, capability-wide fallback, error metadata, initial openness, dependencies, reload, class fallback, missing names/modules, traceback text, package selection, and temporary-package cleanup.
  Fix: None for the expected red state; recorded results report 33 `NotImplementedError` errors and no other failing tests.
  Confidence: 95

## Could not check

- Did not run tests or lint; assessed the recorded results in `specs/001-rudersdorf-2/evidence/T004.md`.
- Did not inspect the external reference implementation, mutation scripts, or leak probe; they are outside the permitted repository.
- The final `make check` result remains pending in the evidence record.
