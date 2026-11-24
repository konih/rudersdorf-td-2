# Loop — 001-rudersdorf-2

Repo: `/home/koni/Projects/rudersdorf-td-2` · Branch: `001-rudersdorf-2` · Base: `main` · Started: 2026-11-24 · Reviewers: two-model duo
Next: stage L — dispatch T001
Budget: paid review legs 2/14 (B reserve 3) · active hours 0/30 (sessions: 2026-11-24 start–) · source: set by the orchestrator at orient (default is claude=12, hours=8; raised because the feature has 46 tasks)

Budget arithmetic, in paid review legs: cap 14 · stage B reserve 3 · spent 2 (stage R, two rounds) · left for L 9.
Estimate per task: 0 (the per-task leg is reviewer A, not a paid leg); 1 only when a diff touches
CI, the Makefile, `close-task.yml`, dependencies or security posture, or reviewer A says BLOCK.
Expected over 46 tasks: 2–4.

## Stages

- [x] 0 orient — feature dir `specs/001-rudersdorf-2`; nothing existed (new repository); branch `001-rudersdorf-2` from `main`; no inbox, no open pull requests
- [x] P plan + tasks — generated: spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/werkstatt-api.md, tasks.md · spec set committed: 37f35ce
- [x] R spec-set review — round 1 on 37f35ce: BLOCK (5 CRITICAL, all fixed); round 2 on 44d37c9 in `reviews/R-spec-set/round-2/`: reviewer A BLOCK (2 CRITICAL, both mechanical contradictions from round-1 fixes, fixed), reviewer B CONCERNS · two-round cap reached; fixes of round 2 are unreviewed and listed in *Triage*
- [ ] L task loop — see *Tasks*
- [ ] B branch review — `reviews/B-branch/round-N/` · rounds: <n> · verdict: <…>
- [ ] Hand-off — <date> · `pr-description.md` · PR: <none | draft link>

## Fitness functions

| Characteristic | Command | Kind | Baseline (number, list, allow-list) | Per task / at B |
|---|---|---|---|---|
| Style and format | `make lint` | triggered | zero findings | per task |
| Layering (no pygame in core, laboratory, workshop, reference) | `tests/architektur/test_schichten.py` in `make check` (from T001) | triggered | no allow-list | per task |
| Workshop ships unsolved | `tests/architektur/test_werkstatt.py` in `make check` (from T003) | triggered | no allow-list | per task |
| Workshop and reference parity | `tests/architektur/test_paritaet.py` in `make check` (from T003) | triggered | no allow-list | per task |
| Content tables consistent | `tests/kern/test_daten.py` in `make check` (from T002) | triggered | — | per task |
| Determinism | `tests/kern/test_determinismus.py` in `make check` (from T014) | triggered | identical state hash | per task |
| Winnability and difficulty | `make test-lang` (`tests/kern/lang_balance.py`, from T030) | holistic | SC-005, SC-006 | T033, T037, T046, T047, B |
| Performance | `make bench`, `tests/kern/lang_leistung.py` (from T037) | holistic | step ≤ 4 ms, frame ≤ 8 ms | T037, T047, B |

Holistic run at B: not run yet

## Triage

