## Verdict: CONCERNS

## Findings

- [WARNING] The 142 expected failures are missing from the required known-red register — `specs/001-rudersdorf-2/evidence/T010.md:175`
  Failure: The evidence says these tests are registered in `loop.md`, but that file contains no T010 entries. The recorded failing `make check` therefore does not qualify for the exception defined in task conventions.
  Fix: Register the six test modules and their classes under `loop.md`’s Known red section, with T011 responsible for clearing them.
  Confidence: 100

- [WARNING] M15 cannot report the explicitly targeted endless-loop mistake — `tests/missionen/test_m15.py:58`
  Failure: Omitting the price subtraction keeps purchasing indefinitely; the test never reaches `wellenfehler`, hangs the suite, and can exhaust memory. The recorded mutant instead stops artificially after 5,001 purchases.
  Fix: Run a termination case in a subprocess with a bounded timeout and report a German assertion failure when it expires.
  Confidence: 100

- [WARNING] Direct constructor and tick calls bypass the required German failure feedback — `tests/missionen/test_m12.py:117`
  Failure: A learner typo such as `self.rets` in `tick` produces a bare `AttributeError`, without expectation, actual result, or hint. `rufe_sicher` cannot handle calls made outside it.
  Fix: Route constructor and tick calls through `rufe_sicher`, preserving its existing propagation of `NochOffen`.
  Confidence: 99

Checked the nine changed files against the track C contract, stand-in rules, workshop/reference stubs, shared helpers, capability probes, constitution, and recorded verification matrix. The requested ordinary behavior cases are represented.

## Could not check

- Tests and lint were not run, as instructed; the evidence records an early successful lint run, with final verification still pending.
- The reference copy and mutation scripts are outside the repository and were not inspected.
- Runtime integration and learner-runner behavior: `rudersdorf/kern/` contains only its package initializer, and `pruefen.py` is absent.
