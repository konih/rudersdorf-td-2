# Loop — 001-rudersdorf-2

Repo: `/home/koni/Projects/rudersdorf-td-2` · Branch: `001-rudersdorf-2` · Base: `main` · Started: 2026-11-24 · Reviewers: two-model duo
Next: stage R — triage the two spec-set review legs, then dispatch T001
Budget: paid review legs 1/14 (B reserve 3) · active hours 0/30 (sessions: 2026-11-24 start–) · source: set by the orchestrator at orient (default is claude=12, hours=8; raised because the feature has 46 tasks)

Budget arithmetic, in paid review legs: cap 14 · stage B reserve 3 · spent 1 (stage R) · left for L 10.
Estimate per task: 0 (the per-task leg is reviewer A, not a paid leg); 1 only when a diff touches
CI, the Makefile, `close-task.yml`, dependencies or security posture, or reviewer A says BLOCK.
Expected over 46 tasks: 2–4.

## Stages

- [x] 0 orient — feature dir `specs/001-rudersdorf-2`; nothing existed (new repository); branch `001-rudersdorf-2` from `main`; no inbox, no open pull requests
- [x] P plan + tasks — generated: spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/werkstatt-api.md, tasks.md · spec set committed: 37f35ce
- [ ] R spec-set review — `reviews/R-spec-set/` on 37f35ce · verdict: <…> · CRITICAL: <…>
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
| Winnability and difficulty | `make test-lang` (`tests/kern/lang_balance.py`, from T030) | holistic | SC-005, SC-006 | T033, T037, T046, B |
| Performance | `make bench`, `tests/kern/lang_leistung.py` (from T037) | holistic | step ≤ 4 ms, frame ≤ 8 ms | T037, T046, B |

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

## Tasks

| Task | Verdict | Review (legs, rounds, paid leg?) | Gaps / decision request |
|---|---|---|---|

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

## Where a human should look first

<!-- filled at hand-off -->

## Proposed harness changes

| Lesson | Seen in | Proposed change (AGENTS.md line / sensor / close-task.yml) |
|---|---|---|

## Owner tasks (skipped by the loop)

| Task | Command sheet |
|---|---|