| Stage | Finding (one line) | Sev | Reviewers | Disposition (fix / reject / defer) | Where it went / why | Needs user? |
|---|---|---|---|---|---|---|
| R1 | T016 speed test impossible (0.4 s needs 24 steps, cap is 12) | CRITICAL | A, B | fix | T016 case rewritten (12 steps at 4× for 0.05 s; backlog discarded); rule in plan.md | no |
| R1 | Magic (missions 19–20) depends on effects and chain lightning of other tracks | CRITICAL (A) / WARNING (B) | A, B | fix | prerequisites made explicit: registry `braucht`, `ABHAENGIG` in the workbench, FR-022 and SC-002 reworded, tests in T004, T018, T020, T025, T046 | no |
| R1 | `bauplan` ignored population, so the plan was not executable; order ambiguous | CRITICAL (A) / WARNING (B) | A, B | fix | population requirements replaced by `haeuser` levels in data and FR-016/FR-019; exact procedure and example in the contract; T022 tests execution of the plan | no |
| R1 | Missions 21–23 ship faulty code, against Constitution I and SC-003 | CRITICAL | A, B | fix | Constitution I amended to 1.1.0 with the craft-mission exception (decision by the orchestrator: the owner chose the bug-hunt topics in the brainstorm; pending owner validation); SC-003 reworded; mission 8 reports "still open" itself | validate |
| R1 | Mutable-default exercise fails lint rule B006 | CRITICAL | A | fix | per-file ignore for `werkstatt/fehlerjagd.py` in pyproject.toml | no |
| R1 | Mission 22 and 23 contracts too vague to test | WARNING | A | fix | functions, checks, base class and report schema fixed in the contract | no |
| R1 | Terminal traceback (FR-025) not tested | WARNING | A | fix | `Lernfehler.spur`; cases in T004 and T020 | no |
| R1 | SC-010: three commands did not reach a test result | WARNING | A | fix | quickstart order; SC-010 and T042 reworded | no |
| R1 | T014 tested interest and village/spell actions built later | WARNING | B | fix | moved to T022 and T025; `fuehre_aus` rule in plan.md | no |
| R1 | Probe inputs and probe failures undefined | WARNING | B | fix | `PROBEN`, missing-name rule, ignored probe errors in plan.md; T004 cases. Time guard rejected: a never-ending learner loop hangs any Python program; mission documents explain Ctrl+C | no |
| R1 | Mission 26 test: which package plays | WARNING | B | fix | always the package under test; prerequisites 3–7 in the registry; skeleton in the document | no |
| R1 | Where resistances apply | WARNING | B | fix | `Gegner.erleide_schaden` rule in plan.md and contract; T012 case | no |
| R1 | Wrong-return-value location, `spielen.main`, pause key | WARNING | B | fix | plan.md; T016 and T020 cases | no |
| R1 | Where the known-red list lives | WARNING | B | fix | tasks.md conventions: loop.md *Known red* | no |
| R1 | Presentation tasks have tests inside, not a separate test task | WARNING | B | reject | close-task records the red inside the task; behaviour is specified by the core test tasks; splitting six presentation tasks would add six fresh-agent rounds for drawing code | no |
| R1 | Coverage gaps: all capabilities, `endlos` in the save, end statistics, FR-008 integration, SC-007 drawn vs headless, FR-030 step time | WARNING | A, B | fix | new T046; `endlos` in contract and data model; `statistik()`; cases in T014, T020, T035 | no |
| R1 | Two unlock sources for spells; stale task ids and file names | NOTE | B | fix | `frei_ab_kirche` only; references corrected | no |
| R1 | Fast tests read the live `werkstatt/` and go red once the learner solves something | NOTE | B | reject | the developer suite is defined on the shipped state (tasks.md conventions); the learner uses `pruefen.py` | no |
| R1 | Balance tables, particle cap, hard-level threshold go beyond explicit requirements | NOTE | A | reject | they are design values the plan needs; T033 may tune the numbers | no |
| R2 | T004 forced-open case contradicted prerequisite propagation | CRITICAL | A | fix | case split: `schadensarten` alone; `wegfindung` with its dependants. Mechanical; no third round (two-round cap) | no |
| R2 | Mission 23 base class import forbidden by the layering guard | CRITICAL | A | fix | `rudersdorf.uebung` added to the allowed imports in T001, contract and plan. Mechanical | no |
| R2 | Constitution 1.1.0 amended without recorded owner approval | WARNING | A, B | fix | reason recorded in this commit's message; the owner chose bug hunts, clean-up and own-tests as topics in the brainstorm on 2026-11-24 and was told of the amendment the same day; still listed for validation at hand-off | validate |
| R2 | `bauregel` stand-in could seal a one-cell ford; a faulty `darf_bauen` could freeze a match | WARNING | B | fix | engine safety net in contract and plan; cases in T006 and T012 | no |
| R2 | `bauplan` recursion: which copy is shared | WARNING | B | fix | contract: one shared copy, inner helper, second example | no |
| R2 | T014 smithy case and reference stubs counted as solved | WARNING | B | fix | case moved to T029; reference stubs raise `NochOffen`; plan says which capabilities the engine calls from which task | no |
| R2 | Constructors of `Karte`, `Gegner`, `Bauwerk`, `Dorf` not fixed | WARNING | A, B | fix | plan.md *Fixed engine interfaces*; `Spiel.erzeuge_gegner` | no |
| R2 | Breaker and the placement rule | WARNING | B | fix | plan.md rule; T028 case | no |
| R2 | Spells adding effects without `fuege_effekt_hinzu`; tick wording; "nothing hit" message | WARNING | A, B | fix | contract; T025 cases | no |
| R2 | Capability check did not reach the end of a match | WARNING | A | fix | T046 plays whole campaigns | no |
| R2 | Mission 24 nested types; `labor.py` options; end screen; SC-003 for all missions | WARNING | A, B | fix | contract type list; plan `labor.main`; T016/T017; T018; T039 | no |
| R2 | Prerequisites in two places; `spur` parameter; `schwer` case wording; research wording; FR-020 level count | NOTE | B | fix | derived from the registry; signatures and wording corrected | no |
| R2 | Empty defence on `leicht` may survive past wave 4 with the starting numbers | NOTE | B | defer | T033 tunes the numbers until T030's slow tests pass | no |

## Tasks

| Task | Verdict | Review (legs, rounds, paid leg?) | Gaps / decision request |
|---|---|---|---|
| T001 | CLOSED | reviewer A (diff), 1 round, CONCERNS → APPROVE (only finding: final `make check` pending, then run green); no paid leg (no trigger) | none; proposal: forbid `rudersdorf/labor` → `rudersdorf.ansicht` in the layering guard (not in the task text) |
| T002 | CLOSED | reviewer A (diff), 2 rounds: round 1 CONCERNS (2 WARNINGs, both verified and fixed: split-only enemy was purchasable under mission 15's rule; tower values unchecked), round 2 CONCERNS (1 NOTE, wording fixed, design change rejected) → APPROVE; no paid leg (no trigger) | none; note for T011/T028: `daten.GEGNER` as a whole is the catalogue for `erzeuge_welle` (`schleimling` has `ab_welle` = `NIE_VON_SELBST`, the boss a price that is never used) |
| T003 | CLOSED | reviewer A (diff), 1 round, CLEAN → APPROVE; no paid leg (no trigger) | none; notes for later tasks: document anchors are `#mission-N` (T042–T045); the names-only parity rule for missions 21–23 means "every registry name exists in both packages" (T040); in the module of mission 8 the reference may add functions with the parameters `kandidaten, turm` |

## Known red

Tests a test task left red for a later task; excluded from "green" at close, nothing else is.

| Test (file:name) | Story | Written in | Cleared in |
|---|---|---|---|

## Test changes

Tests from a test task changed by a later task (close-task `TEST` class); each one changes what green means.

| Test (file:name) | Written in | Changed in | Evidence it was wrong |
|---|---|---|---|

## Lessons

<!-- master list: one line per reusable lesson with the task ids that hit it -->
- A guard's self-test loops over directories written out in the test, never over the guard's own rule tuples; otherwise a narrowed rule narrows its test (T001).
- No mutation gate and no Markdown gate here: prove guards and logic with hand-written mutants on a copy outside the repository, run with `.venv/bin/python` and `PYTHONDONTWRITEBYTECODE=1` (T001).
- Reviewer A flags a pending final `make check` as a WARNING; it is the planned order, answer it by running FINAL and recording it (T001).
- A table handed to learner code must be valid under the contract's rule for that code: test the real table with the contract's rule written out in the test, not only its keys (T002).
- A faulty-copy self-test changes a value nothing else refers to, or the checker rightly reports two errors; a cycle self-test needs a cycle that exists only through the implicit "level before" edge (T002).
- `make check` takes under a second while the engine is small: run it before the review as well and record it, so the reviewer has no pending gate to flag (T002).
- A written-out list in a guard is compared with something it was not filtered by; a test that filters the registry by the list and compares the result with the list cannot fail (T003).
- Besides invented fixtures, break each guarded place of a copy of the real package in turn (each placeholder, each signature): that proves the guard's scope has no hole (T003).
- The parity guard reports every public function or method the reference has and the workshop lacks: reference helpers start with an underscore or are inner functions; the only exception is extra strategies `(kandidaten, turm)` in `strategien.py` (T003).
- The workshop guard pins each placeholder to the text `Mission N: <Titel>` of the registry, and `tests/architektur/test_missionen.py` writes the contract's tables out again: a changed title, name or module is changed in the registry, that test and the stubs together (T003).

## Where a human should look first

<!-- filled at hand-off -->

## Proposed harness changes

| Lesson | Seen in | Proposed change (AGENTS.md line / sensor / close-task.yml) |
|---|---|---|

## Owner tasks (skipped by the loop)

| Task | Command sheet |
|---|---|
